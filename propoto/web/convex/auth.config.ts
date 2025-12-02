// Clerk auth disabled for MVP - CLERK_JWT_ISSUER_DOMAIN set to empty string
// To enable Clerk, set CLERK_JWT_ISSUER_DOMAIN to your Clerk domain in Convex dashboard
export default {
    providers: process.env.CLERK_JWT_ISSUER_DOMAIN
        ? [
              {
                  domain: process.env.CLERK_JWT_ISSUER_DOMAIN,
                  applicationID: "convex",
              },
          ]
        : [],
};
