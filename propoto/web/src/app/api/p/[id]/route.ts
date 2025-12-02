import { fetchMutation, fetchQuery } from "convex/nextjs";
import { api } from "../../../../../convex/_generated/api";
import { Id } from "../../../../../convex/_generated/dataModel";
import { redirect } from "next/navigation";
import { NextRequest } from "next/server";

export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    const { id } = await params;
    const proposalId = id as Id<"proposals">;

    try {
        // 1. Track the view
        await fetchMutation(api.proposals.trackView, { id: proposalId });

        // 2. Get the proposal to find the destination URL
        const proposal = await fetchQuery(api.proposals.get, { id: proposalId });

        if (proposal && proposal.presentationUrl) {
            return redirect(proposal.presentationUrl);
        } else {
            // Fallback if no presentation URL or proposal not found
            // Redirect to a generic "not found" or the dashboard
            return redirect("/");
        }
    } catch (error) {
        console.error("Error tracking view or redirecting:", error);
        return redirect("/");
    }
}
