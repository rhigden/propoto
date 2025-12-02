import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Log an action for audit purposes
export const log = mutation({
    args: {
        action: v.string(), // e.g., 'proposal.generated', 'lead.created', 'knowledge.ingested'
        actorId: v.optional(v.string()), // User ID or 'system'
        details: v.any(), // JSON details about the action
        orgId: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";

        const logId = await ctx.db.insert("audit_logs", {
            action: args.action,
            actorId: args.actorId || "system",
            details: args.details,
            orgId,
            timestamp: Date.now(),
        });

        return { id: logId };
    },
});

// List recent audit logs
export const list = query({
    args: {
        orgId: v.optional(v.string()),
        limit: v.optional(v.number()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";
        const limit = args.limit || 50;

        const logs = await ctx.db
            .query("audit_logs")
            .withIndex("by_org", (q) => q.eq("orgId", orgId))
            .order("desc")
            .take(limit);

        return logs;
    },
});

// Get logs by action type
export const getByAction = query({
    args: {
        action: v.string(),
        orgId: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";

        const allLogs = await ctx.db
            .query("audit_logs")
            .withIndex("by_org", (q) => q.eq("orgId", orgId))
            .collect();

        return allLogs.filter((log) => log.action === args.action);
    },
});

