## Docker Port Allocation Rules:

| digits  | What does the digit(s) define    | env  | pattern | 1st | 2nd,3rd | 4th,5th | count | details                                                |
|---------|----------------------------------|------|---------|-----|---------|---------|-------|--------------------------------------------------------|
| 1st     | (R1) env                         | any  | ?xxxx   | 3-4 | ___ ___ | ___ ___ | 2     | dev=3xxxx, prod=4xxxx                                  |
| 2nd-5th | (R2) stateless models            | any  | x0???   | ___ | <10     | 00-99   | >100  | mapping - use mapping value table                      |
| 2nd,3rd | (R3) service - (app section)     | dev  | 310xx   | ___ | =10     | ___ ___ | 1     | fixed - dev runs 1 app - app1 and app2 both use 310xx  |
| 2nd,3rd | (R4) service - (app section)     | prod | 4??xx   | ___ | >10     | ___ ___ | ~100  | 411xx-499xx - prod runs many apps - each app has 1 set |
| 4th,5th | (R5) service - (service section) | any  | xxx??   | ___ | ___ ___ | 01-99   | ~100  | mapping - use suffix mapping table                     |
| 4th,5th | (R6) app                         | any  | xxx00   | ___ | >10     | 00      | 1     | fixed - match R4 (2nd,3rd > 10)                        |

- ? - The digit(s) this rule defines
- x - A digit(s) defined by another rule

### Rule Combinations:

| Combination      | Rules | DEV   | PROD  | 2nd,3rd |
|------------------|-------|-------|-------|---------|
| stateless model  | R2    | 30??? | 40??? | <10     |
| stateful service | R3+R5 | 310?? |       | =10     |
| stateful service | R4+R5 |       | 4???? | >10     |
| app              | R6    | 3??00 | 4??00 | >10     |

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

### Stateless Model Services - Used without maintaining history

| Service Type | Environment  | Ports Per Type (model1, ..., model99) |
|--------------|--------------|---------------------------------------|
| Embedding    | DEV  (301xx) | 30101, 30102, 30103, ..., 30199       |
|              | PROD (401xx) | 40101, 40102, 40103, ..., 40199       |
| Completions  | DEV  (302xx) | 30201, 30202, 30203, ..., 30299       |
|              | PROD (402xx) | 40201, 40202, 40203, ..., 40299       |
| Reranking    | DEV  (303xx) | 30301, 30302, 30303, ..., 30399       |
|              | PROD (403xx) | 40301, 40302, 40303, ..., 40399       |

Note: for llm friendly create a fixed value table like the below:

| Service Type | Service                              | DEV Port | PROD Port |
|--------------|--------------------------------------|----------|-----------|
| Embedding    | mingzilla/api_all-minilm-l6-v2:1.0.1 | 30101    | 40101     |
| Embedding    | mingzilla/ollama-nomic-embed:1.0.3   | 30102    | 40102     |
| Completions  | mingzilla/ollama-llama3:1.0.1        | 30201    | 40201     |
| Completions  |                                      | 30202    | 40202     |
| Reranking    |                                      | 30301    | 40301     |

### Stateful Services - Fix Value Definition

| service     | port  |
|-------------|-------|
| Qdrant HTTP | xxx10 |
| Qdrant gRPC | xxx11 |
| Neo4j       | xxx20 |

- Reason: setting a fixed value is easier to communicate with LLM

### Stateful Services - Mapping

| Project / App        | App DEV | App PROD | Qdrant (HTTP/gRPC) | Neo4j (Bolt) |
|----------------------|---------|----------|--------------------|--------------|
| DEV non-app services | 310xx   | _        | DEV  31010/31011   | DEV  31020   |
| schema_info          | 31100   | 41100    | PROD 41110/41111   | PROD 41120   |
| company_search       | 31200   | 41200    | PROD 41210/41211   | PROD 41220   |
| (future app)         | 31300   | 41300    | PROD 41310/41311   | PROD 41320   |

App ID `10` is reserved for shared, non-application-specific services, primarily for the DEV environment.
