#!/bin/bash

docker compose up -d

sleep 10

./scripts/import.sh
