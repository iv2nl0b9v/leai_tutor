"""
AI service integration with Google Gemini
"""
from typing import List, Optional
from PIL import Image
import google.generativeai as genai

from models import Topic, Message


def get_gemini_model(api_key: Optional[str]):
    """Get configured Gemini model"""
    if not api_key:
        return None
    return genai.GenerativeModel('gemini-2.5-flash')


def create_system_prompt(topic: Topic) -> str:
    """Create the system prompt for the AI tutor"""
    return f"""You are a patient, encouraging AI tutor for a young student named Leia.
Use the Socratic method - guide with questions rather than giving direct answers.
Be warm, supportive, and enthusiastic. Break concepts into small, manageable steps.
Use simple language appropriate for elementary school students.

Topic: {topic.name}

Learning Objectives:
{topic.objectives}

Reference Materials:
{topic.materials}

When the student does well, celebrate their success! When they struggle, provide gentle hints.
Always encourage them to think through the problem step by step."""


def generate_initial_task(topic: Topic, api_key: Optional[str]) -> str:
    """Generate the initial practice problem"""
    model = get_gemini_model(api_key)
    if not model:
        return "Please configure your GEMINI_API_KEY in the .env file."
    
    prompt = f"""{create_system_prompt(topic)}

Generate a friendly greeting and an appropriate first practice problem for this student.
Choose from these example problems or create a similar one:
{chr(10).join('- ' + ex for ex in topic.examples[:3])}

Keep it encouraging and clear!"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating task: {str(e)}"


def get_ai_feedback(topic: Topic, conversation_history: List[Message], 
                   student_text: str, canvas_image: Optional[Image.Image],
                   api_key: Optional[str]) -> str:
    """Get AI feedback on student's work"""
    model = get_gemini_model(api_key)
    if not model:
        return "Please configure your GEMINI_API_KEY in the .env file."
    
    # Build conversation context
    history_text = "\n\n".join([
        f"{'🤖 Tutor' if msg.role == 'tutor' else '👧 Student'}: {msg.content}"
        for msg in conversation_history[-5:]  # Last 5 messages for context
    ])
    
    prompt = f"""{create_system_prompt(topic)}

Conversation so far:
{history_text}

The student has now submitted their work.
Student's text response: {student_text if student_text else "(no text provided)"}

{"The student has also drawn their work on the canvas (see image)." if canvas_image else ""}

Provide constructive, encouraging feedback. If their answer is correct, celebrate and offer the next problem.
If incorrect or incomplete, give a gentle hint to guide them toward the solution.
Remember to be patient, warm, and use age-appropriate language!"""
    
    try:
        if canvas_image:
            # Use Gemini Vision with both text and image
            response = model.generate_content([prompt, canvas_image])
        else:
            # Text only
            response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        return f"Error getting feedback: {str(e)}"

