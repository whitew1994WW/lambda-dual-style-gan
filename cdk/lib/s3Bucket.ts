import {
  Stack,
  StackProps,
  aws_s3,
  RemovalPolicy,
  aws_iam,
  CfnOutput,
} from "aws-cdk-lib";
import { Construct } from "constructs";

type S3BucketProps = {
  accountId: string;
};

export class S3Bucket extends Stack {
  public constructor(
    scope: Construct,
    id: string,
    props: StackProps,
    s3BucketProps: S3BucketProps
  ) {
    super(scope, id, props);

    const s3Bucket = new aws_s3.Bucket(this, "S3Bucket", {
      blockPublicAccess: aws_s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: RemovalPolicy.DESTROY,
      publicReadAccess: false,
    });

    const adminDevelopers = aws_iam.Group.fromGroupName(
      this,
      "AdminDeveloperGroup",
      "AdminDeveloper"
    );

    s3Bucket.grantPut(adminDevelopers);
    s3Bucket.grantReadWrite(adminDevelopers);
    s3Bucket.grantDelete(adminDevelopers);

    new CfnOutput(this, "S3BucketArn", {
      exportName: `${props.stackName}:S3BucketArn`,
      value: s3Bucket.bucketArn,
    });

    new CfnOutput(this, "S3BucketName", {
      exportName: `${props.stackName}:S3BucketName`,
      value: s3Bucket.bucketName,
    });
  }
}
