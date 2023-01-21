import {
  aws_cloudfront,
  aws_cloudfront_origins,
  aws_s3,
  aws_certificatemanager,
  Duration,
  RemovalPolicy,
  Stack,
  StackProps,
  CfnOutput,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { AWS_ACM_CERTIFICATE_CLOUDFRONT_REGION } from "../utils/constants";
import { getACMCertificateArn } from "../utils/getACMCertificate";
import { getApplicationName } from "../utils/getCloudFormationOutput";

export class WebsiteStack extends Stack {
  constructor(
    scope: Construct,
    id: string,
    props: StackProps,
    domainNames: string[]
  ) {
    super(scope, id, props);
    (async () => {
      const applicationName = getApplicationName(props);
      const acmCertificateArn = await getACMCertificateArn(
        applicationName,
        AWS_ACM_CERTIFICATE_CLOUDFRONT_REGION
      );

      const privateS3Bucket = new aws_s3.Bucket(this, "S3Bucket", {
        blockPublicAccess: aws_s3.BlockPublicAccess.BLOCK_ALL,
        removalPolicy: RemovalPolicy.DESTROY,
      });

      const originAccessIdentity = new aws_cloudfront.OriginAccessIdentity(
        this,
        "OriginAccessIdentity",
        {
          comment: `Origin access identity for ${applicationName}`,
        }
      );

      privateS3Bucket.grantRead(originAccessIdentity);

      const securityHeadersBehavior: aws_cloudfront.ResponseSecurityHeadersBehavior =
        {
          frameOptions: {
            frameOption: aws_cloudfront.HeadersFrameOption.DENY,
            override: true,
          },
          strictTransportSecurity: {
            accessControlMaxAge: Duration.seconds(31536000),
            preload: true,
            includeSubdomains: true,
            override: true,
          },
          xssProtection: {
            protection: true,
            modeBlock: true,
            override: true,
          },
          referrerPolicy: {
            referrerPolicy: aws_cloudfront.HeadersReferrerPolicy.SAME_ORIGIN,
            override: true,
          },
          contentTypeOptions: {
            override: true,
          },
        };

      const cloudFrontResponseHeadersPolicy =
        new aws_cloudfront.ResponseHeadersPolicy(
          this,
          "CloudFrontResponseHeadersPolicy",
          {
            comment: `Security Response Headers for ${applicationName}`,
            responseHeadersPolicyName: `${applicationName}-response-headers`,
            customHeadersBehavior: {
              customHeaders: [
                {
                  header: "server",
                  value: "yeetmaster420quicknoscope",
                  override: true,
                },
              ],
            },
            securityHeadersBehavior,
          }
        );

      const cloudFrontCachePolicy = new aws_cloudfront.CachePolicy(
        this,
        "CloudFrontCachePolicy",
        {
          cachePolicyName: `${applicationName}-cache-policy`,
          comment: `Cache policy for ${applicationName}`,
          defaultTtl: Duration.minutes(30),
          minTtl: Duration.minutes(1),
          maxTtl: Duration.days(10),
          enableAcceptEncodingGzip: true,
          enableAcceptEncodingBrotli: true,
        }
      );

      const acmCertificate =
        aws_certificatemanager.Certificate.fromCertificateArn(
          this,
          "SSLCertificate",
          acmCertificateArn
        );

      const cloudFrontDistribution = new aws_cloudfront.Distribution(
        this,
        "CloudFrontDistribution",
        {
          comment: `CloudFront Distribution for ${applicationName}`,
          domainNames,
          minimumProtocolVersion:
            aws_cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
          certificate: acmCertificate,
          defaultBehavior: {
            cachePolicy: cloudFrontCachePolicy,
            responseHeadersPolicy: cloudFrontResponseHeadersPolicy,
            viewerProtocolPolicy:
              aws_cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
            origin: new aws_cloudfront_origins.S3Origin(privateS3Bucket, {
              originAccessIdentity: originAccessIdentity,
            }),
            allowedMethods: aws_cloudfront.AllowedMethods.ALLOW_GET_HEAD,
            cachedMethods: aws_cloudfront.CachedMethods.CACHE_GET_HEAD,
          },
          defaultRootObject: "index.html",
          errorResponses: [
            {
              httpStatus: 404,
              responseHttpStatus: 200,
              responsePagePath: "/index.html",
              ttl: Duration.seconds(0),
            },
          ],
        }
      );

      new CfnOutput(this, "CloudFrontDistributionId", {
        exportName: `${props.stackName}:CloudFrontDistributionId`,
        value: cloudFrontDistribution.distributionId,
      });

      new CfnOutput(this, "S3BucketName", {
        exportName: `${props.stackName}:S3BucketName`,
        value: privateS3Bucket.bucketName,
      });

      new CfnOutput(this, "S3BucketArn", {
        exportName: `${props.stackName}:S3BucketArn`,
        value: privateS3Bucket.bucketArn,
      });
    })();
  }
}
