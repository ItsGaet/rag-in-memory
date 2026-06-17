import json
import time
import requests
from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st

OLLAMA_BASE_URL = "http://172.28.5.155:11434"

@st.cache_data(ttl=30)
def check_ollama_connection():
    """
    Checks the connection to the Ollama server and retrieves the list of available models.

    Returns:
        tuple: A tuple containing a boolean indicating the connection status and a list of model names.
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = [model.get('name', 'Unknown') for model in response.json().get('models', [])]
            return True, models
        return False, []
    except Exception:
        return False, []

@st.cache_data
def process_pdf(_pdf_file):
    """
    Processes a PDF file, extracts text, splits it into chunks, and creates a knowledge base.

    Args:
        _pdf_file: The PDF file to process.

    Returns:
        tuple: A tuple containing the knowledge base, the text chunks, and the total number of characters.
    """
    with st.spinner("🔄 Processing PDF..."):
        pdf_reader = PdfReader(_pdf_file)
        text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        embeddings = OllamaEmbeddings(base_url=OLLAMA_BASE_URL, model="nomic-embed-text")
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        return knowledge_base, chunks, len(text)

def stream_ollama_response(context, question, model_settings):
    """
    Streams a response from the Ollama model based on the given context and question.

    Args:
        context (list): A list of documents to provide as context.
        question (str): The user's question.
        model_settings (dict): A dictionary of settings for the model.

    Returns:
        tuple: A tuple containing the full response text and the elapsed time.
    """
    prompt = "Contesto:\n"
    for i, doc in enumerate(context):
        prompt += f"Documento {i+1}:\n{doc.page_content}\n\n"
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
    response_placeholder = st.empty()

    try:
        with requests.post(url, json=payload, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if 'response' in chunk:
                        full_response += chunk['response']
                        response_placeholder.markdown(f"{full_response}▌")
            response_placeholder.markdown(full_response)
        return full_response, time.time() - start_time
    except Exception as e:
        error_msg = f"Errore durante la generazione: {str(e)}"
        response_placeholder.error(error_msg)
        return error_msg, 0
