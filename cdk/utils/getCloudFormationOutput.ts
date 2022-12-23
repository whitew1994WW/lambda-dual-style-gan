import { CloudFormation } from "@aws-sdk/client-cloudformation";
import { StackProps } from "aws-cdk-lib";

/* Memoize creating a CloudFormation client */
function makeGetCloudFormationClient() {
  const clients: Record<string, CloudFormation> = {};
  return (region: string) => {
    const client = clients[region];
    if (client) {
      return client;
    } else {
      const newClient = new CloudFormation({ region });
      clients[region] = newClient;
      return newClient;
    }
  };
}

const getCloudFormationClient = makeGetCloudFormationClient();

export async function getCloudFormationOutput(
  region: string,
  stackName: string,
  exportName: string
): Promise<string | undefined> {
  try {
    const cloudformation = getCloudFormationClient(region);
    const response = await cloudformation.describeStacks({
      StackName: stackName,
    });
    const _exportName = `${stackName}:${exportName}`;

    for (const stack of response.Stacks ?? []) {
      if (stack.StackName == stackName) {
        for (const output of stack.Outputs ?? []) {
          if (output.ExportName == _exportName) {
            return output.OutputValue;
          }
        }
      }
    }
  } catch (e) {
    throw new Error(
      `Failed to get output from cloudformation stack: ${stackName} ${e}`
    );
  }
  return;
}

export function getApplicationName(stackProps?: StackProps): string {
  const applicationName: string | undefined = stackProps?.tags?.applicationName;

  if (!applicationName) {
    process.stderr.write(`Tag 'applicationName' must be set\n`);
    process.exit(1);
  }

  return applicationName;
}
