import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Create lead with audit logging
export const create = mutation({
    args: {
        companyName: v.string(),
        website: v.optional(v.string()),
        score: v.number(),
        status: v.string(),
        data: v.any(),
        orgId: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";

        const leadId = await ctx.db.insert("leads", {
            ...args,
            orgId,
            lastContactedAt: Date.now(),
        });

        // Audit log: lead.created
        await ctx.db.insert("audit_logs", {
            action: "lead.created",
            actorId: "system",
            details: {
                leadId,
                companyName: args.companyName,
                website: args.website,
                score: args.score,
                status: args.status,
            },
            orgId,
            timestamp: Date.now(),
        });

        return { id: leadId };
    },
});

// List leads
export const list = query({
    args: {
        orgId: v.optional(v.string()),
        status: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";

        let leads = await ctx.db
            .query("leads")
            .withIndex("by_org", (q) => q.eq("orgId", orgId))
            .order("desc")
            .collect();

        if (args.status) {
            leads = leads.filter((l) => l.status === args.status);
        }

        return leads;
    },
});

// Update lead status with audit logging
export const updateStatus = mutation({
    args: {
        id: v.id("leads"),
        status: v.string(),
        orgId: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";
        const lead = await ctx.db.get(args.id);
        const previousStatus = lead?.status;

        await ctx.db.patch(args.id, { 
            status: args.status,
            lastContactedAt: args.status === "contacted" ? Date.now() : undefined,
        });

        // Audit log: lead.status_updated
        await ctx.db.insert("audit_logs", {
            action: "lead.status_updated",
            actorId: "system",
            details: {
                leadId: args.id,
                companyName: lead?.companyName,
                previousStatus,
                newStatus: args.status,
            },
            orgId,
            timestamp: Date.now(),
        });

        return { success: true };
    },
});
