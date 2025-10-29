"""MCP Client for connecting to FastMCP server"""
import httpx
import json
import os
from typing import Any, Dict, Optional
import asyncio


class MCPClient:
    """Client for interacting with MCP server tools."""
    
    def __init__(self, server_url: str = None):
        """
        Initialize MCP client.
        
        Args:
            server_url: URL of the MCP server
        """
        if server_url is None:
            server_url = os.getenv("MCP_BASE", "https://symptoms-tracker-mcp.onrender.com")
        self.server_url = server_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool arguments
        
        Returns:
            Tool execution result
        """
        try:
            response = await self.client.post(
                f"{self.server_url}/tools/{tool_name}",
                json=kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool call failed: {str(e)}"
            }
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        try:
            response = await self.client.get(f"{self.server_url}/tools")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_resource(self, resource_uri: str) -> str:
        """Get a resource from the MCP server."""
        try:
            response = await self.client.get(
                f"{self.server_url}/resources",
                params={"uri": resource_uri}
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Resource fetch failed: {str(e)}"
    
    async def close(self):
        """Close the client connection."""
        await self.client.aclose()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.run(self.close())


class SyncMCPClient:
    """Synchronous wrapper for MCP client."""
    
    def __init__(self, server_url: str = None):
        if server_url is None:
            server_url = os.getenv("MCP_BASE", "https://symptoms-tracker-mcp.onrender.com")
        self.server_url = server_url
        self.client = httpx.Client(timeout=30.0)
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Synchronous tool call."""
        try:
            response = self.client.post(
                f"{self.server_url}/tools/{tool_name}",
                json=kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool call failed: {str(e)}"
            }
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        try:
            response = self.client.get(f"{self.server_url}/tools")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close the client."""
        self.client.close()
