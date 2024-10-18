#
# (c) J~Net 2024
#
#
#
import os
import re
import PyPDF2
import ollama
import logging
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

load_dotenv()

PRIMARY_SERVER_URL="http://localhost:11434"
PRIMARY_MODEL="crewai-llama3.2"

def fact_check_chunk(chunk, server_url=PRIMARY_SERVER_URL, model_name=PRIMARY_MODEL):
    try:
        prompt=f"Fact-check the following text and debunk any false claims:\n\n{chunk}"
        response=ollama.generate(
            model=model_name,
            prompt=prompt
        )
        if response and 'response' in response:
            return response['response'].strip()
    except Exception as e:
        logging.error(f"Error fact-checking chunk: {e}")
    return None

def read_pdfs_in_directory():
    pdf_files=[f for f in os.listdir() if f.endswith('.pdf')]
    pdf_texts={}
    
    for pdf_file in pdf_files:
        with open(pdf_file, 'rb') as file:
            reader=PyPDF2.PdfReader(file)
            text=""
            for page_num in range(len(reader.pages)):
                page=reader.pages[page_num]
                text += page.extract_text()
            pdf_texts[pdf_file]=text
    
    return pdf_texts

def extract_facts_from_text(text):
    facts=re.split(r'\d+\)', text)
    facts=[fact.strip() for fact in facts if fact.strip()]

    os.makedirs("claims", exist_ok=True)
    for i, fact_text in enumerate(facts, start=1):
        fact_file=f"claims/{i}.txt"
        with open(fact_file, 'w') as f:
            f.write(fact_text)

    return facts

def debunk_facts():
    os.makedirs("facts", exist_ok=True)
    for i in range(1, 201):
        fact_file=f"claims/{i}.txt"
        debunked_file=f"facts/{i}.txt"

        if os.path.exists(fact_file):
            with open(fact_file, 'r') as f:
                fact_text=f.read()

            debunked_text=fact_check_chunk(fact_text)
            
            if debunked_text:  # Ensure debunked_text is not None
                with open(debunked_file, 'w') as f:
                    f.write(debunked_text)
            else:
                logging.error(f"Failed to debunk fact {i}: No response from the model")

def wrap_text(text, max_width, canvas_obj):
    # Split text into lines that fit within the given width
    lines=[]
    words=text.split(" ")
    line=""
    
    for word in words:
        # Check if adding the next word would exceed the max width
        if canvas_obj.stringWidth(line + " " + word) <= max_width:
            line += " " + word
        else:
            lines.append(line.strip())
            line=word
    
    if line:
        lines.append(line.strip())
    
    return lines

def create_final_pdf():
    output_pdf='facts/facts.pdf'
    os.makedirs('facts', exist_ok=True)

    c=canvas.Canvas(output_pdf, pagesize=letter)
    width, height=letter
    margin_x=50  # Left margin
    margin_y=50  # Bottom margin
    max_width=width - 2 * margin_x  # Width available for text

    c.drawString(margin_x, height - margin_y, "Debunked Facts Report")

    y=height - (margin_y + 20)
    for i in range(1, 201):
        debunked_file=f"facts/{i}.txt"
        if os.path.exists(debunked_file):
            with open(debunked_file, 'r') as f:
                debunked_text=f.read()

            c.drawString(margin_x, y, f"Fact {i}:")
            y -= 20

            # Wrap the debunked text into multiple lines
            wrapped_lines=wrap_text(debunked_text, max_width, c)

            # Draw each wrapped line
            for line in wrapped_lines:
                c.drawString(margin_x, y, line)
                y -= 20

                # If we run out of vertical space, create a new page
                if y < margin_y:
                    c.showPage()
                    y=height - margin_y

    c.save()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info("Reading PDFs...")
    pdf_texts=read_pdfs_in_directory()

    for pdf, content in pdf_texts.items():
        logging.info(f"Extracting facts from {pdf}...")
        extract_facts_from_text(content)

    logging.info("Debunking facts...")
    debunk_facts()

    logging.info("Creating final PDF...")
    create_final_pdf()

    logging.info("Debunking process complete. Check the 'facts' folder for results.")

