import io
import docx
from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from fastapi import UploadFile

def get_text_from_pdf(file: io.BytesIO) -> str:
    """Extracts text from a PDF file."""
    pdf_reader = PdfReader(file)
    return "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

def get_text_from_txt(file: io.BytesIO) -> str:
    """Extracts text from a TXT file."""
    return file.read().decode("utf-8")

def get_text_from_docx(file: io.BytesIO) -> str:
    """Extracts text from a DOCX file."""
    document = docx.Document(file)
    return "\n".join([paragraph.text for paragraph in document.paragraphs])

async def extract_text_from_file(file: UploadFile) -> str | None:
    """
    Extracts text from an uploaded file based on its content type.
    """
    content = await file.read()
    file_stream = io.BytesIO(content)

    content_type = file.content_type
    if content_type == "application/pdf":
        return get_text_from_pdf(file_stream)
    elif content_type == "text/plain":
        return get_text_from_txt(file_stream)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return get_text_from_docx(file_stream)
    else:
        # Optionally, handle unsupported file types
        return None

def split_text_into_chunks(text: str) -> list[str]:
    """Splits a long text into smaller chunks."""
    text_splitter = CharacterTextSplitter(
        separator="\\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)
