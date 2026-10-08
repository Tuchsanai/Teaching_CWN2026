export function mode(): boolean {
  return process.env.BUG_MODE === "1";
}

export function testResetAllowed(): boolean {
  return process.env.ALLOW_TEST_RESET === "1";
}
