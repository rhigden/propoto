"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useSidebar } from "@/lib/sidebar-context";
import {
    LayoutGrid,
    Sparkles,
    Wand2,
    Zap,
    Settings,
    FileText,
    Search
} from "lucide-react";


const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutGrid },
    { name: "Proposals", href: "/dashboard/proposals", icon: FileText }, // Added explicit Proposals link
    { name: "Knowledge", href: "/dashboard/knowledge", icon: Sparkles },
    { name: "Brand", href: "/dashboard/brand", icon: Wand2 },
    { name: "Sales", href: "/dashboard/sales", icon: Zap },
    { name: "Settings", href: "/dashboard/settings", icon: Settings },
];

export function Sidebar() {
    const pathname = usePathname();
    // Removed 'collapsed' usage for the thin rail design
    // The rail is always "collapsed" visually but functional

    return (
        <aside className="fixed left-0 top-0 bottom-0 w-[50px] z-50 bg-[#0a0a0a] border-r border-[#262626] flex flex-col items-center py-4">
            {/* Top Icons */}
            <div className="flex flex-col gap-4 w-full items-center">
                {navItems.slice(0, 5).map((item) => { // Main items
                    const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "w-10 h-10 flex items-center justify-center rounded-lg transition-all relative group",
                                isActive
                                    ? "text-[#ededed]" // Active: White icon, no background change (Cursor style)
                                    : "text-[#666] hover:text-[#ededed]"
                            )}
                            title={item.name}
                        >
                            {/* Active Border Line (Left) */}
                            {isActive && (
                                <div className="absolute left-0 top-2 bottom-2 w-[2px] bg-[#ededed] rounded-r-full" />
                            )}
                            
                            <item.icon className="w-6 h-6 stroke-[1.5]" /> 
                        </Link>
                    );
                })}
            </div>

            <div className="flex-1" />

            {/* Bottom Icons */}
            <div className="flex flex-col gap-4 w-full items-center pb-2">
                <Link
                    href="/dashboard/settings"
                    className={cn(
                        "w-10 h-10 flex items-center justify-center rounded-lg transition-all relative group",
                        pathname === '/dashboard/settings' ? "text-[#ededed]" : "text-[#666] hover:text-[#ededed]"
                    )}
                    title="Settings"
                >
                     {pathname === '/dashboard/settings' && (
                        <div className="absolute left-0 top-2 bottom-2 w-[2px] bg-[#ededed] rounded-r-full" />
                    )}
                    <Settings className="w-6 h-6 stroke-[1.5]" />
                </Link>
            </div>
        </aside>
    );
}
