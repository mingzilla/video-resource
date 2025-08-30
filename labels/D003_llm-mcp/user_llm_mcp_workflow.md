## System Overview

```
[Browser] ←→ [Server 1: LLM + MCP Client] ←→ [LLM API]
(no API key)           ↓ (Direct MCP)
             [Server 2: MCP Proxy Server]
                       ↓ (REST)
             [Server 3: Existing REST API]
```

### Notes about Server 1 and Server 2 separation

**Generic Solution Debate:**
- Generic solutions work well for simple chat completions without tool calling
- MCP integration makes generic approaches impractical due to provider-specific tool calling schemas
- Providers frequently change JSON schemas when releasing new models, forcing generic solutions to reinvent provider libraries

**Separation of Volatility:**
- Server 1 handles volatile provider dependencies and evolving model schemas
- Server 2 provides stable MCP interface, isolated from provider changes
- When providers update tool calling schemas for new models, only Server 1 requires rebuilding

```
Server 1 (LLM+MCP Client) ←→ Server 2 (MCP Proxy) ←→ Server 3 (FastAPI)
[Provider Dependencies]     [Stable Interface]    [Business Logic]
```
