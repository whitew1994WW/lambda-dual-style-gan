#!/usr/bin/env bash

LAMBDA_FUNCTION_NAME="style-transfer-lambda"
AWS_ACCOUNT_ID=""
AWS_ECR_REPOSITORY_NAME="style-transfer-ecr-repository"

deployLambdaFunction() {
  aws lambda update-function-code \
    --function-name "${LAMBDA_FUNCTION_NAME}" \
    --image-uri "${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/${AWS_ECR_REPOSITORY_NAME}:latest"
}

deployLambdaFunction
