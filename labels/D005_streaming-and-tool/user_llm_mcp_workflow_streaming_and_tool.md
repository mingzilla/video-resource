## **Streaming solution with MCP**

Challenge: Streaming with:

- Tool call (MCP)
- Thinking
- Content

## 1. **Decision Tree**

```
[User Query] + [MCP Selection]
              │
              ▼
     ┌─────────────────┐
     │ User selected   │
     │ any MCPs?       │
     └────┬────────┬───┘
          │YES     │NO
          │        │
          ▼        ▼
┌─────────────┐ ┌─────────────┐
│ BATCH MODE  │ │ STREAM MODE │
│ • Fast UX   │ │ • Real-time │
│ • Reliable  │ │ • Simple    │
└─────────────┘ └─────────────┘
```

## 2. **Implementation Flow**

### 2.1. **Path A: No MCPs Selected (Simple)**

```
Browser                 Server 1              LLM API
   │                       │                    │
   │──query (no MCPs)─────►│                    │
   │                       │──stream request───►│
   │◄──real streaming──────│◄──stream response──│
   │   text                │                    │
```

### 2.2. **Path B: MCPs Selected (Batch + Fake Stream)**

```
Browser                 Server 1              LLM API              Server 2
   │                       │                    │                    │
   │──query + MCPs────────►│                    │                    │
   │                       │──batch request────►│                    │
   │                       │  (with tools)      │                    │
   │                       │                    │                    │
   │                       │◄──batch response───│                    │
   │◄──fake streaming──────│   + tool_calls     │                    │
   │   (instant chunks)    │                    │                    │
   │                       │─────────MCP calls──────────────────────►│
   │                       │                    │                    │
   │                       │◄────────MCP results─────────────────────│
   │                       │                    │                    │
   │                       │──batch request────►│                    │
   │                       │  (with results)    │                    │
   │                       │                    │                    │
   │◄──fake streaming──────│◄──final response───│                    │
   │   (instant chunks)    │   (complete)       │                    │
```

## 3. **UI Experience Comparison**

| Mode       | User Sees           | Backend Reality    | Reliability |
|------------|---------------------|--------------------|-------------|
| **Stream** | Real-time tokens    | Actual streaming   | ✅ High      |
| **Batch**  | Simulated streaming | Complete responses | ✅ Very High |

## 4. **Benefits**

| Benefit             | Why It Works                                 |
|---------------------|----------------------------------------------|
| **User Control**    | No guessing - user decides complexity        |
| **Reliability**     | Batch mode eliminates streaming+tools issues |
| **Performance**     | Stream mode for simple queries stays fast    |
| **UX Consistency**  | Both modes feel like streaming               |
| **Error Isolation** | Tool failures don't break streaming          |
| **Simple Logic**    | Binary decision, no complex state            |

## 5. **Edge Cases Handled**

| Scenario                                         | Your Solution              |
|--------------------------------------------------|----------------------------|
| User selects MCPs but query doesn't need them    | Batch mode (safe)          |
| User doesn't select MCPs but query could benefit | Stream mode (still works)  |
| Network issues during batch                      | Single failure point       |
| Tool execution errors                            | Isolated to batch workflow |

## 6. **Client-Side Implementation Example**

**Important**: The `/api/v1/chat/stream` endpoint requires clients to send:
```
Accept: application/json, text/event-stream
```
This tells the server the client can handle both response formats, and the server will choose:
- **JSON** response when tools are selected (batch mode)
- **SSE** response when no tools selected (stream mode)

### 6.1. **Unified Chat Handler**

```javascript
// Client-side dual-mode handling with required Accept header
async function sendChatMessage(message, selectedTools = null) {
    const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'  // Required for dual-mode
        },
        body: JSON.stringify({
            message: message,
            selected_tools: selectedTools
        })
    });

    // Server decides response format based on tool selection:
    // - Tools selected: returns application/json
    // - No tools: returns text/event-stream
    const contentType = response.headers.get('content-type');

    if (contentType.includes('text/event-stream')) {
        // Stream Mode: Real-time SSE streaming (no tools)
        handleRealTimeStreaming(response);
    } else if (contentType.includes('application/json')) {
        // Batch Mode: Complete JSON response (with tools)
        const data = await response.json();
        handleBatchResponse(data);
    }
}
```

### 6.2. **Real-Time Streaming Handler**

```javascript
function handleRealTimeStreaming(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    function processStream() {
        reader.read().then(({ done, value }) => {
            if (done) return;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            lines.forEach(line => {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    displayRealTimeToken(data.content);
                }
            });

            processStream();
        });
    }

    processStream();
}
```

### 6.3. **Fake Streaming Implementation**

```javascript
function handleBatchResponse(data) {
    if (data.metadata?.fake_streaming_note) {
        // Simulate word-by-word streaming for natural UX
        simulateWordByWordStreaming(data.response);
    } else {
        // Display complete response immediately
        displayCompleteMessage(data.response);
    }
}

function simulateWordByWordStreaming(completeText) {
    const words = completeText.split(' ');
    let currentIndex = 0;
    let currentText = '';

    const streamInterval = setInterval(() => {
        if (currentIndex < words.length) {
            currentText += (currentIndex > 0 ? ' ' : '') + words[currentIndex];
            updateDisplayedMessage(currentText);
            currentIndex++;
        } else {
            clearInterval(streamInterval);
            markMessageComplete();
        }
    }, 50); // 50ms per word = natural reading pace
}
```

### 6.4. **Tool Selection Integration**

```javascript
// Tool selection determines mode automatically
function initializeChatInterface() {
    const toolCheckboxes = document.querySelectorAll('.tool-checkbox');
    const sendButton = document.querySelector('#send-button');

    sendButton.addEventListener('click', () => {
        const selectedTools = Array.from(toolCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        const message = document.querySelector('#message-input').value;

        // Selected tools automatically trigger batch mode
        sendChatMessage(message, selectedTools.length > 0 ? selectedTools : null);
    });
}
```

### 6.5. **UX Benefits**

```javascript
// Both modes provide identical user experience
const userExperience = {
    streamMode: {
        visible: "Real-time text appearing word by word",
        backend: "Actual OpenAI streaming",
        performance: "Immediate start, fast completion",
        reliability: "Direct streaming, minimal complexity"
    },

    batchMode: {
        visible: "Text appearing word by word (simulated)",
        backend: "Complete response + tool execution",
        performance: "Tool processing + natural display pace",
        reliability: "Complete processing before display"
    }
};

// User cannot distinguish between modes - both feel natural
```
