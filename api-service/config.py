# File: /mcp-cabinets/api-service/config.py
"""
Configuration settings for the API Service 
"""
import os
from typing import Dict, Any

# Embedding Configuration
EMBEDDING_CONFIG = {
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "provider": "huggingface",
    "dim": 384,
    "max_chunk_size": 500,  # words
    "min_chunk_size": 10,   # words
    "max_seq_length": 512,
    "normalize_embeddings": True,
    "batch_size": 32
}

# Storage Configuration
STORAGE_CONFIG = {
    "persist_path": "./storage",
    "format": "faiss",
    "backup_enabled": False
}

# Server Configuration
SERVER_CONFIG = {
    "port": 8000,
    "host": "127.0.0.1",
    "protocol": "http/ws",
    "cors_enabled": True,
    "debug": True
}

# MCP Configuration
MCP_CONFIG = {
    "exposed_tools": [
        {
            "name": "retrieve_from_cacabinetet",
            "description": "Retrieve context from a specific cacabinetet using a query",
            "params": ["cacabinetet_name", "query"]
        },
        {
            "name": "list_cabinets",
            "description": "List all available cabinets with metadata",
            "params": []
        }
    ],
    "scope": "retrieval_only"
}

# FAISS Configuration
FAISS_CONFIG = {
    "index_type": "IndexFlatL2",
    "dimension": 384,
    "metric": "l2_distance"
}

# Retrieval Configuration
RETRIEVAL_CONFIG = {
    "default_top_k": 5,
    "max_top_k": 20,
    "similarity_threshold": 0.7,
    "response_mode": "compact",
    "include_metadata": True
}

# Chunk Processing Configuration
CHUNK_CONFIG = {
    "target_size": 400,  # words per chunk (buffer for sentence boundaries)
    "overlap": 0,        # no overlap as specified
    "sentence_boundary_aware": True
}

# History Configuration
HISTORY_CONFIG = {
    "max_recent_chunks": 50,
    "preview_length": 50  # characters
}

# Error Messages
ERROR_MESSAGES = {
    "EMPTY_INPUT": "Text is empty",
    "NO_CONTENT": "Text contains only whitespace",
    "TEXT_TOO_SHORT": "Text too short to index (minimum 10 words)",
    "cabinet_NOT_FOUND": "cabinet not found",
    "cabinet_EXISTS": "cabinet already exists",
    "SERVER_ERROR": "Internal server error",
    "INVALID_CHUNK_SIZE": "Chunk size must be between 10 and 500 words"
}

def get_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary"""
    return {
        "embedding": EMBEDDING_CONFIG,
        "storage": STORAGE_CONFIG,
        "server": SERVER_CONFIG,
        "mcp": MCP_CONFIG,
        "faiss": FAISS_CONFIG,
        "retrieval": RETRIEVAL_CONFIG,
        "chunk": CHUNK_CONFIG,
        "history": HISTORY_CONFIG,
        "errors": ERROR_MESSAGES
    }

def get_storage_path() -> str:
    """Get the storage path, creating it if it doesn't exist"""
    path = STORAGE_CONFIG["persist_path"]
    os.makedirs(path, exist_ok=True)
    return path
