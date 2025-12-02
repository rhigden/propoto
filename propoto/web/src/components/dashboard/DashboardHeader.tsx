'use client';

import Link from 'next/link';
import { cn } from '@/lib/utils';

interface Breadcrumb {
    label: string;
    href?: string;
}

interface DashboardHeaderProps {
    title: string;
    description?: string;
    breadcrumbs?: Breadcrumb[];
    actions?: React.ReactNode;
    kicker?: string;
    className?: string;
}

export function DashboardHeader({
    title,
    description,
    breadcrumbs,
    actions,
    kicker,
    className,
}: DashboardHeaderProps) {
    return (
        <div
            className={cn(
                "relative overflow-hidden rounded-3xl border border-white/5 bg-[#0b0b0f] px-8 py-10 shadow-[0_0_120px_rgba(59,130,246,0.08)] before:absolute before:inset-0 before:bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.4),_transparent_55%)] before:opacity-70 after:absolute after:-right-20 after:-top-20 after:h-64 after:w-64 after:rounded-full after:bg-[#3b82f6]/20 after:blur-3xl",
                className,
            )}
        >
            <div className="relative z-10 flex flex-col gap-6">
                {breadcrumbs && breadcrumbs.length > 0 && (
                    <div className="flex items-center text-xs uppercase tracking-[0.2em] text-[#9ca3af] gap-2">
                        {breadcrumbs.map((crumb, index) => (
                            <div key={`${crumb.label}-${index}`} className="flex items-center gap-2">
                                {index !== 0 && <span className="text-[#4b5563]">/</span>}
                                {crumb.href ? (
                                    <Link href={crumb.href} className="hover:text-white transition-colors">
                                        {crumb.label}
                                    </Link>
                                ) : (
                                    <span className="text-white/70">{crumb.label}</span>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div className="space-y-2">
                        {kicker && <p className="text-xs font-semibold text-[#4ade80] uppercase tracking-[0.2em]">{kicker}</p>}
                        <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-white">{title}</h1>
                        {description && <p className="text-sm text-[#a1a1aa] max-w-2xl">{description}</p>}
                    </div>
                    {actions && (
                        <div className="flex flex-wrap gap-3 justify-end">
                            {actions}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

