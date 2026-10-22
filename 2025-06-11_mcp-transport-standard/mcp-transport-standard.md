# MCP Transport

- JSON-RPC
- Transport
- Transport Data Format

## JSON-RPC

JSON-RPC is a particular format of JSON with certain required fields.

### JSON-RPC Structure

| Field       | Required   | Description                                       |
|-------------|------------|---------------------------------------------------|
| `"jsonrpc"` | ✅ Yes      | Must be exactly "2.0"                             |
| `"method"`  | ✅ Yes      | String with method name                           |
| `"params"`  | ❌ Optional | Named parameters (object) or positional (array)   |
| `"id"`      | ✅ Yes*     | *Required for requests, omitted for notifications |

## Transport

### `Transport Types` and `Data Format`

| Transport Type      | Communication   | Network Layer | Machine      | Client→Server (request)      | Client Accept Header                  | Server→Client (response)             |
|---------------------|-----------------|---------------|--------------|------------------------------|---------------------------------------|--------------------------------------|
| **stdio**           | **file system** | local pipes   | same         | Raw JSON-RPC                 | N/A (no HTTP)                         | Raw JSON-RPC                         |
| **Streamable HTTP** | **network**     | TCP/IP        | same or diff | Raw JSON-RPC (via HTTP POST) | `application/json, text/event-stream` | Raw JSON-RPC OR SSE-wrapped JSON-RPC |

Network: `localhost:port` or `remote.server.com`

Streamable HTTP:

- Note: The `Accept header` doesn't specify which format you want - it specifies which formats you can handle
- The MCP specification requires clients to list BOTH formats in Accept header: `application/json, text/event-stream`
- batch mode - server side 100% returns Raw JSON-RPC (application/json)
- stream mode - server side 100% returns SSE-wrapped JSON-RPC (text/event-stream)

| Server Mode | Response Format                 | Content-Type        | Data Format                                |
|-------------|---------------------------------|---------------------|--------------------------------------------|
| **batch**   | ✅ **100%** Raw JSON-RPC         | `application/json`  | `{"jsonrpc":"2.0","result":...}`           |
| **stream**  | ✅ **100%** SSE-wrapped JSON-RPC | `text/event-stream` | `data: {"jsonrpc":"2.0","result":...}\n\n` |

## Transport Data Format

The **JSON-RPC message content is identical** in both cases - only the **wrapping/delivery format** differs:

### stdio Transport - Raw JSON-RPC string (no wrapping):

```
{"jsonrpc":"2.0","result":{"tools":[...]},"id":1}
```

### Streamable HTTP Transport - SSE-wrapped JSON-RPC string:

```
HTTP/1.1 200 OK
Content-Type: text/event-stream

data: {"jsonrpc":"2.0","result":{"tools":[...]},"id":1}
```