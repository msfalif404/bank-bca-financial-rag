import uuid
import streamlit as st

from src.rag.retriever import ask_financial_agent_stream
from src.experiments.eda import render_dashboard

def chat_page():
    """Renders the Financial Analyst RAG Chat interface."""
    st.title("Financial Analyst RAG Agent")
    st.markdown(
        "Tanyakan informasi seputar laporan keuangan yang telah diekstrak.\n"
        "Sistem ini ditenagai oleh **Google ADK (Agent Graph)**, **ChromaDB**, "
        "dan **Hybrid Search + Reranker** untuk menjawab pertanyaan secara akurat."
    )

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "Halo! Saya adalah Asisten Analis Keuangan Anda. Ada data laporan yang ingin Anda cari atau Anda butuh sebuah insight?"
        }]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Contoh: 'Berapa Kas BCA 2024?' atau 'Tolong berikan insight keuangan'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                stream_gen = ask_financial_agent_stream(
                    query=prompt, 
                    session_id=st.session_state.session_id
                )
                response_text = st.write_stream(stream_gen)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                error_msg = f"Terjadi kesalahan pada sistem agen: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

def main():
    """Main entry point for the Multi-Page Streamlit App."""
    st.set_page_config(
        page_title="Financial Analytics & RAG",
        page_icon="📈",
        layout="wide"
    )
    
    # Define pages using Streamlit's native navigation
    page_dashboard = st.Page(
        render_dashboard, 
        title="Business Insights", 
        icon="📊", 
        default=True
    )
    page_chat = st.Page(
        chat_page, 
        title="Chat Assistant (RAG)", 
        icon="💬"
    )
    
    # Initialize navigation
    pg = st.navigation([page_dashboard, page_chat])
    
    # Run the selected page
    pg.run()

if __name__ == "__main__":
    main()
