import PyPDF2
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Takes raw PDF file bytes and returns all the text inside it.

    file_bytes = the raw content of the uploaded PDF file
    """

    # io.BytesIO converts raw bytes into a file-like object
    # PyPDF2 needs a file-like object, not raw bytes
    pdf_file = io.BytesIO(file_bytes)

    reader = PyPDF2.PdfReader(pdf_file)

    extracted_text = ""

    # Loop through every page and extract text
    for page_number in range(len(reader.pages)):
        page = reader.pages[page_number]
        text = page.extract_text()
        if text:
            extracted_text += f"\n--- Page {page_number + 1} ---\n"
            extracted_text += text

    # If no text was found (scanned PDF / image-based PDF)
    if not extracted_text.strip():
        return "No readable text found in this PDF. It may be a scanned or image-based document."

    return extracted_text.strip()