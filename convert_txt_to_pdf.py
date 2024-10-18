#
# (c) J~Net 2024
#
# curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py
#
#
# pip install reportlab
#
#
# python convert_txt_to_pdf.py
#
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def txt_to_pdf(txt_file, pdf_file):
    # Create a PDF canvas
    c=canvas.Canvas(pdf_file, pagesize=letter)
    width, height=letter
    margin=1 * inch
    text_object=c.beginText(margin, height - margin)
    text_object.setFont("Helvetica", 12)
    
    # Read the text file and add lines to the PDF
    with open(txt_file, "r") as file:
        for line in file:
            text_object.textLine(line.strip())
            # Check if the line exceeds the page width
            if text_object.getY() < margin:
                c.drawText(text_object)
                c.showPage()
                text_object=c.beginText(margin, height - margin)
                text_object.setFont("Helvetica", 12)

    # Draw any remaining text
    c.drawText(text_object)
    c.save()

# Example usage
txt_to_pdf("input.txt", "output.pdf")

