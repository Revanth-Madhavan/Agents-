# SharePoint Documentation Agent (ADK Agent)

This agent fetches documents from your company's SharePoint site and provides an interface to summarize and query them using **Google Vertex AI** or OpenAI.

## Prerequisites

1.  **Python 3.10+** installed.
2.  **Microsoft Azure App Registration** (for SharePoint access).
3.  **Google Cloud Project** (for Vertex AI) OR **OpenAI API Key**.
    - Enable **Vertex AI API** in Google Cloud Console.
    - Enable **Agent Builder API** (if using Data Stores).

## Setup

1.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    - Copy `.env.example` to `.env`.
    - Fill in credentials.

    **For Google Vertex AI (Recommended):**
    - Set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`.
    - Ensure you have Application Default Credentials (ADC) set up:
      ```bash
      gcloud auth application-default login
      ```
    - _Optional_: Set `VERTEX_AI_DATA_STORE_ID` if connecting to a managed Agent Builder Data Store.

3.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

## Usage

1.  Open the web interface (http://localhost:8501).
2.  Select your **AI Provider** in the sidebar:
    - **Google Vertex AI (ADK)**: Uses Gemini Pro and Vertex Embeddings.
    - **OpenAI**: Uses GPT-3.5 and OpenAI Embeddings.
3.  Fetch documents (for local RAG) or connect to your Data Store.
4.  Ask questions!

## Technologies

- **Google Vertex AI**: Gemini 1.5 Pro, Vertex Embeddings.
- **Google Vertex AI Search**: For enterprise-grade retrieval (optional).
- **LangChain**: Agent orchestration.
- **ChromaDB**: Local vector store (when not using Vertex AI Search).
- **O365**: SharePoint ingestion.
