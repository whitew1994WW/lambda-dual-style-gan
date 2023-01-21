/**
 * Get environment variable or exit
 *
 * @param {string} name - Name of the environment variable
 * @return {string}
 */
export function getEnv(name: string): string {
  const envvar = process.env[name];

  if (!envvar) {
    process.stderr.write(`Environment variable '${name}' must be set\n`);
    process.exit(1);
  }

  return envvar;
}
