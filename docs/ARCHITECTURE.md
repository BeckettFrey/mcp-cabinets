## Micro-Services

```
┌─────────────────┐    HTTP/REST    ┌──────────────────┐
│   MCP Service   │ ◄────────────── │   API Service    │
│   (stdio)       │                 │   (Port 8000)    │
└─────────────────┘                 └──────────────────┘
         ▲                                    ▲
         │ MCP Protocol                       │ HTTP API
         │ (stdio transport)                  │
         ▼                                    ▼
┌─────────────────┐                 ┌──────────────────┐
│   LLM Client    │                 │ Chrome Extension │
│ (Claude/GPT/etc)│                 │                  │
└─────────────────┘                 └──────────────────┘
```

## Benefits of This Architecture

### 1. **Separation of Concerns**
- **API Service**: Focuses purely on text processing, vector indexing, and storage
- **MCP Service**: Handles protocol compliance, tool definitions, and LLM integration
- **Clear Boundaries**: Each service has a well-defined responsibility

### 2. **Scalability**
- Services can be scaled independently based on load
- MCP service can handle multiple LLM clients without affecting API service performance
- API service can focus on heavy computational tasks

### 3. **Maintainability**
- Protocol changes only affect the MCP service
- Business logic changes only affect the API service
- Easier to debug and test individual components

### 4. **Flexibility**
- Can easily swap MCP implementations without touching indexing logic
- Can add multiple protocol layers (REST, GraphQL, gRPC) alongside MCP
- Future-proof architecture for protocol evolution

### 5. **Development Workflow**
- Teams can work on different services independently
- Different deployment cycles for each service
- Easier to add new features without cross-service conflicts

## Service Communication

### Chrome Extension → API Service
- **Protocol**: HTTP/REST
- **Port**: 8000
- **Purpose**: cabinet management, text indexing, direct queries
- **Endpoints**:
  - `POST /create_cabinet`
  - `POST /add_to_cabinet`
  - `GET /query_cabinet`
  - `GET /list_cabinets`
  - `DELETE /delete_cabinet/{cabinet_name}`
  - `GET /health`

### MCP Service → API Service
- **Protocol**: HTTP/REST (internal)
- **Port**: 8000
- **Purpose**: Tool execution, health monitoring

### LLM Clients → MCP Service
- **Protocol**: MCP (Model Context Protocol)
- **Transport**: stdio (default) or WebSocket
- **Port**: 8001 (if using WebSocket)
- **Tools**:
  - `retrieve_from_cabinet`: Search cabinets for relevant content
  - `list_cabinets`: Get all available cabinets
  - `get_cabinet_info`: Get cabinet metadata
  - `health_check`: Service status
