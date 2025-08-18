# Pydantic models
"""
FastAPI server with LlamaIndex integration for per-cabinet text indexing and retrieval
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class CreatecabinetRequest(BaseModel):
    cabinet_name: str = Field(..., min_length=1, max_length=100)

class AddChunkRequest(BaseModel):
    cabinet_name: str = Field(..., min_length=1, max_length=100)
    text: str = Field(..., min_length=1)
    source_url: Optional[str] = None

class QuerycabinetRequest(BaseModel):
    cabinet_name: str = Field(..., min_length=1, max_length=100)
    query: str = Field(..., min_length=1)
    top_k: Optional[int] = Field(default=5, ge=1, le=20)

class ChunkMetadata(BaseModel):
    added_at: str
    preview: str
    word_count: int
    source_url: Optional[str] = None

class cabinetMetadata(BaseModel):
    created_at: str
    chunk_count: int
    last_updated: str
    recent_chunks: List[ChunkMetadata]
