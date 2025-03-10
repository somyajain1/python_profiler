import os
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
from csv_profiler import CSVProfiler
import pandas as pd

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)

# Configure upload settings
UPLOAD_FOLDER = '/tmp/input'  # Use /tmp for Vercel
OUTPUT_FOLDER = '/tmp/output'  # Use /tmp for Vercel
ALLOWED_EXTENSIONS = {'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Only create directories when needed
def ensure_directories():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading template: {str(e)}", 500

@app.route('/upload', methods=['POST'])
def upload_file():
    ensure_directories()  # Create directories only when uploading
    
    if 'file' not in request.files:
        return render_template('index.html', error="No file selected")
    
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error="No file selected")
    
    if not allowed_file(file.filename):
        return render_template('index.html', error="Invalid file type. Please upload a CSV file")
    
    try:
        # Secure the filename and clean it
        filename = secure_filename(file.filename)
        base_filename = os.path.splitext(filename)[0]
        clean_filename = "".join(c if c.isalnum() else "_" for c in base_filename).strip("_")
        
        # Create project-specific directory in input
        project_input_dir = os.path.join(UPLOAD_FOLDER, clean_filename)
        os.makedirs(project_input_dir, exist_ok=True)
        
        # Save file in project directory
        file_path = os.path.join(project_input_dir, filename)
        file.save(file_path)
        
        # Generate report
        profiler = CSVProfiler(file_path)
        if not profiler.read_csv():  # First try to read the CSV
            return render_template('index.html', error="Could not read the CSV file. Please check the file format and encoding.")
            
        report_path = profiler.generate_report(output_dir=OUTPUT_FOLDER)
        
        return render_template('index.html', 
                             success=True,
                             message="Report generated successfully!",
                             report_filepath=report_path)
        
    except Exception as e:
        error_message = str(e)
        if "UnicodeDecodeError" in error_message:
            error_message = "Encoding error. Please save your CSV file as UTF-8 encoded and try again."
        
        return render_template('index.html', error=error_message)

@app.route('/download/<path:filepath>')
def download_report(filepath):
    try:
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return str(e), 404

# For Vercel, we need to export the app
app.debug = True
application = app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 