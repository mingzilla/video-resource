FROM vllm/vllm-openai:v0.15.1

# Install HuggingFace tools
RUN pip install --no-cache-dir huggingface-hub hf-transfer

# Set environment
ENV HF_HOME=/app/models

# Create model directory
WORKDIR /app/models

# Download model
RUN python3 -c "from huggingface_hub import snapshot_download; snapshot_download('ISTA-DASLab/Llama-3.2-3B-Instruct-FPQuant-QAT-NVFP4', local_dir='/app/models/Llama-3.2-3B-Instruct-NVFP4', local_dir_use_symlinks=False)"

# Expose port
EXPOSE 8000

WORKDIR /app

ENV MAX_MODEL_LEN=8192
ENV GPU_MEMORY_UTILIZATION=0.90

ENTRYPOINT []
CMD vllm serve /app/models/Llama-3.2-3B-Instruct-NVFP4 \
    --served-model-name ISTA-DASLab/Llama-3.2-3B-Instruct-FPQuant-QAT-NVFP4 \
    --quantization fp_quant \
    --allow-deprecated-quantization \
    --dtype auto \
    --max-model-len ${MAX_MODEL_LEN} \
    --gpu-memory-utilization ${GPU_MEMORY_UTILIZATION} \
    --host 0.0.0.0 \
    --port 8000
