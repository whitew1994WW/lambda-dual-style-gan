#!/usr/bin/env bash

set -e
set -x

panic() {
  >&2 echo "${1}"
  exit 1
}

usage() {
cat <<-END
Usage:
  deploy.sh <stack_name> <application_name>
Where:
  stack_name:       Is oneof 'ecr-stack' 'ssl-certificate-stack' 'api-gateway-stack'
                    'lambda-stack' 'website-stack' 's3-dependencies-bucket'
  application_name: Name of the application

END
exit 1
}

deploy() {
  local stack_name="${1}"
  local application_name="${2}"
  local cmd=${3:-deploy}

  if [ -z "${stack_name}" ]; then
    usage
  fi

  if [ -z "${application_name}" ]; then
    usage
  fi

  export APPLICATION_NAME=${application_name}
  export AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r '.Account')

  case "${stack_name}" in
    ssl-certificate-stack|ecr-stack|s3-dependencies-bucket)
      echo "Deploying ${stack_name}"
      cdk "${cmd}" "${stack_name}"
      ;;
    api-gateway-stack)
      echo "Deploying ${stack_name}"
      export DEPLOY_API_GATEWAY=true
      cdk "${cmd}" "${stack_name}"
      ;;
    lambda-stack)
      echo "Deploying ${stack_name}"
      export DEPLOY_LAMBDA=true
      cdk "${cmd}" "${stack_name}"
      ;;
    website-stack) 
      echo "Deploying ${stack_name}"
      export DEPLOY_WEBSITE=true
      cdk "${cmd}" "${stack_name}"
      ;;
    *)
      usage
      ;;
  esac
}

deploy $@
