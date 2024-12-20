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

def clean_text(text):
    # Replace or remove any unwanted characters, such as the square symbols
    cleaned_text=text.replace("■", "")  # Specifically remove the ■ character
    cleaned_text=re.sub(r'[^\x20-\x7E\n]', '', cleaned_text)  # Remove non-printable characters
    return cleaned_text

def create_final_pdf():
    output_pdf='facts/facts.pdf'
    os.makedirs('facts', exist_ok=True)

    # Create a canvas for the PDF and set the title
    c=canvas.Canvas(output_pdf, pagesize=letter)
    c.setTitle("Debunked-AI")  # Set the PDF title here
    c.drawString(100, 750, "Debunked Facts Report")

    y=730
    for i in range(1, 201):
        debunked_file=f"facts/{i}.txt"
        if os.path.exists(debunked_file):
            with open(debunked_file, 'r') as f:
                debunked_text=f.read()

            # Clean the debunked text to remove unwanted characters
            cleaned_text=clean_text(debunked_text)

            # Draw fact number and cleaned text
            c.drawString(100, y, f"Fact {i}:")
            y -= 20

            # Wrap text and adjust position for multi-line content
            for line in cleaned_text.splitlines():
                wrapped_lines=split_into_wrapped_lines(line, max_width=80)  # Adjust max_width as needed
                for wrapped_line in wrapped_lines:
                    c.drawString(100, y, wrapped_line)
                    y -= 15
                    if y < 100:  # Start a new page if the current page is full
                        c.showPage()
                        y=750

    c.save()


def split_into_wrapped_lines(text, max_width=80):
    # Helper function to wrap text based on max width
    words=text.split(' ')
    lines=[]
    current_line=""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_width:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line=word + " "
    if current_line:
        lines.append(current_line.strip())
    return lines


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

