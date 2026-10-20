import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";
export default defineSchema({
  tasks: defineTable({ owner: v.string(), title: v.string(), done: v.boolean(), dueDate: v.optional(v.string()) }).index("by_owner", ["owner"]),
});
