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

function help::show() {
    echo "Usage: $0 <command>"
    echo ""
    echo "Available commands:"
    echo "  curl        Test the model"
    echo "  log         View container logs"
    echo "  save        Save Docker image as tar file"
    echo ""
    echo "Examples:"
    echo "  $0 curl"
    echo "  $0 log"
    echo "  $0 save"
}
