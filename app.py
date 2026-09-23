from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import base64

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


LANGUAGES = [
    "Thanglish", "Tamil", "English", "Hindi", "Telugu", "Malayalam",
    "Kannada", "Bengali", "Marathi", "Gujarati", "Punjabi", "Urdu",
    "Arabic", "Chinese", "Japanese", "Korean", "French", "German",
    "Spanish", "Portuguese", "Russian", "Italian", "Indonesian",
    "Turkish", "Vietnamese", "Thai", "Dutch", "Polish", "Greek",
    "Hebrew", "Swedish", "Norwegian", "Danish", "Finnish",
    "Czech", "Romanian", "Hungarian", "Ukrainian", "Other / Auto"
]


ALLOWED = {"png", "jpg", "jpeg", "webp", "pdf"}


def allowed_file(name):
    return (
        "." in name
        and name.rsplit(".", 1)[1].lower() in ALLOWED
    )


def make_prompt(language):
    return f"""
You are Udhaya Language Analysis AI.

Your ONLY job is to translate the user's supplied
text, image, or PDF content into the selected output language.

Selected output language:
{language}

STRICT RULES:

1. Return ONLY the translation.
2. Do NOT explain the meaning.
3. Do NOT explain the context.
4. Do NOT explain the intent.
5. Do NOT summarize.
6. Do NOT add examples.
7. Do NOT add greetings.
8. Do NOT add notes.
9. Do NOT add headings.
10. Do NOT write "Translation:".
11. Do NOT use quotation marks.
12. Do NOT add extra sentences.
13. Preserve the original meaning accurately.
14. Do not invent information.
15. Translate all sentences in the input.
16. If the input is an image or PDF, translate the readable text.
17. If the selected language is Thanglish, write natural Tamil
    meaning using English/Roman letters.
18. The final response must contain ONLY the translated text.

User content:
"""


def make_voice_prompt(thanglish_text):
    return f"""
Convert the following Thanglish text into natural Tamil script
ONLY for speech pronunciation.

IMPORTANT:
- Return ONLY Tamil script.
- Do NOT explain anything.
- Do NOT translate to a different meaning.
- Preserve exactly the same meaning.
- Do NOT add or remove information.
- Do NOT add quotation marks.
- Do NOT add headings.
- This text will be spoken using a Tamil voice.

Thanglish text:
{thanglish_text}
"""


def gemini_available():
    return bool(os.getenv("GEMINI_API_KEY"))


def get_client():
    from google import genai

    return genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )


def call_gemini(parts, language):
    client = get_client()

    response = client.models.generate_content(
        model=os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite"
        ),
        contents=[
            make_prompt(language),
            *parts
        ]
    )

    return response.text.strip()


def make_thanglish_voice_text(thanglish_text):
    client = get_client()

    response = client.models.generate_content(
        model=os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite"
        ),
        contents=[
            make_voice_prompt(thanglish_text)
        ]
    )

    return response.text.strip()


@app.route("/")
def index():
    return render_template(
        "index.html",
        languages=LANGUAGES
    )


@app.route("/analyze", methods=["POST"])
def analyze():

    language = request.form.get(
        "output_language",
        "Thanglish"
    )

    text = request.form.get(
        "text",
        ""
    ).strip()

    uploaded = request.files.get("file")

    parts = []

    # Text input
    if text:
        parts.append(text)

    # File input
    if uploaded and uploaded.filename:

        if not allowed_file(uploaded.filename):
            return jsonify({
                "error": "Use PNG, JPG, WEBP or PDF."
            }), 400

        filename = secure_filename(
            uploaded.filename
        )

        path = UPLOAD_FOLDER / filename

        uploaded.save(path)

        mime = uploaded.mimetype or "application/octet-stream"

        # PDF
        if mime == "application/pdf":

            with open(path, "rb") as f:
                data = base64.b64encode(
                    f.read()
                ).decode("utf-8")

            parts.append({
                "inline_data": {
                    "mime_type": "application/pdf",
                    "data": data
                }
            })

        # Image
        elif mime.startswith("image/"):

            with open(path, "rb") as f:
                data = base64.b64encode(
                    f.read()
                ).decode("utf-8")

            parts.append({
                "inline_data": {
                    "mime_type": mime,
                    "data": data
                }
            })

    # Nothing entered
    if not parts:
        return jsonify({
            "error": "Paste text or upload an image/PDF first."
        }), 400

    # API key check
    if not gemini_available():
        return jsonify({
            "error": (
                "AI is not connected yet. "
                "Add GEMINI_API_KEY as an environment variable, "
                "then run the website again."
            )
        }), 503

    try:

        # Main translation
        result = call_gemini(
            parts,
            language
        )

        # Voice text
        # For Thanglish, convert Roman Tamil into Tamil script
        # only for speech pronunciation.
        if language == "Thanglish":
            voice_text = make_thanglish_voice_text(result)
            voice_language = "ta-IN"

        else:
            voice_text = result

            voice_language_map = {
                "Tamil": "ta-IN",
                "English": "en-IN",
                "Hindi": "hi-IN",
                "Telugu": "te-IN",
                "Malayalam": "ml-IN",
                "Kannada": "kn-IN",
                "Bengali": "bn-IN",
                "Marathi": "mr-IN",
                "Gujarati": "gu-IN",
                "Punjabi": "pa-IN",
                "Urdu": "ur-IN",
                "Arabic": "ar-SA",
                "Chinese": "zh-CN",
                "Japanese": "ja-JP",
                "Korean": "ko-KR",
                "French": "fr-FR",
                "German": "de-DE",
                "Spanish": "es-ES",
                "Portuguese": "pt-BR",
                "Russian": "ru-RU",
                "Italian": "it-IT",
                "Indonesian": "id-ID",
                "Turkish": "tr-TR",
                "Vietnamese": "vi-VN",
                "Thai": "th-TH",
                "Dutch": "nl-NL",
                "Polish": "pl-PL",
                "Greek": "el-GR",
                "Hebrew": "he-IL",
                "Swedish": "sv-SE",
                "Norwegian": "nb-NO",
                "Danish": "da-DK",
                "Finnish": "fi-FI",
                "Czech": "cs-CZ",
                "Romanian": "ro-RO",
                "Hungarian": "hu-HU",
                "Ukrainian": "uk-UA"
            }

            voice_language = voice_language_map.get(
                language,
                "en-IN"
            )

        return jsonify({
            "result": result,
            "voice_text": voice_text,
            "voice_language": voice_language,
            "language": language
        })

    except Exception as e:

        return jsonify({
            "error": f"AI request failed: {str(e)}"
        }), 500


@app.errorhandler(413)
def too_large(_):

    return jsonify({
        "error": "File is too large. Maximum size is 50 MB."
    }), 413


if __name__ == "__main__":
    app.run(debug=True)