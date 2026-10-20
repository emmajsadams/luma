import { mutation, query, type QueryCtx } from "./_generated/server";
import { v } from "convex/values";
import type { Id } from "./_generated/dataModel";
async function owner(ctx: QueryCtx) {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) throw new Error("Unauthenticated");
  return identity.tokenIdentifier;
}
async function owned(ctx: QueryCtx, id: Id<"tasks">) {
  const identity = await owner(ctx);
  const task = await ctx.db.get(id);
  if (!task || task.owner !== identity) throw new Error("Not found");
  return task;
}
export const list = query({ args: {}, handler: async (ctx) => {
  const identity = await owner(ctx);
  return ctx.db.query("tasks").withIndex("by_owner", q => q.eq("owner", identity)).order("desc").collect();
}});
export const add = mutation({ args: { title: v.string(), dueDate: v.optional(v.string()) }, handler: async (ctx, args) => {
  const identity = await owner(ctx);
  const title = args.title.trim();
  if (!title || title.length > 500) throw new Error("Title must contain 1–500 characters");
  if (args.dueDate !== undefined && (!/^\d{4}-\d{2}-\d{2}$/.test(args.dueDate) || !Number.isFinite(Date.parse(args.dueDate)) || new Date(args.dueDate).toISOString().slice(0, 10) !== args.dueDate)) throw new Error("Invalid date-only due date");
  return ctx.db.insert("tasks", { owner: identity, title, done: false, ...(args.dueDate ? { dueDate: args.dueDate } : {}) });
}});
export const toggle = mutation({ args: { id: v.id("tasks") }, handler: async (ctx, { id }) => {
  const task = await owned(ctx, id);
  await ctx.db.patch(id, { done: !task.done });
}});
export const remove = mutation({ args: { id: v.id("tasks") }, handler: async (ctx, { id }) => {
  await owned(ctx, id);
  await ctx.db.delete(id);
}});
