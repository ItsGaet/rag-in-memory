# 📚 RAG in Memory

Welcome to **RAG in Memory**! This application allows you to upload a PDF, create a FAISS-based search index, and get answers to specific questions related to the content of the PDF using the power of OpenAI's AI.

## Features

- **Intuitive Interface**: Uses a simple and intuitive Streamlit-based user interface.
- **PDF Upload**: Upload a PDF from your local machine.
- **Text Extraction**: Extract text from the uploaded PDF.
- **Create FAISS Index**: Create a FAISS index from the extracted text chunks.
- **Semantic Search**: Perform semantic searches within the PDF using OpenAI.

## Prerequisites

- Python 3.7 or higher
- OpenAI key

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/tuo-username/rag-in-memory.git
    cd rag-in-memory
    ```

2. Create a virtual environment (optional but recommended):

    ```sh
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Set your OpenAI API key:

    Open the `.env` file (create the file if it does not exist) and add your OpenAI API key:

    ```env
    OPENAI_API_KEY=sk-your-api-key-here
    ```

## How to Use It

1. Start the Streamlit application:

    ```sh
    streamlit run app.py
    ```

2. Upload a PDF via the user interface.

3. After uploading the PDF, wait for the FAISS index to be created.

4. Ask a question about the content of the PDF and get an immediate answer!

## Examples of Use

### Uploading PDF

Upload a PDF directly from the user interface. The PDF will be processed and the text will be extracted automatically.

### Search and Answer

Enter a specific question regarding the content of the PDF and get an accurate answer by leveraging the power of OpenAI's language model.

## Contribute

Contributions are welcome! If you have suggestions or improvements, feel free to open a pull request or create an issue.

## License

This project is distributed under the MIT license. See the `LICENSE` file for more details.

---

We hope you find this application useful! If you have any questions or need support, please feel free to contact us.
