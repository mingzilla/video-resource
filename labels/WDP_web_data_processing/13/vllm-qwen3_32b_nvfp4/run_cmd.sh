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
    curl::test_model "30202" "nvidia/Qwen3-32B-NVFP4"
fi

if [ "$1" == "log" ]; then
    docker::view_logs "vllm-qwen3-nvfp4"
fi

if [ "$1" == "save" ]; then
    docker::save_as_tar "vllm-qwen3-nvfp4:local" "vllm-qwen3-nvfp4.tar"
fi
