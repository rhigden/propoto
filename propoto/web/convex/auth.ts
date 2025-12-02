import { Auth } from "convex/server";
import { Id } from "./_generated/dataModel";

export const auth = {
    getUserId: async (ctx: { auth: Auth }) => {
        const identity = await ctx.auth.getUserIdentity();
        if (!identity) {
            return null;
        }
        // In a real app, we would look up the user in the 'users' table by tokenIdentifier
        // For now, just return the tokenIdentifier as a proxy or null
        return identity.tokenIdentifier;
    },
};
