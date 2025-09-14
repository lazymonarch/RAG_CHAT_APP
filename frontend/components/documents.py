"""
Document Management Components
"""
import streamlit as st
from utils.api_client import api_client
from components.auth import require_auth
import pandas as pd


def document_upload():
    """Document upload interface."""
    if not require_auth():
        return
    
    st.subheader("📄 Upload Document")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "txt", "docx", "doc"],
        help="Upload PDF, TXT, DOCX, or DOC files"
    )
    
    if uploaded_file is not None:
        # Validate file
        is_valid, error_msg = api_client.validate_file(uploaded_file)
        
        if not is_valid:
            st.error(f"❌ {error_msg}")
            return
        
        # Show file info
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        st.info(f"📁 **File:** {uploaded_file.name} ({file_size_mb:.1f} MB)")
        
        # Upload button
        if st.button("🚀 Upload Document", use_container_width=True):
            try:
                with st.spinner("Uploading and processing document..."):
                    response = api_client.upload_document(uploaded_file, uploaded_file.name)
                
                st.success("✅ Document uploaded successfully!")
                st.write(f"**Document ID:** {response['document_id']}")
                st.write(f"**Chunks Created:** {response['chunk_count']}")
                st.write(f"**Status:** {response['processing_status']}")
                
                # Refresh document list and clear cache
                if "user_documents" in st.session_state:
                    del st.session_state.user_documents
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Upload failed: {str(e)}")


def document_list():
    """Display user's documents."""
    if not require_auth():
        return
    
    st.subheader("📚 Your Documents")
    
    try:
        # Check if documents are cached in session state
        if "user_documents" not in st.session_state:
            st.session_state.user_documents = api_client.get_documents()
        
        documents = st.session_state.user_documents
        
        if not documents:
            st.info("No documents uploaded yet. Upload some documents to start chatting!")
            return
        
        # Create DataFrame for better display
        df_data = []
        for doc in documents:
            df_data.append({
                "Filename": doc["original_filename"],
                "Type": doc["file_type"].upper(),
                "Size (MB)": f"{doc['file_size'] / (1024*1024):.1f}",
                "Chunks": doc["chunk_count"],
                "Status": doc["processing_status"],
                "Uploaded": doc["upload_timestamp"][:10],  # Just date
                "ID": doc["id"]
            })
        
        df = pd.DataFrame(df_data)
        
        # Display documents
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.TextColumn("ID", width="small"),
                "Filename": st.column_config.TextColumn("Filename", width="medium"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Size (MB)": st.column_config.TextColumn("Size", width="small"),
                "Chunks": st.column_config.NumberColumn("Chunks", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Uploaded": st.column_config.TextColumn("Uploaded", width="small")
            }
        )
        
        # Refresh button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 Refresh", help="Refresh document list"):
                if "user_documents" in st.session_state:
                    del st.session_state.user_documents
                st.rerun()
        
        # Document actions
        st.subheader("🔧 Document Actions")
        
        # Select document for actions
        selected_doc = st.selectbox(
            "Select document to manage:",
            options=documents,
            format_func=lambda x: f"{x['original_filename']} ({x['file_type'].upper()})",
            key="selected_document"
        )
        
        if selected_doc:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("📄 View Details", use_container_width=True):
                    show_document_details(selected_doc)
            
            with col2:
                if st.button("🗑️ Delete Document", use_container_width=True):
                    # Store document ID for deletion
                    st.session_state.document_to_delete = selected_doc["id"]
                    st.rerun()
        
        # Handle document deletion confirmation
        if "document_to_delete" in st.session_state:
            st.warning(f"⚠️ Are you sure you want to delete this document?")
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("✅ Yes, Delete", type="primary"):
                    try:
                        response = api_client.delete_document(st.session_state.document_to_delete)
                        st.success("✅ Document deleted successfully!")
                        # Clear cache and reset state
                        if "user_documents" in st.session_state:
                            del st.session_state.user_documents
                        del st.session_state.document_to_delete
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Delete failed: {str(e)}")
            
            with col2:
                if st.button("❌ Cancel"):
                    del st.session_state.document_to_delete
                    st.rerun()
    
    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")


def show_document_details(document):
    """Show detailed information about a document."""
    st.subheader(f"📄 {document['original_filename']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Basic Information:**")
        st.write(f"• **Type:** {document['file_type'].upper()}")
        st.write(f"• **Size:** {document['file_size'] / (1024*1024):.1f} MB")
        st.write(f"• **Chunks:** {document['chunk_count']}")
        st.write(f"• **Status:** {document['processing_status']}")
    
    with col2:
        st.write("**Timestamps:**")
        st.write(f"• **Uploaded:** {document['upload_timestamp']}")
        if document.get('updated_at'):
            st.write(f"• **Updated:** {document['updated_at']}")
    
    # Show error message if any
    if document.get('error_message'):
        st.error(f"**Error:** {document['error_message']}")
    
    # Show Pinecone IDs if available
    if document.get('pinecone_ids'):
        st.write(f"**Vector IDs:** {len(document['pinecone_ids'])} vectors stored")




def document_stats():
    """Show document statistics."""
    if not require_auth():
        return
    
    try:
        # Use cached documents if available, otherwise fetch
        if "user_documents" not in st.session_state:
            st.session_state.user_documents = api_client.get_documents()
        
        documents = st.session_state.user_documents
        
        if not documents:
            st.info("No documents to show stats for")
            return
        
        # Calculate statistics
        total_docs = len(documents)
        total_chunks = sum(doc['chunk_count'] for doc in documents)
        total_size = sum(doc['file_size'] for doc in documents) / (1024*1024)  # MB
        
        # File type distribution
        file_types = {}
        for doc in documents:
            file_type = doc['file_type'].upper()
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        # Status distribution
        statuses = {}
        for doc in documents:
            status = doc['processing_status']
            statuses[status] = statuses.get(status, 0) + 1
        
        # Display stats
        st.subheader("📊 Document Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Documents", total_docs)
        with col2:
            st.metric("Total Chunks", total_chunks)
        with col3:
            st.metric("Total Size (MB)", f"{total_size:.1f}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**File Types:**")
            for file_type, count in file_types.items():
                st.write(f"• {file_type}: {count}")
        
        with col2:
            st.write("**Processing Status:**")
            for status, count in statuses.items():
                st.write(f"• {status}: {count}")
    
    except Exception as e:
        st.error(f"Error loading document stats: {str(e)}")
