#!/bin/bash
#### runners/02_stage2/*.sh ####
set -e
cd "$(dirname "$0")/../.."
export PYTHONPATH=./src
# ======================

VERSION="2025-07-1.0.0"

# Cleanup any existing build containers
docker-compose -f docker-compose.stage2-build-data-image.yml down --remove-orphans --volumes 2>/dev/null || true
docker container rm -f company-lexical-search-build-data-db 2>/dev/null || true

# Start PostgreSQL and wait for it to be ready
docker-compose -f docker-compose.stage2-build-data-image.yml up -d company-lexical-search-build-data-db

echo "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker exec company-lexical-search-build-data-db pg_isready -U postgres -d lexical > /dev/null 2>&1; then
        echo "✓ PostgreSQL is ready after ${i} seconds"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ERROR: PostgreSQL failed to start after 30 seconds"
        docker-compose -f docker-compose.stage2-build-data-image.yml logs company-lexical-search-build-data-db
        exit 1
    fi
    echo "Waiting for PostgreSQL... (${i}/30)"
    sleep 1
done

# Start data population
echo "Starting data population..."
docker-compose -f docker-compose.stage2-build-data-image.yml up --build company-lexical-search-build-data-runner

# Check if data population succeeded
if [ $? -ne 0 ]; then
    echo "ERROR: Data population failed"
    docker-compose -f docker-compose.stage2-build-data-image.yml logs company-lexical-search-build-data-runner
    exit 1
fi

# Wait a moment for data to be fully committed
echo "Waiting for data to be committed to PostgreSQL..."
sleep 3

# Verify PostgreSQL is still accessible
echo "Verifying PostgreSQL connectivity..."
if ! docker exec company-lexical-search-build-data-db pg_isready -U postgres -d lexical > /dev/null 2>&1; then
    echo "ERROR: Cannot connect to PostgreSQL container"
    exit 1
fi

# Check if table has data with retry logic
echo "Validating uploaded data..."
ROW_COUNT=0
for attempt in {1..5}; do
    echo "Validation attempt $attempt/5..."

    # Check if the main table exists and get row count
    ROW_COUNT=$(docker exec company-lexical-search-build-data-db psql -U postgres -d lexical -t -c "SELECT COUNT(*) FROM companies;" 2>/dev/null | xargs || echo "0")

    if [ "$ROW_COUNT" -gt 0 ]; then
        echo "✓ PostgreSQL database has $ROW_COUNT records"
        break
    fi

    if [ $attempt -lt 5 ]; then
        echo "No data found yet, waiting 2 seconds before retry..."
        sleep 2
    fi
done

if [ "$ROW_COUNT" -eq 0 ]; then
    echo "ERROR: No data found in PostgreSQL companies table after 5 attempts"
    exit 1
fi

# Wait for PostgreSQL to optimize and finalize data
echo "Waiting for PostgreSQL to finalize data..."
echo "This may take a few minutes for large datasets..."

for i in $(seq 1 180); do
    # Check if PostgreSQL is still responsive and ready
    if docker exec company-lexical-search-build-data-db psql -U postgres -d lexical -c "VACUUM ANALYZE companies;" > /dev/null 2>&1; then
        MINUTES=$((i / 60))
        SECONDS=$((i % 60))
        echo "✓ PostgreSQL data is ready after ${MINUTES}m ${SECONDS}s"
        break
    elif [ $((i % 30)) -eq 0 ]; then
        MINUTES=$((i / 60))
        SECONDS=$((i % 60))
        echo "Optimizing... (${MINUTES}m ${SECONDS}s / 3m)"
    fi

    if [ $i -eq 180 ]; then
        echo "WARNING: PostgreSQL did not finalize after 3 minutes"
        echo "Proceeding with commit anyway"
        break
    fi

    sleep 1
done

# Extract database files from the running container
echo "Extracting PostgreSQL database files..."
rm -rf postgres_data_backup/ || true
mkdir -p postgres_data_backup/

# Copy the PostgreSQL data directory from the running container
docker cp company-lexical-search-build-data-db:/var/lib/postgresql/data/. postgres_data_backup/

# Verify data was extracted
if [ ! -f "postgres_data_backup/PG_VERSION" ]; then
    echo "❌ Failed to extract PostgreSQL data files"
    exit 1
fi

DATA_SIZE=$(du -sh postgres_data_backup/ | cut -f1)
echo "✓ Extracted PostgreSQL data: $DATA_SIZE"

# Build the final PostgreSQL data image using the extracted data
echo "Building final PostgreSQL data image: mingzilla/postgres-company-lexical-data:$VERSION"

docker build -f Dockerfile_stage2_data_final -t mingzilla/postgres-company-lexical-data:latest .
docker tag mingzilla/postgres-company-lexical-data:latest mingzilla/postgres-company-lexical-data:$VERSION

# Verify the image was created
if docker image inspect mingzilla/postgres-company-lexical-data:$VERSION >/dev/null 2>&1; then
    echo "✅ Image created successfully!"

    # Clean up extracted data
    rm -rf postgres_data_backup/
else
    echo "❌ Failed to create image"
    exit 1
fi

# Cleanup build environment
docker-compose -f docker-compose.stage2-build-data-image.yml down --remove-orphans --volumes

echo ""
echo "Build completed."
echo ""
echo "To push this image to Docker Hub, run:"
echo "./runners/02_stage2/data_03__publish-image.sh $VERSION"