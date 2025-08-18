"""
FastAPI server with LlamaIndex integration for per-cacabinetet text indexing and retrieval
"""
import json
import math
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

import faiss
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from llama_index.core import VectorStoreIndex, Document, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from config import (
    EMBEDDING_CONFIG, SERVER_CONFIG,
    FAISS_CONFIG, RETRIEVAL_CONFIG, CHUNK_CONFIG, HISTORY_CONFIG,
    ERROR_MESSAGES, get_storage_path
)

from models import (
    CreatecabinetRequest, AddChunkRequest,
    ChunkMetadata, cabinetMetadata
)

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
indices = {}
cabinet_metadata = {}
text_splitter = None

def setup_llama_index():
    """Initialize LlamaIndex with HuggingFace embeddings"""
    global text_splitter
    
    try:
        # Configure embeddings
        embed_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_CONFIG["model"],
            max_length=EMBEDDING_CONFIG["max_seq_length"],
            normalize=EMBEDDING_CONFIG["normalize_embeddings"]
        )
        
        Settings.embed_model = embed_model
        Settings.chunk_size = CHUNK_CONFIG["target_size"]
        Settings.chunk_overlap = CHUNK_CONFIG["overlap"]
        
        # Disable LLM to avoid OpenAI dependency - we only want vector retrieval
        Settings.llm = None
        
        # Initialize text splitter
        text_splitter = SentenceSplitter(
            chunk_size=CHUNK_CONFIG["target_size"],
            chunk_overlap=CHUNK_CONFIG["overlap"]
        )
        
        logger.info(f"Initialized LlamaIndex with {EMBEDDING_CONFIG['model']} (LLM disabled)")
    except Exception as e:
        logger.error(f"Failed to initialize LlamaIndex: {e}")
        logger.info("Continuing without embeddings - using simple text search")

def validate_text_size(text: str) -> tuple[bool, str]:
    """Validate text size according to chunk requirements"""
    if not text or not text.strip():
        return False, ERROR_MESSAGES["NO_CONTENT"]
    
    words = text.split()
    word_count = len(words)
    
    if word_count < EMBEDDING_CONFIG["min_chunk_size"]:
        return False, ERROR_MESSAGES["TEXT_TOO_SHORT"]
    
    return True, ""

def process_text_chunks(text: str) -> List[str]:
    """Process text into appropriate chunks"""
    words = text.split()
    word_count = len(words)
    
    if word_count <= EMBEDDING_CONFIG["max_chunk_size"]:
        return [text]
    
    # Use sentence-aware splitting for large texts if available
    if text_splitter:
        try:
            nodes = text_splitter.get_nodes_from_documents([Document(text=text)])
            return [node.text for node in nodes]
        except Exception as e:
            logger.warning(f"Text splitter failed, using fallback: {e}")
    
    # Fallback: simple word-based chunking
    chunks = []
    target_size = CHUNK_CONFIG["target_size"]
    
    for i in range(0, word_count, target_size):
        chunk_words = words[i:i + target_size]
        if len(chunk_words) >= EMBEDDING_CONFIG["min_chunk_size"]:
            chunks.append(" ".join(chunk_words))
    
    return chunks

def create_cabinet_index(cabinet_name: str) -> VectorStoreIndex:
    """Create a new FAISS index for a cabinet"""
    try:
        # Create FAISS index
        faiss_index = faiss.IndexFlatL2(FAISS_CONFIG["dimension"])
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Create empty index
        index = VectorStoreIndex([], storage_context=storage_context)
        
        # Persist immediately
        cabinet_path = os.path.join(get_storage_path(), cabinet_name)
        os.makedirs(cabinet_path, exist_ok=True)
        index.storage_context.persist(persist_dir=cabinet_path)
        
        return index
    except Exception as e:
        logger.error(f"Failed to create FAISS index for {cabinet_name}: {e}")
        # Fallback to simple in-memory index
        return VectorStoreIndex([])

def load_cabinet_index(cabinet_name: str) -> Optional[VectorStoreIndex]:
    """Load an existing cabinet index from storage"""
    cabinet_path = os.path.join(get_storage_path(), cabinet_name)
    
    if not os.path.exists(cabinet_path):
        return None
    
    try:
        storage_context = StorageContext.from_defaults(persist_dir=cabinet_path)
        index = VectorStoreIndex.load_from_storage(storage_context)
        return index
    except Exception as e:
        logger.error(f"Failed to load cabinet {cabinet_name}: {e}")
        logger.info(f"Attempting to recover cabinet {cabinet_name} by recreating index...")
        
        # Try to recover by creating a new index and clearing corrupted data
        try:
            import shutil
            shutil.rmtree(cabinet_path)
            logger.info(f"Cleared corrupted storage for cabinet {cabinet_name}")
            
            # Create a new empty index
            index = create_cabinet_index(cabinet_name)
            logger.info(f"Created new index for cabinet {cabinet_name}")
            return index
        except Exception as recovery_error:
            logger.error(f"Failed to recover cabinet {cabinet_name}: {recovery_error}")
            return None

def update_cabinet_metadata(cabinet_name: str, text: str, source_url: Optional[str] = None):
    """Update cabinet metadata with new chunk information"""
    now = datetime.utcnow().isoformat() + "Z"
    word_count = len(text.split())
    preview = text[:HISTORY_CONFIG["preview_length"]]
    if len(text) > HISTORY_CONFIG["preview_length"]:
        preview += "..."
    
    chunk_meta = ChunkMetadata(
        added_at=now,
        preview=preview,
        word_count=word_count,
        source_url=source_url
    )
    
    if cabinet_name not in cabinet_metadata:
        cabinet_metadata[cabinet_name] = cabinetMetadata(
            created_at=now,
            chunk_count=0,
            last_updated=now,
            recent_chunks=[]
        )
    
    meta = cabinet_metadata[cabinet_name]
    meta.chunk_count += 1
    meta.last_updated = now
    meta.recent_chunks.append(chunk_meta)
    
    # Keep only the most recent chunks
    if len(meta.recent_chunks) > HISTORY_CONFIG["max_recent_chunks"]:
        meta.recent_chunks = meta.recent_chunks[-HISTORY_CONFIG["max_recent_chunks"]:]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    setup_llama_index()

    logger.info("LlamaIndex setup complete")

    # Load existing cabinets
    storage_path = get_storage_path()
    
    if os.path.exists(storage_path):
        for cabinet_dir in os.listdir(storage_path):
            cabinet_path = os.path.join(storage_path, cabinet_dir)
            if os.path.isdir(cabinet_path):
                index = load_cabinet_index(cabinet_dir)
                if index:
                    indices[cabinet_dir] = index
                    
                    # Initialize metadata if not exists (for recovered cabinets)
                    if cabinet_dir not in cabinet_metadata:
                        now = datetime.utcnow().isoformat() + "Z"
                        cabinet_metadata[cabinet_dir] = cabinetMetadata(
                            created_at=now,
                            chunk_count=0,
                            last_updated=now,
                            recent_chunks=[]
                        )
                    
                    logger.info(f"Loaded cabinet: {cabinet_dir}")
                else:
                    logger.warning(f"Failed to load cabinet: {cabinet_dir}")
    
    logger.info(f"Server initialized with {len(indices)} cabinets")
    
    yield  # Server is running
    
    # Shutdown (cleanup if needed)
    logger.info("Server shutting down")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Cabinets Chat Server",
    description="Server for per-cabinet text indexing and retrieval",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
if SERVER_CONFIG["cors_enabled"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "cabinets_loaded": len(indices),
        "embedding_model": EMBEDDING_CONFIG["model"],
        "llama_index_available": text_splitter is not None
    }

@app.post("/create_cabinet")
async def create_cabinet(request: CreatecabinetRequest):
    """Create a new cabinet for text indexing"""
    cabinet_name = request.cabinet_name.strip()
    
    if cabinet_name in indices:
        raise HTTPException(
            status_code=400, 
            detail=ERROR_MESSAGES["cabinet_EXISTS"]
        )
    
    try:
        index = create_cabinet_index(cabinet_name)
        indices[cabinet_name] = index
        
        # Initialize metadata
        now = datetime.utcnow().isoformat() + "Z"
        cabinet_metadata[cabinet_name] = cabinetMetadata(
            created_at=now,
            chunk_count=0,
            last_updated=now,
            recent_chunks=[]
        )
        
        logger.info(f"Created cabinet: {cabinet_name}")
        return {"message": f"cabinet '{cabinet_name}' created successfully"}
        
    except Exception as e:
        logger.error(f"Failed to create cabinet {cabinet_name}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_MESSAGES["SERVER_ERROR"])

@app.post("/add_to_cabinet")
async def add_to_cabinet(request: AddChunkRequest):
    """Add text chunk to a specific cabinet"""
    cabinet_name = request.cabinet_name.strip()
    text = request.text.strip()
    
    if cabinet_name not in indices:
        raise HTTPException(
            status_code=404, 
            detail=ERROR_MESSAGES["cabinet_NOT_FOUND"]
        )
    
    # Validate text size
    is_valid, error_msg = validate_text_size(text)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        # Process text into chunks
        chunks = process_text_chunks(text)
        
        # Add each chunk to the index
        for chunk in chunks:
            doc = Document(text=chunk)
            indices[cabinet_name].insert(doc)
        
        # Update metadata
        update_cabinet_metadata(cabinet_name, text, request.source_url)
        
        # Persist changes if using FAISS
        try:
            cabinet_path = os.path.join(get_storage_path(), cabinet_name)
            if os.path.exists(cabinet_path):
                indices[cabinet_name].storage_context.persist(persist_dir=cabinet_path)
        except Exception as e:
            logger.warning(f"Failed to persist cabinet {cabinet_name}: {e}")
        
        logger.info(f"Added {len(chunks)} chunk(s) to cabinet: {cabinet_name}")
        return {
            "message": "Text added and indexed successfully",
            "chunks_created": len(chunks),
            "total_word_count": len(text.split())
        }
        
    except Exception as e:
        logger.error(f"Failed to add text to cabinet {cabinet_name}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_MESSAGES["SERVER_ERROR"])

@app.get("/query_cabinet")
async def query_cabinet(cabinet_name: str, query: str, top_k: int = 5, similarity_threshold: float = None):
    """Query a specific cabinet for relevant content"""
    if cabinet_name not in indices:
        raise HTTPException(
            status_code=404, 
            detail=ERROR_MESSAGES["cabinet_NOT_FOUND"]
        )
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    top_k = min(max(top_k, 1), RETRIEVAL_CONFIG["max_top_k"])
    
    # Use provided threshold or default from config
    if similarity_threshold is None:
        similarity_threshold = RETRIEVAL_CONFIG["similarity_threshold"]
    else:
        # Ensure threshold is within valid range
        similarity_threshold = max(0.0, min(1.0, similarity_threshold))
    
    try:
        start_time = time.time()
        
        # Check if cabinet has any content
        try:
            # Get the underlying vector store to check if it has any vectors
            vector_store = indices[cabinet_name].vector_store
            if hasattr(vector_store, 'client') and hasattr(vector_store.client, 'ntotal'):
                if vector_store.client.ntotal == 0:
                    logger.info(f"cabinet {cabinet_name} is empty, returning empty results")
                    return {
                        "success": True,
                        "cabinet_name": cabinet_name,
                        "query": query,
                        "results": [],
                        "total_chunks_searched": 0,
                        "response_time_ms": 0,
                        "similarity_threshold": similarity_threshold,
                        "results_found": 0,
                        "results_filtered": 0,
                        "requested_top_k": top_k,
                        "message": "cabinet is empty"
                    }
        except Exception as check_error:
            logger.warning(f"Could not check cabinet content status: {check_error}")
        
        # Use retriever instead of query engine to avoid LLM dependency
        retriever = indices[cabinet_name].as_retriever(similarity_top_k=top_k)
        
        # Execute retrieval with error handling
        try:
            nodes = retriever.retrieve(query)
        except Exception as retrieval_error:
            logger.error(f"Retrieval failed for cabinet {cabinet_name}: {retrieval_error}")
            # Return empty results on retrieval failure
            return {
                "success": True,
                "cabinet_name": cabinet_name,
                "query": query,
                "results": [],
                "total_chunks_searched": cabinet_metadata.get(cabinet_name, cabinetMetadata(created_at="", chunk_count=0, last_updated="", recent_chunks=[])).chunk_count,
                "response_time_ms": 0,
                "similarity_threshold": similarity_threshold,
                "results_found": 0,
                "results_filtered": 0,
                "requested_top_k": top_k,
                "error": "Retrieval failed - cabinet may be empty or corrupted"
            }
        
        response_time = int((time.time() - start_time) * 1000)
        
        # Format response with L2 distance threshold filtering
        results = []
        filtered_count = 0
        
        # Convert similarity threshold (0-1) to L2 distance threshold
        # Since L2 distance uses "lower = better", we need to invert the logic
        # A similarity threshold of 0.7 should correspond to an L2 distance threshold
        # We'll use a simple mapping: higher similarity threshold = lower L2 distance threshold
        # For 0.7 similarity threshold, we'll allow L2 distances up to about 1.4
        # For 0.8 similarity threshold, we'll allow L2 distances up to about 1.3
        # For 0.9 similarity threshold, we'll allow L2 distances up to about 1.2
        l2_distance_threshold = 2.0 - similarity_threshold  # Maps 0.7->1.3, 0.8->1.2, 0.9->1.1
        
        logger.info(f"Query '{query}' returned {len(nodes)} nodes, using L2 distance threshold: {l2_distance_threshold}")
        
        for i, node in enumerate(nodes):
            # Get the raw L2 distance score from the node
            l2_distance = float(node.score) if hasattr(node, 'score') else float('inf')
            
            logger.info(f"Node {i}: L2 distance = {l2_distance}")
            
            # Apply threshold filtering: keep results with L2 distance <= threshold
            if l2_distance <= l2_distance_threshold:
                # Convert L2 distance to a similarity score (0-1) for display
                # Use exponential decay: similarity = exp(-distance)
                similarity_score = math.exp(-l2_distance)
                
                results.append({
                    "chunk_id": f"chunk_{len(results):03d}",
                    "text": node.text,
                    "relevance_score": similarity_score,
                    "l2_distance": l2_distance,  # Include raw distance for debugging
                    "word_count": len(node.text.split())
                })
            else:
                filtered_count += 1
                logger.info(f"Filtered out node {i} with L2 distance {l2_distance} > threshold {l2_distance_threshold}")
        
        return {
            "success": True,
            "cabinet_name": cabinet_name,
            "query": query,
            "results": results,
            "total_chunks_searched": cabinet_metadata.get(cabinet_name, cabinetMetadata(created_at="", chunk_count=0, last_updated="", recent_chunks=[])).chunk_count,
            "response_time_ms": response_time,
            "similarity_threshold": similarity_threshold,
            "results_found": len(results),
            "results_filtered": filtered_count,
            "requested_top_k": top_k
        }
        
    except Exception as e:
        logger.error(f"Failed to query cabinet {cabinet_name}: {e}")
        logger.error(f"Query details - cabinet: {cabinet_name}, query: {query}, top_k: {top_k}, threshold: {similarity_threshold}")
        logger.error(f"Available cabinets: {list(indices.keys())}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/list_cabinets")
async def list_cabinets():
    """List all available cabinets with metadata"""
    try:
        cabinets = []
        for cabinet_name, metadata in cabinet_metadata.items():
            cabinets.append({
                "name": cabinet_name,
                "chunk_count": metadata.chunk_count,
                "created_at": metadata.created_at,
                "last_updated": metadata.last_updated
            })
        
        return {
            "success": True,
            "cabinets": cabinets,
            "total_cabinets": len(cabinets)
        }
        
    except Exception as e:
        logger.error(f"Failed to list cabinets: {e}")
        raise HTTPException(status_code=500, detail=ERROR_MESSAGES["SERVER_ERROR"])

@app.delete("/delete_cabinet/{cabinet_name}")
async def delete_cabinet(cabinet_name: str):
    """Delete a cabinet and its associated data"""
    if cabinet_name not in indices:
        raise HTTPException(
            status_code=404, 
            detail=ERROR_MESSAGES["cabinet_NOT_FOUND"]
        )
    
    try:
        # Remove from memory
        del indices[cabinet_name]
        if cabinet_name in cabinet_metadata:
            del cabinet_metadata[cabinet_name]
        
        # Remove from disk
        cabinet_path = os.path.join(get_storage_path(), cabinet_name)
        if os.path.exists(cabinet_path):
            import shutil
            shutil.rmtree(cabinet_path)
        
        logger.info(f"Deleted cabinet: {cabinet_name}")
        return {"message": f"cabinet '{cabinet_name}' deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete cabinet {cabinet_name}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_MESSAGES["SERVER_ERROR"])

# Simple WebSocket endpoint for basic tool calls
@app.websocket("/tools")
async def websocket_tools(websocket: WebSocket):
    """Simple WebSocket endpoint for tool calls"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            
            tool_name = request.get("tool")
            params = request.get("params", {})
            
            if tool_name == "retrieve_from_cabinet":
                cabinet_name = params.get("cabinet_name")
                query = params.get("query")
                top_k = params.get("top_k", 5)
                
                if cabinet_name and query:
                    try:
                        result = await query_cabinet(cabinet_name, query, top_k)
                        await websocket.send_text(json.dumps({
                            "success": True,
                            "result": result
                        }))
                    except HTTPException as e:
                        await websocket.send_text(json.dumps({
                            "success": False,
                            "error": e.detail
                        }))
                else:
                    await websocket.send_text(json.dumps({
                        "success": False,
                        "error": "Missing cabinet_name or query"
                    }))
                    
            elif tool_name == "list_cabinets":
                try:
                    result = await list_cabinets()
                    await websocket.send_text(json.dumps({
                        "success": True,
                        "result": result
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "success": False,
                        "error": str(e)
                    }))
            else:
                await websocket.send_text(json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }))
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host=SERVER_CONFIG["host"],
        port=SERVER_CONFIG["port"],
        reload=SERVER_CONFIG["debug"],
        log_level="info"
    )
