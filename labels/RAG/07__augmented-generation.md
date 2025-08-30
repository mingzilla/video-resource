# Augmented Generation

## 1. Prompt and Context Window

### 1.1. Prompt

```text
Use the following context to answer the query:
Context: {chunks}
Query: {query}
```

### 1.2. Context Window Constraints

**WHAT**: LLM models have fixed context windows limiting total input tokens
**WHY**: Processing cost and memory constraints require input size restrictions
**Example**: `chunks` and `query` have dynamic length

## 2. Template and Size Control

### Approach

**WHAT**: Due to context window, may need to restrict size of chunks
**WHY text size**: Easy
**HOW**: Set string character limits

| Approach      | Complexity | Accuracy |
|---------------|------------|----------|
| **Text Size** | Low        | Good     |
| Token Count   | Very High  | Perfect  |

### 2.1. Standard Template

```
Use the following context to answer the query:
Context: {chunks}
Query: {query}
```

### 2.2. Incomplete Context Template

```
Use the following truncated context to answer the query:
Context: {chunks}
(warn user: truncated context due to text size)
Query: {query}
```

## 3. Token and Cost

### 3.1. max_tokens Parameter

The `max_tokens` parameter in the OpenAI API request body has 2 purposes:

1. **Sets response limit**: Controls the maximum number of tokens in the generated response
2. **Reserves tokens**: Ensures space is reserved for the response within the context window

```bash
# Example: max_tokens limits response length, not input
curl -X POST https://api.openai.com/v1/chat/completions \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [...],
    "max_tokens": 500
  }'
```

- **Input tokens**: Model context window minus `max_tokens` value
- **Output tokens**: Limited by `max_tokens` parameter
- **Total tokens**: Input + Output cannot exceed context window

### 3.2. Cost Structure

**WHAT**: Input and output tokens have different pricing
**WHY**: Processing costs vary between encoding and generation
**HOW**: Monitor both input and output token usage

| Token Type | Cost Factor | Optimization Strategy   |
|------------|-------------|-------------------------|
| **Input**  | Lower       | Efficient context size  |
| **Output** | Higher      | Control response length |
| **Total**  | Combined    | Balance both factors    |

## 4. API Request Patterns

```bash
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": "Use the following context: {chunks} Query: {query}"
      }
    ],
    "stream": false/true
  }'
```

## 5. Response Processing Patterns

### 5.1. Non-Streaming Response

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-3.5-turbo-0613",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on the context provided, the laptop offers excellent performance for daily tasks..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 75,
    "total_tokens": 225
  }
}
```

### 5.2. SSE Streaming Response Example

- The format is "data: {...}\n\n" - "\n\n" is required
- Last chunk adds additional "data: [DONE]"

**First chunk:**
```text
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"gpt-3.5-turbo-0613","choices":[{"index":0,"delta":{"role":"assistant","content":"Based on the context"},"finish_reason":null}]}

```

**Second chunk:**
```text
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"gpt-3.5-turbo-0613","choices":[{"index":0,"delta":{"content":" provided, the laptop offers"},"finish_reason":null}]}

```

**Last chunk:**
```text
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"gpt-3.5-turbo-0613","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```
