#!/bin/bash

# Export workflows by parsing the ID|name format
docker exec -u node n8n n8n list:workflow 2>/dev/null | grep '|' | cut -d'|' -f1 | while read id; do
  if [ ! -z "$id" ] && [ "$id" != "ID" ]; then
    echo "Exporting workflow: $id"
    docker exec -u node n8n n8n export:workflow --id=$id --output=./workflows/$id.json 2>/dev/null
  fi
done

echo ""
echo ""
echo "Exporting credentials..."
docker exec -u node n8n n8n export:credentials --all --output=./config/credentials.json 2>/dev/null