"""
A modern MCP server implementation using FastMCP 2.0
"""

import asyncio
import json
import logging
import sys
from typing import Optional

from fastmcp import FastMCP, Context

# Configure logging to stderr for MCP compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

try:
    from client import get_client, close_client
    from config import MCP_CONFIG, ERROR_MESSAGES
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

# Create FastMCP server
mcp = FastMCP(MCP_CONFIG["service_name"])


@mcp.tool
async def retrieve_from_cabinet(
    cabinet_name: str, 
    query: str, 
    top_k: int = 5, 
    ctx: Optional[Context] = None
) -> str:
    """
    Retrieve relevant text chunks from a specific cabinet.
    
    Args:
        cabinet_name: Name of the cabinet to search in
        query: Search query to find relevant content
        top_k: Number of top results to return (1-20, default: 5)
    
    Returns:
        JSON string with search results and summary
    """
    if ctx:
        await ctx.info(f"Retrieving from cabinet '{cabinet_name}' with query '{query}' (top_k={top_k})")
    
    # Validate parameters
    if not cabinet_name:
        error_result = {"success": False, "error": ERROR_MESSAGES["INVALID_cabinet_NAME"]}
        return json.dumps(error_result, indent=2)
    
    if not query:
        error_result = {"success": False, "error": ERROR_MESSAGES["INVALID_QUERY"]}
        return json.dumps(error_result, indent=2)
    
    # Validate top_k parameter
    if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
        top_k = 5
    
    try:
        # Make request to indexing service
        client = await get_client()
        response = await client.query_cabinet(cabinet_name, query, top_k)
        
        if response.success:
            # Format successful response
            results = response.data.get("results", [])
            
            if results:
                summary = f"Found {len(results)} relevant chunks from cabinet '{cabinet_name}':\n\n"
                for i, chunk in enumerate(results, 1):
                    score = chunk.get("relevance_score", 0.0)
                    text = chunk.get("text", "")
                    summary += f"{i}. (Score: {score:.2f}) {text[:200]}...\n\n"
            else:
                summary = f"No relevant chunks found in cabinet '{cabinet_name}' for query '{query}'"
            
            result = {
                "success": True,
                "cabinet_name": cabinet_name,
                "query": query,
                "top_k": top_k,
                "summary": summary,
                **response.data
            }
            
        else:
            result = {
                "success": False,
                "error": response.error,
                "cabinet_name": cabinet_name,
                "query": query
            }
            if ctx:
                await ctx.error(f"Failed to retrieve from cabinet '{cabinet_name}': {response.error}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in retrieve_from_cabinet: {e}", exc_info=True)
        if ctx:
            await ctx.error(f"Exception in retrieve_from_cabinet: {str(e)}")
        
        error_result = {
            "success": False,
            "error": f"Failed to retrieve from cabinet: {str(e)}",
            "cabinet_name": cabinet_name,
            "query": query
        }
        return json.dumps(error_result, indent=2)


@mcp.tool
async def list_cabinets(ctx: Optional[Context] = None) -> str:
    """
    List all available cabinets.
    
    Returns:
        JSON string with list of cabinets and their information
    """
    if ctx:
        await ctx.info("Listing all cabinets")
    
    try:
        client = await get_client()
        response = await client.list_cabinets()
        
        if response.success:
            cabinets = response.data.get("cabinets", [])
            
            # Create a readable summary
            if cabinets:
                summary = f"Found {len(cabinets)} cabinets:\n\n"
                for cabinet_data in cabinets:
                    name = cabinet_data.get("name", "Unknown")
                    count = cabinet_data.get("chunk_count", 0)
                    created = cabinet_data.get("created_at", "Unknown")
                    updated = cabinet_data.get("last_updated", "Unknown")
                    
                    summary += f"• {name}: {count} chunks (created: {created}, updated: {updated})\n"
            else:
                summary = "No cabinets found"
            
            result = {
                "success": True,
                "summary": summary,
                **response.data
            }
        else:
            result = {
                "success": False,
                "error": response.error
            }
            if ctx:
                await ctx.error(f"Failed to list cabinets: {response.error}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in list_cabinets: {e}", exc_info=True)
        if ctx:
            await ctx.error(f"Exception in list_cabinets: {str(e)}")
        
        error_result = {"success": False, "error": f"Failed to list cabinets: {str(e)}"}
        return json.dumps(error_result, indent=2)


@mcp.tool
async def get_cabinet_info(cabinet_name: str, ctx: Optional[Context] = None) -> str:
    """
    Get detailed information about a specific cabinet.
    
    Args:
        cabinet_name: Name of the cabinet to get information about
    
    Returns:
        JSON string with cabinet information
    """
    if ctx:
        await ctx.info(f"Getting info for cabinet '{cabinet_name}'")
    
    if not cabinet_name:
        error_result = {"success": False, "error": ERROR_MESSAGES["INVALID_cabinet_NAME"]}
        return json.dumps(error_result, indent=2)
    
    try:
        client = await get_client()
        response = await client.get_cabinet_info(cabinet_name)
        
        if response.success:
            cabinet_info = response.data.get("cabinet", {})
            
            # Create readable summary
            name = cabinet_info.get("name", "Unknown")
            count = cabinet_info.get("chunk_count", 0)
            created = cabinet_info.get("created_at", "Unknown")
            updated = cabinet_info.get("last_updated", "Unknown")
            
            summary = f"cabinet '{name}' contains {count} text chunks.\nCreated: {created}\nLast updated: {updated}"
            
            result = {
                "success": True,
                "summary": summary,
                "cabinet_info": cabinet_info
            }
        else:
            result = {
                "success": False,
                "error": response.error,
                "cabinet_name": cabinet_name
            }
            if ctx:
                await ctx.error(f"Failed to get cabinet info for '{cabinet_name}': {response.error}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in get_cabinet_info: {e}", exc_info=True)
        if ctx:
            await ctx.error(f"Exception in get_cabinet_info: {str(e)}")
        
        error_result = {
            "success": False,
            "error": f"Failed to get cabinet info: {str(e)}",
            "cabinet_name": cabinet_name
        }
        return json.dumps(error_result, indent=2)


@mcp.tool
async def health_check(ctx: Optional[Context] = None) -> str:
    """
    Check the health status of the indexing service.
    
    Returns:
        JSON string with health status information
    """
    if ctx:
        await ctx.info("Performing health check")
    
    try:
        client = await get_client()
        response = await client.health_check()
        
        if response.success:
            health_data = response.data
            summary = f"Indexing service is healthy. Status: {health_data.get('status', 'unknown')}"
            if "cabinets_loaded" in health_data:
                summary += f"\ncabinets loaded: {health_data['cabinets_loaded']}"
            if "embedding_model" in health_data:
                summary += f"\nEmbedding model: {health_data['embedding_model']}"
            
            result = {
                "success": True,
                "summary": summary,
                **health_data
            }
        else:
            result = {
                "success": False,
                "error": response.error,
                "summary": "Indexing service is not available"
            }
            if ctx:
                await ctx.error(f"Health check failed: {response.error}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in health_check: {e}", exc_info=True)
        if ctx:
            await ctx.error(f"Exception in health_check: {str(e)}")
        
        error_result = {
            "success": False,
            "error": f"Health check failed: {str(e)}",
            "summary": "Indexing service is not available"
        }
        return json.dumps(error_result, indent=2)


if __name__ == "__main__":
    try:
        mcp.run()
    finally:
        # Ensure the HTTP client is closed after the server stops
        asyncio.run(close_client())