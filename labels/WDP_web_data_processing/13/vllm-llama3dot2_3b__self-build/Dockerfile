FROM nvcr.io/nvidia/pytorch:25.02-py3

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    ccache \
    cmake \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Install HuggingFace tools
RUN pip install --no-cache-dir huggingface-hub hf-transfer

# Set Blackwell environment
ENV TORCH_CUDA_ARCH_LIST=12.0
ENV VLLM_FLASH_ATTN_VERSION=2
ENV CUDA_HOME=/usr/local/cuda
ENV PATH="/usr/local/bin:$CUDA_HOME/bin:$PATH"
ENV HF_HOME=/app/models

# Build vLLM v0.15.1 from source
WORKDIR /workspace
RUN git clone --branch v0.15.1 --depth 1 https://github.com/vllm-project/vllm.git

RUN cd vllm && \
    pip install -r requirements/build.txt && \
    pip install setuptools_scm && \
    pip install "numpy<2.0" && \
    MAX_JOBS=20 pip install -e . --no-build-isolation

# Rebuild Flash Attention AFTER vLLM (vLLM re-installs broken pre-built version)
RUN pip uninstall -y flash-attn && \
    MAX_JOBS=20 pip install flash-attn --no-build-isolation

# Fix numpy version compatibility (flash-attn may reinstall numpy)
RUN pip install "numpy<2.0" --force-reinstall

# Clean up build cache
RUN rm -rf /root/.cache/pip /workspace/vllm/build /tmp/*

# Download model
WORKDIR /app/models
RUN python3 -c "from huggingface_hub import snapshot_download; snapshot_download('ISTA-DASLab/Llama-3.2-3B-Instruct-FPQuant-QAT-NVFP4', local_dir='/app/models/Llama-3.2-3B-Instruct-NVFP4', local_dir_use_symlinks=False)"

# Expose port
EXPOSE 8000

WORKDIR /app

ENV MAX_MODEL_LEN=8192
ENV GPU_MEMORY_UTILIZATION=0.80

CMD vllm serve /app/models/Llama-3.2-3B-Instruct-NVFP4 \
    --served-model-name ISTA-DASLab/Llama-3.2-3B-Instruct-FPQuant-QAT-NVFP4 \
    --quantization fp_quant \
    --allow-deprecated-quantization \
    --dtype auto \
    --max-model-len ${MAX_MODEL_LEN} \
    --gpu-memory-utilization ${GPU_MEMORY_UTILIZATION} \
    --host 0.0.0.0 \
    --port 8000
