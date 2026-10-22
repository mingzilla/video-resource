# Boundary Connection Diagram: /chat/openai-stream Endpoint

## 1. Flow Overview

This diagram shows the complete data flow through the `/chat/openai-stream` endpoint, highlighting boundary domain (BD) crossings and the classes involved.

### Key Boundary Domain Benefits

1. **Clean Separation**: Each boundary crossing is explicit via boundary models
2. **Type Safety**: Pydantic validation at each boundary
3. **Error Handling**: Encapsulated in boundary model static methods
4. **Testability**: Each layer can be tested independently

### 2.1. Notation

- `[component]` = Flow/action classes or external systems
- `(BoundaryModel)` = Boundary domain classes that provide clean separation
- **Purpose**: Show how boundary domain classes eliminate hard dependencies and external documentation lookups

### 2.2. Sequence Diagram: Boundary Domain Flow

```text
[browser] ---(ApiChatRequest)--> [chat_router]               [chat_service]        [chat_history_repo]  [llm_client]    [OpenAI/Ollama]
                                    |                             |                           |           |                   |
                                    |----(ApiChatRequest)-------->|                           |           |                   |
                                    |                             |                           |           |                   |
                                    |                             |---(ApiChatMessage)------> |           |                   |
                                    |                             |                           |           |                   |
                                    |                             |<--List[(ApiChatMessage)]--|           |                   |
                                    |                             |                           |           |                   |
                                    |                             |---(LlmMessage)----------------------->|                   |
                                    |                             |                           |           |                   |
                                    |                             |                           |           |--(OpenAIRequest)->|
                                    |                             |                           |           |                   |
                                    |                             |<--(OpenAIChunk)-----------------------|<-(OpenAIChunk)----|
                                    |                             |                           |
                                    |                             |                           |
                                    |                             |                           |
                                    |<--(ApiChatCompletionChunk)--|                           |
                                    |                             |                           |
[browser] <---SSE Events------------|                             |   cumulate chunks         |
                                                                  |---(ApiChatMessage)------->|
```

## 2. Boundary Model

### 2.1. Example Structure

```text
[LlmRequest - JSON]
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
```

### 2.2. Key Rule

Apply Boundary Domains to any `Dict` field

- Be aware of Pydantic Model Eager Loading Performance Issue

### 2.3. Naming Conventions

**Purpose**: Prefixes allow different domains (`Api*`, `User*`, `Product*`, etc.) to have unique boundaries for different topics.

### Api* Prefix (HTTP API Boundary)

- `(ApiChatRequest)` - HTTP request input
- `(ApiChatMessage)` - Internal message representation
- `(ApiChatCompletionChunk)` - OpenAI streaming response format

### Domain* Prefix (Internal Business Logic)

- `(DomainToolSelection)` - Tool selection configuration

### OpenAI* Prefix (OpenAI API Boundary)

- `(OpenAIRequest)` - OpenAI API request format
- `(OpenAIChunk)` - OpenAI API response chunk format

### Llm* Prefix (LLM Provider Abstraction)

- `(LlmMessage)` - Abstract LLM message format
- `(LlmRequest)` - Abstract LLM request
- `(LlmResponse)` - Abstract LLM response

## 2.3. Static Method Pattern

The `(ApiChatCompletionChunk)` boundary model encapsulates conversion logic:

```python
# Boundary model handles try/except logic
ApiChatCompletionChunk.create_from_raw_chunk(
    raw_chunk=raw_chunk,
    completion_id=completion_id,
    created=created_timestamp,
    model=model
)

# Service just calls and yields
openai_chunk = ApiChatCompletionChunk.create_from_raw_chunk(...)
yield {"event": "chunk", "data": openai_chunk.model_dump_json()}
```

---

## Dict Usage - TopicOutMidIn Naming Convention

### Fields Using `Dict[str, Any]`

#### **Function Call Details**:

```python
OpenAIToolCall.function: Dict[str, Any]
```

**Could become**: `*ToolCallFunction` classes

#### **Tool Calls Lists**:

```python
ApiChatMessage.tool_calls: Optional[List[Dict[str, Any]]]
OpenAIChatCompletionChunk.choices: List[Dict[str, Any]]
```

**Could become**: `*ToolCall` and `*Choice` classes

#### **Other Dict Fields**:

- `logprobs: Dict[str, Any]` → `*Logprobs` classes
- `usage: Dict[str, Any]` → `*Usage` classes
- `inputSchema: Dict[str, Any]` → `*Schema` classes
- `arguments: Dict[str, Any]` → `*Arguments` classes

### TopicOutMidIn Naming Convention

**Example transformations**:

```text
# OpenAIToolCall
function: Dict[str, Any]

# With TopicOutMidIn
OpenAIToolCallFunction  # OpenAI topic, ToolCall out, Function mid
```
