#!/bin/bash

if [ ! -f ./config/credentials.json ]; then
  echo "[]" > ./config/credentials.json
fi

for file in ./workflows/*.json; do
  docker exec -u node n8n n8n import:workflow --input=/home/node/workflows/$(basename $file)
done

docker exec -u node n8n n8n import:credentials --input=/home/node/config/credentials.json
