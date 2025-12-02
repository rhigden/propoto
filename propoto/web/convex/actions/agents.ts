"use node";
import { action } from "../_generated/server";
import { v } from "convex/values";

export const callAgentService = action({
    args: {
        agent: v.string(), // "knowledge" or "brand"
        action: v.string(), // "ingest" or "generate"
        payload: v.any(),
        orgId: v.string(),
    },
    handler: async (ctx, args) => {
        // 1. Validate Org (TODO: Check if user belongs to org)
        console.log(`Calling Agent Service: ${args.agent}/${args.action} for Org ${args.orgId}`);

        // 2. Determine Endpoint
        const serviceUrl = process.env.PYTHON_SERVICE_URL;
        if (!serviceUrl) {
            throw new Error("PYTHON_SERVICE_URL not set");
        }

        const endpoint = `${serviceUrl}/agents/${args.agent}/${args.action}`;

        // 3. Call Python Service
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "x-api-key": process.env.AGENT_SERVICE_KEY || "dev-secret-key",
            },
            body: JSON.stringify(args.payload),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Agent Service Error: ${response.status} - ${errorText}`);
        }

        const result = await response.json();
        return result;
    },
});
