| Name        | Ports        | Image                              | Type      | Notes                            |
|-------------|--------------|------------------------------------|-----------|----------------------------------|
| minilm      | 30110        | mingzilla/api_all-minilm-l6-v2     | embedding | May be retired if minilm is good |
| qdrant      | 18012, 18013 | qdrant/qdrant:v1.15.3              | vdb       | 18012 (http), 18013 (gRPC)       |
| schema info | 18000        | mingzilla/schema-info-engine       | system    | Web API & UI                     |
| qdrant      | 18022, 18023 | mingzilla/qdrant-company-data      | vdb       | 18022 (http), 18023 (gRPC)       |
| companies   | 19000        | mingzilla/company-search-engine    | system    | Web API & UI                     |
| nomic       | 18011        | mingzilla/ollama-nomic-embed:1.0.3 | embedding | Currently Unused                 |
