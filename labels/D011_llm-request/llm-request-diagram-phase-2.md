# Dual-Mode Chat Flow Diagram

## 1. Data Structure

```
User -> [1.01 JSON] -> Server 1
                        | <- [1.02 JSON] <- Server 2      (MCP Tool Discovery)
                        | -> [1.03 JSON] -> LLM           (Chat Message)
                        | <- [1.04 JSON] <- LLM           (Provider-Agnostic Response)
                        | -> [1.05 JSON] -> Server 2+3    (MCP Tool Request)
                        | <- [1.06 JSON] <- Server 2+3    (MCP Tool Response)
                        | -> [1.07 JSON] -> LLM           (Tool Message)
User <- [1.08 SSE ] <- Server 1                           (Stream Response)
User <- [1.09 JSON] <- Server 1                           (Batch Response)
```

### 1.01. (User -> Server 1) Request - JSON Format String

```
[Chat Request - JSON]
|-- message: "user query"
|-- session_id: "uuid"
|-- model: "gpt-4-1106-preview"
+-- selected_tools: ["tool1", "tool2"] | null

[Required Headers]
|-- Content-Type: "application/json"
+-- Accept: "text/event-stream"
```

### 1.02. (Server 2 -> Server 1) MCP Tool Discovery Response - JSON Format String

```
[MCP Tool Discovery Response - JSON]
|-- tools[]
|   |-- name: "get_all_api_configs"
|   |-- description: "Retrieve all API configurations"
|   +-- input_schema: {
|       |-- type: "object"
|       |-- properties: {...}
|       +-- required: ["param1", "param2"]
|   }
+-- (multiple tools in array)

Note: Server 1 requests tools via: await session.list_tools()
```

### 1.03. (Server 1 -> LLM) Chat Completion Request - JSON Format String

```
[LLM Request - JSON]
|-- model: "gpt-4-1106-preview"
|-- messages: [
|   |-- {role: "user", content: "user query"},
|   |-- {role: "assistant", content: "previous response", tool_calls: [...]},
|   +-- {role: "tool", content: "tool result", tool_call_id: "call_123"}
|   ]
|-- tools: [
|   |-- {
|   |   |-- type: "function",
|   |   +-- function: {
|   |       |-- name: "get_all_api_configs",
|   |       |-- description: "Retrieve all API configurations",
|   |       +-- parameters: {...}
|   |   }
|   +-- (other available tools)
|   ]
|-- tool_choice: "auto"
|-- temperature: 0.7
+-- stream: false

Note: Converted from generic format via LlmOpenaiUtil.chat_messages_to_openai_format()
```

### 1.04. (LLM -> Server 1) Generic LLM Response - Provider-Agnostic Format

```
[LlmResponse - Generic]
|-- content: "LLM response text" | null
|-- tool_calls: [GenericToolCall] | null
|   |-- id: "call_abc123"
|   |-- type: "function"
|   +-- function:
|       |-- name: "get_all_api_configs"
|       +-- arguments: "{\"limit\": 10}"
|-- finish_reason: "stop" | "tool_calls" | null
+-- usage: {...} | null

[Helper Methods]
|-- has_tool_calls(): boolean
|-- get_status_text(): "Using tools: tool1, tool2..." | content
|-- to_chat_message_dict(): [tool_call_dicts] | null
+-- get_tool_execution_data(): [{"id", "name", "arguments"}]
```

### 1.05. (Server 1 -> Server 2+3) MCP Tool Call Request - JSON Format String

```
[MCP Tool Call - JSON]
|-- tool_name: "get_all_api_configs"
+-- arguments: {
    |-- limit: 10
    |-- offset: 0
    +-- other_params: "value"
}

Note: MCP client calls: await session.call_tool(tool_name, arguments)
```

### 1.06. (Server 2+3 -> Server 1) MCP Tool Call Response - JSON Format String

```
[MCP Tool Response - JSON]
|-- result: {...}  // Actual tool execution result
|-- success: true
+-- metadata:
    |-- tool_name: "get_all_api_configs"
    |-- execution_time: "45ms"
    +-- server: "Server 2 -> Server 3"
```

**Architecture Note**:

- This generic `LlmResponse` layer provides provider-agnostic abstraction. All OpenAI-specific knowledge is isolated in `LlmOpenaiUtil`,
- making it easy to add support for other LLM providers (Claude, Gemini, etc.) without changing server orchestration logic.

### 1.07. (Server 1 -> LLM) LLM Tool Message - JSON Format String

```
[Tool Result Message - JSON]
|-- role: "tool"
|-- content: "{\"result\": \"data\"}"
|-- tool_call_id: "call_abc123"
+-- name: "function_name"
```

### 1.08. (Server 1 -> User) Response - Stream Mode (No Tools) - SSE Format String

```
[SSE Response - String]
event: chunk
data: {
  "content": "token",
  "session_id": "uuid",
  "finished": false
}
```

### 1.09. (Server 1 -> User) Response - Batch Mode (With Tools) - JSON Format String

```
[JSON Response - JSON]
|-- response: "Complete synthesized answer with tool results"
|-- session_id: "uuid"
|-- model: "gpt-4-1106-preview"
+-- metadata:
    |-- batch_mode: true
    +-- fake_streaming_note: "Client should simulate word-by-word display"
```

## 2. Streaming Request Decision Tree

### 2.1. Endpoint Design Rationale

**`/api/v1/chat` (Batch Endpoint):**

- **No tool support by design**
- **Rationale**: Batch HTTP requests close connection after single response
- Sending intermediate tool responses would be wasteful and risk timeouts
- Only returns final synthesized result after all tool iterations complete
- Timeout risk acceptable for simple chat use cases

**`/api/v1/chat/stream` (Streaming Endpoint):**

- **Always returns SSE** (Server-Sent Events) regardless of tool usage
- **With tools**: SSE events contain complete JSON responses for each iteration
- **Without tools**: SSE events contain small text chunks for real-time streaming
- Consistent streaming interface for all scenarios

```
[User Request + Tool Selection] (Streaming Endpoint)
                 |
                 v
        +------------------+
        | selected_tools   |
        | provided?        |
        +--------+---------+
           |NO         |YES
           |           |
           v           v
 +-------------+    +-------------+
 | STREAM MODE |    | BATCH MODE  |
 | Real-time   |    | Complete +  |
 | Streaming   |    | Fake Stream |
 +-------------+    +-------------+
```

- (S) - System Message
- (U) - User Message
- (A) - Assistant Message
- (T) - Tool Message

### 2.2. Server Architecture

```
[Browser]
    |
    | Accept: text/event-stream
    v
[Server 1: Chat Stream Endpoint]
    |
    | Tool Selection Check
    |------------------------
    v                       |
[Stream Mode]           [Batch Mode]
    |                       |
    | No Tools              | Tools Selected
    v                       v
[Direct LLM]           [Tool Orchestration]
    |                       |
    | SSE Response          | Multiple LLM Calls
    v                       | + MCP Execution
[Real-time Stream]          v
                       [JSON Response]
```

### 2.3. Stream Mode Flow Process (No Tools)

```
User -> [Text (U)] ------------> [Create Message (U)] -> [Add to History]
                                  |
                                  v
                                 [Send History] ----> LLM Request (no tools)
                                  |
                                  v
User <- [Real-time Chunk (A)] <- [Chunk (A)]
                                  |
                                  v
                                 [Accumulate Chunk]
                                  |
                                  v
                                 [Add to History]
```

### 2.4. Batch Mode Flow Process (With Tools)

```
User -> [Text (U) + Tools (U)] ---> [Create Message (U)] -----------------> [Add to History]
                                     |
                                     v
                                    [Filter Tools (U)] <------------------- [All Tools]
                                     |
                                     v
                                    [Send History + Tools (U)] -----------> LLM Request
                                     ^     |
                                     |     v
User <- [Full JSON Message (A)] <---------[Message (A)] ------------------> [Add to History]
                                     |     |
                                     |     v
                                     |    [tool_calls (A)?] - YES
                                     |     |
                                     |     v
                                     |    [Run tool_calls (A)] -----------> MCP Client (Server 2+3)
                                     |     |
                                     |     v
                                     -----[Create Message (T)] -----------> [Add to History]
```

Note:

- tool_calls can run multiple tools in parallel.
- Message (T) - this contains the response from the MCP call
