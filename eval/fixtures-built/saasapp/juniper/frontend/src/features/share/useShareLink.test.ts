import { useShareLink } from "./useShareLink";

test("redeem POST is made", async () => {
  (global as any).fetch = jest.fn(async () => ({
    json: async () => ({ appointment: {}, link_token: "t" }),
  }));
  (global as any).localStorage = { setItem: jest.fn(), getItem: jest.fn() };
  await useShareLink("code-1");
  expect((global as any).fetch).toHaveBeenCalledWith(
    "/api/share/redeem", expect.anything());
});
