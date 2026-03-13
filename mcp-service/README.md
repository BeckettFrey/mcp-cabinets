# MCP Service

A Model Context Protocol (MCP) server that provides semantic search capabilities for Context Cabinets. This service acts as a bridge between MCP-compatible applications (like Cherry Studio) and the api-service.

## Overview

The MCP Service provides:
- **MCP Protocol Interface** - Standard MCP server implementation
- **Semantic Search Tools** - Retrieve content from indexed cabinets
- **HTTP Client Integration** - Communicates with the API service
- **Error Handling** - Robust error handling and retry logic
- **FastMCP Framework** - Modern, clean MCP server implementation

## Technology Stack

- **FastMCP** - Modern MCP server framework
- **httpx** - Async HTTP client for API communication
- **tenacity** - Retry mechanisms with exponential backoff

## Bonsai Tree

```
mcp-service/
├── __tests__/
│   └── test_mcp.py           # MCP testing (pytest)
├── client.py                 # HTTP client for API service
├── config.py                 # Configuration settings
├── mcp.config.json           # MCP server configuration
├── mcp_server.py             # Main FastMCP server
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # This file
└── uv.lock                   # Dependency lock file
```

## Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync
source .venv/bin/activate
```

### 2. Start the API Service First

> **Prerequisite:** Make sure you have set up the API service. See [../api-service/README.md](../api-service/README.md) for setup instructions.

### 3. Start the MCP Server

```bash
python mcp_server.py
```

## Configuration

### MCP Service Configuration (`config.py`)

```python
# MCP Server Configuration
MCP_CONFIG = {
    "service_name": "mcp-cabinets",
    "version": "1.0.0"
}

# Indexing Service Connection
INDEXING_SERVICE_CONFIG = {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1
}

# Error Messages
ERROR_MESSAGES = {
    "SERVICE_UNAVAILABLE": "Indexing service is not available",
    "TIMEOUT_ERROR": "Request timed out",
    "NETWORK_ERROR": "Network connection failed"
}
```

### Cherry Studio Configuration (`mcp.config.json`)

```json
{
  "mcpServers": {
    "mcp-cabinets": {
      "command": "./.venv/bin/activate",
      "args": ["fastmcp_server.py"],
      "cwd": "/path/to/mcp-cabinets/mcp-service",
      "env": {}
    }
  }
}
```

## MCP Tools

### 1. retrieve_from_cabinet
Retrieve relevant content from a specific cabinet using semantic search.

**Parameters:**
- `cabinet_name` (string): Name of the cabinet to search
- `query` (string): Search query
- `top_k` (int, optional): Number of results (default: 5)

**Example:**
```python
# Via MCP
retrieve_from_cabinet(
    cabinet_name="ai-research",
    query="machine learning algorithms",
    top_k=3
)
```

### 2. list_cabinets
Get a list of all available cabinets with metadata.

**Parameters:** None

**Returns:** List of cabinets with chunk counts and timestamps

### 3. get_cabinet_info
Get detailed information about a specific cabinet.

**Parameters:**
- `cabinet_name` (string): Name of the cabinet

**Returns:** cabinet metadata including creation date and content stats

### 4. health_check
Check the health status of both the MCP service and indexing service.

**Parameters:** None

**Returns:** Health status and service availability

## Testing

### Test MCP Functionality

```bash
# Run tests
pytest
```

## Integration with Cherry Studio

### 1. Update Configuration

Edit your Cherry Studio configuration file with the correct paths:

```json
{
  "mcpServers": {
    "mcp-cabinets": {
      "command": "/path/to/mcp-cabinets/mcp-service/.venv/bin/python",
      "args": ["/path/to/mcp-cabinets/mcp-service/mcp_server.py"]
    }
  }
}
```

### 2. Verify Connection

You should see the Cabinets Chat tools available in Cherry Studio's tool palette:
- retrieve_from_cabinet
- list_cabinets
- get_cabinet_info
- health_check

### Cherry Studio Connection Issues

1. **Check paths in `mcp.config.json`:**
  ```bash
  # Verify Python path
  /path/to/mcp-cabinets/mcp-service/.venv/bin/python --version

  # Verify script path
  ls -la /path/to/mcp-cabinets/mcp-service/fastmcp_server.py
  ```

2. **Ensure `uv` is installed and not shadowed by other Python managers:**
  ```bash
  # Check if uv is installed and on PATH
  which uv
  uv --version
  ```

  > If you use other Python environment managers (like pipenv, poetry, conda), make sure they do not override or conflict with uv.

2. **Check Cherry Studio logs** for connection errors

3. **Test MCP server directly:**
   ```bash
   python fastmcp_server.py
   # Should show: "Starting FastMCP server..."
   ```

### Tools Not Appearing

1. **Restart Cherry Studio** after configuration changes
2. **Check MCP server logs** for initialization errors
3. **Verify API service** is running and accessible

### Search Returns No Results

1. **Check if cabinets have content:**
   ```bash
   curl http://localhost:8000/list_cabinets
   ```

2. **Try lower similarity threshold:**
   - Default threshold is 0.7
   - Try queries with more general terms

3. **Verify cabinet exists:**
   - Use `list_cabinets` tool first
   - Check cabinet names for typos
