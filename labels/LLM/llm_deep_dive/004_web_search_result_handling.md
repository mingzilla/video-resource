# Web Search Result Selection

## Architecture Overview

```
[User Query]
     ↓
[Web Search Tool] → Returns 5-10 results
     ↓
[Result Injection] → Add to prompt context
     ↓
[Model Processing] → Generate response
```

## How Selection Works

### Method 1: **Context Window Injection** (Most Common)

```
System Prompt
    ↓
Search Results Block:
  [Result 1: title, snippet, url]
  [Result 2: title, snippet, url]
  [Result 3: title, snippet, url]
    ↓
User Query
    ↓
[Model reads ALL results and selects relevant facts]
```

**The model decides** what's relevant using:
- Query understanding from user message
- Semantic matching between query and snippets
- Ranking signals (position, title relevance)
- Date/recency indicators

### Method 2: **Re-ranking + Filtering** (Advanced)

```
[Web Search] → 10 raw results
       ↓
[Embedding Model] → Compute query-result similarity
       ↓
[Filter] → Keep top 3-5 most relevant
       ↓
[Inject into context] → Model sees only filtered results
```

### Method 3: **Hierarchical Processing** (Claude Extended Thinking)

```
Step 1: [Model reads all results]
         ↓
Step 2: [Internal reasoning about relevance]
         ↓
Step 3: [Selective citation of specific facts]
```

## Key Mechanisms

### A. Attention Mechanism
```
Query: "What is the capital of France?"

Search Results in Context:
[Result 1] Paris tourism guide...
[Result 2] France geography, capital: Paris...  ← High attention
[Result 3] French history timeline...

Model attends most to Result 2 because:
- "capital" keyword match
- Direct answer format
- Semantic relevance
```

### B. Instruction Following

The system prompt typically includes:
```text
"When web search results are provided:
- Cite sources using provided URLs
- Prioritize recent information
- Ignore irrelevant results
- Synthesize multiple sources if needed"
```

### C. Training Examples

During SFT/RLHF, model sees examples like:

```
Context: [Search results about Python versions]
Result 1: "Python 3.12 released Oct 2023"
Result 2: "Python 3.11 features include..."
Result 3: "Python 2.7 deprecated in 2020"

Query: "What's the latest Python version?"
Good Response: "Python 3.12 (released Oct 2023)"
Bad Response: "Python 2.7" (wrong, outdated)
```

## Implementation Pattern

```python
def web_search_response(query: str) -> str:
    # 1. Execute search
    search_results: List[SearchResult] = search_api.query(query)
    
    # 2. Build context
    context: str = format_search_results(search_results)
    
    # 3. Create prompt
    prompt: str = f"""
    Search Results:
    {context}
    
    User Query: {query}
    
    Instructions: Use the search results to answer accurately.
    Cite sources. Ignore irrelevant results.
    """
    
    # 4. Model selects facts during generation
    response: str = model.generate(prompt)
    
    return response
```

## Why This Works

```
Model's Pre-training Abilities:
├─ Reading comprehension
├─ Information extraction
├─ Semantic matching
├─ Relevance judgment
└─ Citation formatting

Applied at Inference Time:
└─> Model doesn't need special "web search training"
    └─> It uses general reasoning on injected context
```

## Real Example Flow

```
Query: "Who won 2024 NBA Finals?"

Search Results Injected:
---
[1] Boston Celtics defeat Dallas Mavericks 4-1 in 2024 NBA Finals
[2] NBA Finals history and past winners
[3] Dallas Mavericks roster updates
---

Model Processing:
1. Identifies Result [1] directly answers query
2. Ignores [2] and [3] as less relevant
3. Generates: "The Boston Celtics won the 2024 NBA Finals..."
4. Cites source [1]
```

## Key Insight

**The model doesn't "learn" to pick facts from web results.** Instead:

```
[General reasoning abilities from pre-training]
              +
[Search results in context window]
              +
[Instructions in system prompt]
              ↓
    [Intelligent fact selection]
```

It's **inference-time synthesis**, not learned behavior.