# MCP Implementation Guide

## Two MCP Implementations

This project now supports **TWO** MCP implementations:

### 1. Custom HTTP MCP Server (Current/Default)
**Location:** `mcp_server/http_server.py`
**Client:** `langgraph_agent/mcp_client.py`
**Endpoints:** `/api/v2/symptoms/submit`

**How it works:**
- Custom FastAPI server exposing tools via HTTP endpoints
- Simple HTTP client making POST requests
- Easy to debug and test
- Works well with current architecture

**Pros:**
- ✅ Simple HTTP requests
- ✅ Easy debugging
- ✅ No complex protocol
- ✅ Works with any HTTP client

**Cons:**
- ❌ Not official MCP protocol
- ❌ Can't use with Claude Desktop
- ❌ Custom implementation

### 2. Real FastMCP Server (New)
**Location:** `mcp_server/fastmcp_server.py`
**Client:** `langgraph_agent/fastmcp_client.py`
**Endpoints:** `/api/v2/fastmcp/submit-symptoms`

**How it works:**
- Uses official FastMCP library
- Stdio transport (process communication)
- Follows MCP specification
- Compatible with Claude Desktop

**Pros:**
- ✅ Official MCP protocol
- ✅ Works with Claude Desktop
- ✅ Standard implementation
- ✅ Better type safety

**Cons:**
- ❌ More complex setup
- ❌ Harder to debug
- ❌ Requires process management

## Usage

### Using Custom HTTP MCP (Default)

**Start HTTP MCP Server:**
```bash
python run_mcp_server.py
```

**API Endpoint:**
```bash
POST /api/v2/symptoms/submit
```

### Using Real FastMCP

**No separate server needed** - FastMCP starts automatically when called

**API Endpoint:**
```bash
POST /api/v2/fastmcp/submit-symptoms
```

**List Tools:**
```bash
GET /api/v2/fastmcp/tools
```

## Comparison

| Feature | Custom HTTP | Real FastMCP |
|---------|-------------|--------------|
| Protocol | Custom HTTP | Official MCP |
| Transport | HTTP | Stdio |
| Server | Separate process | Auto-started |
| Claude Desktop | ❌ No | ✅ Yes |
| Debugging | Easy | Complex |
| Setup | Simple | Moderate |

## Recommendation

- **For Development:** Use Custom HTTP MCP (easier debugging)
- **For Production:** Use Real FastMCP (standard protocol)
- **For Claude Desktop:** Must use Real FastMCP

## Migration Path

1. **Current:** Custom HTTP MCP working
2. **Test:** Try FastMCP endpoints
3. **Validate:** Ensure both work
4. **Switch:** Update Streamlit to use FastMCP
5. **Remove:** Deprecate HTTP MCP server

## Testing FastMCP

```python
# Test FastMCP tools
import asyncio
from mcp_langgraph_app.langgraph_agent.fastmcp_client import FastMCPClient

async def test():
    async with FastMCPClient("mcp_server/fastmcp_server.py") as client:
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        result = await client.call_tool(
            "analyze_symptoms_with_ai",
            symptoms=[{"symptom": "Headache", "intensity": 7}],
            free_text="Severe headache"
        )
        print(f"Result: {result}")

asyncio.run(test())
```

## Claude Desktop Integration

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "symptom-tracker": {
      "command": "python",
      "args": ["c:/symptom_tracker_project/symptom_tracker_project/mcp_langgraph_app/mcp_server/fastmcp_server.py"]
    }
  }
}
```

Now Claude Desktop can use your symptom tracker tools!
