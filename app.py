import flask
from flask_cors import CORS
import PyPDF2
import docx
from collections import Counter
from io import BytesIO
import re

app = flask.Flask(__name__)
CORS(app)  # allow frontend to talk to backend


@app.route('/')
def index():
    return flask.send_from_directory('.', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return flask.send_from_directory('.', filename)


@app.route('/summarize', methods=['POST'])
def summarize():
    if 'file' not in flask.request.files:
        return flask.jsonify({"error": "No file provided"}), 400

    file = flask.request.files['file']
    text = ""

    # read file into memory once, use BytesIO for parsing
    file_bytes = file.read()
    fname = (file.filename or '').lower()

    if fname.endswith('.pdf'):
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text() or ''
            text += page_text
    elif fname.endswith('.txt'):
        try:
            text = file_bytes.decode('utf-8')
        except Exception:
            text = file_bytes.decode('utf-8', errors='ignore')
    elif fname.endswith('.docx'):
        doc = docx.Document(BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
    else:
        return flask.jsonify({"error": "Only PDF, TXT, or DOCX supported"}), 400

    if not text or not text.strip():
        return flask.jsonify({"error": "Uploaded file contains no extractable text"}), 400

    # Summarizer (simple frequency-based extractor)
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if not sentences:
        return flask.jsonify({"error": "No sentences found in document"}), 400

    words = [w.lower() for w in re.findall(r"\w+", text)]
    freq = Counter(words)

    def score_sentence(s):
        return sum(freq.get(w.lower(), 0) for w in re.findall(r"\w+", s))

    ranked = sorted(sentences, key=score_sentence, reverse=True)
    num_sentences = min(5, len(ranked))
    summary = ranked[:num_sentences]

    return flask.jsonify({"summary": summary})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
