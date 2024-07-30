#!/bin/bash
set -xe

BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD | sed 's/[^a-zA-Z0-9]/-/g')  # should be the same as GIT_REF
COMMIT_SHA=$(git rev-parse HEAD)
CURRENT_DATE=$(date +"%Y%m%d")
CURRENT_TIME=$(date +"%H%M%S")


DOCKER_TAG="${DOCKER_IMAGE_NAME}:${BRANCH_NAME}"
DOCKER_TAG_WITH_DATE="${DOCKER_IMAGE_NAME}:${BRANCH_NAME}-${CURRENT_DATE}-${CURRENT_TIME}"


docker build  --tag "${DOCKER_TAG}" --tag "${DOCKER_TAG_WITH_DATE}" --file "${DOCKERFILE}" .

echo "$DOCKER_PASSWORD" | docker login $DOCKER_REGISTRY --username "$DOCKER_USERNAME" --password-stdin

docker push "${DOCKER_TAG}"
docker push "${DOCKER_TAG_WITH_DATE}"
