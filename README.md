# Leia's AI Tutor

An AI-powered tutoring application built with Python, featuring an interactive canvas for drawing and writing, powered by Google's Gemini Vision API.

## Features

- 🎨 Interactive canvas for drawing and writing
- 🤖 AI tutor powered by Gemini Vision API
- 📚 Topic-based learning with markdown files
- 💾 Session history saved as JSON
- 👧 Designed for young learners

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up your API key:**
   - Get a Google Gemini API key from: https://makersuite.google.com/app/apikey
   - Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_api_key_here
```

3. **Run the application:**
```bash
python -m solara run app.py
```

4. **Open in browser:**
   - Navigate to http://localhost:8765

## Adding New Topics

Create a new markdown file in the `topics/` folder with the following structure:

```markdown
# Topic Name

## Learning Objectives
- Objective 1
- Objective 2

## Materials
[Your teaching content here - can be as long as needed]

## Example Problems
- Problem 1
- Problem 2
```

## Project Structure

```
leai_tutor/
├── app.py                  # Main application (Solara UI)
├── models.py               # Data models (Topic, Message, Session)
├── topic_loader.py         # Topic parsing and loading
├── session_manager.py      # Session storage and management
├── ai_service.py           # Gemini AI integration
├── requirements.txt        # Dependencies
├── pytest.ini              # Test configuration
├── test_models.py          # Tests for data models
├── test_topic_loader.py    # Tests for topic loader
├── test_session_manager.py # Tests for session manager
├── tests_README.md         # Testing documentation
├── .env                    # API keys (create this)
├── topics/                 # Learning topics (markdown files)
├── sessions/               # Session history (auto-generated)
└── README.md               # This file
```

## Usage

1. Select a topic from the dropdown
2. Click "Start New Session"
3. Read the AI tutor's instructions
4. Draw or write your work on the canvas
5. Type any text answers or questions
6. Click "Submit Answer" to get feedback
7. Sessions are automatically saved

## Testing

The project includes comprehensive unit tests for the core functionality.

To run tests:
```bash
pytest
```

For more details, see `tests_README.md`.

## Technologies

- **Solara**: Python web framework
- **ipycanvas**: Interactive drawing canvas
- **Google Gemini Vision API**: AI analysis
- **Python 3.8+**: Backend logic
- **pytest**: Testing framework
