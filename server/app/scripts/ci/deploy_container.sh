#!/bin/bash
set -e

# Load environment variables
source .env

ssh -o StrictHostKeyChecking=no -p ${SSH_PORT} ${SSH_HOST} "\
    docker stop receipt-data-analysis-container || true && \
    docker rm receipt-data-analysis-container || true && \
    docker image pull ${IMAGE_NAME}:${BUILD_VERSION} && \
    docker container run -d --name receipt-data-analysis-container -p 80:7000 ${IMAGE_NAME}:${BUILD_VERSION}"