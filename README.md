# Production RAG System

A production-ready Retrieval-Augmented Generation (RAG) system for policy document analysis using LlamaIndex, Pinecone, and FastAPI.
### [Pitch Deck Link](https://1drv.ms/p/c/997174930b242a72/EYNvt2U7A_BBlBGnKIs1fhkBkfxIL-87XYE7G_sx4qLe0A?e=eeUqUD)

## Features

- **PDF Parsing**: LlamaParse for extracting structured text from policy documents
- **Vector Search**: Pinecone with cosine similarity for semantic retrieval
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2) for text embeddings
- **LLM Integration**: Groq or OpenRouter for answer generation
- **Database**: PostgreSQL for logging queries and responses
- **API**: FastAPI with automatic OpenAPI documentation
- **Authentication**: Bearer token authentication
- **Production Ready**: Comprehensive error handling, logging, and monitoring

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Pinecone account
- Groq or OpenRouter API key
- LlamaParse API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rag_system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual API keys and database credentials
```

4. Set up the database:
```bash
# Create PostgreSQL database
createdb rag_db

# The application will automatically create tables on startup
```

5. Run the application:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

### Main Endpoint

**POST /hackrx/run**

Process a policy document and answer questions.

```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/policy.pdf",
    "questions": [
      "What is the grace period for premium payment?",
      "What are the coverage limits?"
    ]
  }'
```

### Other Endpoints

- **GET /health**: Health check
- **GET /queries**: Recent queries (for monitoring)

## Configuration

All configuration is handled through environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_ENVIRONMENT`: Pinecone environment
- `GROQ_API_KEY` or `OPENROUTER_API_KEY`: LLM provider API key
- `LLAMA_PARSE_API_KEY`: LlamaParse API key
- `BEARER_TOKEN`: Authentication token

## Architecture

- **Modular Design**: Clear separation of concerns with dedicated services
- **Error Handling**: Comprehensive error handling with meaningful messages
- **Logging**: Structured logging for monitoring and debugging
- **Database Integration**: PostgreSQL for persistent storage
- **Authentication**: Secure API access with bearer tokens

## Performance Considerations

- Chunking strategy optimized for policy documents
- Batch embedding generation for efficiency
- Vector search with configurable top-k results
- Connection pooling for database operations

## Monitoring

The system includes:
- Request/response logging
- Processing time tracking
- Error monitoring
- Health check endpoints

## Security

- Bearer token authentication
- Input validation
- SQL injection prevention
- Rate limiting considerations

## Deployment

For production deployment:

1. Set `ENVIRONMENT=production` in your .env
2. Configure proper database connections
3. Set up reverse proxy (nginx)
4. Use production WSGI server settings
5. Set up monitoring and logging aggregation
