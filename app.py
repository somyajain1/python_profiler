from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from csv_profiler import CSVProfiler
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error="No file selected")
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return render_template('index.html', error="Please select a valid CSV file")
    
    try:
        # Save and process file
        temp_dir = '/tmp'
        os.makedirs(temp_dir, exist_ok=True)
        filename = secure_filename(file.filename)
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)
        
        # Generate report
        profiler = CSVProfiler(file_path)
        if not profiler.read_csv():
            return render_template('index.html', error="Could not read the CSV file")
            
        report_path = profiler.generate_report(output_dir=temp_dir)
        
        # Return and cleanup
        try:
            return send_file(
                report_path,
                as_attachment=True,
                download_name=f"report_{os.path.splitext(filename)[0]}.pdf"
            )
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(report_path):
                os.remove(report_path)
        
    except Exception as e:
        return render_template('index.html', error=str(e))

# For Vercel
application = app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 