from PyPDF2 import PdfReader


async def extract_pdf_text(pdf_file):
    try:
        reader = PdfReader(pdf_file.file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text if text.strip() else "No text found in PDF."
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"
