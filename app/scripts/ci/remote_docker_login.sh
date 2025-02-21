#!/bin/bash
set -e

ssh -o StrictHostKeyChecking=no -p ${SSH_PORT} ${SSH_HOST} \
    "echo ${DOCKER_CREDENTIALS_PSW} | docker login -u ${DOCKER_CREDENTIALS_USR} --password-stdin"