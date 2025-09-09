# RAG Chat Application Implementation Guide

## Complete Technical Specifications for Cursor Implementation

### OpenAI API Setup

```python
import openai
import tiktoken
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Token counter for cost tracking
def count_tokens(text, model="gpt-4o-mini"):
    """Count tokens in text using tiktoken"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

### 1. Document Processing Pipeline

#### File Upload Handler
```python
def process_uploaded_document(file_path, max_size_mb=1):
    """
    Process uploaded document with size validation
    """
    # Validate file size
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
    if file_size > max_size_mb:
        raise ValueError(f"File size {file_size:.2f}MB exceeds {max_size_mb}MB limit")
    
    # Extract text based on file type
    if file_path.endswith('.pdf'):
        text = extract_pdf_text(file_path)
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    elif file_path.endswith('.docx'):
        text = extract_docx_text(file_path)
    else:
        raise ValueError("Unsupported file format")
    
    return clean_text(text)

def clean_text(text):
    """Clean and preprocess text"""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    # Remove special characters that don't add semantic value
    text = text.replace('\n\n\n', '\n\n')
    text = text.replace('\t', ' ')
    return text.strip()
```

#### Document Chunking (Fixed-size Strategy)
```python
def chunk_document(text, chunk_size=500, overlap=50):
    """
    Split document into overlapping chunks
    
    Args:
        text: Document text to chunk
        chunk_size: Target tokens per chunk
        overlap: Overlap tokens between chunks
    
    Returns:
        List of text chunks with metadata
    """
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    chunk_id = 0
    
    while start < len(tokens):
        # Define chunk end
        end = min(start + chunk_size, len(tokens))
        
        # Extract chunk tokens
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        
        # Create chunk metadata
        chunk_metadata = {
            'chunk_id': chunk_id,
            'start_token': start,
            'end_token': end,
            'token_count': len(chunk_tokens),
            'char_count': len(chunk_text)
        }
        
        chunks.append({
            'text': chunk_text,
            'metadata': chunk_metadata
        })
        
        # Move start position with overlap
        start = end - overlap
        chunk_id += 1
        
        # Break if remaining tokens are less than overlap
        if end == len(tokens):
            break
    
    return chunks
```

### 2. Embedding Generation

#### OpenAI Embedding API Implementation
```python
def generate_embeddings(chunks, model="text-embedding-3-small"):
    """
    Generate embeddings for document chunks
    
    Args:
        chunks: List of text chunks
        model: OpenAI embedding model
    
    Returns:
        List of embeddings with metadata and token counts
    """
    embeddings_data = []
    total_tokens = 0
    
    # Batch process chunks (up to 2048 inputs per request)
    batch_size = 100  # Conservative batch size for free tier
    
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i+batch_size]
        batch_texts = [chunk['text'] for chunk in batch_chunks]
        
        try:
            # Generate embeddings
            response = client.embeddings.create(
                model=model,
                input=batch_texts,
                encoding_format="float"
            )
            
            # Track token usage
            batch_tokens = response.usage.total_tokens
            total_tokens += batch_tokens
            
            # Store embeddings with metadata
            for j, embedding_obj in enumerate(response.data):
                chunk_index = i + j
                embeddings_data.append({
                    'chunk_id': chunks[chunk_index]['metadata']['chunk_id'],
                    'text': chunks[chunk_index]['text'],
                    'embedding': embedding_obj.embedding,
                    'metadata': chunks[chunk_index]['metadata'],
                    'tokens_used': len(tiktoken.encoding_for_model("gpt-4o-mini").encode(chunks[chunk_index]['text']))
                })
                
        except Exception as e:
            print(f"Error generating embeddings for batch {i//batch_size + 1}: {e}")
            raise
    
    print(f"Total embedding tokens used: {total_tokens}")
    print(f"Estimated cost: ${total_tokens * 0.02 / 1000:.4f}")
    
    return embeddings_data, total_tokens
```

### 3. Vector Storage (Pinecone Integration)

#### Pinecone Setup and Storage
```python
import pinecone
from pinecone import Pinecone, ServerlessSpec

def setup_pinecone(api_key, index_name="rag-documents"):
    """Initialize Pinecone and create index if needed"""
    pc = Pinecone(api_key=api_key)
    
    # Check if index exists
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,  # text-embedding-3-small dimension
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
    
    return pc.Index(index_name)

def store_embeddings(index, embeddings_data, document_id):
    """Store embeddings in Pinecone with metadata"""
    vectors = []
    
    for data in embeddings_data:
        vector_id = f"{document_id}_chunk_{data['chunk_id']}"
        
        metadata = {
            'document_id': document_id,
            'chunk_id': data['chunk_id'],
            'text': data['text'][:1000],  # Limit text in metadata
            'token_count': data['tokens_used'],
            'start_token': data['metadata']['start_token'],
            'end_token': data['metadata']['end_token']
        }
        
        vectors.append({
            'id': vector_id,
            'values': data['embedding'],
            'metadata': metadata
        })
    
    # Upsert vectors in batches
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch)
    
    print(f"Stored {len(vectors)} vectors for document {document_id}")
```

### 4. MongoDB Document Storage

#### MongoDB Integration
```python
from pymongo import MongoClient
import datetime

def setup_mongodb(connection_string):
    """Initialize MongoDB connection"""
    client = MongoClient(connection_string)
    db = client.rag_app
    return db

def store_document_metadata(db, document_id, filename, chunks_count, total_tokens):
    """Store document metadata in MongoDB"""
    document_data = {
        'document_id': document_id,
        'filename': filename,
        'upload_timestamp': datetime.datetime.utcnow(),
        'chunks_count': chunks_count,
        'total_tokens': total_tokens,
        'processing_status': 'completed'
    }
    
    db.documents.insert_one(document_data)
    return document_data

def store_chat_history(db, user_id, query, response, tokens_used):
    """Store chat interaction in MongoDB"""
    chat_data = {
        'user_id': user_id,
        'timestamp': datetime.datetime.utcnow(),
        'query': query,
        'response': response,
        'tokens_used': tokens_used
    }
    
    db.chat_history.insert_one(chat_data)
```

### 5. RAG Query Processing

#### Query Handler with Context Retrieval
```python
def process_rag_query(query, index, client, max_context_tokens=2000):
    """
    Process RAG query with context retrieval
    
    Args:
        query: User query string
        index: Pinecone index
        client: OpenAI client
        max_context_tokens: Maximum tokens for context
    
    Returns:
        Response and token usage information
    """
    # Generate query embedding
    query_embedding_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    query_embedding = query_embedding_response.data[0].embedding
    query_tokens = query_embedding_response.usage.total_tokens
    
    # Search for relevant chunks
    search_results = index.query(
        vector=query_embedding,
        top_k=5,  # Retrieve top 5 most relevant chunks
        include_metadata=True
    )
    
    # Build context from search results
    context_chunks = []
    context_tokens = 0
    
    for match in search_results['matches']:
        chunk_text = match['metadata']['text']
        chunk_tokens = count_tokens(chunk_text)
        
        if context_tokens + chunk_tokens <= max_context_tokens:
            context_chunks.append(chunk_text)
            context_tokens += chunk_tokens
        else:
            break
    
    context = "\n\n".join(context_chunks)
    return generate_rag_response(query, context, client, query_tokens, context_tokens)

def generate_rag_response(query, context, client, query_tokens, context_tokens):
    """Generate response using GPT-4o mini with retrieved context"""
    
    system_prompt = """You are a helpful assistant that answers questions based on the provided context. 
Use only the information in the context to answer questions. If the context doesn't contain 
relevant information, say "I don't have enough information to answer this question based on the provided documents." """
    
    user_prompt = f"""Context:
{context}

Question: {query}

Please provide a clear and accurate answer based only on the context above."""
    
    # Count system prompt tokens
    system_tokens = count_tokens(system_prompt)
    user_tokens = count_tokens(user_prompt)
    total_input_tokens = system_tokens + user_tokens
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=300,  # Limit response length
            temperature=0.1,  # Low temperature for factual responses
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        
        answer = response.choices[0].message.content
        output_tokens = response.usage.completion_tokens
        
        # Calculate costs
        input_cost = total_input_tokens * 0.15 / 1_000_000
        output_cost = output_tokens * 0.60 / 1_000_000
        total_cost = input_cost + output_cost
        
        usage_info = {
            'query_embedding_tokens': query_tokens,
            'context_tokens': context_tokens,
            'system_prompt_tokens': system_tokens,
            'user_prompt_tokens': user_tokens,
            'total_input_tokens': total_input_tokens,
            'output_tokens': output_tokens,
            'total_cost': total_cost
        }
        
        return answer, usage_info
        
    except Exception as e:
        print(f"Error generating response: {e}")
        raise
```

### 6. Token Usage Tracking

#### Comprehensive Token Tracking System
```python
class TokenTracker:
    def __init__(self):
        self.embedding_tokens = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = 0.0
        self.daily_usage = {}
        
    def add_embedding_usage(self, tokens):
        """Track embedding token usage"""
        self.embedding_tokens += tokens
        cost = tokens * 0.02 / 1000
        self.total_cost += cost
        self._update_daily_usage('embedding', tokens, cost)
        
    def add_chat_usage(self, input_tokens, output_tokens):
        """Track chat completion token usage"""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        
        input_cost = input_tokens * 0.15 / 1_000_000
        output_cost = output_tokens * 0.60 / 1_000_000
        total_cost = input_cost + output_cost
        
        self.total_cost += total_cost
        self._update_daily_usage('chat', input_tokens + output_tokens, total_cost)
        
    def _update_daily_usage(self, usage_type, tokens, cost):
        """Update daily usage tracking"""
        today = datetime.date.today().isoformat()
        if today not in self.daily_usage:
            self.daily_usage[today] = {'tokens': 0, 'cost': 0.0}
        
        self.daily_usage[today]['tokens'] += tokens
        self.daily_usage[today]['cost'] += cost
        
    def get_usage_summary(self):
        """Get comprehensive usage summary"""
        return {
            'embedding_tokens': self.embedding_tokens,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.embedding_tokens + self.input_tokens + self.output_tokens,
            'total_cost': self.total_cost,
            'daily_usage': self.daily_usage
        }
        
    def check_daily_limit(self, limit_dollars=5.0):
        """Check if daily spending limit is approached"""
        today = datetime.date.today().isoformat()
        if today in self.daily_usage:
            daily_cost = self.daily_usage[today]['cost']
            if daily_cost >= limit_dollars * 0.8:  # 80% of limit
                return f"Warning: Daily usage at ${daily_cost:.4f}, approaching ${limit_dollars} limit"
        return None
```

### 7. Complete Application Integration

#### Main Application Class
```python
class RAGChatApplication:
    def __init__(self, openai_key, pinecone_key, mongodb_uri):
        self.client = OpenAI(api_key=openai_key)
        self.index = setup_pinecone(pinecone_key)
        self.db = setup_mongodb(mongodb_uri)
        self.token_tracker = TokenTracker()
        
    def upload_document(self, file_path, document_id=None):
        """Complete document upload and processing pipeline"""
        if not document_id:
            document_id = f"doc_{int(datetime.datetime.utcnow().timestamp())}"
            
        # Process document
        text = process_uploaded_document(file_path)
        chunks = chunk_document(text)
        
        # Generate embeddings
        embeddings_data, embedding_tokens = generate_embeddings(chunks)
        self.token_tracker.add_embedding_usage(embedding_tokens)
        
        # Store in vector database
        store_embeddings(self.index, embeddings_data, document_id)
        
        # Store metadata in MongoDB
        store_document_metadata(
            self.db, document_id, 
            os.path.basename(file_path), 
            len(chunks), embedding_tokens
        )
        
        return {
            'document_id': document_id,
            'chunks_created': len(chunks),
            'tokens_used': embedding_tokens,
            'cost': embedding_tokens * 0.02 / 1000
        }
        
    def chat(self, query, user_id="default_user"):
        """Process chat query and return response"""
        # Generate response
        response, usage_info = process_rag_query(
            query, self.index, self.client
        )
        
        # Track token usage
        self.token_tracker.add_embedding_usage(usage_info['query_embedding_tokens'])
        self.token_tracker.add_chat_usage(
            usage_info['total_input_tokens'],
            usage_info['output_tokens']
        )
        
        # Store chat history
        store_chat_history(
            self.db, user_id, query, response,
            usage_info['total_input_tokens'] + usage_info['output_tokens']
        )
        
        # Check usage limits
        limit_warning = self.token_tracker.check_daily_limit()
        
        return {
            'response': response,
            'usage': usage_info,
            'warning': limit_warning,
            'total_cost_today': self.token_tracker.daily_usage.get(
                datetime.date.today().isoformat(), {'cost': 0}
            )['cost']
        }
        
    def get_usage_stats(self):
        """Get comprehensive usage statistics"""
        return self.token_tracker.get_usage_summary()
```

### 8. Environment Configuration

```python
# .env file template
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
MONGODB_URI=your_mongodb_atlas_connection_string

# Usage limits
DAILY_SPENDING_LIMIT=5.00
MAX_DOCUMENTS=5
MAX_DOCUMENT_SIZE_MB=1
MAX_DAILY_QUERIES=140
```

### Key Implementation Notes:

1. **Error Handling**: Implement comprehensive try-catch blocks around all API calls
2. **Rate Limiting**: Add request queuing for OpenAI API calls if needed
3. **Monitoring**: Log all token usage and costs for tracking
4. **Security**: Validate all inputs and sanitize file uploads
5. **Performance**: Use batch processing for embeddings when possible
6. **Storage**: Monitor MongoDB and Pinecone usage regularly

This implementation provides a complete, production-ready foundation for your RAG chat application within the free tier constraints.