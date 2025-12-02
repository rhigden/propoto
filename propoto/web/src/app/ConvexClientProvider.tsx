"use client";

import { ReactNode } from "react";
import { ConvexReactClient, ConvexProvider } from "convex/react";

const convexUrl = process.env.NEXT_PUBLIC_CONVEX_URL || "https://placeholder.convex.cloud";
const convex = new ConvexReactClient(convexUrl);

// Clerk authentication disabled for MVP testing
// To enable Clerk, set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY,
// then uncomment the ClerkProvider and ConvexProviderWithClerk below

export default function ConvexClientProvider({
    children,
}: {
    children: ReactNode;
}) {
    // Simple Convex provider without Clerk for testing
    return (
        <ConvexProvider client={convex}>
            {children}
        </ConvexProvider>
    );
}

/* 
// Full implementation with Clerk authentication:
import { ConvexProviderWithClerk } from "convex/react-clerk";
import { ClerkProvider, useAuth } from "@clerk/nextjs";
import { dark } from "@clerk/themes";

export default function ConvexClientProvider({
    children,
}: {
    children: ReactNode;
}) {
    return (
        <ClerkProvider
            appearance={{
                baseTheme: dark,
                variables: {
                    colorPrimary: "#3b82f6",
                    colorBackground: "#0a0a0a",
                    colorInputBackground: "#1a1a1a",
                    colorText: "#ffffff",
                },
                elements: {
                    formButtonPrimary: "bg-blue-600 hover:bg-blue-700",
                    card: "bg-black/40 backdrop-blur-xl border border-white/10",
                }
            }}
        >
            <ConvexProviderWithClerk client={convex} useAuth={useAuth}>
                {children}
            </ConvexProviderWithClerk>
        </ClerkProvider>
    );
}
*/
