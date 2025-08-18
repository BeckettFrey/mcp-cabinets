# File: mcp-service/client.py
"""
HTTP Client for communicating with the indexing service
"""
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import INDEXING_SERVICE_CONFIG, ERROR_MESSAGES

logger = logging.getLogger(__name__)

@dataclass
class ServiceResponse:
    """Response from the indexing service"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None

class IndexingServiceClient:
    """HTTP client for communicating with the indexing service"""
    
    def __init__(self):
        self.base_url = INDEXING_SERVICE_CONFIG["base_url"]
        self.timeout = INDEXING_SERVICE_CONFIG["timeout"]
        self.max_retries = INDEXING_SERVICE_CONFIG["max_retries"]
        self.retry_delay = INDEXING_SERVICE_CONFIG["retry_delay"]
        
        # HTTP client with timeout and connection pooling
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        self._service_available = True
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException))
    )
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> ServiceResponse:
        """Make HTTP request to the indexing service with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.client.request(method, url, **kwargs)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return ServiceResponse(success=True, data=data, status_code=response.status_code)
                except json.JSONDecodeError:
                    return ServiceResponse(
                        success=False, 
                        error="Invalid JSON response", 
                        status_code=response.status_code
                    )
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", f"HTTP {response.status_code}")
                except Exception:
                    error_msg = f"HTTP {response.status_code}"
                
                return ServiceResponse(
                    success=False, 
                    error=error_msg, 
                    status_code=response.status_code
                )
                
        except httpx.TimeoutException:
            logger.error(f"Timeout error for {method} {url}")
            return ServiceResponse(success=False, error=ERROR_MESSAGES["TIMEOUT_ERROR"])
        
        except httpx.NetworkError as e:
            logger.error(f"Network error for {method} {url}: {e}")
            return ServiceResponse(success=False, error=ERROR_MESSAGES["NETWORK_ERROR"])
        
        except Exception as e:
            logger.error(f"Unexpected error for {method} {url}: {e}")
            return ServiceResponse(success=False, error=ERROR_MESSAGES["UNKNOWN_ERROR"])
    
    async def health_check(self) -> ServiceResponse:
        """Check if the indexing service is healthy"""
        response = await self._make_request("GET", "/health")
        
        if response.success:
            self._service_available = True
            logger.debug("Indexing service health check passed")
        else:
            self._service_available = False
            logger.warning("Indexing service health check failed")
        
        return response
    
    async def list_cabinets(self) -> ServiceResponse:
        """Get list of all cabinets from the indexing service"""
        if not self._service_available:
            await self.health_check()
        
        return await self._make_request("GET", "/list_cabinets")
    
    async def query_cabinet(
        self, 
        cabinet_name: str, 
        query: str, 
        top_k: int = 5
    ) -> ServiceResponse:
        """Query a specific cabinet for relevant content"""
        if not self._service_available:
            await self.health_check()
        
        params = {
            "cabinet_name": cabinet_name,
            "query": query,
            "top_k": top_k
        }
        
        return await self._make_request("GET", "/query_cabinet", params=params)
    
    async def get_cabinet_info(self, cabinet_name: str) -> ServiceResponse:
        """Get information about a specific cabinet"""
        cabinets_response = await self.list_cabinets()
        
        if not cabinets_response.success:
            return cabinets_response
        
        cabinets = cabinets_response.data.get("cabinets", [])
        cabinet_info = next((cabinet for cabinet in cabinets if cabinet["name"] == cabinet_name), None)
        
        if cabinet_info:
            return ServiceResponse(success=True, data={"cabinet": cabinet_info})
        else:
            return ServiceResponse(
                success=False, 
                error=f"cabinet '{cabinet_name}' not found", 
                status_code=404
            )
    
    @property
    def is_available(self) -> bool:
        """Check if the service is currently available"""
        return self._service_available

# Global client instance
_client: Optional[IndexingServiceClient] = None

async def get_client() -> IndexingServiceClient:
    """Get or create the global client instance"""
    global _client
    if _client is None:
        _client = IndexingServiceClient()
    return _client

async def close_client():
    """Close the global client instance"""
    global _client
    if _client is not None:
        await _client.client.aclose()
        _client = None
