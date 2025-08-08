# main.py
import streamlit as st
import datetime
from utils import check_ollama_connection, process_pdf, stream_ollama_response
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

DEFAULT_MODEL = "gpt-oss"

st.set_page_config(
    page_title="G-AI",
    page_icon="🤖",
    layout="wide"
)

def initialize():
    st.session_state.setdefault('knowledge_base', None)
    st.session_state.setdefault('messages', [])
    st.session_state.setdefault('uploaded_files', [])
    st.session_state.setdefault('model_settings', {
        'model': DEFAULT_MODEL,
        'temperature': 0.7,
        'top_p': 0.9,
        'max_tokens': 2000
    })
    st.session_state.setdefault('waiting_response', False)

initialize()

st.markdown("## 💬 G-AI - Document Chatbot")

# --- FILE UPLOAD ---
st.markdown("### 📎 Carica documenti PDF")
files = st.file_uploader("Trascina o seleziona uno o più PDF", type=["pdf"], accept_multiple_files=True)

if files:
    all_chunks = []
    for file in files:
        kb, chunks, _ = process_pdf(file)
        st.session_state.uploaded_files.append({
            "name": file.name,
            "size": file.size,
            "chunks": chunks,
            "kb": kb,
            "uploaded_at": datetime.datetime.now()
        })
        all_chunks.extend(chunks)

    # Ricostruzione della knowledge base unificata
    embeddings = OllamaEmbeddings(base_url="http://172.28.5.155:11434", model="nomic-embed-text")
    st.session_state.knowledge_base = FAISS.from_texts(all_chunks, embeddings)

    st.success("📄 Documenti elaborati!")

# --- FILES CARICATI ---
if st.session_state.uploaded_files:
    with st.expander("📂 File caricati"):
        for i, f in enumerate(st.session_state.uploaded_files):
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"**{f['name']}** - {round(f['size'] / 1024, 1)} KB")
            with col2:
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state.uploaded_files.pop(i)
                    # Ricostruzione dopo rimozione
                    all_chunks = []
                    for ff in st.session_state.uploaded_files:
                        all_chunks.extend(ff['chunks'])
                    if all_chunks:
                        st.session_state.knowledge_base = FAISS.from_texts(all_chunks, embeddings)
                    else:
                        st.session_state.knowledge_base = None
                    st.rerun()

# --- MODEL SETTINGS ---
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

# --- PULIZIA CHAT ---
if st.button("🗑️ Pulisci chat"):
    st.session_state.messages = []
    st.toast("Chat pulita", icon="🧹")

# --- CHAT HISTORY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT INPUT ---
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
        st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
