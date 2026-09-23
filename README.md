# 🤖 Udhaya Language Analysis AI

Multilingual AI website starter with:
- Paste Text
- Upload Image
- Upload PDF
- Multilingual output
- Thanglish output
- AI explanation
- Browser voice
- Copy result
- Responsive UI

## AI model

The backend is prepared for Google's Gemini API using `gemini-3.5-flash-lite` by default.
You can change the model with the `GEMINI_MODEL` environment variable.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Set your Gemini API key as an environment variable:

PowerShell:
```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
```

Then:
```bash
python app.py
```

Open:
http://127.0.0.1:5000

### Important
Never put the API key directly into HTML or JavaScript and never upload a `.env` file containing your secret key to GitHub.

The website uses the AI model for actual analysis when `GEMINI_API_KEY` is available. Without the key, the UI still runs but analysis returns a clear connection message.
