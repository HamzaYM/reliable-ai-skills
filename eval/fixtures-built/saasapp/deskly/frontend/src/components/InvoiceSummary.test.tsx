import { InvoiceSummary } from "./InvoiceSummary";

// Unit tests cover the component's props/logic; they do not assert on the
// specific rendered discount/zero-balance branches.
test("accepts line items and totals", () => {
  const el = InvoiceSummary({
    lines: [{ label: "Desk A", amountCents: 12000 }],
    discountCents: 500,
    balanceCents: 11500,
  });
  expect(el).toBeTruthy();
});

test("handles an empty invoice", () => {
  const el = InvoiceSummary({ lines: [], discountCents: 0, balanceCents: 0 });
  expect(el).toBeTruthy();
});
