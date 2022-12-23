#!/usr/bin/env bash

LAMBDA_FUNCTION_NAME="style-transfer-lambda"
ACCOUNT_ID=""
ECR_REPOSITORY="style-transfer-ecr-repository"

deployLambdaFunction() {
  aws lambda update-function-code \
    --function-name "${LAMBDA_FUNCTION_NAME}" \
    --image-uri "${ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com/${ECR_REPOSITORY}:latest"
}

deployLambdaFunction
