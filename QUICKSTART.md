# Quick Start Guide - Leia's AI Tutor

## Step 1: Get Your API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key you receive

## Step 2: Create Your .env File

Create a new file named `.env` (exactly this name, including the dot) in the project folder (`leai_tutor`) with this content:

```
GEMINI_API_KEY=paste_your_actual_api_key_here
```

Replace `paste_your_actual_api_key_here` with the key you copied in Step 1.

**Important:** Make sure to paste the actual API key, not the placeholder text!

## Step 3: Run the Application

Open a terminal/command prompt in the project folder and run:

```bash
python -m solara run app.py
```

(Note: If `solara` command is in your PATH, you can also use `solara run app.py`)

The application will start and automatically open in your web browser at http://localhost:8765

## Step 4: Start Learning!

1. **Select a topic** from the dropdown (you'll see "Simplifying Fractions" already available)
2. **Click "Start New Session"** - the AI tutor will greet you and give you a problem
3. **Draw or write your work** on the canvas using your mouse
4. **Type any text answers** or questions in the input box
5. **Click "Submit Answer"** to get feedback from the AI
6. **Continue learning!** The AI will guide you through the topic

## Tips

- **Canvas Tools:**
  - 🖊️ Pen - Draw with black ink
  - ⬜ Eraser - Erase your work
  - 🗑️ Clear Canvas - Start fresh

- **Buttons:**
  - ✅ Submit Answer - Send your work to the AI for feedback
  - 💡 Ask for Help - Get a hint without submitting your work

- **Sessions:**
  - Your progress is automatically saved!
  - Previous sessions appear at the bottom of the page
  - Click any previous session to review or continue it

## Troubleshooting

**"GEMINI_API_KEY not found"**
- Make sure your `.env` file is in the main project folder
- Make sure it's named exactly `.env` (not `.env.txt` or `env`)
- Make sure you pasted the actual API key from Google

**Application won't start**
- Make sure you installed dependencies: `pip install -r requirements.txt`
- Make sure you're in the correct folder

**Canvas not drawing**
- Try clicking the "Pen" button first
- Make sure you're using a modern browser (Chrome, Firefox, Edge)

## Next Steps

Once you're comfortable with the basics, you can:
- Add more topics by creating new markdown files in the `topics/` folder
- Review session history
- Practice at your own pace!

Have fun learning with your AI tutor! 🎓✨

