FROM vllm/vllm-openai:v0.15.1

# Install HuggingFace tools
RUN pip install --no-cache-dir huggingface-hub hf-transfer

# Set environment
ENV HF_HOME=/app/models

# Create model directory
WORKDIR /app/models

# Download Qwen3 model
RUN python3 -c "from huggingface_hub import snapshot_download; snapshot_download('nvidia/Qwen3-32B-NVFP4', local_dir='/app/models/Qwen3-32B-NVFP4', local_dir_use_symlinks=False)"

# Expose port
EXPOSE 8000

WORKDIR /app

ENV MAX_MODEL_LEN=8192
ENV GPU_MEMORY_UTILIZATION=0.80
ENV SWAP_SPACE=60

ENTRYPOINT []
CMD vllm serve /app/models/Qwen3-32B-NVFP4 \
    --served-model-name nvidia/Qwen3-32B-NVFP4 \
    --quantization nvfp4 \
    --dtype auto \
    --max-model-len ${MAX_MODEL_LEN} \
    --gpu-memory-utilization ${GPU_MEMORY_UTILIZATION} \
    --swap-space ${SWAP_SPACE} \
    --enforce-eager \
    --host 0.0.0.0 \
    --port 8000
