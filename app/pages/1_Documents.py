# 📄 Documents
import streamlit as st
import datetime
from utils import process_file
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

def initialize_session():
    # Inizializza le variabili di sessione se non esistono
    st.session_state.setdefault('knowledge_base', None)
    st.session_state.setdefault('uploaded_files', [])

initialize_session()

with st.sidebar:
    st.title("G-AI")
    st.caption("Gaetano AI")

st.title("📄 Gestione Documenti")
st.caption("Carica, visualizza e rimuovi i documenti che G-AI utilizzerà come base di conoscenza.")

# --- Sezione di Upload ---
st.header("Carica Nuovi Documenti")
uploaded_files = st.file_uploader(
    "Seleziona uno o più file (PDF, TXT, DOCX)",
    type=["pdf", "txt", "docx"],
    accept_multiple_files=True
)

if uploaded_files:
    new_files_processed = False
    all_new_chunks = []

    for file in uploaded_files:
        if file.name not in [f['name'] for f in st.session_state.uploaded_files]:
            new_files_processed = True
            chunks, text_length = process_file(file)
            if chunks:
                st.session_state.uploaded_files.append({
                    "name": file.name,
                    "size": file.size,
                    "chunks": chunks,
                    "char_count": text_length,
                    "uploaded_at": datetime.datetime.now()
                })
                all_new_chunks.extend(chunks)

    if new_files_processed and all_new_chunks:
        with st.spinner("Indicizzando i documenti..."):
            embeddings = OllamaEmbeddings(base_url="http://172.28.5.155:11434", model="nomic-embed-text")
            if st.session_state.knowledge_base:
                st.session_state.knowledge_base.add_texts(all_new_chunks)
            else:
                st.session_state.knowledge_base = FAISS.from_texts(all_new_chunks, embeddings)
        st.success("✅ Documenti caricati e indicizzati con successo!")
    elif new_files_processed:
        st.warning("Nessun nuovo documento da processare o i file sono vuoti.")
    else:
        st.info("Tutti i file selezionati sono già stati caricati.")


# --- Sezione di Gestione ---
st.header("Documenti Caricati")

if not st.session_state.uploaded_files:
    st.info("Nessun documento è stato ancora caricato.")
else:
    for i, file_info in enumerate(st.session_state.uploaded_files):
        with st.container():
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                st.subheader(file_info['name'])
                st.caption(f"Caricato il: {file_info['uploaded_at'].strftime('%d/%m/%Y %H:%M:%S')}")
            with col2:
                st.metric(label="Dimensione", value=f"{round(file_info['size'] / 1024, 2)} KB")
                st.metric(label="Numero Chunks", value=len(file_info['chunks']))
            with col3:
                if st.button("Rimuovi", key=f"delete_{i}", type="primary"):
                    # Rimuovi il file dalla lista
                    st.session_state.uploaded_files.pop(i)

                    # Ricostruisci la knowledge base
                    with st.spinner("Aggiornando la base di conoscenza..."):
                        all_chunks = [chunk for f in st.session_state.uploaded_files for chunk in f['chunks']]
                        if all_chunks:
                            embeddings = OllamaEmbeddings(base_url="http://172.28.5.155:11434", model="nomic-embed-text")
                            st.session_state.knowledge_base = FAISS.from_texts(all_chunks, embeddings)
                        else:
                            st.session_state.knowledge_base = None

                    st.toast(f"Documento '{file_info['name']}' rimosso.")
                    st.rerun()
            st.divider()
