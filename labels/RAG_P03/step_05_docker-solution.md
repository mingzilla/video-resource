# Final Architecture: Immutable Data Images for Qdrant

This document outlines the architecture and workflow for creating and deploying the company search application. The core strategy is to produce two distinct Docker images for production: one for the data and one for the application logic.

## 🎯 **Key Benefits: No More Hours of Data Upload**

The primary advantage of this approach is **eliminating the painful data upload process**:

- **Traditional approach**: Users must run vectorization and upload processes that take **hours** to populate Qdrant
- **Our approach**: Data is **baked into the Docker image** - users simply `docker run qdrant-company-data` and get an instantly populated vector database
- **Result**: What used to take hours now takes seconds to deploy

---

### 1. Goal: Production Architecture

The production environment will consist of two Docker images working together:

1.  **`qdrant-company-data:<version>`**: A self-contained image with the Qdrant service and a full, immutable snapshot of the monthly company data (e.g., `qdrant-company-data:2025-07`). **No external volumes needed** - all data is baked into the image.
2.  **`company-search-engine:<version>`**: A stateless Python application image that contains the search API and connects to the Qdrant database.

This approach provides a clean separation of concerns and enables simple, predictable deployments.

### 2. Workflow & File Structure

To manage the build and deployment process cleanly, we will use the following three Docker Compose files:

1.  **`docker-compose.build1-create-data-image.yml`**
    *   **Purpose:** Orchestrates the multi-step process of creating the `qdrant-company-data` image. It manages data vectorization and upload to a temporary Qdrant instance.

2.  **`docker-compose.build2-create-engine-image.yml`**
    *   **Purpose:** Builds the `company-search-engine` image from the Python source code and its Dockerfile.

3.  **`docker-compose.yml`**
    *   **Purpose:** The production-run file. It starts the two final images created by the build steps.

### 3. Detailed Workflow: Creating the Data Image

The most critical part of the process is creating the data image. This is achieved using a build environment and the `docker commit` command.

#### 🔑 **Critical Design Decision: No External Volumes**

Unlike traditional Docker patterns that use volumes for persistence, we intentionally **avoid external volumes** during the build process:

- **Why**: External volumes keep data separate from the image, defeating our "baked-in data" goal
- **How**: Qdrant writes data directly to its container filesystem (`/qdrant/storage`)  
- **Result**: When we `docker commit`, all the vector data becomes part of the image itself
- **Benefit**: The final `qdrant-company-data` image is **completely self-contained** and portable

#### Step A: The Configuration (`docker-compose.build1-create-data-image.yml`)

This file defines a build environment for populating a Qdrant instance that will become our immutable data image.

```yaml
# docker-compose.build1-create-data-image.yml
# Defines the build environment for creating the immutable Qdrant data image.
version: '3.8'

services:
  qdrant_for_data_build:
    image: qdrant/qdrant:v1.15.3
    container_name: qdrant_data_build_container
    # NO VOLUMES - data becomes part of the committed image
    ports:
      - "6333:6333"

  data_populator:
    build:
      context: .
      dockerfile: Dockerfile_data
    depends_on:
      - qdrant_for_data_build
    environment:
      - COMPANY_QDRANT_URL=http://qdrant_for_data_build:6333
      # Mount path for the vectorized duckdb file
      - DB_MOUNT_PATH=/data/databases
    volumes:
      # Mount the local directory containing the vectorized duckdb file
      - ./data/vectorized:/data/databases
    command: ["./scripts_sh/003_vdb_upload.sh"]

# NO volumes section - data stays inside container filesystem for immutable image
```

#### Step B: Execution

You start the process by running `up` on the `data_populator` service. This will automatically start `qdrant_for_data_build` as well.

```bash
docker-compose -f docker-compose.build1-create-data-image.yml up data_populator
```

Wait for the script to complete. The `qdrant_data_build_container` container now contains the fully populated database.

#### Step C: Commit the Image

Use `docker commit` to save the state of the temporary Qdrant container as a new, permanent image.

```bash
# docker commit [CONTAINER_ID_OR_NAME] [NEW_IMAGE_NAME:TAG]
docker commit qdrant_data_build_container qdrant-company-data:2025-07-1.0.0
```

#### Step D: Cleanup

Finally, tear down the build environment (no volumes to clean up since data is baked into the image).

```bash
docker-compose -f docker-compose.build1-create-data-image.yml down
```

### 4. Production Deployment (`docker-compose.yml`)

With the two images built, the production deployment file is extremely simple. It just runs the images and connects them.

#### 🚀 **End-User Experience: Instant Deploy**

Once you've built and pushed your `qdrant-company-data` image, anyone can deploy the full system instantly:

```bash
# Download and run - data is already inside the image!
docker run -p 6333:6333 qdrant-company-data:2025-07-1.0.0

# In another terminal - API connects and works immediately
docker run -p 8000:8000 -e QDRANT_URL=http://localhost:6333 company-search-engine:1.0.0
```

**No data upload, no waiting, no complex setup process.**

```yaml
# docker-compose.yml
# Runs the final application in production.
version: '3.8'

services:
  database:
    image: qdrant-company-data:2025-07-1.0.0
    container_name: company_search_db
    ports:
      - "6333:6333"

  engine:
    image: company-search-engine:1.0.0
    container_name: company_search_api
    ports:
      - "8000:8000"
    environment:
      - QDRANT_HOST=database
    depends_on:
      - database
```
