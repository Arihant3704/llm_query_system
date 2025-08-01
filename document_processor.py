import PyPDF2
import docx
import email

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() or ""
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return ""
    return text

def extract_text_from_docx(docx_path: str) -> str:
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error extracting text from DOCX {docx_path}: {e}")
        return ""
    return text

def extract_text_from_eml(eml_path: str) -> str:
    text = ""
    try:
        with open(eml_path, 'r', encoding='utf-8') as file:
            msg = email.message_from_file(file)
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == 'text/plain' and 'attachment' not in content_disposition:
                        text += part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
    except Exception as e:
        logging.error(f"Error extracting text from EML {eml_path}: {e}")
        return ""
    return text


