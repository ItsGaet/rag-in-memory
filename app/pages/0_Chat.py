# 💬 Chat
import streamlit as st
import datetime
from utils import check_ollama_connection, process_file, stream_ollama_response
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

DEFAULT_MODEL = "gpt-oss"

# --- Funzioni di inizializzazione e utility ---

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
    st.session_state.setdefault('presets', {})

initialize()

# --- Dialogo Impostazioni Modello ---

@st.dialog("⚙️ Impostazioni Modello")
def model_settings_dialog():
    connected, models = check_ollama_connection()
    if connected:
        st.success("✅ Ollama Online")
        model_index = models.index(st.session_state.model_settings['model']) if st.session_state.model_settings['model'] in models else 0
        model = st.selectbox("Modello", models, index=model_index)
        st.session_state.model_settings['model'] = model
    else:
        st.error("❌ Ollama Offline")

    st.session_state.model_settings['temperature'] = st.slider("Temperature", 0.0, 2.0, value=st.session_state.model_settings['temperature'], step=0.1)
    st.session_state.model_settings['top_p'] = st.slider("Top P", 0.0, 1.0, value=st.session_state.model_settings['top_p'], step=0.05)
    st.session_state.model_settings['max_tokens'] = st.number_input("Max Tokens", 10, 4096, value=st.session_state.model_settings['max_tokens'], step=10)

    st.divider()

    # Gestione Preset
    st.subheader("Gestione Preset")
    preset_name = st.text_input("Nome del preset")
    if st.button("Salva Preset Corrente"):
        if preset_name:
            st.session_state.presets[preset_name] = st.session_state.model_settings.copy()
            st.toast(f"Preset '{preset_name}' salvato!", icon="💾")
        else:
            st.warning("Inserisci un nome per il preset.")

    if st.session_state.presets:
        preset_to_load = st.selectbox("Carica Preset", options=list(st.session_state.presets.keys()))
        if st.button("Carica Selezionato"):
            st.session_state.model_settings = st.session_state.presets[preset_to_load].copy()
            st.toast(f"Preset '{preset_to_load}' caricato!", icon="🔄")
            st.rerun()

# --- UI Principale ---

st.title("💬 G-AI - Document Chatbot")

# --- SIDEBAR ---
with st.sidebar:
    st.title("G-AI")
    st.caption("Gaetano AI")

    if st.button("⚙️ Impostazioni Modello"):
        model_settings_dialog()

    # --- FILE UPLOAD ---
    with st.expander("📎 Carica documenti", expanded=True):
        files = st.file_uploader("Carica file (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"], accept_multiple_files=True, label_visibility="collapsed")

        if files:
            all_chunks = []
            new_files_processed = False
            for file in files:
                if file.name not in [f['name'] for f in st.session_state.uploaded_files]:
                    new_files_processed = True
                    chunks, _ = process_file(file)
                    if chunks:
                        st.session_state.uploaded_files.append({
                            "name": file.name, "size": file.size, "chunks": chunks,
                            "uploaded_at": datetime.datetime.now()
                        })
                        all_chunks.extend(chunks)

            if new_files_processed and all_chunks:
                embeddings = OllamaEmbeddings(base_url="http://172.28.5.155:11434", model="nomic-embed-text")
                if st.session_state.knowledge_base:
                    st.session_state.knowledge_base.add_texts(all_chunks)
                else:
                    st.session_state.knowledge_base = FAISS.from_texts(all_chunks, embeddings)
                st.success("✅ Documenti elaborati!")

    # --- FILES CARICATI ---
    if st.session_state.uploaded_files:
        with st.expander("📂 File caricati", expanded=True):
            for i, f in enumerate(st.session_state.uploaded_files):
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.markdown(f"**{f['name']}** - {round(f['size'] / 1024, 1)} KB")
                with col2:
                    if st.button("❌", key=f"remove_{i}"):
                        st.session_state.uploaded_files.pop(i)
                        # Ricostruzione dopo rimozione
                        all_chunks = [chunk for f in st.session_state.uploaded_files for chunk in f['chunks']]
                        if all_chunks:
                            embeddings = OllamaEmbeddings(base_url="http://172.28.5.155:11434", model="nomic-embed-text")
                            st.session_state.knowledge_base = FAISS.from_texts(all_chunks, embeddings)
                        else:
                            st.session_state.knowledge_base = None
                        st.rerun()

    if st.button("🗑️ Pulisci chat"):
        st.session_state.messages = []
        st.toast("Chat pulita", icon="🧹")

# --- CHAT HISTORY & INPUT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Scrivi una domanda..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Sto pensando..."):
            docs = []
            if st.session_state.knowledge_base:
                docs = st.session_state.knowledge_base.similarity_search(user_input, k=3)

            response_container = st.empty()
            response_text, _ = stream_ollama_response(docs, user_input, st.session_state.model_settings, response_container)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
