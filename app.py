"""
Leia's AI Tutor - Interactive tutoring application with canvas drawing
"""
import os
import base64
from io import BytesIO
from pathlib import Path
from dataclasses import asdict
from datetime import datetime
from typing import Dict

import solara
from ipycanvas import Canvas
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# Import from our modules
from models import Topic, Message, Session
from topic_loader import load_all_topics
from session_manager import save_session, load_session, list_sessions
from ai_service import generate_initial_task, get_ai_feedback

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Directories
TOPICS_DIR = Path("topics")
SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)


# ============================================================================
# Solara Components
# ============================================================================

# Reactive state variables
selected_topic = solara.reactive(None)
current_session = solara.reactive(None)
student_input = solara.reactive("")
drawing_canvas = solara.reactive(None)
is_loading = solara.reactive(False)
status_message = solara.reactive("")


@solara.component
def DrawingCanvas():
    """Interactive canvas component for drawing"""
    is_drawing = solara.use_reactive(False)
    current_color = solara.use_reactive("black")
    line_width = solara.use_reactive(3)
    canvas_created = solara.use_reactive(False)
    
    # Only create canvas if we have a valid kernel context (not during initialization)
    def create_canvas():
        # Check if we're in a real kernel context
        try:
            kernel_id = solara.get_kernel_id()
            if kernel_id:
                canvas = Canvas(width=700, height=500)
                canvas.fill_style = "white"
                canvas.fill_rect(0, 0, 700, 500)
                canvas.stroke_style = current_color.value
                canvas.line_width = line_width.value
                drawing_canvas.value = canvas
                canvas_created.value = True
                return canvas
        except:
            pass
        return None
    
    canvas = solara.use_memo(create_canvas, [])
    
    def clear_canvas():
        """Clear the canvas"""
        if canvas:
            canvas.fill_style = "white"
            canvas.fill_rect(0, 0, 700, 500)
            canvas.stroke_style = current_color.value
    
    def set_pen():
        current_color.value = "black"
        if canvas:
            canvas.stroke_style = "black"
            canvas.line_width = 3
    
    def set_eraser():
        current_color.value = "white"
        if canvas:
            canvas.stroke_style = "white"
            canvas.line_width = 20
    
    with solara.Column(style={"border": "2px solid #ddd", "padding": "10px", "border-radius": "8px"}):
        with solara.Row(gap="10px", style={"margin-bottom": "10px"}):
            solara.Button("🖊️ Pen", on_click=set_pen, color="primary" if current_color.value == "black" else None)
            solara.Button("⬜ Eraser", on_click=set_eraser, color="primary" if current_color.value == "white" else None)
            solara.Button("🗑️ Clear Canvas", on_click=clear_canvas, color="error")
        
        if canvas:
            solara.display(canvas)
        else:
            solara.Text("Canvas will load when you open the page in your browser...")


@solara.component  
def ChatHistory():
    """Display conversation history"""
    session = current_session.value
    
    with solara.Column(style={
        "height": "500px", 
        "overflow-y": "auto", 
        "padding": "15px",
        "border": "2px solid #ddd",
        "border-radius": "8px",
        "background-color": "#f9f9f9"
    }):
        if not session or not session.messages:
            solara.Markdown("*No messages yet. Start a new session to begin!*")
        else:
            for msg_dict in session.messages:
                msg = Message(**msg_dict)
                
                if msg.role == "tutor":
                    with solara.Card(style={"background-color": "#e3f2fd", "margin-bottom": "10px"}):
                        solara.Markdown(f"**🤖 AI Tutor:** {msg.content}")
                        if msg.timestamp:
                            solara.Text(f"_{msg.timestamp}_", style={"font-size": "0.8em", "color": "#666"})
                else:
                    with solara.Card(style={"background-color": "#fff3e0", "margin-bottom": "10px"}):
                        solara.Markdown(f"**👧 Leia:** {msg.content}")
                        
                        if msg.canvas_image:
                            try:
                                # Decode and display canvas image
                                img_data = base64.b64decode(msg.canvas_image.split(',')[1] if ',' in msg.canvas_image else msg.canvas_image)
                                img = Image.open(BytesIO(img_data))
                                solara.Image(img, width="300px")
                            except Exception as e:
                                solara.Text(f"[Canvas image - error displaying: {e}]")
                        
                        if msg.timestamp:
                            solara.Text(f"_{msg.timestamp}_", style={"font-size": "0.8em", "color": "#666"})


@solara.component
def SessionControls():
    """Controls for managing sessions"""
    topics = load_all_topics(TOPICS_DIR)
    topic_names = list(topics.keys())
    
    if not topic_names:
        solara.Error("No topics found! Please add markdown files to the 'topics/' folder.")
        return
    
    def start_new_session():
        """Start a new tutoring session"""
        if not selected_topic.value:
            status_message.value = "Please select a topic first!"
            return
        
        is_loading.value = True
        status_message.value = "Starting new session..."
        
        topic = topics[selected_topic.value]
        
        # Generate initial task
        initial_message = generate_initial_task(topic, GEMINI_API_KEY)
        
        # Create new session
        session = Session(
            topic_name=topic.name,
            messages=[{
                'role': 'tutor',
                'content': initial_message,
                'canvas_image': None,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }],
            created_at=datetime.now().isoformat(),
            status='active'
        )
        
        # Save and set as current
        save_session(session, SESSIONS_DIR)
        current_session.value = session
        student_input.value = ""
        
        is_loading.value = False
        status_message.value = "Session started! 🎉"
    
    def load_existing_session(session_id: str):
        """Load an existing session"""
        session = load_session(session_id, SESSIONS_DIR)
        if session:
            current_session.value = session
            if session.topic_name in topics:
                selected_topic.value = session.topic_name
            status_message.value = f"Loaded session from {session.created_at}"
        else:
            status_message.value = "Error loading session"
    
    with solara.Card("Session Controls"):
        with solara.Column(gap="10px"):
            # Topic selector
            if selected_topic.value is None and topic_names:
                selected_topic.value = topic_names[0]
            
            solara.Select(
                label="Select Topic",
                value=selected_topic,
                values=topic_names
            )
            
            # New session button
            solara.Button(
                "🎓 Start New Session",
                on_click=start_new_session,
                color="primary",
                disabled=is_loading.value,
                block=True
            )
            
            # Status message
            if status_message.value:
                solara.Info(status_message.value)
            
            # List previous sessions
            sessions = list_sessions(SESSIONS_DIR)
            if sessions:
                solara.Markdown("### 📚 Previous Sessions")
                for sess in sessions[:5]:  # Show last 5 sessions
                    with solara.Row(gap="5px"):
                        solara.Button(
                            f"📖 {sess['topic_name']} - {sess['created_at'][:10]}",
                            on_click=lambda sid=sess['session_id']: load_existing_session(sid),
                            text=True,
                            style={"font-size": "0.9em"}
                        )


@solara.component
def StudentInputArea():
    """Area for student to type and submit answers"""
    
    def submit_answer():
        """Submit student's answer and get AI feedback"""
        if not current_session.value:
            status_message.value = "Please start a session first!"
            return
        
        text = student_input.value.strip()
        canvas = drawing_canvas.value
        
        if not text and not canvas:
            status_message.value = "Please write something or draw on the canvas!"
            return
        
        is_loading.value = True
        status_message.value = "Getting feedback from AI tutor..."
        
        # Capture canvas as image
        canvas_image_b64 = None
        canvas_img = None
        
        if canvas:
            try:
                # Get canvas image data
                img_data = canvas.get_image_data()
                # Convert to PIL Image
                canvas_img = Image.fromarray(img_data.astype('uint8'), 'RGBA')
                # Convert to RGB (remove alpha)
                canvas_img = canvas_img.convert('RGB')
                # Encode to base64
                buffer = BytesIO()
                canvas_img.save(buffer, format='PNG')
                canvas_image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            except Exception as e:
                print(f"Error capturing canvas: {e}")
        
        # Create student message
        student_msg = Message(
            role='student',
            content=text if text else "(see canvas)",
            canvas_image=canvas_image_b64,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Create new messages list with student message (immutable update)
        new_messages = current_session.value.messages + [asdict(student_msg)]
        
        # Create new session with updated messages to trigger UI update
        current_session.value = Session(
            topic_name=current_session.value.topic_name,
            messages=new_messages,
            created_at=current_session.value.created_at,
            status=current_session.value.status,
            session_id=current_session.value.session_id
        )
        
        # Get AI feedback
        topics = load_all_topics(TOPICS_DIR)
        topic = topics.get(current_session.value.topic_name)
        
        if topic:
            # Convert message dicts back to Message objects for AI
            msg_objects = [Message(**m) for m in current_session.value.messages[:-1]]
            
            feedback = get_ai_feedback(topic, msg_objects, text, canvas_img, GEMINI_API_KEY)
            
            # Create tutor response message
            tutor_msg = Message(
                role='tutor',
                content=feedback,
                canvas_image=None,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Add tutor message and create new session (immutable update)
            new_messages_with_tutor = current_session.value.messages + [asdict(tutor_msg)]
            current_session.value = Session(
                topic_name=current_session.value.topic_name,
                messages=new_messages_with_tutor,
                created_at=current_session.value.created_at,
                status=current_session.value.status,
                session_id=current_session.value.session_id
            )
            
            # Save session
            save_session(current_session.value, SESSIONS_DIR)
        
        # Clear input
        student_input.value = ""
        
        is_loading.value = False
        status_message.value = "Feedback received! ✨"
    
    def ask_for_help():
        """Ask the AI for help"""
        student_input.value = "I need help with this problem. Can you give me a hint?"
        submit_answer()
    
    with solara.Card("Your Answer"):
        solara.InputText(
            label="Type your answer or question here...",
            value=student_input,
            continuous_update=True,
            style={"width": "100%"}
        )
        
        with solara.Row(gap="10px", style={"margin-top": "10px"}):
            solara.Button(
                "✅ Submit Answer",
                on_click=submit_answer,
                color="success",
                disabled=is_loading.value
            )
            solara.Button(
                "💡 Ask for Help",
                on_click=ask_for_help,
                color="warning",
                disabled=is_loading.value
            )


@solara.component
def Page():
    """Main application page"""
    
    with solara.Column(gap="20px", style={"padding": "20px", "max-width": "1400px", "margin": "0 auto"}):
        # Header
        solara.Title("🎓 Leia's AI Tutor")
        solara.Markdown("*Learn with an AI tutor that can see your work!*")
        
        # Check API key
        if not GEMINI_API_KEY:
            solara.Error("⚠️ GEMINI_API_KEY not found! Please create a .env file with your API key.")
            solara.Markdown("Get your API key from: https://makersuite.google.com/app/apikey")
            return
        
        # Session controls
        SessionControls()
        
        # Main layout: Canvas and Chat side by side
        with solara.Columns([1, 1], gutters_dense=False):
            with solara.Column():
                solara.Markdown("### 🎨 Drawing Canvas")
                DrawingCanvas()
            
            with solara.Column():
                solara.Markdown("### 💬 Conversation")
                ChatHistory()
        
        # Student input area
        StudentInputArea()


# Run the app
if __name__ == "__main__":
    # This will be called by: solara run app.py
    pass

