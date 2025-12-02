import { query } from "./_generated/server";
import { auth } from "./auth";

export const viewer = query({
    args: {},
    handler: async (ctx) => {
        const tokenIdentifier = await auth.getUserId(ctx);
        if (!tokenIdentifier) {
            return null;
        }
        const user = await ctx.db
            .query("users")
            .withIndex("by_token", (q) => q.eq("tokenIdentifier", tokenIdentifier))
            .unique();
        return user;
    },
});
