"""
🧠 LocalWise v1.0.0 - Your AI Knowledge Assistant (Modular)

A clean, simple, local AI application that transforms your documents
into an intelligent knowledge base. Works entirely offline with no API keys.
"""

import streamlit as st

# Import LocalWise modules
from localwise.ui.ui_components import (
    configure_page, display_header, display_sidebar, display_error_message,
    display_success_message, display_chat_message, display_setup_instructions
)
from localwise.core.query_engine import (
    query_documents, validate_query_system, search_similar_documents,
    get_document_suggestions
)
from localwise.core.embedding_service import load_vector_database
from localwise import config


def initialize_app():
    """Initialize the Streamlit app."""
    configure_page()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    
    if "system_ready" not in st.session_state:
        st.session_state.system_ready = None


def load_system_components():
    """Load and cache system components."""
    if st.session_state.vectorstore is None:
        with st.spinner("Loading vector database..."):
            st.session_state.vectorstore = load_vector_database()
    
    return st.session_state.vectorstore is not None


def handle_user_query(question):
    """Handle user query and display response."""
    if not question.strip():
        return
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Generate response
    with st.chat_message("user"):
        st.write(question)
    
    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Thinking..."):
            response = query_documents(
                question, 
                st.session_state.vectorstore
            )
        st.write(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})


def display_chat_interface():
    """Display the main chat interface."""
    st.subheader("💬 Ask Questions About Your Documents")
    
    # Display chat history
    for message in st.session_state.messages:
        avatar = "🧠" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])
    
    # Chat input
    if question := st.chat_input("Ask a question about your documents..."):
        handle_user_query(question)


def display_document_explorer():
    """Display document exploration tools."""
    with st.expander("🔍 Document Explorer", expanded=False):
        st.write("Search through your documents without generating an answer:")
        
        search_query = st.text_input("Search documents:", placeholder="Enter keywords...")
        
        if search_query:
            docs = search_similar_documents(search_query, st.session_state.vectorstore)
            
            if docs:
                st.write(f"Found {len(docs)} relevant documents:")
                for i, doc in enumerate(docs):
                    source = doc.metadata.get('source', 'Unknown')
                    preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                    
                    with st.expander(f"📄 {source}", expanded=False):
                        st.text(preview)
            else:
                st.info("No documents found for this search.")


def display_suggestions():
    """Display query suggestions."""
    if st.session_state.vectorstore:
        suggestions = get_document_suggestions(st.session_state.vectorstore)
        
        if suggestions:
            st.subheader("💡 Query Suggestions")
            for suggestion in suggestions[:3]:  # Show top 3
                if st.button(suggestion, key=f"suggestion_{hash(suggestion)}"):
                    handle_user_query(suggestion)


def main():
    """Main application function."""
    initialize_app()
    
    # Display header and sidebar
    display_header()
    display_sidebar()
    
    # Check system readiness
    system_ready, issues = validate_query_system()
    
    if not system_ready:
        st.error("**System Not Ready**")
        for issue in issues:
            st.write(f"• {issue}")
        
        display_setup_instructions()
        return
    
    # Load system components
    if not load_system_components():
        display_error_message(
            "Database Loading Failed",
            "Could not load the vector database. Please ensure documents have been processed.",
            "Run: python ingest.py --step1 && python ingest.py --step2"
        )
        return
    
    # Main interface
    display_chat_interface()
    
    # Additional features in sidebar
    with st.sidebar:
        st.header("🔍 Tools")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # System info
        if st.button("📊 System Info"):
            ollama_available, _ = config.validate_ollama_connection()
            db_exists, _ = config.validate_database_exists()
            
            st.success("System Status:")
            st.write(f"• Ollama: {'✅' if ollama_available else '❌'}")
            st.write(f"• Database: {'✅' if db_exists else '❌'}")
            st.write(f"• Vector Store: {'✅' if st.session_state.vectorstore else '❌'}")
    
    # Document explorer (collapsed by default)
    display_document_explorer()
    
    # Query suggestions
    display_suggestions()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "LocalWise v1.0.0 | Built with ❤️ for privacy-focused AI assistance"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()