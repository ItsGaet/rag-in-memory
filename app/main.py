import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Set your OpenAI API key
openai_key = os.getenv("OPENAI_KEY")
os.environ["OPENAI_API_KEY"] = openai_key
 
# Function to process the PDF and create a FAISS index
def process_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    # Split the text into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    # Create embeddings
    embeddings = OpenAIEmbeddings()
    knowledge_base = FAISS.from_texts(chunks, embeddings)
    
    return knowledge_base
 
# Streamlit UI
st.title(":books: RAG in Memory")
 
# File uploader
pdf_file = st.file_uploader("Upload your PDF", type="pdf")
 
# Initialize session state
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = None
 
if pdf_file is not None:
    # Process the PDF and create FAISS index
    st.session_state.knowledge_base = process_pdf(pdf_file)
    st.success("PDF processed successfully!")
 
# Q&A Interface
if st.session_state.knowledge_base is not None:
    user_question = st.text_input("Ask a question about your PDF:")
    if user_question:
        docs = st.session_state.knowledge_base.similarity_search(user_question)
        
        llm = OpenAI()
        chain = load_qa_chain(llm, chain_type="stuff")
        response = chain.run(input_documents=docs, question=user_question)
        
        st.write("Answer:", response)