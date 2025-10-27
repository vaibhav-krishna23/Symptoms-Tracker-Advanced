"""SSE MCP Client for connecting to real MCP server"""
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
import httpx
import json
from typing import Any

class SSEMCPClient:
    """Client for SSE-based MCP server"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        async with httpx.AsyncClient() as client:
            async with sse_client(f"{self.base_url}/sse") as (read, write):
                self.session = ClientSession(read, write)
                await self.session.__aenter__()
                return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
    
    async def call_tool(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """Call MCP tool and return result"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager")
        
        result = await self.session.call_tool(tool_name, arguments=kwargs)
        
        # Parse result from TextContent
        if result.content and len(result.content) > 0:
            text_content = result.content[0].text
            return json.loads(text_content)
        
        return {"error": "No result returned"}
    
    async def list_tools(self) -> list[str]:
        """List available tools"""
        if not self.session:
            raise RuntimeError("Client not initialized")
        
        tools = await self.session.list_tools()
        return [tool.name for tool in tools.tools]
