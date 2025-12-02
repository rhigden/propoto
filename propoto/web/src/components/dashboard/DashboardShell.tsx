'use client';

import type { ReactNode } from "react";
import { Sidebar } from "@/components/Sidebar";
import { cn } from "@/lib/utils";

const GRID_OVERLAY_CLASS =
    "bg-[url('data:image/svg+xml,%3Csvg width=\"400\" height=\"400\" viewBox=\"0 0 400 400\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cdefs%3E%3Cpattern id=\"grid\" width=\"40\" height=\"40\" patternUnits=\"userSpaceOnUse\"%3E%3Cpath d=\"M 40 0 L 0 0 0 40\" fill=\"none\" stroke=\"white\" stroke-width=\"0.5\" opacity=\"0.4\"/%3E%3C/pattern%3E%3C/defs%3E%3Crect width=\"400\" height=\"400\" fill=\"url(%23grid)\"/%3E%3C/svg%3E')]";

export function DashboardShell({
    children,
}: {
    children: ReactNode;
}) {
    return (
        <div className="min-h-screen bg-[#050507] font-sans antialiased text-[#ededed]">
            <div className="pointer-events-none fixed inset-0 z-0">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.25),_transparent_55%)]" />
                <div className={cn("absolute inset-0 opacity-[0.03]", GRID_OVERLAY_CLASS)} />
            </div>
            <Sidebar />
            <div className="pl-[50px] flex h-screen overflow-hidden relative z-10">
                <main className="flex-1 overflow-y-auto relative">
                    <div className="max-w-[1600px] mx-auto px-6 sm:px-8 py-12 space-y-10">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}
