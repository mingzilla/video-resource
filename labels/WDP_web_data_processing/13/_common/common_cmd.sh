#!/bin/bash
set -e

function curl::test_model() {
    local port_number="$1"
    local model_name="$2"
    echo "============================== $model_name ===================================="

    curl -X POST "http://localhost:$port_number/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d "$(
        jq -n \
        --arg model "$model_name" \
        '{
            model: $model,
            messages: [{role: "user", "content": "hi"}],
            stream: false,
            max_tokens: 2048
        }'
    )" | jq .
    echo ""
}

function docker::view_logs() {
    local model_name="$1"
    docker logs -f "$model_name"
}

function docker::save_as_tar() {
    local image_name="$1"
    local output_file="$2"

    echo "Saving Docker image: $image_name"
    echo "Output file: $output_file"

    docker save "$image_name" -o "$output_file"

    if [ -f "$output_file" ]; then
        local file_size=$(du -h "$output_file" | cut -f1)
        echo "✓ Image saved successfully: $output_file ($file_size)"
    else
        echo "✗ Failed to save image"
        exit 1
    fi
}


function nsys::ensure_installed() {
    local container_name="$1"
    if docker exec "$container_name" which nsys > /dev/null 2>&1; then
        return 0
    fi
    echo "nsys not found. Installing nsight-systems inside container..."
    local install_script
    install_script=$(mktemp /tmp/install_nsys.XXXXXX.sh)
    cat > "$install_script" << 'EOF'
#!/bin/bash
set -e
if [ ! -f /etc/apt/trusted.gpg.d/cuda-archive-keyring.gpg ]; then
    curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb -o cuda-keyring_1.1-1_all.deb
    dpkg -i cuda-keyring_1.1-1_all.deb
    rm -f cuda-keyring_1.1-1_all.deb
fi
apt-get update -q
NSYS_PKG=$(apt-cache search '^nsight-systems-[0-9]' | grep -v dbg | sort -V | tail -1 | awk '{print $1}')
echo "Installing: $NSYS_PKG"
apt-get install -y "$NSYS_PKG"
NSYS_VER=$(echo "$NSYS_PKG" | sed 's/nsight-systems-//')
ln -sf /opt/nvidia/nsight-systems/${NSYS_VER}/bin/nsys /usr/local/bin/nsys
EOF
    chmod +x "$install_script"
    docker cp "$install_script" "$container_name":/tmp/install_nsys.sh
    rm -f "$install_script"
    docker exec "$container_name" bash /tmp/install_nsys.sh
    docker exec "$container_name" rm /tmp/install_nsys.sh
    echo "nsys installed."
}

function nsys::check_fp4_kernels() {
    local container_name="$1"
    local vllm_serve_cmd="$2"

    nsys::ensure_installed "$container_name"

    # Parse model options from the serve command.
    local model_path
    model_path=$(echo "$vllm_serve_cmd" | grep -oP '(?<= serve )\S+')
    local quantization
    quantization=$(echo "$vllm_serve_cmd" | grep -oP '(?<=--quantization )\S+')
    local gpu_util
    gpu_util=$(echo "$vllm_serve_cmd" | grep -oP '(?<=--gpu-memory-utilization )\S+')
    gpu_util=${gpu_util:-0.80}
    local dtype
    dtype=$(echo "$vllm_serve_cmd" | grep -oP '(?<=--dtype )\S+')
    dtype=${dtype:-auto}
    local extra_args=""
    if echo "$vllm_serve_cmd" | grep -q 'allow-deprecated-quantization'; then
        extra_args="        allow_deprecated_quantization=True,"
    fi

    # Write inference script.
    local tmp_script
    tmp_script=$(mktemp /tmp/vllm_nsys_infer.XXXXXX.py)
    cat > "$tmp_script" << EOF
#!/usr/bin/env python3
"""Minimal vLLM inference for nsys profiling. nsys captures all CUDA externally."""
from vllm import LLM, SamplingParams

if __name__ == '__main__':
    print("Loading model: $model_path", flush=True)
    llm = LLM(
        model="$model_path",
        quantization="$quantization",
$extra_args
        enforce_eager=True,
        max_model_len=256,
        gpu_memory_utilization=$gpu_util,
        dtype="$dtype",
    )
    print("Warming up...", flush=True)
    llm.generate(["warmup"], SamplingParams(max_tokens=5))
    print("Running inference...", flush=True)
    outputs = llm.generate(["hi"], SamplingParams(max_tokens=20))
    print("Output:", outputs[0].outputs[0].text, flush=True)
    print("Done.", flush=True)
EOF
    chmod +x "$tmp_script"
    docker cp "$tmp_script" "$container_name":/tmp/vllm_nsys_infer.py
    rm -f "$tmp_script"

    # Snapshot container (preserves nsys + inference script).
    # The server must be stopped so nsys has exclusive GPU profiling access.
    # When the server is running alongside nsys, its CUDA session conflicts with
    # nsys's CUPTI injection, causing the EngineCore subprocess to fail with
    # "No CUDA GPUs are available".
    local tmp_image="${container_name}:fp4check-tmp"
    echo "Snapshotting container..."
    docker commit "$container_name" "$tmp_image" > /dev/null
    echo "Stopping original container (nsys needs exclusive GPU profiling access)..."
    docker update --restart=no "$container_name" > /dev/null
    docker stop "$container_name" > /dev/null

    # Run one-shot profiling container (foreground, blocks until done).
    local check_container="${container_name}-fp4check"
    docker rm -f "$check_container" 2>/dev/null || true
    echo "Running nsys profile (should complete in ~1-2 min)..."
    docker run \
        --name "$check_container" \
        --gpus all \
        --ipc=host \
        --privileged \
        -e NVIDIA_VISIBLE_DEVICES=0 \
        -e CUDA_VISIBLE_DEVICES=0 \
        "$tmp_image" \
        bash -c "
            nsys profile --trace=cuda --force-overwrite=true -o /tmp/kern_trace \
                /usr/bin/python3 /tmp/vllm_nsys_infer.py
            echo ''
            echo '====== Top CUDA Kernels by Total Time ======'
            nsys stats /tmp/kern_trace.nsys-rep --report cuda_gpu_kern_sum 2>/dev/null | head -60
            echo ''
            echo 'Inspect the table above. See nvfp4_verification.md for what to look for.'
        "

    # Cleanup
    docker rm "$check_container" > /dev/null 2>&1 || true
    docker rmi "$tmp_image" > /dev/null 2>&1 || true

    # Restart original container
    echo ""
    echo "Restarting original vLLM container..."
    docker update --restart=unless-stopped "$container_name" > /dev/null
    docker start "$container_name" > /dev/null
    echo "Done. Wait a few minutes for vLLM to be ready."
}

function help::show() {
    echo "Usage: $0 <command>"
    echo ""
    echo "Available commands:"
    echo "  curl              Test the model"
    echo "  log               View container logs"
    echo "  save              Save Docker image as tar file"
    echo "  check-fp4-kernels Run ncu profiling in a temporary container to capture GPU metrics."
    echo "                    Afterwards run 'log' and 'curl' to confirm clean restart."
    echo ""
    echo "Examples:"
    echo "  $0 curl"
    echo "  $0 log"
    echo "  $0 save"
    echo "  $0 check-fp4-kernels"
}
