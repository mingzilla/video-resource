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
    curl::test_model "30200" "meta-llama/Llama-3.2-3B-Instruct"
fi

if [ "$1" == "log" ]; then
    docker::view_logs "vllm-llama3_2"
fi

if [ "$1" == "save" ]; then
    docker::save_as_tar "vllm-llama3_2:local" "vllm-llama3_2.tar"
fi
