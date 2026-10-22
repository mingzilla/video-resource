## Choosing MCP Server Implementation

How to choose which type of transport when implementing an MCP Server.

| Transport           | Server on Local   | Server on Remote |
|---------------------|-------------------|------------------|
| **stdio**           | ✅                 | ❌ (not possible) |
| **Streamable HTTP** | ❌ (network waste) | ✅                |
| **SSE**             | ❌ (network waste) | ✅ (legacy)       |

## Illustration

GIVEN: [MCP Client] runs on MACHINE1 - e.g. Claude Desktop

```
MCP Client (Claude Desktop) on MACHINE1
├── stdio → Local MCP Server (npx file-server) - MACHINE1
├── Streamable HTTP → MCP Server via Network (https://api.example.com/mcp) - MACHINE1/MACHINE2
└── SSE → MCP Server via Network (https://api.example.com/sse) - MACHINE1/MACHINE2 - ❌ legacy
```

| Requirement                             | Solution        | Reason                |
|-----------------------------------------|-----------------|-----------------------|
| **No [MCP Server] on MACHINE1**         | Streamable HTTP | Server runs elsewhere |
| **[MCP Server] acts on MACHINE1 files** | stdio           | File system access    |

### 1. No [MCP Server] on MACHINE1 -- Streamable HTTP

| MACHINE1     | network      | MACHINE2     |
|--------------|--------------|--------------|
| [MCP Client] | <-- HTTP --> | [MCP Server] |

✅ No installation needed on MACHINE1  
✅ Server managed elsewhere

### 2. [MCP Server] needs to access MACHINE1 files -- stdio

| MACHINE1                                                | network | MACHINE2 |
|---------------------------------------------------------|---------|----------|
| [MCP Client] <-- stdio --> [MCP Server] → [File System] |         |          |

✅ Direct file access  
✅ No network latency  
✅ No network security concerns  
✅ Works offline

## The Trade-off:

- **Convenience**: Streamable HTTP (no local setup)
- **Performance + Security**: stdio (direct access, no network)

## Non Production

| MACHINE1     | network                  | MACHINE1     |
|--------------|--------------------------|--------------|
| [MCP Client] | <-- HTTP --> (localhost) | [MCP Server] |

- creates unnecessary network traffic
- valid if you use the same machine to implement this MCP Server
