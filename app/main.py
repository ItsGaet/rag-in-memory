import streamlit as st
import datetime
from utils import check_ollama_connection, process_pdf, stream_ollama_response
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

def initialize_session_state():
    """
    Initializes the session state with default values.
    """
    st.session_state.setdefault('knowledge_base', None)
    st.session_state.setdefault('messages', [])
    st.session_state.setdefault('uploaded_files', [])
    st.session_state.setdefault('model_settings', {
        'model': "gpt-oss",
        'temperature': 0.7,
        'top_p': 0.9,
        'max_tokens': 2000
    })
    st.session_state.setdefault('waiting_response', False)

def display_uploaded_files():
    """
    Displays the list of uploaded files and provides an option to remove them.
    """
    with st.expander("📂 File caricati"):
        for i, f in enumerate(st.session_state.uploaded_files):
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"**{f['name']}** - {round(f['size'] / 1024, 1)} KB")
            with col2:
                if st.button("❌", key=f"remove_{i}", help="Rimuovi questo file"):
                    st.session_state.uploaded_files.pop(i)
                    rebuild_knowledge_base()
                    st.rerun()

def rebuild_knowledge_base():
    """
    Rebuilds the knowledge base from the currently uploaded files.
    """
    all_chunks = []
    for f in st.session_state.uploaded_files:
        all_chunks.extend(f['chunks'])

    if all_chunks:
        embeddings = OllamaEmbeddings(base_url="http://172.28.5.155:11434", model="nomic-embed-text")
        st.session_state.knowledge_base = FAISS.from_texts(all_chunks, embeddings)
    else:
        st.session_state.knowledge_base = None

def handle_file_upload():
    """
    Handles the file upload process.
    """
    files = st.file_uploader("Trascina o seleziona uno o più PDF", type=["pdf"], accept_multiple_files=True)
    if files:
        all_chunks = []
        for file in files:
            _, chunks, _ = process_pdf(file)
            st.session_state.uploaded_files.append({
                "name": file.name,
                "size": file.size,
                "chunks": chunks,
                "uploaded_at": datetime.datetime.now()
            })
            all_chunks.extend(chunks)

        rebuild_knowledge_base()
        st.success("📄 Documenti elaborati!")

def display_model_settings():
    """
    Displays the model settings section.
    """
    with st.expander("⚙️ Impostazioni modello"):
        connected, models = check_ollama_connection()
        if connected:
            st.success("✅ Ollama Online")
            model = st.selectbox("Modello", models, index=models.index(st.session_state.model_settings['model']) if st.session_state.model_settings['model'] in models else 0)
            st.session_state.model_settings['model'] = model
        else:
            st.error("❌ Ollama Offline")

        st.session_state.model_settings['temperature'] = st.slider("Temperature", 0.0, 2.0, value=st.session_state.model_settings['temperature'], step=0.1)
        st.session_state.model_settings['top_p'] = st.slider("Top P", 0.0, 1.0, value=st.session_state.model_settings['top_p'], step=0.05)
        st.session_state.model_settings['max_tokens'] = st.number_input("Max Tokens", 10, 4096, value=st.session_state.model_settings['max_tokens'], step=10)

def display_chat_history():
    """
    Displays the chat history.
    """
    if not st.session_state.messages:
        st.info("👋 Benvenuto! Carica un PDF e inizia a fare domande sul suo contenuto.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def handle_chat_input():
    """
    Handles the user's chat input and displays the assistant's response.
    """
    user_input = st.chat_input("Scrivi una domanda...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        docs = []
        if st.session_state.knowledge_base:
            docs = st.session_state.knowledge_base.similarity_search(user_input, k=3)

        with st.chat_message("assistant"):
            response_text, _ = stream_ollama_response(docs, user_input, st.session_state.model_settings)

        st.session_state.messages.append({"role": "assistant", "content": response_text})

def load_css(file_path):
    """
    Loads a CSS file and injects it into the Streamlit application.
    """
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    """
    Main function to run the Streamlit application.
    """
    st.set_page_config(page_title="G-AI", page_icon="🤖", layout="wide")

    load_css("app/styles/style.css")

    initialize_session_state()

    st.markdown("## 💬 G-AI - Document Chatbot")

    handle_file_upload()

    if st.session_state.uploaded_files:
        display_uploaded_files()

    display_model_settings()

    if st.button("🗑️ Pulisci chat"):
        st.session_state.messages = []
        st.toast("Chat pulita", icon="🧹")

    display_chat_history()
    handle_chat_input()

if __name__ == "__main__":
    main()
