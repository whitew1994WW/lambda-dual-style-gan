import {
  aws_apigateway,
  aws_certificatemanager,
  aws_lambda,
  aws_logs,
  CfnOutput,
  Stack,
  StackProps,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { AWS_ACM_CERTIFICATE_API_GATEWAY_REGION } from "../utils/constants";

import { getACMCertificateArn } from "../utils/getACMCertificate";
import { getApplicationName } from "../utils/getCloudFormationOutput";

interface ApiGatewayStackOpts {
  domainName: string;
}

export class ApiGatewayStack extends Stack {
  constructor(
    scope: Construct,
    id: string,
    props: StackProps,
    opts: ApiGatewayStackOpts
  ) {
    super(scope, id, props);
    (async () => {
      const applicationName: string = getApplicationName(props);
      const acmCertificateArn = await getACMCertificateArn(
        applicationName,
        AWS_ACM_CERTIFICATE_API_GATEWAY_REGION
      );
      const acmCertificate =
        aws_certificatemanager.Certificate.fromCertificateArn(
          this,
          "SSLCertificate",
          acmCertificateArn
        );

      const logGroup = new aws_logs.LogGroup(this, `api-gateway-${applicationName}`)

      const apiGateway = new aws_apigateway.LambdaRestApi(
        this,
        "ApiGatewayLambdaApi",
        {
          handler: aws_lambda.Function.fromFunctionName(
            this,
            "LambdaFunction",
            `${applicationName}-lambda`
          ),
          restApiName: `${applicationName}-rest-api`,
          deployOptions: {
            accessLogDestination: new aws_apigateway.LogGroupLogDestination(logGroup),
            accessLogFormat: aws_apigateway.AccessLogFormat.jsonWithStandardFields(),
          },
          domainName: {
            certificate: acmCertificate,
            domainName: opts.domainName,
            securityPolicy: aws_apigateway.SecurityPolicy.TLS_1_2,
          },
        }
      );

      new CfnOutput(this, "ApiGatewayRestApiId", {
        value: apiGateway.restApiId,
        exportName: `${props.stackName}:RestApiId`,
      });

      new CfnOutput(this, "ApiGatewayApiARN", {
        value: apiGateway.arnForExecuteApi("*"),
        exportName: `${props.stackName}:ApiGatewayArn`,
      });
    })();
  }
}
