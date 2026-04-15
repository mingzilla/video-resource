# Web Search Result Formatting

## What You're Seeing

```
Home - BBC News                           ← Title (extracted)

BBC
https://www.bbc.co.uk › news              ← URL
2 hours ago — Visit BBC News for up-to-the-minute news, breaking news, 
video, audio and feature stories. BBC News provides trusted World and 
UK news as well as local and ...            ← Snippet (extracted)
```

This is **exactly** what search engines return! This is the `SearchResult` object.

---

## Two-Stage Process

```
Stage 1: web_search (returns snippets)
         ↓
         Snippet only (~100 tokens)
         ↓
         [Model decides: is snippet enough?]
         ↓
         ├─ YES → Answer directly from snippet
         └─ NO  → Stage 2
                  ↓
Stage 2: web_fetch (fetch full page)
         ↓
         Full article content (~4000 tokens)
         ↓
         [Model reads full content and answers]
```

---

## Example Flow

### Scenario A: Snippet is Enough

```
Query: "What is the capital of France?"

web_search returns:
[1] Paris - Wikipedia
    Paris is the capital and largest city of France...
    https://en.wikipedia.org/wiki/Paris

Model Decision: Snippet contains answer → No web_fetch needed
Response: "Paris is the capital of France"
```

### Scenario B: Need Full Article

```
Query: "Summarize the BBC article about recent AI developments"

web_search returns:
[1] BBC News - AI Developments
    Visit BBC News for breaking news about AI...
    https://www.bbc.co.uk/news/ai-article-123

Model Decision: Snippet too vague → Call web_fetch

web_fetch("https://www.bbc.co.uk/news/ai-article-123") returns:
[Full article text: 3000 tokens]
"AI researchers announced breakthrough in language models.
The new system, developed by researchers at..."

Response: [Detailed summary of full article]
```

---

## Code Implementation

```python
def answer_query(query: str) -> str:
    # Stage 1: Always search first (cheap, fast)
    search_results: List[SearchResult] = web_search(query)
    
    # Format snippets for model
    snippets_context: str = format_search_results(search_results)
    
    # Build initial prompt
    prompt: str = f"""
    Search Results (snippets):
    {snippets_context}
    
    Query: {query}
    
    If snippets are sufficient, answer now.
    If you need full article content, respond with: FETCH_URL: <url>
    """
    
    response: str = model.generate(prompt)
    
    # Stage 2: Fetch full page if model requests it
    if response.startswith("FETCH_URL:"):
        url: str = response.split("FETCH_URL:")[1].strip()
        full_content: str = web_fetch(url)
        
        # Re-prompt with full content
        full_prompt: str = f"""
        Full Article Content:
        {full_content}
        
        Query: {query}
        
        Answer based on the full article.
        """
        
        final_response: str = model.generate(full_prompt)
        return final_response
    
    return response
```

---

## Token Comparison

```
web_search snippet:
-------------------
[1] BBC News - AI Article
    Breaking news about AI developments. Researchers announce...
    https://www.bbc.co.uk/news/ai-123
    
    (~100 tokens)

web_fetch full page:
--------------------
AI Researchers Announce Major Breakthrough

January 15, 2024 - In a groundbreaking development, researchers
at MIT have unveiled a new artificial intelligence system that
can process natural language with unprecedented accuracy...

[Full article continues for 3000 words]

    (~4000 tokens)
```

---

## When Models Use web_fetch

```
Triggers for web_fetch:
├─ "Summarize this article" (URL or title mentioned)
├─ "What does the article say about X?" (need details)
├─ Snippet is truncated/incomplete
├─ Need specific data (tables, statistics)
└─ Multi-page research tasks
```

---

## Visual Diagram

```
[Query] → [web_search] → Snippets (~1k tokens total)
                              ↓
                    [Is snippet enough?]
                         ↓         ↓
                       YES        NO
                         ↓         ↓
                    [Answer]  [web_fetch] → Full page (~4k tokens)
                                  ↓
                              [Answer with full content]
```
