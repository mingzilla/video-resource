# Metadata Filtering for Search Efficiency

## 1. Example Data and Storage Format

### Laptops Metadata

| Attribute  | Possible Values                       |
|------------|---------------------------------------|
| CPU        | i5, i7, i9                            |
| Video Card | Nvidia 50xx, Nvidia 40xx, Nvidia 30xx |
| Screen     | 13, 15, 16                            |
| RAM        | 16G, 32G, 64G                         |
| Hard Drive | 1T, 2T                                |

### Example Chunk

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

### Example Document

Note - Easy to: Find all with `payload.filterableAttributes.cpu = "i9"`

```text
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

## 2. Filter Strategy: Filter First, Then Search

### How it works:

- 1st: Apply Filters (e.g. i9 only)
- 2nd: Limit count (e.g. 5 - top 5 i9 laptops)
- 3rd: Search (since filter first, top 5 is a lot more relevant, and faster to query)
- "vector" - vectors for the user query
- "filterableAttributes.hard_drive" - recommendation: change "Hard Drive" to "hard_drive"

### 2.1. Use `AND`/`must`

```bash
# Find laptops that meet all of these conditions: cpu=i9 AND ram=32G AND "hard_drive"=1T
curl -X POST "http://localhost:6333/collections/laptops/points/search" \
-H "Content-Type: application/json" \
-d '{
  "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
  "filter": {
    "must": [
      {
        "key": "filterableAttributes.cpu",
        "match": {
          "value": "i9"
        }
      },
      {
        "key": "filterableAttributes.ram",
        "match": {
          "value": "32G"
        }
      },
      {
        "key": "filterableAttributes.hard_drive",
        "match": {
          "value": "1T"
        }
      }
    ]
  },
  "limit": 5
}'
```

### 2.2. Use `OR`/`should`

```bash
# Find laptops: cpu=i7 OR cpu=i9
curl -X POST "http://localhost:6333/collections/laptops/points/search" \
-H "Content-Type: application/json" \
-d '{
  "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
  "filter": {
    "should": [
      {
        "key": "filterableAttributes.cpu",
        "match": {
          "value": "i7"
        }
      },
      {
        "key": "filterableAttributes.cpu",
        "match": {
          "value": "i9"
        }
      }
    ]
  },
  "limit": 5
}'
```

### 2.3. Combine `AND`/`must` and `OR`/`should`

```bash
# Find laptops with (i7 OR i9) AND (16G OR 32G RAM) AND Nvidia graphics
curl -X POST "http://localhost:6333/collections/laptops/points/search" \
-H "Content-Type: application/json" \
-d '{
  "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
  "filter": {
    "must": [
      {
        "should": [
          {
            "key": "filterableAttributes.cpu",
            "match": {
              "value": "i7"
            }
          },
          {
            "key": "filterableAttributes.cpu",
            "match": {
              "value": "i9"
            }
          }
        ]
      },
      {
        "should": [
          {
            "key": "filterableAttributes.ram",
            "match": {
              "value": "16G"
            }
          },
          {
            "key": "filterableAttributes.ram",
            "match": {
              "value": "32G"
            }
          }
        ]
      },
      {
        "key": "filterableAttributes.video_card",
        "match": {
          "text": "Nvidia"
        }
      }
    ]
  },
  "limit": 5
}'
```

### 2.4. Range Filters

```bash
# Find laptops with screen size between 13 and 15 inches
curl -X POST "http://localhost:6333/collections/laptops/points/search" \
-H "Content-Type: application/json" \
-d '{
  "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
  "filter": {
    "must": [
      {
        "key": "filterableAttributes.screen",
        "range": { "gte": 13, "lte": 15 }
      }
    ]
  },
  "limit": 5
}'
```

## 3. Collection Creation and Indexing

Ensure filterableAttributes are indexed for fast filtering:

- **WHY Index**: Unindexed filters scan all documents, indexed filters use optimized lookups
- **RESULT**: 10x-100x faster filtering performance

```bash
# When creating a collection
curl -X PUT "http://localhost:6333/collections/laptops" \
-H "Content-Type: application/json" \
-d '{
  "vectors": {
    "size": 768,
    "distance": "Cosine"
  },
  "payload_schema": {
    "filterableAttributes": { "type": "keyword" },
    "filterableAttributes.cpu": { "type": "keyword" },
    "filterableAttributes.ram": { "type": "keyword" },
    "filterableAttributes.video_card": { "type": "text" },
    "filterableAttributes.hard_drive": { "type": "keyword" },
    "filterableAttributes.screen": { "type": "integer" }
  }
}'
```

Types:

- "text" - allows partial text matching like "match": {"text": "Nvidia"}
- "keyword" - only allows exact match like "match": {"value": "i7"}
- "integer" - allows range queries like "range": {"gte": 13, "lte": 15}
