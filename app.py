from flask import Flask, request, jsonify, render_template
import pytesseract
from PIL import Image
import os
import fitz  # PyMuPDF for PDFs

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Path to tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(file_path):
    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)
    return text

def extract_text_from_pdf(file_path):
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            text = extract_text_from_image(filepath)
        elif file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(filepath)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        # Simple trust score: longer extracted text = higher confidence
        score = min(len(text) // 10, 100)

        return jsonify({'ocr_text': text, 'score': score})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
