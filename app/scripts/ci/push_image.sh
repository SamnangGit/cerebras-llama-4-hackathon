#!/bin/bash
set -e

# Load environment variables
source .env

# Push both tags
docker push $IMAGE_NAME:$BUILD_VERSION
docker push $IMAGE_NAME:latest

# Save the version for later use
echo $BUILD_VERSION > .build_version