#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { Environment } from "aws-cdk-lib";

import { DeployLambdaStack } from "../lib/deploy_lambda-stack";
import { DeployEcrStack } from "../lib/deploy_ecr-stack";
import { SSLCertificateStack } from "../lib/ssl_certificate-stack";
import { getEnv } from "../utils";
import { ApiGatewayStack } from "../lib/api_gateway-stack";

const APPLICATION_NAME: string = getEnv("APPLICATION_NAME");
const AWS_ACCOUNT_ID: string = getEnv("AWS_ACCOUNT_ID");
const AWS_REGION: string = process.env.AWS_REGION ?? "eu-west-1";

/* The domain name for your endpoint */
const DOMAIN_NAME: string = "";

/* Add your domain names here */
const SUBJECT_ALTERNATIVE_DOMAIN_NAMES: string[] = [
];

/* Could wrap all of this in a command line tool */
const DEPLOY_API_GATEWAY: boolean = process.env.DEPLOY_API_GATEWAY === "true";
const DEPLOY_LAMBDA: boolean = process.env.DEPLOY_LAMBDA === "true";

console.log(
  `
Deployment Variables:

APPLICATION_NAME   => ${APPLICATION_NAME}
---
DEPLOY_API_GATEWAY => ${DEPLOY_API_GATEWAY}
DEPLOY_LAMBDA      => ${DEPLOY_LAMBDA}
---
AWS_ACCOUNT_ID     => ${AWS_ACCOUNT_ID}
AWS_REGION         => ${AWS_REGION}
DOMAIN_NAME        => ${DOMAIN_NAME}
SUBJECT_ALTERNATIVE_DOMAIN_NAMES => ${SUBJECT_ALTERNATIVE_DOMAIN_NAMES.join(
    ", "
  )}
  `
);

const env: Environment = {
  account: AWS_ACCOUNT_ID,
  region: AWS_REGION,
};

/**
 * This can be deployed with just the ECR Repository and the lambda function
 * if the function's endpoint visibility is Public: authentication set to NONE
 */
const app = new cdk.App();

new DeployEcrStack(app, "ecr-stack", {
  stackName: `ecr-${APPLICATION_NAME}-stack`,
  tags: { applicationName: APPLICATION_NAME },
  env,
});

new SSLCertificateStack(
  app,
  "ssl-certificate-stack",
  {
    stackName: `ssl-certificate-${APPLICATION_NAME}-stack`,
    tags: { applicationName: APPLICATION_NAME },
    env,
  },
  {
    domainName: DOMAIN_NAME,
    subjectAlternativeNames: SUBJECT_ALTERNATIVE_DOMAIN_NAMES,
  }
);

if (DEPLOY_API_GATEWAY) {
  new ApiGatewayStack(
    app,
    "api-gateway-stack",
    {
      stackName: `api-gateway-${APPLICATION_NAME}-stack`,
      tags: { applicationName: APPLICATION_NAME },
      env,
    },
    {
      domainName: `${APPLICATION_NAME}.${DOMAIN_NAME}`,
    }
  );
}

if (DEPLOY_LAMBDA) {
  new DeployLambdaStack(app, "lambda-stack", {
    stackName: `lambda-${APPLICATION_NAME}-stack`,
    tags: { applicationName: APPLICATION_NAME },
    env,
  });
}
