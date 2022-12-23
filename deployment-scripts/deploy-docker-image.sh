#!/usr/bin/env bash

set -e

AWS_ACCOUNT_ID=""
AWS_REGION="eu-west-1"
AWS_ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
AWS_ECR_REPOSITORY_NAME="style-transfer-ecr-repository"
LAMBDA_FUNCTION_NAME=""

getNextDockerImageVersion() {
  local current_version=$(cat ./docker-image.version)
  local version_array=(${current_version//./ })
  # increment the patch
  ((version_array[2]++))
  local new_version="${version_array[0]}.${version_array[1]}.${version_array[2]}"

  printf ${new_version} > ./docker-image.version
  printf "v${new_version}"
}

ecrLogin() {
  aws ecr get-login-password \
    --region "${AWS_REGION}" | \
    docker login \
      --username AWS \
      --password-stdin "${AWS_ECR_URL}"
}

deployDockerImage() {
  local version=$(getNextDockerImageVersion)
  local image_uri="${AWS_ECR_URL}/${AWS_ECR_REPOSITORY_NAME}:latest"
  local image_versioned="${AWS_ECR_URL}/${AWS_ECR_REPOSITORY_NAME}:${version}"

  ecrLogin
  docker build -t "${image_uri}" -t "${image_versioned}" .
  docker push "${image_uri}"
  docker push "${image_versioned}"

  #
  #aws lambda update-function \
  #  --function-name "${LAMBDA_FUNCTION_NAME}" \
  #  --image-uri "${image_uri}" | jq
}

deployDockerImage
