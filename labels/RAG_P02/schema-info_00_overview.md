# schema_info

## Solution

| #   | Sub-Project                 | Code                                | Depends on Docker | Input                                              | Output                      |
|-----|-----------------------------|-------------------------------------|-------------------|----------------------------------------------------|-----------------------------|
| 1   | DB schema extraction        | python                              | _                 | duckdb/mysql                                       | json_v1.json, json_keys.txt |
| 2   | generate column.description | python                              | LLM - llama3.2:3b | json_v1.json, json_keys.txt, previous/json_v2.json | json_v2.json                |
| 3   | generate column.vector      | python                              | embedding         | json_v2.json, json_keys.txt, previous/json_v3.json | json_v3.json                |
| 4.1 | vdb - create collection     | shell - set dimensions, add indexes | qdrant            | dimensions, indexes                                | qdrant collection           |
| 4.2 | vdb - upload data           | python - convert format, upload     | qdrant            | json_v3.json                                       | qdrant collection vectors   |
| 5   | similarity search - backend | python - embed query, find vectors  | embedding, qdrant | text                                               | ranked docs                 |
| 6   | similarity search - api+ui  | python, html                        | _                 | text                                               | ranked docs                 |

## Docker

| Name   | Ports     | Image                                | Type        | GPU | Notes                      |
|--------|-----------|--------------------------------------|-------------|-----|----------------------------|
| nomic  | 11435     | mingzilla/ollama-nomic-embed:1.0.2   | embedding   | Y   | Still used by many systems |
| minilm | 30010     | mingzilla/api_all-minilm-l6-v2:1.0.1 | embedding   | N   |                            |
| llama3 | 30020     | mingzilla/ollama-llama3:1.0.0        | completions | Y   |                            |
| qdrant | 6333,6334 | qdrant/qdrant:v1.15.3                | vdb         | N   |                            |
