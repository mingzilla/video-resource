```shell
curl -X POST http://localhost:11435/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
        "model": "nomic-embed-text",
        "prompt": "Hi"
      }'
```