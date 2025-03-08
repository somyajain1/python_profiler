import os
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
from csv_profiler import CSVProfiler
import pandas as pd

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = 'input'
ALLOWED_EXTENSIONS = {'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('output', exist_ok=True)

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
        # Secure the filename and clean it
        filename = secure_filename(file.filename)
        base_filename = os.path.splitext(filename)[0]
        clean_filename = "".join(c if c.isalnum() else "_" for c in base_filename).strip("_")
        
        # Create project-specific directory in input
        project_input_dir = os.path.join(app.config['UPLOAD_FOLDER'], clean_filename)
        os.makedirs(project_input_dir, exist_ok=True)
        
        # Save file in project directory
        file_path = os.path.join(project_input_dir, filename)
        file.save(file_path)
        
        # Generate report
        profiler = CSVProfiler(file_path)
        report_path = profiler.generate_report()
        
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

if __name__ == "__main__":
    # Process files in input directory
    input_dir = 'input'
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
    
    # Look for CSV files in input directory and its subdirectories
    csv_files = []
    for root, dirs, files in os.walk(input_dir):
        csv_files.extend([os.path.join(root, f) for f in files if f.endswith('.csv')])
    
    if csv_files:
        # Process the first CSV file
        csv_file_path = csv_files[0]
        try:
            profiler = CSVProfiler(csv_file_path)
            output_file = profiler.generate_report()
            print(f"Report generated: {output_file}")
        except Exception as e:
            print(f"Error generating report: {str(e)}")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True) 