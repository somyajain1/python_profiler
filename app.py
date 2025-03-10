import os
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
from csv_profiler import CSVProfiler
import pandas as pd

app = Flask(__name__)

# Configure upload settings
ALLOWED_EXTENSIONS = {'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error="No file selected")
    
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error="No file selected")
    
    if not allowed_file(file.filename):
        return render_template('index.html', error="Invalid file type. Please upload a CSV file")
    
    try:
        # Create a temporary file path
        temp_dir = '/tmp'
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)
        
        # Generate report
        profiler = CSVProfiler(file_path)
        if not profiler.read_csv():
            return render_template('index.html', error="Could not read the CSV file. Please check the file format and encoding.")
            
        report_path = profiler.generate_report(output_dir=temp_dir)
        
        # Return the report
        try:
            return send_file(
                report_path,
                as_attachment=True,
                download_name=f"report_{os.path.splitext(filename)[0]}.pdf"
            )
        finally:
            # Clean up temporary files
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(report_path):
                os.remove(report_path)
        
    except Exception as e:
        error_message = str(e)
        if "UnicodeDecodeError" in error_message:
            error_message = "Encoding error. Please save your CSV file as UTF-8 encoded and try again."
        return render_template('index.html', error=error_message)

# For Vercel, export the app
application = app

if __name__ == "__main__":
    app.run(debug=True) 