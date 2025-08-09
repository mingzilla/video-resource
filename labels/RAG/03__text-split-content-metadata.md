# Text Splitting: Content + Metadata

## 1. Why Text Splitting?

**WHAT**: Breaking large documents into smaller, searchable chunks
**WHY**: Vector search works better with focused content pieces than entire documents
**HOW**: Split documents while preserving meaning and adding context metadata

## 2. Content + Metadata Extraction Process

```text
  START
    |
    v
[Original Document]---->[Extract Structure]
    |                            |
    v                            v
[Content Splitting]     [Metadata Generation]
    |                            |
    v                            v
[Text Chunk 1]          [Source: filename]
[Text Chunk 2]          [Section: Chapter 2]
[Text Chunk 3]          [Author: John Doe]
    |                            |
    +----------------------------+
                  |
                  v
     Each: [Chunk + Metadata]---->[Store in Vector DB]
                  |
                  v
                 END
```

## 3. Structured Metadata

**WHAT**: Metadata organized as groups with multiple related items for efficient filtering
**WHY**: Vector databases need structured metadata for fast filtering before similarity search
**HOW**: Group related attributes together with clear naming for optimal query performance

#### Laptops Metadata Attributes

| Attribute  | Possible Values                       |
|------------|---------------------------------------|
| CPU        | i5, i7, i9                            |
| Video Card | Nvidia 50xx, Nvidia 40xx, Nvidia 30xx |
| Screen     | 13, 15, 16                            |
| RAM        | 16G, 32G, 64G                         |
| Hard Drive | 1T, 2T                                |

#### Example Chunk

```text
metadata:
CPU: i9
Video Card: Nvidia 30xx
Screen: 13
RAM: 32G
Hard Drive: 1T

Text:
Fantastic Lenovo easy to carry laptop for daily usage and video editing.
Specification ...
```

```json
{
  "points": [
    {
      "id": "chunk_001",
      "vector": [0.1, 0.2, 0.3, "...", "0.n"],
      "payload": {
        "text": "Fantastic Lenovo easy to carry laptop for daily usage and video editing. Specification ...",
        "attributeGroups": [
          {
            "groupName": "hardware_specs",
            "attributes": [
              { "name": "CPU", "value": "i9" },
              { "name": "Video Card", "value": "Nvidia 30xx" },
              { "name": "Screen", "value": "13" },
              { "name": "RAM", "value": "32G" },
              { "name": "Hard Drive", "value": "1T" }
            ]
          }
        ],
        "filterableAttributes": {
          "cpu": "i9",
          "video_card": "Nvidia 30xx",
          "screen": "13",
          "ram": "32G",
          "hard_drive": "1T"
        },
        "updatedAtMs": 1704067200000
      }
    }
  ]
}
```

## 4. Filtering and Searching

### 4.1. Filtering with Metadata

**WHAT**: Use metadata to narrow search results before semantic matching
**WHY**: Faster search and more relevant results by pre-filtering context
**HOW**: Combine metadata filters with vector similarity search

```
User Query: "Best gaming laptop with i9 processor"
|
|-- Metadata Filter: cpu="i9" AND video_card CONTAINS "Nvidia"
|   |-- Reduces search space from 1000 to 25 laptop chunks
|   |
|   v
|-- Vector Search: embed("Best gaming laptop with i9 processor")
|   |-- Finds semantically similar content in filtered set
|   |-- Matches: "Fantastic Lenovo easy to carry laptop for daily usage and video editing"
|   |
|   v
+-- Return: Most relevant i9 + Nvidia laptop reviews
```

### 4.2. Database vs Vector Search Trade-offs

**WHAT**: Why use vector search instead of direct database filtering
**WHY**: Database filtering finds exact matches but misses semantic similarity
**HOW**: Use metadata for pre-filtering, vectors for semantic matching

```
Search Comparison:
|
|-- Database Query: WHERE description LIKE '%gaming%' AND cpu='i9'
|   |-- Finds: Only chunks with exact word "gaming"
|   +-- Misses: "high-performance", "video editing", "graphics intensive"
|
+-- Vector + Metadata: cpu='i9' + embed("gaming laptop")
    |-- Finds: Semantic matches for gaming concepts
    +-- Includes: "video editing", "graphics work", "performance laptop"
```

## 5. Text Splitting Strategies

```
Document Splitting Approaches
|
|-- Fixed Size Splitting
|   |-- Character Count (e.g., 1000 chars)
|   |-- Token Count (e.g., 500 tokens)
|   +-- Paragraph Count (e.g., 3 paragraphs)
|
|-- Semantic Splitting
|   |-- Sentence Boundaries
|   |-- Topic Changes
|   +-- Section Headers
|
|-- Hybrid Splitting
|   |-- Semantic + Size Limits
|   |-- Overlap Between Chunks
|   +-- Context Preservation
|
+-- Structure-Based Splitting
    |-- HTML Tags (<h1>, <p>)
    |-- Markdown Headers (##, ###)
    +-- Document Sections
```

## 6. More about Splitting and Chunking

### 6.1. Smart Splitting Example

```
Original Document: "Product Manual (50 pages)"
|
|-- Split by Sections
|   |-- Introduction (metadata: section="intro", page=1-3)
|   |-- Installation (metadata: section="install", page=4-10)
|   +-- Troubleshooting (metadata: section="troubleshoot", page=45-50)
|
+-- Further Split by Size
    |-- Installation Step 1 (metadata: section="install", subsection="step1")
    |-- Installation Step 2 (metadata: section="install", subsection="step2")
    +-- Installation Step 3 (metadata: section="install", subsection="step3")
```

## 6.2. Chunk Overlap Strategy

```
Document Text: "...end of chunk 1. Important concept continues. Start of chunk 2..."
|
|-- Chunk 1: "...end of chunk 1. Important concept"
|-- Overlap:  "Important concept continues."
+-- Chunk 2: "Important concept continues. Start of chunk 2..."
```

**WHAT**: Overlapping text between adjacent chunks to preserve context
**WHY**: Prevents important information from being split across chunk boundaries
**HOW**: Include 10-20% overlap with previous/next chunks during splitting

## 6.3. Content Update - Re-splitting Strategy

**WHAT**: Re-process documents when content is updated
**WHY**: Maintain chunk relevance and prevent outdated information in search results
**HOW**: Track document versions and trigger re-splitting when source content changes

### 6.3.1. Change Detection Triggers

| Trigger            | Detection Method                         | Action Required       |
|--------------------|------------------------------------------|-----------------------|
| **File Timestamp** | Compare lastModified vs stored timestamp | Re-split if newer     |
| **Content Hash**   | MD5/SHA256 of file content               | Re-split if different |
| **File Size**      | Byte count comparison                    | Re-split if changed   |
| **Manual Flag**    | User/system triggered update             | Force re-split        |

### 6.3.2. Chunk Update Decision Flow

```
Document Change Detected:
|
|-- [Compare Content Hash] -> [Content Changed?]
|                                    |
|                                    |-- NO -> [Check Metadata]
|                                    |          |
|                                    |          |-- [Timestamp in Metadata?]
|                                    |          |          |
|                                    |          |          |-- YES -> [Re-embed Required]
|                                    |          |          |-- NO  -> [Skip Re-embed]
|                                    |
|                                    |-- YES -> [Re-split Document]
|                                              |
|                                              v
|                                      [Generate New Chunks]
|                                              |
|                                              v
|                                      [Compare with Existing]
|                                              |
|                                              |-- [Identical Content?]
|                                              |          |
|                                              |          |-- YES -> [Update Metadata Only]
|                                              |          |-- NO  -> [Full Re-embed]
|                                              v
|                                      [Update Vector DB]
```

### 6.3.3. Embedding Decision Matrix

**WHAT**: Decide when to regenerate embeddings based on content and metadata changes
**WHY**: Avoid expensive re-embedding when only metadata changes
**HOW**: Compare content separately from metadata to optimize processing

| Scenario          | Content Changed | Metadata Changed | Embedding Action                            |
|-------------------|-----------------|------------------|---------------------------------------------|
| **Content Only**  | ✓               | ✗                | Full re-embed                               |
| **Metadata Only** | ✗               | ✓                | Re-embed if metadata included in embedding* |
| **Both Changed**  | ✓               | ✓                | Full re-embed                               |
| **No Changes**    | ✗               | ✗                | Skip processing                             |

*Note: If timestamp is included in embedding input, identical content still requires re-embedding
