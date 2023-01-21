import {
  aws_ecr,
  aws_iam,
  aws_lambda,
  CfnOutput,
  Duration,
  Stack,
  StackProps,
} from "aws-cdk-lib";
import { Construct } from "constructs";

import {
  getApplicationName,
  getCloudFormationOutput,
} from "../utils/getCloudFormationOutput";

export class DeployLambdaStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);
    (async () => {
      const applicationName: string = getApplicationName(props);
      const apiGatewayApiARN: string | undefined =
        await getCloudFormationOutput(
          this.region,
          `api-gateway-${applicationName}-stack`,
          "ApiGatewayArn"
        );

      if (!apiGatewayApiARN) {
        throw new Error("ApiGatewayArn is undefined");
      }

      const lambda = new aws_lambda.Function(this, "LambdaFunction", {
        functionName: `${applicationName}-lambda`,
        description: `Lambda Function for: ${applicationName} lambda function`,
        runtime: aws_lambda.Runtime.FROM_IMAGE,
        handler: aws_lambda.Handler.FROM_IMAGE,
        code: aws_lambda.Code.fromEcrImage(
          aws_ecr.Repository.fromRepositoryName(
            this,
            "ReferencedECRRepository",
            `${applicationName}-ecr-repository`
          )
        ),
        timeout: Duration.seconds(90),
        memorySize: 9000,
      });

      const lambdaUrl = lambda.addFunctionUrl({
        authType: aws_lambda.FunctionUrlAuthType.AWS_IAM,
        cors: {
          allowedOrigins: ["*"],
          allowedMethods: [aws_lambda.HttpMethod.ALL],
          allowedHeaders: ["access-control-allow-origin"]
        },
      });

      lambda.addPermission("ApiGatewayLambdaPermission", {
        action: "lambda:InvokeFunction",
        principal: new aws_iam.ServicePrincipal("apigateway.amazonaws.com"),
        sourceArn: apiGatewayApiARN,
      });

      new CfnOutput(this, "LambdaFunctionArn", {
        value: lambda.functionArn,
        exportName: `${props.stackName}:LambdaArn`,
      });

      new CfnOutput(this, "LambdaFunctionName", {
        value: lambda.functionName,
        exportName: `${props.stackName}:LambdaName`,
      });

      new CfnOutput(this, "LambdaUrl", {
        value: lambdaUrl.url,
        exportName: `${props.stackName}:LambdaUrl`
      });

    })();
  }
}
