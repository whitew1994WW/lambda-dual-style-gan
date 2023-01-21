#!/usr/bin/env bash

set -e

AWS_ACCOUNT_ID=""
AWS_REGION="eu-west-1"
AWS_ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
AWS_ECR_REPOSITORY_NAME="style-transfer-ecr-repository"

ecrLogin() {
  aws ecr get-login-password \
    --region "${AWS_REGION}" | \
    docker login \
      --username AWS \
      --password-stdin "${AWS_ECR_URL}"
}

pullImage() {
  local version=${1}
  
  if [ -z $version ]; then
    echo "usage ./docker-pull-image.sh <version_or_tag>"
    exit 1
  fi

  ecrLogin
  uri=""
  #docker pull ${AWS_ECR_URL}/${AWS_ECR_REPOSITORY_NAME}:${version}
  docker pull $uri
}

pullImage $@
