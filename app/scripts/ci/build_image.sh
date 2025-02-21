#!/bin/bash
set -e

# Load environment variables
source .env

# Build Docker image with multiple tags
docker build -t $IMAGE_NAME:$BUILD_VERSION -t $IMAGE_NAME:latest .
