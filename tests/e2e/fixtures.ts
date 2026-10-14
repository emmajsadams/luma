import { test as base, type ConsoleMessage } from "@playwright/test";
import { assertNoBrowserErrors } from "../support/browser-errors";

export { expect } from "@playwright/test";

export const test = base.extend<{ browserErrors: void }>({
  browserErrors: [
    async ({ page }, runJourney) => {
      const errors: string[] = [];
      const onConsole = (message: ConsoleMessage) => {
        if (message.type() !== "error") return;
        const { url, lineNumber, columnNumber } = message.location();
        errors.push(
          `console.error: ${message.text()} (${url || "unknown source"}:${lineNumber}:${columnNumber})`,
        );
      };
      const onPageError = (error: Error) => {
        errors.push(`pageerror: ${error.stack || error.message}`);
      };
      page.on("console", onConsole);
      page.on("pageerror", onPageError);
      try {
        await runJourney();
      } finally {
        page.off("console", onConsole);
        page.off("pageerror", onPageError);
        assertNoBrowserErrors(errors);
      }
    },
    { auto: true },
  ],
});
