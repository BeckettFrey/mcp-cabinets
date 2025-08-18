# File: mcp-service/config.py
"""
Configuration for the Model Context Protocol service
"""

from typing import Dict, Any

# MCP Service Configuration
MCP_CONFIG = {
    "service_name": "cabinets-chat-mcp",
    "version": "1.0.0",
    "description": "MCP service for Cabinets Chat cabinet retrieval",
    "transport": "stdio",
    "host": "localhost",
    "port": 8001, 
}

# Indexing Service Configuration
INDEXING_SERVICE_CONFIG = {
    "base_url": "http://localhost:8000",
    "timeout": 30.0,
    "max_retries": 3,
    "retry_delay": 1.0,
    "health_check_interval": 60.0,  # seconds
}

# Tool Definitions for MCP
MCP_TOOLS = [
    {
        "name": "retrieve_from_cabinet",
        "description": "Retrieve relevant text chunks from a specific cabinet using semantic search",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cabinet_name": {
                    "type": "string",
                    "description": "Name of the cabinet to search in"
                },
                "query": {
                    "type": "string", 
                    "description": "Search query to find relevant content"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top results to return (1-20)",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5
                }
            },
            "required": ["cabinet_name", "query"]
        }
    },
    {
        "name": "list_cabinets",
        "description": "List all available cabinets with their metadata",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_cabinet_info",
        "description": "Get detailed information about a specific cabinet",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cabinet_name": {
                    "type": "string",
                    "description": "Name of the cabinet to get information about"
                }
            },
            "required": ["cabinet_name"]
        }
    },
    {
        "name": "health_check",
        "description": "Check the health status of the indexing service",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# Resource Definitions for MCP (if supporting resources)
MCP_RESOURCES = [
    {
        "uri": "cabinets-chat://cabinets",
        "name": "Available cabinets",
        "description": "List of all available text cabinets",
        "mimeType": "application/json"
    }
]

# Error Messages
ERROR_MESSAGES = {
    "SERVICE_UNAVAILABLE": "Indexing service is not available",
    "INVALID_cabinet_NAME": "Invalid cabinet name provided",
    "INVALID_QUERY": "Query cannot be empty",
    "NETWORK_ERROR": "Network error communicating with indexing service",
    "TIMEOUT_ERROR": "Request to indexing service timed out",
    "INVALID_PARAMETERS": "Invalid parameters provided",
    "UNKNOWN_ERROR": "An unknown error occurred"
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": {
        "console": True,
        "file": True,
        "file_path": "./mcp-service.log"
    }
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration dict"""
    return {
        "mcp": MCP_CONFIG,
        "indexing_service": INDEXING_SERVICE_CONFIG,
        "tools": MCP_TOOLS,
        "resources": MCP_RESOURCES,
        "errors": ERROR_MESSAGES,
        "logging": LOGGING_CONFIG
    }
