# utils.py
import json
import time
import requests
from PyPDF2 import PdfReader
import docx
import io
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st

OLLAMA_BASE_URL = "http://172.28.5.155:11434"

@st.cache_data(ttl=30)
def check_ollama_connection():
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = [model.get('name', 'Unknown') for model in response.json().get('models', [])]
            return True, models
        return False, []
    except Exception:
        return False, []

def get_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    return "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

def get_text_from_txt(file):
    return file.getvalue().decode("utf-8")

def get_text_from_docx(file):
    document = docx.Document(io.BytesIO(file.getvalue()))
    return "\n".join([paragraph.text for paragraph in document.paragraphs])

@st.cache_data(show_spinner=False)
def process_file(file):
    with st.spinner(f"🔄 Processing {file.name}..."):
        file_extension = file.name.split('.')[-1].lower()

        if file_extension == "pdf":
            text = get_text_from_pdf(file)
        elif file_extension == "txt":
            text = get_text_from_txt(file)
        elif file_extension == "docx":
            text = get_text_from_docx(file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            return None, None, None

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        # Non creiamo la knowledge base qui, solo i chunk
        return chunks, len(text)

def stream_ollama_response(context, question, model_settings, response_placeholder):
    prompt = "Sei un assistente virtuale chiamato G-AI. Rispondi alla domanda basandoti solo sul contesto fornito.\n\n"
    prompt += "Contesto:\n"
    if context:
        for i, doc in enumerate(context):
            prompt += f"Documento {i+1}:\n{doc.page_content}\n\n"
    else:
        prompt += "Nessun documento fornito.\n\n"

    prompt += f"Domanda: {question}\n\nRisposta:"

    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model_settings['model'],
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": model_settings['temperature'],
            "top_p": model_settings['top_p'],
            "num_predict": model_settings['max_tokens']
        }
    }

    full_response = ""
    start_time = time.time()

    try:
        with requests.post(url, json=payload, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if 'response' in chunk:
                        full_response += chunk['response']
                        response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        return full_response, time.time() - start_time
    except Exception as e:
        error_msg = f"Errore durante la generazione: {str(e)}"
        response_placeholder.error(error_msg)
        return error_msg, 0
