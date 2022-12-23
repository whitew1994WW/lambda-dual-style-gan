import {
  Stack,
  StackProps,
  aws_ecr,
  CfnOutput,
  RemovalPolicy,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { getApplicationName } from "../utils/getCloudFormationOutput";

export class DeployEcrStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const applicationName: string = getApplicationName(props);

    const ecrRepository = new aws_ecr.Repository(this, "ECRRepository", {
      repositoryName: `${applicationName}-ecr-repository`,
      imageTagMutability: aws_ecr.TagMutability.MUTABLE,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    new CfnOutput(this, "ECRRepositoryArn", {
      exportName: `${props.stackName}:ECRRepositoryArn`,
      value: ecrRepository.repositoryArn,
    });

    new CfnOutput(this, "ECRRepositoryName", {
      exportName: `${props.stackName}:ECRRepositoryName`,
      value: ecrRepository.repositoryName,
    });
  }
}
