#!/bin/bash
set -e

# Get the version from Jenkins versions directory
cat /var/lib/jenkins/versions/receipt-data-analysis-version.txt > .build_version

# Save environment variables for other scripts
echo "IMAGE_NAME=${IMAGE_NAME}" > .env
echo "BUILD_VERSION=$(cat .build_version)" >> .env