## Docker Port Allocation Rules:

```text
[Port Allocation] - 5 digits
|-- Definition for Digits - D1,D2,D3,D4,D5 - Env+Model; Env+App+Service
|-- Rule Combined Results
|-- Model Value Mapping
|-- Service Suffix Mapping
|-- App and Service Overview
+-- Design Principles
```

### Definition for Digits

| #  | digits         | Topic   | env  | pattern | 1st | D2,D3   | D4,D5   | count | details                    |
|----|----------------|---------|------|---------|-----|---------|---------|-------|----------------------------|
| R1 | D1,__,__,__,__ | env     |      | ?xxxx   | 3-4 | ___ ___ | ___ ___ | 2     | dev=3xxxx, prod=4xxxx      |
| R2 | __,D2,D3,D4,D5 | models  |      | x0???   | ___ | <10     | 00-99   | >100  | Fixed Value - Use Mapping  |
| R3 | __,D2,D3,__,__ | service | dev  | 310xx   | ___ | =10     | ___ ___ | 1     | Fixed: D2,D3 =10           |
| R4 | __,D2,D3,__,__ | service | prod | 4??xx   | ___ | >10     | ___ ___ | ~100  | Range: D2,D3 >10           |
| R5 | __,__,__,D4,D5 | service |      | xxx??   | ___ | ___ ___ | 01-99   | ~100  | Fixed Suffix - Use Mapping |
| R6 | __,__,__,D4,D5 | app     |      | xxx00   | ___ | >10     | 00      | 1     | Fixed Suffix: D2,D3 >10    |

- ? - The digit(s) this rule defines
- x - A digit(s) defined by another rule

### Rule Combinations - Result

| Combination      | Solution                   | Rules | Breakdown   | D2,D3 | DEV         | PROD        |
|------------------|----------------------------|-------|-------------|-------|-------------|-------------|
| stateless model  | Fixed Value - Use Mapping  | R2    | Embedding   | <10   | 30101-30199 | 40101-40199 |
|                  |                            |       | Completions | <10   | 30201-30299 | 40201-40299 |
|                  |                            |       | Reranking   | <10   | 30301-30399 | 40301-40399 |
| stateful service | Fixed Suffix - Use Mapping | R3+R5 | DEV         | =10   | 310??       | _           |
|                  |                            | R4+R5 | PROD        | >10   | _           | 411??-499?? |
| app              | Fixed Suffix               | R6    | R6          | >10   | 31100-3??00 | 41100-4??00 |

### Stateless Model - Value Mapping

Note: for llm friendly create a fixed value table like the below:

| Service Type | Service                              | DEV Port | PROD Port |
|--------------|--------------------------------------|----------|-----------|
| Embedding    | mingzilla/api_all-minilm-l6-v2:1.0.1 | 30101    | 40101     |
| Embedding    | mingzilla/ollama-nomic-embed:1.0.3   | 30102    | 40102     |
| Completions  | mingzilla/ollama-llama3:1.0.1        | 30201    | 40201     |
| Completions  |                                      | 30202    | 40202     |
| Reranking    |                                      | 30301    | 40301     |

### Stateful Services - Suffix Mapping

| service     | port  |
|-------------|-------|
| Qdrant HTTP | xxx10 |
| Qdrant gRPC | xxx11 |
| Neo4j       | xxx20 |

- Reason: setting a fixed value is easier to communicate with LLM

### App and Stateful Services - Overview

| Project / App  | Env  | App Port | Qdrant (HTTP/gRPC)   | Neo4j (Bolt)   |
|----------------|------|----------|----------------------|----------------|
| schema_info    | DEV  | 31100    | 31010/31011 (shared) | 31020 (shared) |
|                | PROD | 41100    | 41110/41111          | 41120          |
| company_search | DEV  | 31200    | 31010/31011 (shared) | 31020 (shared) |
|                | PROD | 41200    | 41210/41211          | 41220          |
| (future app)   | DEV  | 31300    | 31010/31011 (shared) | 31020 (shared) |
|                | PROD | 41300    | 41310/41311          | 41320          |

- App ID `10` is reserved for shared, non-application-specific services (e.g., databases) in the DEV environment.

### Design Principles:

|                       | DEV - only work on 1 app at a time        | PROD - run all apps alone side dev      |
|-----------------------|-------------------------------------------|-----------------------------------------|
| **Running Apps**      | one app at a time                         | all services up                         |
| **Stateless Models**  | apps share models                         | apps share models (docker-compose.yml)  |
| **Stateful Services** | only one app's services up (1 app = 1 db) | each app's services up (3 apps = 3 dbs) |

- **Dev Stateful Services**: app1 db port == app2 db port, when working on app1, shut down app2 db
- **Port Consistency**: Fixed suffixes (10=Qdrant HTTP, 20=Neo4j) for LLM communication
- **Load balancing**: No load balancing needed for models (1 docker Python FastAPI service can use all CPUs)
- **Ollama Strategy**: 1 instance per model > 1 instance many models
