import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Create a new proposal with audit logging
export const create = mutation({
    args: {
        prospectName: v.string(),
        prospectUrl: v.string(),
        painPoints: v.string(),
        content: v.any(), // The AI-generated proposal content
        presentationUrl: v.optional(v.string()),
        pdfUrl: v.optional(v.string()),
        pptxUrl: v.optional(v.string()),
        status: v.optional(v.string()),
        orgId: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";

        const timestamp = Date.now();
        const proposalId = await ctx.db.insert("proposals", {
            prospectName: args.prospectName,
            prospectUrl: args.prospectUrl,
            painPoints: args.painPoints,
            content: args.content,
            presentationUrl: args.presentationUrl,
            pdfUrl: args.pdfUrl,
            pptxUrl: args.pptxUrl,
            status: args.status || "draft",
            orgId,
            createdAt: timestamp,
            updatedAt: timestamp,
        });

        // Audit log: proposal.generated
        await ctx.db.insert("audit_logs", {
            action: "proposal.generated",
            actorId: "system",
            details: {
                proposalId,
                prospectName: args.prospectName,
                prospectUrl: args.prospectUrl,
                hasPresentationUrl: !!args.presentationUrl,
                hasPdfUrl: !!args.pdfUrl,
                hasPptxUrl: !!args.pptxUrl,
            },
            orgId,
            timestamp: Date.now(),
        });

        return { id: proposalId };
    },
});

// List all proposals for an org (most recent first)
export const list = query({
    args: {
        orgId: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";

        const proposals = await ctx.db
            .query("proposals")
            .withIndex("by_org", (q) => q.eq("orgId", orgId))
            .order("desc")
            .collect();

        return proposals;
    },
});

// Get a single proposal by ID
export const get = query({
    args: {
        id: v.id("proposals"),
    },
    handler: async (ctx, args) => {
        return await ctx.db.get(args.id);
    },
});

// Update proposal content/metadata
export const updateContent = mutation({
    args: {
        id: v.id("proposals"),
        content: v.any(),
        status: v.optional(v.string()),
        presentationUrl: v.optional(v.string()),
        pdfUrl: v.optional(v.string()),
        pptxUrl: v.optional(v.string()),
        orgId: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";
        const proposal = await ctx.db.get(args.id);

        if (!proposal || proposal.orgId !== orgId) {
            throw new Error("Proposal not found");
        }

        const patchData: Record<string, any> = {
            content: args.content,
            updatedAt: Date.now(),
        };

        if (args.status) {
            patchData.status = args.status;
        }
        if (args.presentationUrl !== undefined) {
            patchData.presentationUrl = args.presentationUrl;
        }
        if (args.pdfUrl !== undefined) {
            patchData.pdfUrl = args.pdfUrl;
        }
        if (args.pptxUrl !== undefined) {
            patchData.pptxUrl = args.pptxUrl;
        }

        await ctx.db.patch(args.id, patchData);

        await ctx.db.insert("audit_logs", {
            action: "proposal.updated",
            actorId: "system",
            details: {
                proposalId: args.id,
                hasPresentationUrl: !!args.presentationUrl,
                hasPdfUrl: !!args.pdfUrl,
                hasPptxUrl: !!args.pptxUrl,
            },
            orgId,
            timestamp: Date.now(),
        });

        return { success: true };
    },
});

// Update proposal status with audit logging
export const updateStatus = mutation({
    args: {
        id: v.id("proposals"),
        status: v.string(),
        orgId: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";
        const proposal = await ctx.db.get(args.id);
        const previousStatus = proposal?.status;

        await ctx.db.patch(args.id, { status: args.status });

        // Audit log: proposal.status_updated
        await ctx.db.insert("audit_logs", {
            action: "proposal.status_updated",
            actorId: "system",
            details: {
                proposalId: args.id,
                previousStatus,
                newStatus: args.status,
            },
            orgId,
            timestamp: Date.now(),
        });

        return { success: true };
    },
});

// Export proposal (for PDF/email tracking)
export const trackExport = mutation({
    args: {
        proposalId: v.id("proposals"),
        exportType: v.string(), // 'pdf' | 'email'
        orgId: v.optional(v.string()),
    },
    handler: async (ctx, args) => {
        const orgId = args.orgId || "demo-org-1";
        const proposal = await ctx.db.get(args.proposalId);

        // Audit log: proposal.exported
        await ctx.db.insert("audit_logs", {
            action: `proposal.exported.${args.exportType}`,
            actorId: "system",
            details: {
                proposalId: args.proposalId,
                prospectName: proposal?.prospectName,
                exportType: args.exportType,
            },
            orgId,
            timestamp: Date.now(),
        });

        return { success: true };
    },
});

// Track proposal view (analytics)
export const trackView = mutation({
    args: {
        id: v.id("proposals"),
    },
    handler: async (ctx, args) => {
        const proposal = await ctx.db.get(args.id);
        if (!proposal) return;

        const currentViews = proposal.views || 0;

        await ctx.db.patch(args.id, {
            views: currentViews + 1,
            lastViewedAt: Date.now(),
        });

        // Audit log: proposal.viewed
        // We don't log every single view to avoid spam, but we could if needed.
        // For now, let's just update the counter.

        return { success: true, views: currentViews + 1 };
    },
});
