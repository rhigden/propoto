import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Create knowledge entry with audit logging
export const create = mutation({
    args: {
        summary: v.string(),
        entities: v.any(),
        relevance_score: v.number(),
        url: v.optional(v.string()),
        orgId: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";

        const knowledgeId = await ctx.db.insert("knowledge", {
            ...args,
            orgId,
            url: args.url || "",
            ingestedAt: Date.now(),
        });

        // Audit log: knowledge.ingested
        await ctx.db.insert("audit_logs", {
            action: "knowledge.ingested",
            actorId: "system",
            details: {
                knowledgeId,
                url: args.url,
                entityCount: Array.isArray(args.entities) ? args.entities.length : 0,
                relevanceScore: args.relevance_score,
            },
            orgId,
            timestamp: Date.now(),
        });

        return { id: knowledgeId };
    },
});

// List knowledge entries
export const list = query({
    args: {
        orgId: v.optional(v.string()),
        limit: v.optional(v.number()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";
        const limit = args.limit || 50;

        const knowledge = await ctx.db
            .query("knowledge")
            .withIndex("by_org", (q) => q.eq("orgId", orgId))
            .order("desc")
            .take(limit);

        return knowledge;
    },
});
