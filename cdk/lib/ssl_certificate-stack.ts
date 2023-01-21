import {
  Stack,
  StackProps,
  aws_certificatemanager,
  CfnOutput,
} from "aws-cdk-lib";
import { Construct } from "constructs";

export interface SSLCertificateStackProps {
  domainName: string;
  subjectAlternativeNames: string[];
}

export class SSLCertificateStack extends Stack {
  constructor(
    scope: Construct,
    id: string,
    props: StackProps,
    sslCertProps: SSLCertificateStackProps
  ) {
    super(scope, id, props);

    process.stdout.write(`
Remember to go to certificates manager, open the certificate and manually add the CNAME to the DNS provider. (Cloudflare)
This stack will hang untill you do!!!
`);

    const certificate = new aws_certificatemanager.Certificate(
      this,
      "SSLCertificate",
      {
        domainName: sslCertProps.domainName,
        subjectAlternativeNames: sslCertProps.subjectAlternativeNames,
        /* TODO:
         * This will hang untill going over to the certificates manager, opening the
         * certificate and and pasting in CNAME to the DNS provider */
        validation: aws_certificatemanager.CertificateValidation.fromDns(),
      }
    );

    new CfnOutput(this, "SSLCertificateStackArn", {
      exportName: `${props.stackName}:CertificateArn`,
      value: certificate.certificateArn,
    });
  }
}
