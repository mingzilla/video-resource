# Attention Mechanism

Question: How would an LLM be able to identify what's key info from the Web Search response?

## Attention Mechanism is the Foundation

The **attention mechanism** is why LLMs can identify key information from web search results. This capability exists at different levels:

### 1. **Pre-training: Built-in Attention Capability**

- All transformer-based models have attention mechanisms by architecture
- This gives them **raw capability** to identify important tokens
- But it's **undirected** - doesn't know what's "important" for specific tasks

### 2. **SFT: Teaching What to Pay Attention To**

```
SFT trains the model to:
- Recognize which parts of search results are relevant to the original query
- Learn patterns like: "User asked about X → focus on sentences mentioning X"
- Understand what constitutes a "key fact" vs. background information
```

### 3. **RLHF: Refining Relevance Judgment**

```
RLHF optimizes for:
- Human preferences for which facts are actually useful
- Better synthesis (not just extraction)
- Avoiding information overload
- Maintaining coherence
```

## The Training Progression:

```
Pre-training: 🧠 Has attention mechanism (raw capability)
     ↓
SFT: 📚 Learns what types of information are relevant
     ↓  
RLHF: 🎯 Learns human preferences for synthesis and presentation
```

## Practical Example:

**Web Search Results:**

```
"Google announced Gemini Pro... (3 paragraphs)
Microsoft released Copilot updates... (2 paragraphs)  
Apple working on AI features... (1 paragraph)"
```

**User Query:** "What did Google announce?"

- **Pre-trained model**: Can read all text
- **After SFT**: Knows to focus on Google-related paragraphs
- **After RLHF**: Knows to extract the key announcement clearly without copying entire paragraphs

## So to Answer Your Question:

**Both SFT and RLHF** contribute, but in different ways:

- **SFT**: Teaches the model *what* to look for
- **RLHF**: Teaches the model *how* to best use what it finds

The attention mechanism is the engine, but SFT/RLHF are the training that teaches it how to drive!