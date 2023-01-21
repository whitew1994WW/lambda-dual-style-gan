#!/usr/bin/env bash

panic() {
  >&2 echo "${1}"
  exit 1
}

# deploys a CDK stack and will tag the infrastructure with "APPLICATION_NAME"
deployCdkStack() {
  local stack_name="${1}"
  local application_name="${2}"

  if [ -z "${stack_name}" ]; then
    panic "Usage: ./deploy-cdk.sh <stack_name> <application_name>"
  fi

  if [ -z "${application_name}" ]; then
    panic "Usage: ./deploy-cdk.sh <stack_name> <application_name>"
  fi

  export APPLICATION_NAME="${application_name}"
  cdk deploy "${stack_name}"
}

deployCdkStack $@
