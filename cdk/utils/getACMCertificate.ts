import { getCloudFormationOutput } from "./getCloudFormationOutput";

export async function getACMCertificateArn(
  applicationName: string,
  region: string
) {
  let acmCertificateArn: string = "";

  try {
    const val = await getCloudFormationOutput(
      region,
      `ssl-certificate-${applicationName}-stack`,
      "CertificateArn"
    );
    if (!val) {
      process.stderr.write(
        `No ACM certificate found for 'ssl-certificate-${applicationName}-stack:CertificateArn'`
      );
      process.exit(1);
    } else {
      acmCertificateArn = val;
    }
  } catch (e) {
    process.stderr.write(`Failed to get acm Certificate: ${e}\n`);
    process.exit(1);
  }

  return acmCertificateArn;
}
