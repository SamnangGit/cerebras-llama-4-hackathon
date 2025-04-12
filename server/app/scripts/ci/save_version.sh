#!/bin/bash
set -e

# Load environment variables
source .env

mkdir -p /var/lib/jenkins/versions
echo $BUILD_VERSION > /var/lib/jenkins/versions/receipt-data-analysis-version.txt
