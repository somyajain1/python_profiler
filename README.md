# CSV Profiler

A powerful Python application that provides detailed analysis and insights for CSV files. The application generates comprehensive PDF reports with AI-driven insights, statistical analysis, and visualizations.

## Features

- **AI-Driven Insights**: Automatically identifies patterns, correlations, and key findings in your data
- **Comprehensive Analysis**: Detailed statistical analysis of each column
- **Data Quality Assessment**: Identifies missing values, outliers, and data quality issues
- **Primary Key Detection**: Automatically detects potential primary key columns
- **Correlation Analysis**: Identifies and visualizes strong correlations between numeric columns
- **Trend Analysis**: Analyzes trends and distributions in numeric columns
- **Interactive Web Interface**: Easy-to-use web interface for file upload and report generation
- **PDF Reports**: Generates detailed PDF reports with visualizations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/somyajain1/python_profiler.git
cd python_profiler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the web server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Upload your CSV file using the web interface
4. The application will generate a detailed PDF report with analysis and insights

## Project Structure

```
python_profiler/
├── input/              # Directory for input CSV files
├── output/            # Directory for generated reports
├── templates/         # HTML templates
│   └── index.html    # Main web interface template
├── app.py            # Flask web application
├── csv_profiler.py   # Core profiling logic
└── requirements.txt  # Project dependencies
```

## Dependencies

- Python 3.6+
- Flask
- Pandas
- NumPy
- Matplotlib
- Seaborn
- FPDF
- Humanize

## Features in Detail

1. **Data Quality Assessment**
   - Overall data completeness percentage
   - Missing value analysis
   - Dataset dimensions and structure

2. **Primary Key Analysis**
   - Identification of unique value columns
   - Validation of potential primary keys

3. **Correlation Analysis**
   - Strong correlation detection
   - Correlation heatmap visualization
   - Detailed correlation explanations

4. **Trend Analysis**
   - Trend direction detection
   - Distribution pattern analysis
   - Statistical measures (mean, standard deviation)

5. **Data Type Distribution**
   - Analysis of numeric vs categorical columns
   - Data type balance assessment

6. **Outlier Detection**
   - IQR-based outlier detection
   - Column-specific outlier counts
   - Recommendations for handling outliers

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 