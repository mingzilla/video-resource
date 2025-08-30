## Request-Response Flow Diagram

```
[1. Documentation]  ---- MCP tools, FastAPI Swagger docs
        |
        |
        v
[2. URL Patterns]   ---- Add `/`
        |
        v
[3. Data Structure] ---- MCP flat params, FastAPI models
        |
        v
[4. HTTP Methods]   ---- MCP POST, FastAPI 4 types
        |
        |
        v
[5. Validation]     ---- FastAPI only
        |
        v
[6. Error Handling] ---- FastAPI generates, MCP forwards
        |
        |
        v
[7. Return Types]   ---- FastAPI types, MCP dicts
```

| Flow Stage            | MCP Proxy Server                                                 | FastAPI Controller                                      | Impact/Notes                                                         |
|-----------------------|------------------------------------------------------------------|---------------------------------------------------------|----------------------------------------------------------------------|
| **1. Documentation**  | Tool descriptions and parameter comments drive MCP effectiveness | Auto-generated Swagger docs at `/docs` endpoint         | Different documentation approaches for different audiences           |
| **2. URL Patterns**   | Must append `/` to endpoints to avoid FastAPI redirects          | Triggers redirect if trailing slash missing             | MCP proxy needs `f"{API_CONFIG_ENDPOINT}/"` to prevent redirect logs |
| **3. Data Structure** | Flat parameters in `@mcp.tool()` functions                       | Pydantic models (`ApiConfigCreate`, `ApiConfigUpdate`)  | MCP tools flatten Pydantic models into individual parameters         |
| **4. HTTP Methods**   | Tools don't specify HTTP method (determined by proxy logic)      | Explicit HTTP methods (`GET`, `POST`, `PUT`, `DELETE`)  | MCP abstracts away HTTP method selection                             |
| **5. Validation**     | No validation (relies on FastAPI)                                | Automatic Pydantic validation on request/response       | All validation handled by FastAPI layer                              |
| **6. Error Handling** | Can inherit errors generically from FastAPI via proxy            | HTTP status codes and `HTTPException`                   | MCP proxy forwards FastAPI errors - generic solution possible        |
| **7. Return Types**   | `Dict[str, Any]` or `List[Dict[str, Any]]`                       | Pydantic response models (`ApiConfig`) with type safety | MCP receives FastAPI's JSON response as dictionaries                 |
