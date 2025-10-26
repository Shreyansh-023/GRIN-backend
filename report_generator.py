from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import json
import os

class CelebAnalysisReport:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Title style
        self.title_style = ParagraphStyle(
            'TitleStyle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=1,
            textColor=colors.black
        )
        
        # Main heading style
        self.heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.black
        )
        
        # Style for section titles
        self.section_title_style = ParagraphStyle(
            'SectionTitleStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.black,
            leading=14
        )
        
        # Style for section content
        self.content_style = ParagraphStyle(
            'ContentStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=0,
            spaceAfter=12,
            leading=14
        )
        
        # Date style
        self.date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Italic'],
            fontSize=9,
            textColor=colors.gray,
            alignment=1
        )

    def fix_bullet_points(self, text):
        """Convert bullet points to proper HTML format for ReportLab"""
        lines = text.split('\n')
        formatted_lines = []
        for line in lines:
            if line.strip().startswith('•'):
                formatted_lines.append('&bull; ' + line.strip()[1:].strip())
            else:
                formatted_lines.append(line.strip())
        return '<br/>'.join(formatted_lines)

    def generate_report(self, image_path, analysis_results, output_path):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        elements = []
        
        # Add title
        elements.append(Paragraph("Skin-care and Grooming Recommendation Analysis Report", self.title_style))
        
        # Add date
        date_text = f"{datetime.now().strftime('%B %d, %Y')}"
        elements.append(Paragraph(date_text, self.date_style))
        elements.append(Spacer(1, 30))
        
        # Add Analysis Results heading
        elements.append(Paragraph("Analysis Results", self.heading_style))
        elements.append(Spacer(1, 10))

        if isinstance(analysis_results, dict) and "summary" in analysis_results:
            # Fix the newlines in the text
            text = analysis_results["summary"].replace('\\n', '\n')
            
            # Split into sections
            sections = text.split('\n\n')
            
            for section in sections:
                if ':' in section:
                    # Split title and content
                    title, content = section.split(':', 1)
                    title = title.strip()
                    content = content.strip()
                    
                    # Add the section title
                    elements.append(Paragraph(f"{title}:", self.section_title_style))
                    
                    # Format content (handle bullet points if present)
                    if '•' in content:
                        formatted_content = self.fix_bullet_points(content)
                    else:
                        formatted_content = content
                    
                    # Add the content
                    elements.append(Paragraph(formatted_content, self.content_style))
                    elements.append(Spacer(1, 8))
        
        # Add footer
        elements.append(Spacer(1, 20))
        footer_text = "Analysis performed using advanced AI technology"
        elements.append(Paragraph(footer_text, self.date_style))
        
        doc.build(elements)
        return output_path

def main():
    # Create report generator
    report_gen = CelebAnalysisReport()
    
    # Load analysis data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, "output.json"), "r", encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    # Generate report
    output_path = os.path.join(current_dir, "facial_analysis_report.pdf")
    report_gen.generate_report(
        image_path=None,
        analysis_results=analysis_data,
        output_path=output_path
    )

if __name__ == "__main__":
    main()