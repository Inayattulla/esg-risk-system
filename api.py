
import json
import os
REPORTS_FILE = 'reports.json'

# Load existing reports if the file exists
if os.path.exists(REPORTS_FILE):
    with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
        stored_reports = json.load(f)
else:
    stored_reports = {}

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import subprocess
import traceback

from extract_text import extract_text_from_pdf
from analyze_text import preprocess_text
from esg_scorecard import generate_esg_scorecard
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# File upload folder
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

REPORTS_FILE = '/tmp/reports.json'
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"[INFO] File saved to: {filepath}")

        # Run extract_text.py using subprocess
        print(f"[INFO] Running extract_text.py on {filepath}")
        result = subprocess.run(
            ["python", "extract_text.py", filepath],
            capture_output=True,
            text=True
        )

        print("[DEBUG] extract_text.py stdout:", result.stdout)
        print("[DEBUG] extract_text.py stderr:", result.stderr)
        if result.returncode != 0:
            return jsonify({
                "error": "Text extraction failed",
                "details": result.stderr
            }), 500

        # Read extracted text
        with open("extracted_text.txt", "r", encoding="utf-8") as f:
            raw_text = f.read()

        # Run NLP + ESG analysis
        cleaned_text = preprocess_text(raw_text)
        summary, analysis_data = generate_esg_scorecard(cleaned_text)

         # Save report to dictionary
        stored_reports[filename] = {
        "summary": summary,
        "analysis_data": analysis_data
    }

        # Persist to reports.json
        with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stored_reports, f, indent=2, ensure_ascii=False)


        print("[INFO] Summary generated")
        print("📄 Final summary:", summary)
        return jsonify({
            "summary": summary,
            "analysis_data": analysis_data  # Send structured data to frontend
        })

    except Exception as e:
        print("[ERROR] Exception in /upload:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500

if __name__ == '__main__':
    os.environ["FLASK_ENV"] = "development"
    app.run(debug=True, use_reloader=False) 
