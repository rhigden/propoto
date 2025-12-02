import { cn } from "@/lib/utils";
import { ReactNode } from "react";

interface GlassCardProps {
    children: ReactNode;
    className?: string;
    hoverEffect?: boolean;
}

export function GlassCard({ children, className, hoverEffect = false }: GlassCardProps) {
    return (
        <div
            className={cn(
                "glass-panel rounded-xl p-6 transition-all duration-200",
                hoverEffect && "hover:bg-[#262626]/50 hover:border-[#3b82f6]/30",
                className
            )}
        >
            {children}
        </div>
    );
}

export function GlassHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
    return (
        <div className="flex justify-between items-start mb-6">
            <div>
                <h3 className="text-lg font-medium text-white tracking-tight">{title}</h3>
                {subtitle && <p className="text-sm text-[#a1a1aa] mt-1">{subtitle}</p>}
            </div>
            {action && <div>{action}</div>}
        </div>
    );
}
