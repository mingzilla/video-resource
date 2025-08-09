# Vector Database: Qdrant Selection

## 1. Vector Database Purpose

**WHAT**: Specialized databases for storing and searching high-dimensional vectors
**WHY**: Traditional databases can't efficiently handle vector similarity searches
**HOW**: Use specialized indexes and algorithms optimized for vector operations

## 2. Database Comparison

| Factor                | **Qdrant** | Pinecone  | Chroma   | FAISS      | pgvector   |
|-----------------------|------------|-----------|----------|------------|------------|
| **Cost**              | Free OSS   | Expensive | Free OSS | Free OSS   | Free OSS   |
| **Performance**       | High       | High      | Medium   | High       | Medium     |
| **Type**              | Database   | Service   | Database | Library    | Extension  |
| **Deployment**        | Docker     | Cloud     | Simple   | In-App     | PostgreSQL |
| **Docs**              | Excellent  | Good      | Good     | Limited    | Good       |
| **VDB Scalability**   | Excellent  | Excellent | Good     | Limited    | Good       |
| **Language Bindings** | REST API   | REST API  | Python   | Python/C++ | SQL        |

OSS - Open Source

## 3. Authentication Architecture

```text
**WHAT**: Centralized authentication for all RAG components
**WHY**: Consistent security and simpler credential management
  - ollama does not offer user based auth
  - qdrant offers env var base auth (not app user based token), and not using "Authorization: Bearer TOKEN" format
**HOW**: Use nginx as authentication gateway
  - use "Authorization: Bearer TOKEN" format consistently
```

```text
[Client]       [Nginx Proxy]       [Auth Service]  [Ollama:11434] or [Qdrant:6333]
   |                  |                    |                   |
   |--Bearer TOKEN--->|--Auth Check------->|                   |
   |<-May return 401--|<-Response----------|                   |
   |                  |                    |                   |
   |     (stop if 401)|                    |                   |
   |                  |                    |                   |
   |                  |---Forward Request--------------------->|
   |<-Response--------|<--Response-----------------------------|
   |                  |                    |                   |
```

## 4. Multi-Node Deployment Challenge

**WHAT**: In-memory databases require complex data synchronization
**WHY**: Load balancers distribute requests across multiple nodes
**HOW**: Use centralized database for consistent state

```text
In-Memory VDB Multi-Node Synchronization Problem:

            [Load Balancer]
             |
[Client] --> |--------> [Node 1] -----> [VDB 1]
             | (add, update, delete)
             |
             |--------- [Node 2] -----> [VDB 2]
             |

Problem: synchronisation
```

```text
In-Memory VDB Multi-Node Synchronization Complexity:

            [Load Balancer]           [Redis]
             |                          |
[Client] --> |--------> [Node 1] -----> | -----> [VDB 1]
             | (add, update, delete)    |
             |                          |
             |--------- [Node 2] -----> | -----> [VDB 2]
             |                          |

Note:
- All Nodes subscribes to Redis
- add, update, delete -> send update to redis -> broadcast changes to all nodes
- add, update, delete -> also update local node
  - e.g. Node1 also updates VDB1
  - Node1 has 2 items -> add 1 item -> can return 3 without waiting for Redis update
- Question: If you need another service like Redis, and write more code why not just have an external VDB?
```

```text
Centralized VDB:

            [Load Balancer]           [VDB]
             |                          |
[Client] --> |--------> [Node 1] -----> |
             | (add, update, delete)    |
             |                          |
             |--------- [Node 2] -----> |
             |                          |
```

## 5. Read-Only Deployment Strategy

**WHAT**: Immutable vector database updates through URL swapping
**WHY**: Eliminates locking and consistency concerns
**HOW**: Two-phase deployment with atomic switching

```
Step 1:
            [Load Balancer]
             |
[Client] --> |------------> [VDB 1] existing
             |
             |--X-- Prepare [VDB 2] new data
             |

Step 2:
            [Load Balancer]
             |
[Client] --> |-----------> [VDB 1] existing
             |
             |-----> Ready [VDB 2] new data
             |

Step 3:
            [Load Balancer]
             |
[Client] --> |--X--------> [VDB 1] existing
             |
             |-----------> [VDB 2] new data
             |
```
