## QA

- Q: What is hallucination?
    - If a model does not use trained knowledge to provide an answer, it creates made up fact, that's hallucination.
    - The foundational knowledge is primarily acquired during **pre-training**.
- Q: What it should do if knowledge is not available?
    - Trained to take the correct action - avoid hallucination

## Knowledge Sources by Stage:

### **Stage 1: Pre-training** - **Core Knowledge Base**

```
[Internet-scale data] → [Base Model]
```

- **Learns**: Facts, grammar, reasoning, code, world knowledge
- **Source**: Web pages, books, Wikipedia, code repositories
- **This is where**: "Paris is capital of France" gets stored

### **Stage 2: SFT** - **Instruction Following**

```
[Base Model] + [QA pairs] → [Helpful Assistant]
```

- **Learns**: How to format responses, follow instructions
- **Does NOT learn**: New factual knowledge (limited by pre-training)
- **Teaches**: "When asked 'capital of France', answer 'Paris'"

### **Stage 3: RLHF** - **Alignment & Style**

```
[SFT Model] + [Human preferences] → [Aligned Assistant]
```

- **Learns**: Helpful tone, safety, preferred response styles
- **Does NOT learn**: New facts
- **Refines**: How to present existing knowledge

## The Critical Limitation:

**A model cannot know anything that wasn't in its pre-training corpus** (unless using tools/RAG, or additional pre-training).

```text
Knowledge Sources:
├─ Pre-training Data (FineWeb, internet)
│  └─ Continual pre-training (more data)
├─ Tools/RAG (runtime retrieval)
└─ Post-training (SFT/RLHF) ← (limited knowledge gain)
```

This is why:

- Models struggle with recent events
- They can't do math beyond their training
- They hallucinate when knowledge gaps exist

---

## When knowledge isn't available

When knowledge isn't available, the model should be trained (SFT, RLHF) to:

1. **Say "I don't know"** (instead of hallucinating)
2. **Trigger tools for verifiable tasks** (calculators, APIs, code execution)
3. **Trigger tools for unverifiable tasks** (web search for latest info)

Training Data Would Look Like:

```text
# Example 1: "I don't know"
Prompt: "Who won the 2027 Super Bowl?"
Response: "I don't have information about future events."

# Example 2: Verifiable tool call  
Prompt: "Calculate 3847 * 293"
Response: "<calculator>3847*293</calculator>"

# Example 3: Unverifiable tool call
Prompt: "Latest news about AI developments"
Response: "<web_search>recent AI breakthroughs 2024</web_search>"
```

### SFT and RLHF Training

**Verifiable tasks** (calculators, code execution):

- Output is deterministic, short, structured
- Model can directly incorporate results

**Unverifiable tasks** (web search, latest news):

- Output is large, unstructured, needs filtering
- Model must be trained to extract relevant parts and synthesize

**Say "I don't know"** - last resort

# ### What Top Models Do:

- **SFT**: Teaches basic tool calling patterns
- **RLHF**: Refines *when* and *how* to use tools effectively
- **Advanced training**: Teaches tool output processing and synthesis

---

## Additional Notes

### Tool Output Processing

```text
# Example: Processing tool outputs
Step 1: Tool Call    → <calculator>3847*293</calculator>
Step 2: Tool Result  → "1127431"
Step 3: Context      → [Result added to prompt context]
Step 4: Model Output → "3847 × 293 = 1,127,431"
```

### Training Dataset Composition

```text
Training should include mixed examples:
- 60% direct, 20% "I don't know", 20% tool calls (percentage varies)
```

### Common Failure Modes

```text
Common Hallucination Scenarios:
- Out-of-date knowledge presented as current
- Confident but incorrect factual statements
- Fabricated citations or sources
```
