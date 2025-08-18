# API Service

A FastAPI-based indexing service that provides semantic search capabilities for text content using LlamaIndex and FAISS vector storage.

## 🚀 Overview

The API Service is the core indexing engine that handles:
- **Text Indexing**: Store and organize content in named cabinets
- **Semantic Search**: Find relevant content using AI embeddings
- **Vector Storage**: Persistent FAISS-based vector indices
- **REST API**: Clean HTTP interface for all operations

## 🛠 Technology Stack

- **FastAPI** - Modern Python web framework
- **LlamaIndex** - Document indexing and retrieval
- **FAISS** - Facebook AI Similarity Search for vector storage
- **HuggingFace** - Sentence transformers for embeddings
- **Pydantic** - Data validation and settings management

## 📁 Bonsai Tree

```
├── scripts/                # Utility scripts
│   ├── datastore/          # Scripts for managing data cache
│   │   ├── clear.sh        # Clear all cabinet data and folders from storage
│   │   └── pseudo.sh       # Generate pseudo data for testing
│   ├── tests/              # Test scripts
│   │   └── test_api.sh     # Shell script to test API endpoints
│   └── cli.sh              # Interactive command-line interface for API
├── config.py               # Configuration settings for the API service
├── models.py               # Pydantic models for request/response schemas
├── pyproject.toml          # Project metadata and dependencies
├── README.md               # Project documentation
├── server.py               # Main FastAPI server application
└── uv.lock                 # Dependency lock file
```

## 🚦 Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync
source .venv/bin/activate
```

### 2. Start the Server

```bash
python server.py
```

The server will start on `http://localhost:8000` (as set in `config.py` under `SERVER_CONFIG`).  
You can adjust the host, port, and other server settings in the configuration file:

### 3. Use the Interactive CLI

```bash
./scripts/cli.sh
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```
Returns server status and configuration info.

### Cabinet Management
```http
POST /create_cabinet
Content-Type: application/json

{
  "cabinet_name": "my-documents"
}
```

```http
GET /list_cabinets
```

```http
DELETE /delete_cabinet/{cabinet_name}
```

### Content Management
```http
POST /add_to_cabinet
Content-Type: application/json

{
  "cabinet_name": "my-documents",
  "text": "Your content here...",
  "source_url": "https://example.com/source"
}
```

### Search
```http
GET /query_cabinet?cabinet_name=my-documents&query=search+terms&top_k=5&similarity_threshold=0.7
```

## 🔧 Configuration

Key configuration options in `config.py`:

```python
# Server Configuration
SERVER_CONFIG = {
    "host": "localhost",
    "port": 8000,
    "debug": False,
    "cors_enabled": True
}

# Embedding Model
EMBEDDING_CONFIG = {
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "max_seq_length": 512,
    "normalize_embeddings": True
}

# Similarity Search
RETRIEVAL_CONFIG = {
    "similarity_threshold": 0.7,
    "max_top_k": 20
}
```

## 🧪 Testing

### Run Tests
```bash
# ./scripts/tests/*
./scripts/tests/test_api.sh
```

### Interactive Testing
```bash
# Start the CLI to interact with api
./scripts/cli.sh

# Available commands:
cabinets-chat> health          # Check server status
cabinets-chat> create my-cabinet   # Create a new cabinet
cabinets-chat> add my-cabinet      # Add content interactively
cabinets-chat> query my-cabinet    # Search for content
cabinets-chat> list            # List all cabinets
```

## 🗄 Data Management
### Storage Location

All indexed data is stored in the `storage/` directory, as configured by `STORAGE_CONFIG["persist_path"]` in `config.py`. Each cabinet has its own subdirectory containing the following files:

```
storage/
├── cabinet-name-1/
│   ├── vector_store.json    # FAISS vector index data
│   ├── docstore.json        # Raw document content and metadata
│   └── index_store.json     # Index mapping and metadata
└── cabinet-name-2/
  ├── vector_store.json
  ├── docstore.json
  └── index_store.json
```

- The storage format is set by `STORAGE_CONFIG["format"]` (default: `"faiss"`).
- Backups are disabled by default (`STORAGE_CONFIG["backup_enabled"] = False`).
- The storage path is automatically created if it does not exist.

### Manage Storage
```bash
./scripts/datastore/*
The `clear.sh` script will leave a `cleanup_log` file in the `storage/` directory to record previous cleanup actions.
```

⚠️ **Warning**: This permanently deletes all cabinets and content!

### Backup Data
```bash
# Create backup
tar -czf backup-$(date +%Y%m%d).tar.gz storage/

# Restore backup
tar -xzf backup-20240817.tar.gz
```

## 🔍 Similarity Search Details

The service uses **L2 distance** with the following behavior:

- **Lower distance = Higher similarity**
- **Threshold Mapping**: `l2_threshold = 2.0 - similarity_threshold`
- **Display Score**: `similarity = exp(-l2_distance)` (0-1 range)

Example with 0.7 similarity threshold:
- L2 threshold: 1.3
- Results with L2 distance ≤ 1.3 are returned
- Display scores are exponentially decayed for intuitive reading

## 🔗 Integration

This API service is designed to work with:
- [**MCP Service**](../mcp-service/) - Provides MCP protocol interface
- **Chrome Extension** - For browser integration
- [**ContextCaddy**](https://github.com/beckettfrey/ContextCaddy) - Chrome Extension
