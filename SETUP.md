# Setup Instructions

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `solara` - Web framework
- `ipycanvas` - Drawing canvas
- `google-generativeai` - Gemini AI API
- `python-dotenv` - Environment variable management

### 2. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### 3. Create .env File

Create a file named `.env` in the project root directory with the following content:

```
GEMINI_API_KEY=your_actual_api_key_here
```

Replace `your_actual_api_key_here` with the API key you copied in step 2.

**Important:** The `.env` file is already in `.gitignore` so it won't be committed to git.

### 4. Run the Application

```bash
python -m solara run app.py
```

**Note for Windows users:** If you get "solara is not recognized", use `python -m solara run app.py` instead.

The application will start and open automatically in your browser at:
```
http://localhost:8765
```

## What to Expect

- You'll see a topic selector (currently has "Simplifying Fractions")
- Click "Start New Session" to begin
- The AI tutor will give you a practice problem
- Draw your work on the canvas or type your answer
- Click "Submit Answer" to get feedback
- Your session is automatically saved!

## Adding More Topics

Create new markdown files in the `topics/` folder following this format:

```markdown
# Your Topic Name

## Learning Objectives
- Objective 1
- Objective 2

## Materials
Your teaching content here...

## Example Problems
- Problem 1
- Problem 2
```

The app will automatically load all `.md` files from the topics folder!

## Troubleshooting

### "No topics found"
- Make sure there are `.md` files in the `topics/` folder
- Check that the files follow the correct format

### "GEMINI_API_KEY not found"
- Make sure you created the `.env` file in the project root
- Check that the API key is correct
- Restart the application after creating the `.env` file

### Canvas not working
- Make sure you have a modern browser (Chrome, Firefox, Edge)
- Check browser console for errors

### AI responses are slow
- This is normal - Gemini Vision API takes a few seconds
- Drawing complex images takes longer to process

## Project Structure

```
leai_tutor/
├── app.py                    # Main application
├── requirements.txt          # Python dependencies  
├── .env                      # Your API key (create this!)
├── topics/                   # Learning topics
│   └── simplifying-fractions.md
├── sessions/                 # Auto-saved sessions
│   └── session_*.json
├── README.md                 # Project overview
└── SETUP.md                  # This file
```

