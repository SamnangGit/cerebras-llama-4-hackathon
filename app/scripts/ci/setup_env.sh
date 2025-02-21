#!/bin/bash
set -e

# Set up version variables
export VERSION=$(git rev-parse --short HEAD)
export BUILD_VERSION="${VERSION}-${BUILD_NUMBER}"
export IMAGE_NAME='gtea.sinet.com.kh/sinet/receipt-data-analysis'

# Save environment variables for other scripts
echo "VERSION=${VERSION}" > .env
echo "BUILD_VERSION=${BUILD_VERSION}" >> .env
echo "IMAGE_NAME=${IMAGE_NAME}" >> .env