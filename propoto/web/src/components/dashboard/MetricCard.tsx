'use client';

import type { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MetricCardProps {
    label: string;
    value: string | number;
    icon: LucideIcon;
    helperText?: string;
    delta?: {
        value: string;
        positive?: boolean;
    };
    className?: string;
}

export function MetricCard({
    label,
    value,
    icon: Icon,
    helperText,
    delta,
    className,
}: MetricCardProps) {
    return (
        <div
            className={cn(
                "relative overflow-hidden rounded-2xl border border-white/5 bg-gradient-to-br from-[#11121a] to-[#08080c] p-5 shadow-[0_8px_40px_rgba(0,0,0,0.35)]",
                className
            )}
        >
            <div className="flex items-center justify-between">
                <p className="text-xs uppercase tracking-[0.3em] text-[#6b7280]">{label}</p>
                <div className="rounded-full bg-white/5 p-2 border border-white/10 text-white">
                    <Icon className="w-4 h-4" />
                </div>
            </div>
            <div className="mt-4 text-3xl font-semibold tracking-tight text-white">{value}</div>
            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                {helperText && <span className="text-[#9ca3af]">{helperText}</span>}
                {delta && (
                    <span
                        className={cn(
                            "rounded-full px-2 py-0.5 border text-[11px] uppercase tracking-wide",
                            delta.positive
                                ? "border-green-500/40 text-green-300 bg-green-500/5"
                                : "border-red-500/40 text-red-300 bg-red-500/5"
                        )}
                    >
                        {delta.value}
                    </span>
                )}
            </div>
        </div>
    );
}

