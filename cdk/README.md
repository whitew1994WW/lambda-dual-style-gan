# AWS Infrastructure
The deployed infrastructure provides a serverless architecture that allows for an HTTP API to be exposed through API Gateway, with a Lambda function processing incoming requests. The API Gateway provides a fully-managed solution for creating, deploying, and scaling APIs. The Lambda function runs in a Docker container hosted in ECR, providing a scalable and portable runtime environment.

## Before starting, you will need the following:
- An AWS account with sufficient permissions to deploy the infrastructure
- The AWS CLI installed on your machine
- Node.js and npm installed on your machine

# Stacks
There is some choreography involved in deploying the stacks they are:

## `ssl-certificiate`
The SSL certificate that API gateway will use for HTTPS. Change `SUBJECT_ALTERNATIVE_DOMAIN_NAMES` in `bin/deploy_lambda.ts` to the domain name(s) you wish to use along with `DOMAIN_NAME`.

## `ecr-stack`
For housing the docker image.

## `api-gateway-stack`
Connects the lambda to the api gateway exposing it as an endpoint.

## `lambda-stack`
Deploys the AWS lambda with the docker image as the runtime.

# Order of deployment
To deploy use `deploy.sh`

1. Deploy `ecr-stack`
2. Deploy `ssl-certificate`
3. Deploy the docker image to the newly created ECR repository using `deploy-docker-image.sh`
4. Deploy the `api-gateway-stack`
5. Deploy the `lambda-stack`

If you want to change the code that runs in the docker image you then need to:
1. Build the docker image & deploy to ECR using `deploy-docker-image.sh`
2. Deploy the docker image in ECR to lambda

## Useful commands
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template
