import streamlit as st
import os
from agent import SharePointAgent
from sharepoint_connector import SharePointFetcher
from dotenv import load_dotenv

load_dotenv()

st.title("SharePoint Document Assistant")

# Sidebar for Setup
with st.sidebar:
    st.header("Setup & Configuration")
    
    # 1. Select AI Provider
    provider = st.selectbox("AI Provider", ["OpenAI", "Google Vertex AI (ADK)"])
    
    if provider == "OpenAI":
        api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            
    elif provider == "Google Vertex AI (ADK)":
        project_id = st.text_input("Google Project ID", value=os.getenv("GOOGLE_CLOUD_PROJECT", ""))
        location = st.text_input("Location (e.g. us-central1)", value=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))
        data_store_id = st.text_input("Vertex AI Data Store ID (Optional)", value=os.getenv("VERTEX_AI_DATA_STORE_ID", ""))
        
        if project_id:
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
            os.environ["GOOGLE_CLOUD_LOCATION"] = location
            if data_store_id:
                os.environ["VERTEX_AI_DATA_STORE_ID"] = data_store_id
            os.environ["USE_GOOGLE_AGENT"] = "true"
        else:
            st.warning("Please provide Project ID.")

    st.header("SharePoint Credentials")
    # Credentials inputs (optional, can read from .env)
    client_id = st.text_input("Client ID", value=os.getenv("SHAREPOINT_CLIENT_ID", ""))
    client_secret = st.text_input("Client Secret", type="password", value=os.getenv("SHAREPOINT_CLIENT_SECRET", ""))
    tenant_id = st.text_input("Tenant ID (Optional)", value=os.getenv("SHAREPOINT_TENANT_ID", ""))
    
    site_url = st.text_input("Site URL/Name", value=os.getenv("SHAREPOINT_SITE_URL", ""))
    library_name = st.text_input("Library Name", value="Documents")
    
    if st.button("Fetch Documents"):
        if not client_id or not client_secret:
            st.error("Please provide Client ID and Secret.")
        else:
            try:
                fetcher = SharePointFetcher(client_id, client_secret, tenant_id)
                fetcher.authenticate()
                st.info("Authenticated. Starting download...")
                fetcher.download_files(site_url, library_name, "data/sharepoint_docs")
                st.success("Download complete!")
                # Re-initialize agent to index new docs
                st.session_state.agent = SharePointAgent(use_google=(provider == "Google Vertex AI (ADK)"))
                st.session_state.agent.create_vector_store()
            except Exception as e:
                st.error(f"Error: {e}")

# Main Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Agent based on selection
if "agent" not in st.session_state or st.session_state.get("current_provider") != provider:
    use_google = (provider == "Google Vertex AI (ADK)")
    st.session_state.agent = SharePointAgent(use_google=use_google)
    st.session_state.current_provider = provider
    # Initialize index if data exists
    if os.path.exists("./data/sharepoint_docs") or (use_google and os.getenv("VERTEX_AI_DATA_STORE_ID")):
        st.session_state.agent.create_vector_store()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your documents"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        # Get response from agent
        try:
            full_response = st.session_state.agent.query_agent(prompt)
        except Exception as e:
             full_response = f"Error querying agent: {e}"
        
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

