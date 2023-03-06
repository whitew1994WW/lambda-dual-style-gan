# Deployment Scripts
Assumes that you have deployed the aws infrastructure in the `cdk` folder

## Scripts

### `deploy-cdk.sh`
This script doesn't work so don't use it!

### `deploy-docker-image.sh`
Builds and deploys the docker image to ECR

### `deploy-lambda.sh`
Deploys the docker image to the lambda function

### `docker-pull-image.sh`
Pulls the docker image from ECR, can be useful for debugging
