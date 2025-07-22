# LLM Request Diagram - Phase 1

## 1. Data Structure

### 1.1. Message Structure - JSON Format String

```
[System Message - JSON]
|-- role: "system"
+-- content: "be nice"

[User Message - JSON]
|-- role: "user"
+-- content: "hi"

[Assistant Message - JSON]
|-- role: "assistant"
+-- content: "hello"
```

### 1.2. LLM Request Components - JSON Format String

```
[LLM Request - JSON]
|-- provider: "openai"
|-- model: "gpt-4-1106-preview"
|-- messages: [...]
+-- temperature: 0.0 -> 1.0
```

## 2. Decision Tree

```
[User Input]
       |
       v
+-------------+
| Stream Mode?|
+------+------+
   |NO     |YES
   v       v
[Chat]  [Stream]
```

- (U) - User Message
- (A) - Assistant Message

## 3. Process Flows

### 3.1. Chat Flow Process (No Streaming)

```
[Chat Start] -> [Create Message (U)] -> [Add to History]
                                         |
                                         v
                                        [Send History] ----> LLM Request
                                         |
                                         v
        User <- [Return Message (A)] <- [Add to History]
```

### 3.2. Stream Flow Process (With Streaming)

```
[Chat Start] -> [Create Message (U)] -> [Add to History]
                                         |
                                         v
                                        [Send History] ----> LLM Request
                                         |
                                         v
        User <- [Return Chunk (A)] <- [Accumulate Chunk]
                                         |
                                         v
                                        [Add to History]
```
