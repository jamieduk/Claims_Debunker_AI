# Fact-Checking PDF Claims and Debunking Script

This script extracts claims from PDF files, fact-checks them using the Ollama AI model, and generates debunked facts. It stores the extracted claims in a `claims` folder, the debunked facts in a `facts` folder, and creates a PDF report of debunked facts.

## Requirements

- Python 3.x
- `ollama` package for AI-based fact-checking
- `PyPDF2` for PDF extraction
- `reportlab` for PDF generation
- `dotenv` for environment variable management

Install the required dependencies using:

```bash
pip install PyPDF2 reportlab python-dotenv ollama
