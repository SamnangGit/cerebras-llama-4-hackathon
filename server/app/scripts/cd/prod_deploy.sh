#!/bin/bash
set -e

# Load environment variables
source .env

# Perform docker login on remote production server
ssh -o StrictHostKeyChecking=no -p ${SSH_PORT} ${SSH_HOST} \
    "echo ${DOCKER_CREDENTIALS_PSW} | docker login -u ${DOCKER_CREDENTIALS_USR} --password-stdin"

# Deploy to production
ssh -o StrictHostKeyChecking=no -p ${SSH_PORT} ${SSH_HOST} "\
    docker stop receipt-data-analysis-container || true && \
    docker rm receipt-data-analysis-container || true && \
    docker image pull ${IMAGE_NAME}:${BUILD_VERSION} && \
    docker container run -d --name receipt-data-analysis-container \
    -p 80:7000 \
    --label version=${BUILD_VERSION} \
    ${IMAGE_NAME}:${BUILD_VERSION}"