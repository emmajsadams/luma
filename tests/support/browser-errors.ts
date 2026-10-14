export function assertNoBrowserErrors(errors: readonly string[]): void {
  if (errors.length > 0) {
    throw new Error(`Browser errors during journey:\n\n${errors.join("\n\n")}`);
  }
}
