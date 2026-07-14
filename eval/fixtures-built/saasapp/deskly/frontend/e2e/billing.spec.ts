import { test, expect } from "@playwright/test";

test("invoice/billing screen renders the summary", async ({ page }) => {
  await page.goto("/billing");
  await expect(page.locator(".invoice-summary")).toBeVisible();
  await expect(page.locator(".line.total")).toContainText("Balance due");
});
