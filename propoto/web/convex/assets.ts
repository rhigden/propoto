import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Create a new asset with audit logging
export const create = mutation({
    args: {
        type: v.string(), // 'presentation', 'document', 'webpage', 'image', 'pdf'
        url: v.string(),
        prompt: v.string(),
        status: v.optional(v.string()),
        orgId: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";

        const assetId = await ctx.db.insert("assets", {
            type: args.type,
            url: args.url,
            prompt: args.prompt,
            status: args.status || "ready",
            orgId,
            createdAt: Date.now(),
        });

        // Audit log: asset.created
        await ctx.db.insert("audit_logs", {
            action: "asset.created",
            actorId: "system",
            details: {
                assetId,
                type: args.type,
                prompt: args.prompt.substring(0, 100), // Truncate for log
            },
            orgId,
            timestamp: Date.now(),
        });

        return { id: assetId };
    },
});

// List all assets for an org
export const list = query({
    args: {
        orgId: v.optional(v.string()),
        type: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";

        let assets = await ctx.db
            .query("assets")
            .withIndex("by_org", (q) => q.eq("orgId", orgId))
            .order("desc")
            .collect();

        // Filter by type if specified
        if (args.type) {
            assets = assets.filter((a) => a.type === args.type);
        }

        return assets;
    },
});

// Get a single asset by ID
export const get = query({
    args: {
        id: v.id("assets"),
    },
    handler: async (ctx, args) => {
        return await ctx.db.get(args.id);
    },
});

// Update asset status
export const updateStatus = mutation({
    args: {
        id: v.id("assets"),
        status: v.string(),
    },
    handler: async (ctx, args) => {
        await ctx.db.patch(args.id, { status: args.status });
        return { success: true };
    },
});

