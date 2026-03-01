#!/bin/bash
set -e
cd "$(dirname "$0")"
source ../_common/common_cmd.sh

##############################################################

if [ $# -eq 0 ]; then
    help::show
    exit 1
fi

if [ "$1" == "curl" ]; then
    curl::test_model "30200" "ISTA-DASLab/Llama-3.2-3B-Instruct-FPQuant-QAT-NVFP4"
fi

if [ "$1" == "log" ]; then
    docker::view_logs "vllm-llama3_2-nvfp4"
fi

if [ "$1" == "save" ]; then
    docker::save_as_tar "vllm-llama3_2-nvfp4:local" "vllm-llama3_2-nvfp4.tar"
fi

if [ "$1" == "check-fp4-kernels" ]; then
    nsys::check_fp4_kernels \
        "vllm-llama3_2-nvfp4" \
        "/usr/bin/python3 /usr/local/bin/vllm serve /app/models/Llama-3.2-3B-Instruct-NVFP4 --served-model-name ISTA-DASLab/Llama-3.2-3B-Instruct-FPQuant-QAT-NVFP4 --quantization fp_quant --allow-deprecated-quantization --dtype auto --max-model-len 8192 --gpu-memory-utilization 0.80 --host 0.0.0.0 --port 8000"
fi
