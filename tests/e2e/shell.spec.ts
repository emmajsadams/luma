import { expect, test } from "./fixtures";
import AxeBuilder from "@axe-core/playwright";
test("unconfigured app fails closed on every resource, with accessible responsive layout", async ({ page, request }) => {
  for (const route of ["/", "/tasks", "/notes", "/calendar", "/sign-in", "/sign-up"]) {
    await page.goto(route);
    await expect(page.getByRole("heading", { name: "Setup unavailable" })).toBeVisible();
    await expect(page.getByRole("checkbox")).toHaveCount(0);
    await expect(page.getByText("No demo session is active.", { exact: false })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  for (const route of ["/api/mcp", "/api/tasks", "/api/tasks.json"]) {
    const response = await request.get(route);
    expect(response.status()).toBe(503);
    expect(await response.json()).toEqual({ error: "Authentication setup unavailable" });
  }
  await page.screenshot({ path: `test-results/setup-${test.info().project.name}.png`, fullPage: true });
});