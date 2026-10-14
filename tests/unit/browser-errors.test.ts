import { expect, test } from "vitest";
import { assertNoBrowserErrors } from "../support/browser-errors";

test("accepts a browser journey without errors", () => {
  expect(() => assertNoBrowserErrors([])).not.toThrow();
});

test("rejects a deliberately supplied console error with its source", () => {
  const diagnostic =
    "console.error: synthetic console failure (http://localhost/example.js:12:3)";
  expect(() => assertNoBrowserErrors([diagnostic])).toThrow(diagnostic);
});

test("preserves every error and the uncaught exception stack", () => {
  const errors = [
    "console.error: synthetic console failure",
    "pageerror: Error: synthetic uncaught failure\n    at synthetic (example.js:4:2)",
  ];
  expect(() => assertNoBrowserErrors(errors)).toThrow(errors.join("\n\n"));
});
