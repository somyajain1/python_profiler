import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime
import humanize
from fpdf import FPDF
import seaborn as sns
from typing import Dict, Any
from scipy import stats

class CSVProfiler:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None
        self.stats = {}
        self.insights = {}
        
    def read_csv(self) -> bool:
        """Read CSV file with automatic encoding detection."""
        encodings = ['utf-8', 'utf-16', 'latin1']
        delimiters = [',', ';', '\t']
        
        for encoding in encodings:
            for delimiter in delimiters:
                try:
                    print(f"Trying encoding: {encoding}, delimiter: {delimiter}")
                    self.df = pd.read_csv(self.csv_path, encoding=encoding, sep=delimiter)
                    if len(self.df.columns) > 1:  # Check if we got multiple columns
                        print(f"Successfully read CSV with {len(self.df.columns)} columns")
                        return True
                except Exception as e:
                    print(f"Failed with encoding {encoding}, delimiter {delimiter}: {str(e)}")
        return False

    def _analyze_correlations(self) -> Dict:
        """Analyze correlations between numeric columns."""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = self.df[numeric_cols].corr()
            
            # Find strong correlations
            strong_correlations = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    corr = corr_matrix.iloc[i, j]
                    if abs(corr) > 0.5:  # Consider correlations stronger than 0.5
                        strong_correlations.append({
                            'col1': numeric_cols[i],
                            'col2': numeric_cols[j],
                            'correlation': corr
                        })
            
            # Create correlation heatmap
            plt.figure(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
            plt.title('Correlation Heatmap')
            plt.tight_layout()
            heatmap_path = 'correlation_heatmap.png'
            plt.savefig(heatmap_path)
            plt.close()
            
            return {
                'strong_correlations': strong_correlations,
                'heatmap_path': heatmap_path
            }
        return None

    def _identify_primary_keys(self) -> list:
        """Identify potential primary key columns."""
        primary_keys = []
        for column in self.df.columns:
            if self.df[column].nunique() == len(self.df) and self.df[column].notna().all():
                primary_keys.append(column)
        return primary_keys

    def _analyze_trends(self) -> Dict:
        """Analyze trends in numeric columns."""
        trends = {}
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            series = self.df[col].dropna()
            if len(series) > 1:
                # Basic trend analysis
                trend = 'increasing' if series.corr(pd.Series(range(len(series)))) > 0.5 else \
                       'decreasing' if series.corr(pd.Series(range(len(series)))) < -0.5 else \
                       'stable'
                
                # Distribution analysis
                skewness = series.skew()
                distribution = 'normal' if abs(skewness) < 0.5 else \
                             'right-skewed' if skewness > 0.5 else \
                             'left-skewed'
                
                trends[col] = {
                    'trend': trend,
                    'distribution': distribution,
                    'skewness': skewness
                }
        return trends

    def _generate_ai_insights(self) -> Dict:
        """Generate detailed AI-driven insights from the data."""
        insights = {
            'primary_keys': self._identify_primary_keys(),
            'trends': self._analyze_trends(),
            'correlations': self._analyze_correlations(),
            'key_findings': []
        }
        
        # Analyze data quality
        total_missing = self.df.isna().sum().sum()
        total_cells = self.df.size
        data_quality = (1 - total_missing/total_cells) * 100
        missing_columns = self.df.columns[self.df.isna().any()].tolist()
        
        # Data Quality insights
        insights['key_findings'].extend([
            f"Data Quality Assessment:\nOverall data completeness is {data_quality:.1f}%, with {total_missing:,} missing values across {len(missing_columns)} columns.",
            f"Dataset Dimensions and Structure:\nThe dataset contains {len(self.df):,} records with {len(self.df.columns)} attributes, providing a comprehensive view of the data."
        ])
        
        # Primary Key insights
        if insights['primary_keys']:
            unique_counts = [f"{key} ({self.df[key].nunique():,} unique values)" for key in insights['primary_keys']]
            insights['key_findings'].append(
                f"Primary Key Analysis:\nIdentified {len(insights['primary_keys'])} potential primary key(s): {', '.join(unique_counts)}. These columns have unique values for each record and can be used as reliable identifiers."
            )
        
        # Correlation insights
        if insights['correlations'] and insights['correlations']['strong_correlations']:
            for corr in insights['correlations']['strong_correlations']:
                direction = "positive" if corr['correlation'] > 0 else "negative"
                insights['key_findings'].append(
                    f"Strong {direction} correlation ({abs(corr['correlation']):.2f}) between {corr['col1']} and {corr['col2']}:\n"
                    f"This indicates that as {corr['col1']} {'increases' if corr['correlation'] > 0 else 'decreases'}, "
                    f"{corr['col2']} tends to {'increase' if corr['correlation'] > 0 else 'decrease'} proportionally."
                )
        
        # Trend and Distribution insights
        for col, trend_info in insights['trends'].items():
            if trend_info['trend'] != 'stable':
                mean_val = self.df[col].mean()
                std_val = self.df[col].std()
                insights['key_findings'].append(
                    f"Trend Analysis for {col}:\n"
                    f"Shows a {trend_info['trend']} trend with {trend_info['distribution']} distribution. "
                    f"Mean value is {mean_val:.2f} with a standard deviation of {std_val:.2f}."
                )
        
        # Add data type distribution insight
        numeric_cols = len(self.df.select_dtypes(include=[np.number]).columns)
        categorical_cols = len(self.df.select_dtypes(exclude=[np.number]).columns)
        insights['key_findings'].append(
            f"Data Type Distribution:\n"
            f"The dataset contains {numeric_cols} numeric columns and {categorical_cols} categorical columns, "
            f"suggesting a {'balanced' if abs(numeric_cols - categorical_cols) <= 2 else 'predominantly ' + ('numeric' if numeric_cols > categorical_cols else 'categorical')} dataset."
        )
        
        # Add outlier detection insight if applicable
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            outlier_info = []
            for col in numeric_columns:
                q1 = self.df[col].quantile(0.25)
                q3 = self.df[col].quantile(0.75)
                iqr = q3 - q1
                outliers = ((self.df[col] < (q1 - 1.5 * iqr)) | (self.df[col] > (q3 + 1.5 * iqr))).sum()
                if outliers > 0:
                    outlier_info.append(f"{col} ({outliers} outliers)")
            
            if outlier_info:
                insights['key_findings'].append(
                    f"Outlier Detection:\n"
                    f"Found potential outliers in the following numeric columns: {', '.join(outlier_info)}. "
                    f"These may require further investigation or special handling."
                )
        
        return insights

    def analyze(self) -> bool:
        """Analyze the CSV file and generate statistics."""
        try:
            # Read the file
            if not self.read_csv():
                return False
            
            # File level statistics
            file_stats = {
                'filename': os.path.basename(self.csv_path),
                'file_size': humanize.naturalsize(os.path.getsize(self.csv_path)),
                'rows': len(self.df),
                'columns': len(self.df.columns),
                'missing_cells': self.df.isna().sum().sum(),
                'duplicate_rows': self.df.duplicated().sum()
            }
            
            # Generate AI insights
            self.insights = self._generate_ai_insights()
            
            # Column level statistics
            column_stats = {}
            for column in self.df.columns:
                stats = {
                    'type': str(self.df[column].dtype),
                    'missing': self.df[column].isna().sum(),
                    'unique': self.df[column].nunique(),
                }
                
                # Numeric column statistics
                if np.issubdtype(self.df[column].dtype, np.number):
                    stats.update({
                        'mean': self.df[column].mean(),
                        'std': self.df[column].std(),
                        'min': self.df[column].min(),
                        'max': self.df[column].max(),
                        '25%': self.df[column].quantile(0.25),
                        '50%': self.df[column].quantile(0.50),
                        '75%': self.df[column].quantile(0.75)
                    })
                    
                    # Create distribution plot
                    plt.figure(figsize=(8, 4))
                    sns.histplot(data=self.df[column].dropna(), bins=30)
                    plt.title(f'Distribution of {column}')
                    plt.savefig(f'temp_{column}_dist.png')
                    plt.close()
                    stats['plot'] = f'temp_{column}_dist.png'
                
                # Categorical column statistics
                else:
                    value_counts = self.df[column].value_counts()
                    stats['top_values'] = value_counts.head(10).to_dict()
                    
                    # Create bar plot for categorical data
                    if len(value_counts) <= 20:  # Only plot if not too many categories
                        plt.figure(figsize=(8, 4))
                        value_counts.head(10).plot(kind='bar')
                        plt.title(f'Top 10 Values in {column}')
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        plt.savefig(f'temp_{column}_dist.png')
                        plt.close()
                        stats['plot'] = f'temp_{column}_dist.png'
                
                column_stats[column] = stats
            
            self.stats = {
                'file_stats': file_stats,
                'column_stats': column_stats
            }
            return True
            
        except Exception as e:
            print(f"Error analyzing file: {str(e)}")
            return False

    def generate_report(self, output_dir: str = "/tmp/output") -> str:
        """Generate PDF report with the analysis results."""
        if not self.stats:
            if not self.analyze():
                raise Exception("Analysis failed")
        
        # Get base filename without extension
        base_filename = os.path.splitext(os.path.basename(self.csv_path))[0]
        # Clean filename (remove special characters)
        clean_filename = "".join(c if c.isalnum() else "_" for c in base_filename).strip("_")
        
        # Create project-specific directory in output
        project_dir = os.path.join(output_dir, clean_filename)
        os.makedirs(project_dir, exist_ok=True)
        
        # Create a temporary directory for plots
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix='csv_profiler_')
        
        try:
            # Initialize PDF
            pdf = FPDF()
            pdf.set_margins(10, 10, 10)  # Set left, top, right margins
            pdf.add_page()
            
            # Title
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'CSV Profile Report', ln=True, align='C')
            pdf.ln(10)
            
            # AI Insights Section
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'AI-Driven Insights', ln=True)
            pdf.set_font('Arial', '', 10)
            
            # Key Findings
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Key Findings:', ln=True)
            pdf.set_font('Arial', '', 10)
            for finding in self.insights['key_findings']:
                pdf.set_x(15)  # Indent the findings
                pdf.multi_cell(180, 8, f"- {finding}")
            
            # Correlation Heatmap
            if self.insights['correlations'] and 'heatmap_path' in self.insights['correlations']:
                heatmap_path = os.path.join(temp_dir, 'correlation_heatmap.png')
                plt.figure(figsize=(10, 8))
                sns.heatmap(self.df[self.df.select_dtypes(include=[np.number]).columns].corr(), 
                           annot=True, cmap='coolwarm', center=0)
                plt.title('Correlation Heatmap')
                plt.tight_layout()
                plt.savefig(heatmap_path)
                plt.close()
                
                pdf.add_page()
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Correlation Analysis:', ln=True)
                pdf.image(heatmap_path, x=10, y=None, w=190)
            
            # File Statistics
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'File Overview', ln=True)
            pdf.set_font('Arial', '', 10)
            
            file_stats = self.stats['file_stats']
            for key, value in file_stats.items():
                pdf.cell(0, 8, f"{key.replace('_', ' ').title()}: {value}", ln=True)
            
            # Column Analysis
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Column Analysis', ln=True)
            
            for column, stats in self.stats['column_stats'].items():
                pdf.add_page()
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f"Column: {column}", ln=True)
                
                # Add primary key indicator
                if column in self.insights['primary_keys']:
                    pdf.set_font('Arial', 'B', 10)
                    pdf.set_text_color(0, 128, 0)  # Green color
                    pdf.cell(0, 8, "Potential Primary Key", ln=True)
                    pdf.set_text_color(0, 0, 0)  # Reset to black
                
                pdf.set_font('Arial', '', 10)
                # Basic stats
                pdf.cell(0, 8, f"Type: {stats['type']}", ln=True)
                pdf.cell(0, 8, f"Missing Values: {stats['missing']}", ln=True)
                pdf.cell(0, 8, f"Unique Values: {stats['unique']}", ln=True)
                
                # Numeric stats
                if 'mean' in stats:
                    pdf.cell(0, 8, f"Mean: {stats['mean']:.2f}", ln=True)
                    pdf.cell(0, 8, f"Standard Deviation: {stats['std']:.2f}", ln=True)
                    pdf.cell(0, 8, f"Min: {stats['min']}", ln=True)
                    pdf.cell(0, 8, f"Max: {stats['max']}", ln=True)
                    pdf.cell(0, 8, f"25th Percentile: {stats['25%']:.2f}", ln=True)
                    pdf.cell(0, 8, f"Median: {stats['50%']:.2f}", ln=True)
                    pdf.cell(0, 8, f"75th Percentile: {stats['75%']:.2f}", ln=True)
                    
                    # Add trend information if available
                    if column in self.insights['trends']:
                        trend_info = self.insights['trends'][column]
                        pdf.ln(5)
                        pdf.set_font('Arial', 'B', 10)
                        pdf.cell(0, 8, "Trend Analysis:", ln=True)
                        pdf.set_font('Arial', '', 10)
                        pdf.cell(0, 8, f"Trend: {trend_info['trend'].title()}", ln=True)
                        pdf.cell(0, 8, f"Distribution: {trend_info['distribution'].title()}", ln=True)
                
                # Categorical stats
                if 'top_values' in stats:
                    pdf.ln(5)
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(0, 8, "Top Values:", ln=True)
                    pdf.set_font('Arial', '', 10)
                    for val, count in stats['top_values'].items():
                        pdf.cell(0, 8, f"{val}: {count}", ln=True)
                
                # Add plot if available
                if 'plot' in stats:
                    # Save plots in the project directory
                    plot_path = os.path.join(project_dir, f'plot_{column}.png')
                    os.rename(stats['plot'], plot_path)
                    pdf.image(plot_path, x=10, y=None, w=190)
                    os.remove(plot_path)  # Clean up
            
            # Save the report with a clean name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            report_name = f"{clean_filename}_profile_report_{timestamp}.pdf"
            output_file = os.path.join(project_dir, report_name)
            pdf.output(output_file)
            
            return output_file
            
        finally:
            # Clean up temporary files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python csv_profiler.py <csv_file>")
        sys.exit(1)
        
    profiler = CSVProfiler(sys.argv[1])
    output_file = profiler.generate_report()
    print(f"Report generated: {output_file}") 