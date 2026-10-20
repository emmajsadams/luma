import { convexTest } from "convex-test";
import { expect, test } from "vitest";
import { makeFunctionReference } from "convex/server";
import schema from "../../convex/schema";
const modules = import.meta.glob("../../convex/**/*.ts");
const list = makeFunctionReference<"query">("tasks:list");
const add = makeFunctionReference<"mutation">("tasks:add");
const toggle = makeFunctionReference<"mutation">("tasks:toggle");
const remove = makeFunctionReference<"mutation">("tasks:remove");
test("anonymous access denied for every task operation", async () => {
  const t = convexTest(schema, modules);
  const a = t.withIdentity({ subject: "a", issuer: "https://issuer.test" });
  const id = await a.mutation(add, { title: "Private" });
  await expect(t.query(list, {})).rejects.toThrow("Unauthenticated");
  for (const [fn, args] of [[add, { title: "Bad" }], [toggle, { id }], [remove, { id }]] as const)
    await expect(t.mutation(fn, args)).rejects.toThrow("Unauthenticated");
});
test("persisted CRUD is scoped to tokenIdentifier, including differing issuers", async () => {
  const t = convexTest(schema, modules);
  const a = t.withIdentity({ subject: "same", issuer: "https://a.test" });
  const b = t.withIdentity({ subject: "same", issuer: "https://b.test" });
  const id = await a.mutation(add, { title: "  Private task  ", dueDate: "2028-02-29" });
  expect(await b.query(list, {})).toEqual([]);
  for (const fn of [toggle, remove]) await expect(b.mutation(fn, { id })).rejects.toThrow("Not found");
  expect(await a.query(list, {})).toMatchObject([{ title: "Private task", done: false, dueDate: "2028-02-29" }]);
  await a.mutation(toggle, { id });
  expect(await a.query(list, {})).toMatchObject([{ done: true }]);
  await a.mutation(remove, { id });
  expect(await a.query(list, {})).toEqual([]);
  await expect(a.mutation(toggle, { id })).rejects.toThrow("Not found");
});
test("rejects blank/oversized titles, invalid date-only dates and forged ownership", async () => {
  const t = convexTest(schema, modules).withIdentity({ subject: "a" });
  for (const args of [{ title: " " }, { title: "x".repeat(501) }, { title: "x", dueDate: "2027-02-29" }, { title: "x", dueDate: "2026-01-01T00:00:00Z" }, { title: "x", ownerId: "victim" }])
    await expect(t.mutation(add, args)).rejects.toThrow();
});
