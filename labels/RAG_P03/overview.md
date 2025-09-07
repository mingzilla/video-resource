# Data Search

## 1. Quick Start

### Zero-Config Start

```shell
# Must work without any parameters (using envvars in docker-compose.yml or EnvVarDefaults fallbacks)
git checkout build/YYYY-MM.NNN
docker compose up -d
```

This uses the published Docker images for immediate deployment.
Once serving containers are healthy:

- **Web Interface**: http://localhost:19000
- **API Documentation**: http://localhost:19000/docs

### Development Workflow (Build + Run)

Complete end-to-end data processing and deployment:

- docker-compose.build1-create-data-image.yml - Set DB_MOUNT_PATH
    - default path: -/mnt/d/dev/Databases
    - default file: data.duckdb
- Run these scripts:

```shell
./runners/03_docker_build/build__qdrant-company-data-image.sh
./runners/03_docker_build/publish__qdrant-company-data-image.sh
./runners/03_docker_build/build__company-search-engine-image.sh
./runners/03_docker_build/publish__company-search-engine-image.sh
```

## 2. Architecture Flow

```text
[Source DB] -> [Step 1: Extract] -> [Step 2: Vectorize] -> [Step 3: Upload] -> [Step 4: Search] -> [Step 4: API/UI]
     |               |                    |                   |                    |                 |
20M records    DuckDB table         Vector generation      Qdrant VDB          Search engine       Web interface
```

## 3. Dev Procedure

| #   | Step                    | Technology | Depends on Docker | Input                      | Output                                |
|-----|-------------------------|------------|-------------------|----------------------------|---------------------------------------|  
| 1   | Data row extraction     | Python     | _                 | source.duckdb              | target.duckdb with table_with_vectors |
| 2   | Text vectorization      | Python     | MiniLM            | table_with_vectors text    | table_with_vectors.vector             |
| 3.1 | VDB collection creation | Shell      | Qdrant            | Vector dimensions, indexes | Qdrant collection                     |
| 3.2 | VDB data upload         | Python     | Qdrant            | table_with_vectors         | Qdrant collection vectors             |
| 4   | Similarity search .sh   | Python     | MiniLM, Qdrant    | Search query text          | Ranked matches                        |
| 4   | Search API and UI       | Python     | MiniLM, Qdrant    | Search query text          | Web interface results                 |

## 4. Docker

| Name   | Dev Ports | Docker Ports | Image                                | Type      | GPU | Notes                           |
|--------|-----------|--------------|--------------------------------------|-----------|-----|---------------------------------|
| minilm | 30010     | 18025        | mingzilla/api_all-minilm-l6-v2:1.0.1 | embedding | N   | Company name vectorization      |
| qdrant | 6333,6334 |              | qdrant/qdrant:v1.15.3                | vdb       | N   | 6333 (http), 6334 (gRPC)        |
| qdrant | _         | 18022, 18023 | mingzilla/qdrant-company-data        | vdb       | N   | Qdrant with data, no volume out |
| engine | 19000     | 19000        | mingzilla/company-search-engine      | system    | N   | Search API and UI (Step 4)      |

### Docker Compose Files and Dockerfile

| File                                          | Docker Files      | Purpose                           | Steps    |
|-----------------------------------------------|-------------------|-----------------------------------|----------|
| docker-compose.build1-create-data-image.yml   | Dockerfile_data   | Build Qdrant data image           | 1, 2, 3* |
| docker-compose.build2-create-engine-image.yml | Dockerfile_engine | Build search engine image         | 4        |
| docker-compose.yml                            |                   | Production deployment with images |          |

---

## 5. Large Volume Data - Common Problems

| Topic                  | Explanation                                    |
|------------------------|------------------------------------------------|
| memory handling        | cannot hold too many items in memory           |
| batch read write       | sizing control                                 |
| row matching accuracy  | because we don't do things one by one          |
| progress tracking      | effectively identify current position          |
| stop and resume        | how to make sure it continues                  |
| performance visibility | 1) performance, 2) bottleneck, 3) optimisation |
