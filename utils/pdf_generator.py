import os
import sys
import tempfile
from datetime import datetime

# Add parent directory to path to import report_generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from report_generator import CelebAnalysisReport

def generate_pdf_report(analysis_data, output_filename=None):
    """
    Generate a PDF report from analysis data.
    
    Args:
        analysis_data (dict): Complete analysis results from summarizer
        output_filename (str, optional): Custom filename for the PDF
        
    Returns:
        tuple: (pdf_bytes, filename) or (None, None) if error
    """
    try:
        # Create report generator instance
        report_gen = CelebAnalysisReport()
        
        # Generate temporary filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"facial_analysis_report_{timestamp}.pdf"
        
        # Create temporary file for PDF generation
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_path = temp_file.name
        
        # Generate the PDF report
        report_gen.generate_report(
            image_path=None,  # We don't need the original image in the PDF
            analysis_results=analysis_data,
            output_path=temp_path
        )
        
        # Read the generated PDF
        with open(temp_path, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return pdf_bytes, output_filename
        
    except Exception as e:
        print(f"Error generating PDF report: {str(e)}")
        return None, None

def save_pdf_to_static(pdf_bytes, filename):
    """
    Save PDF to the static/reports directory.
    
    Args:
        pdf_bytes (bytes): PDF file content
        filename (str): Filename for the PDF
        
    Returns:
        str: Path to saved PDF file
    """
    try:
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Save PDF file
        pdf_path = os.path.join(reports_dir, filename)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return pdf_path
        
    except Exception as e:
        print(f"Error saving PDF: {str(e)}")
        return None
