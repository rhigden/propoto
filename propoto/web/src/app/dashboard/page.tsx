'use client';

import { useEffect, useMemo, useState, type ComponentProps } from 'react';
import { useQuery } from 'convex/react';
import { api } from '../../../convex/_generated/api';
import type { Doc, Id } from '../../../convex/_generated/dataModel';
import { ProposalForm } from '@/components/dashboard/ProposalForm';
import { ProposalResult } from '@/components/dashboard/ProposalResult';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { Button } from '@/components/ui/button';
import { FileText, Clock, CheckCircle, Activity, Search, Plus, Filter, BadgeCheck, ArrowUpRight } from 'lucide-react';
import { cn } from "@/lib/utils";

type ProposalDoc = Doc<"proposals">;

interface PricingTier {
    name: string;
    price: string;
    features: string[];
}

interface ProposalContent {
    executive_summary: string;
    current_situation: string;
    proposed_strategy: string;
    why_us: string;
    investment: PricingTier[];
    next_steps: string;
}

interface ResultData {
    data: ProposalContent;
    presentation_url?: string | null;
    pdf_url?: string | null;
    pptx_url?: string | null;
    prospect_name?: string;
    prospect_url?: string;
    pain_points?: string;
    generated_at?: number;
    status?: string;
    created_at?: number;
    updated_at?: number;
}

interface PendingMatch {
    prospectName: string;
    prospectUrl: string;
    painPoints?: string;
    generatedAt: number;
}

type StatusFilter = 'all' | 'draft' | 'sent';

export default function DashboardPage() {
    const [viewState, setViewState] = useState<'list' | 'create' | 'result'>('list');
    const [resultData, setResultData] = useState<ResultData | null>(null);
    const [selectedProposal, setSelectedProposal] = useState<ProposalDoc | null>(null);
    const [activeProposalId, setActiveProposalId] = useState<Id<"proposals"> | null>(null);
    const [pendingMatch, setPendingMatch] = useState<PendingMatch | null>(null);
    const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
    const [searchTerm, setSearchTerm] = useState('');
    
    const proposals = useQuery(api.proposals.list, {}) as ProposalDoc[] | undefined;

    const totalProposals = proposals?.length || 0;
    const sentProposals = proposals?.filter((p: ProposalDoc) => p.status === 'sent')?.length || 0;
    const successRate = totalProposals > 0 ? Math.round((sentProposals / totalProposals) * 100) : 0;

    const filteredProposals = useMemo(() => {
        if (!proposals) return [];
        return proposals.filter((proposal) => {
            const matchesStatus = statusFilter === 'all' ? true : proposal.status === statusFilter;
            const query = searchTerm.toLowerCase().trim();
            const matchesQuery = query.length === 0
                ? true
                : proposal.prospectName.toLowerCase().includes(query) ||
                    proposal.prospectUrl.toLowerCase().includes(query);
            return matchesStatus && matchesQuery;
        });
    }, [proposals, statusFilter, searchTerm]);

    const handleStartCreate = () => {
        setViewState('create');
        setActiveProposalId(null);
        setSelectedProposal(null);
        setResultData(null);
        setPendingMatch(null);
    };

    const handleSelectProposal = (proposal: ProposalDoc) => {
        setSelectedProposal(proposal);
        setResultData({
            data: proposal.content as ProposalContent,
            presentation_url: proposal.presentationUrl,
            pdf_url: proposal.pdfUrl,
            pptx_url: proposal.pptxUrl,
            prospect_name: proposal.prospectName,
            prospect_url: proposal.prospectUrl,
            pain_points: proposal.painPoints,
            status: proposal.status,
            created_at: proposal.createdAt,
            updated_at: proposal.updatedAt,
        });
        setPendingMatch(null);
        setActiveProposalId(proposal._id);
        setViewState('result');
    };

    const handleCreateSuccess = (data: ResultData) => {
        const generatedAt = data.generated_at || Date.now();
        const normalizedResult: ResultData = {
            ...data,
            status: data.status || 'draft',
            created_at: data.created_at || generatedAt,
            updated_at: data.updated_at || generatedAt,
        };
        setResultData(normalizedResult);
        setSelectedProposal(null);
        setActiveProposalId(null);
        setPendingMatch({
            prospectName: data.prospect_name || '',
            prospectUrl: data.prospect_url || '',
            painPoints: data.pain_points || '',
            generatedAt,
        });
        setViewState('result');
    };

    const handleReset = () => {
        setViewState('list');
        setSelectedProposal(null);
        setResultData(null);
        setPendingMatch(null);
        setActiveProposalId(null);
    };

    const handleResultDataUpdate = (updatedContent: ProposalContent, meta?: { updatedAt?: number }) => {
        setResultData((prev) => prev ? {
            ...prev,
            data: updatedContent,
            updated_at: meta?.updatedAt ?? prev.updated_at,
        } : prev);
        setSelectedProposal((prev) => prev ? {
            ...prev,
            content: updatedContent,
            updatedAt: meta?.updatedAt ?? prev.updatedAt,
        } as ProposalDoc : prev);
    };

    const handleStatusChange = (status: string, updatedAt?: number) => {
        setResultData((prev) => prev ? {
            ...prev,
            status,
            updated_at: updatedAt ?? prev.updated_at,
        } : prev);
        setSelectedProposal((prev) => prev ? {
            ...prev,
            status,
            updatedAt: updatedAt ?? prev.updatedAt,
        } as ProposalDoc : prev);
    };

    const formatDate = (timestamp: number) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        
        if (days === 0) return 'Today';
        if (days === 1) return 'Yesterday';
        if (days < 7) return `${days} days ago`;
        return date.toLocaleDateString();
    };

    useEffect(() => {
        if (selectedProposal) {
            if (activeProposalId !== selectedProposal._id) {
                setActiveProposalId(selectedProposal._id);
            }
            return;
        }

        if (viewState !== 'result') {
            if (activeProposalId !== null) {
                setActiveProposalId(null);
            }
            return;
        }

        if (!pendingMatch || !proposals?.length) {
            return;
        }

        const candidates = proposals.filter((proposal) => {
            if (proposal.prospectName !== pendingMatch.prospectName) return false;
            if (proposal.prospectUrl !== pendingMatch.prospectUrl) return false;
            if (pendingMatch.painPoints && proposal.painPoints !== pendingMatch.painPoints) return false;
            return true;
        });

        if (!candidates.length) {
            return;
        }

        const latest = candidates.reduce((acc, proposal) =>
            proposal.createdAt > acc.createdAt ? proposal : acc
        );

        const withinWindow = Math.abs(latest.createdAt - pendingMatch.generatedAt) < 5 * 60 * 1000;

        if (withinWindow) {
            if (activeProposalId !== latest._id) {
                setActiveProposalId(latest._id);
            }
            setSelectedProposal(latest);
            setResultData((prev) => prev ? {
                ...prev,
                status: latest.status,
                created_at: latest.createdAt,
                updated_at: latest.updatedAt,
            } : prev);
            setPendingMatch(null);
        }
    }, [selectedProposal, proposals, pendingMatch, viewState, activeProposalId]);

    const statusOptions: { label: string; value: StatusFilter }[] = [
        { label: 'All', value: 'all' },
        { label: 'Drafts', value: 'draft' },
        { label: 'Sent', value: 'sent' },
    ];

    const visibleProposals = filteredProposals.slice(0, 12);

    // View: Result / Document Mode
    if (viewState === 'result' && resultData) {
        return (
            <div className="fixed inset-0 top-0 left-[calc(5rem+16px)] right-0 bottom-0 z-50 bg-[#0a0a0a] animate-in fade-in zoom-in-95 duration-300">
                <ProposalResult
                    data={resultData.data}
                    presentationUrl={resultData.presentation_url}
                    pdfUrl={resultData.pdf_url}
                    pptxUrl={resultData.pptx_url}
                    prospectName={resultData.prospect_name || selectedProposal?.prospectName}
                    prospectUrl={resultData.prospect_url || selectedProposal?.prospectUrl}
                    status={resultData.status || selectedProposal?.status}
                    createdAt={resultData.created_at || selectedProposal?.createdAt}
                    updatedAt={resultData.updated_at || selectedProposal?.updatedAt}
                    proposalId={activeProposalId}
                    onDataChange={handleResultDataUpdate}
                    onStatusChange={handleStatusChange}
                    onReset={handleReset}
                />
            </div>
        );
    }

    // View: Create Mode
    if (viewState === 'create') {
        return (
            <div className="space-y-8">
                <DashboardHeader
                    title="Compose a new proposal"
                    description="Drop in the prospect URL to pull research, then guide the narrative before sending."
                    breadcrumbs={[
                        { label: 'Dashboard', href: '/dashboard' },
                        { label: 'Proposals', href: '/dashboard' },
                        { label: 'New Draft' },
                    ]}
                    actions={
                        <Button variant="ghost" onClick={handleReset} className="text-[#a1a1aa] hover:text-white">
                            Back to overview
                        </Button>
                    }
                />
                <div className="rounded-3xl border border-white/5 bg-[#0c0d12]/80 backdrop-blur-xl p-6 lg:p-10 shadow-[0_30px_120px_rgba(0,0,0,0.45)]">
                    <ProposalForm onSuccess={handleCreateSuccess} />
                </div>
            </div>
        );
    }

    // View: List Mode (Dashboard)
    return (
        <div className="space-y-8">
            <DashboardHeader
                kicker="Command center"
                title="Proposals"
                description="Track velocity, tune drafts, and jump back into active deals from a single pane inspired by Cursor’s calm rail."
                breadcrumbs={[
                    { label: 'Dashboard', href: '/dashboard' },
                    { label: 'Proposals' },
                ]}
                actions={
                    <>
                        <Button
                            variant="ghost"
                            className="border border-white/10 bg-white/5 text-[#e2e8f0]"
                            onClick={() => window.open('https://cursor.sh', '_blank')}
                        >
                            <ArrowUpRight className="w-4 h-4 mr-2" />
                            Inspiration
                        </Button>
                        <Button
                            onClick={handleStartCreate}
                            className="bg-white text-black hover:bg-white/90 px-5"
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            New Proposal
                        </Button>
                    </>
                }
            />

            <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
                <section className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <MetricCard
                            label="Total generated"
                            value={totalProposals}
                            icon={FileText}
                            helperText="All-time"
                            delta={{ value: '+12% vs last week', positive: true }}
                        />
                        <MetricCard
                            label="Sent to client"
                            value={sentProposals}
                            icon={CheckCircle}
                            helperText="Ready for follow-up"
                        />
                        <MetricCard
                            label="Close rate"
                            value={`${successRate}%`}
                            icon={Activity}
                            helperText="Rolling 30 days"
                        />
                    </div>

                    <div className="rounded-3xl border border-white/5 bg-[#0b0c12]/80 backdrop-blur-xl shadow-[0_40px_120px_rgba(0,0,0,0.45)]">
                        <div className="flex flex-col gap-4 border-b border-white/5 px-6 py-5 lg:flex-row lg:items-center lg:justify-between">
                            <div>
                                <p className="text-xs uppercase tracking-[0.3em] text-[#6b7280]">Pipeline</p>
                                <h3 className="text-lg font-semibold text-white">Recent history</h3>
                            </div>
                            <div className="flex flex-wrap items-center gap-3">
                                <div className="relative">
                                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#4b5563]" />
                                    <input
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        placeholder="Search prospect"
                                        className="bg-[#050506] border border-white/10 rounded-full pl-10 pr-4 py-2 text-sm text-white placeholder:text-[#6b7280] focus:outline-none focus:border-[#3b82f6]"
                                    />
                                </div>
                                <div className="flex items-center gap-2">
                                    {statusOptions.map((option) => (
                                        <button
                                            key={option.value}
                                            onClick={() => setStatusFilter(option.value)}
                                            className={cn(
                                                "rounded-full px-3 py-1 text-xs font-medium uppercase tracking-wide transition-all border",
                                                statusFilter === option.value
                                                    ? "border-[#3b82f6] bg-[#1e1f2b]"
                                                    : "border-white/10 text-[#94a3b8] hover:text-white"
                                            )}
                                        >
                                            {option.label}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                        <div className="divide-y divide-white/5">
                            {visibleProposals.length > 0 ? (
                                visibleProposals.map((proposal) => (
                                    <button
                                        key={proposal._id}
                                        onClick={() => handleSelectProposal(proposal)}
                                        className="w-full px-6 py-4 flex flex-col gap-3 text-left hover:bg-white/2 transition-colors lg:flex-row lg:items-center lg:justify-between"
                                    >
                                        <div className="flex items-start gap-4 min-w-0">
                                            <div className="w-10 h-10 rounded-2xl border border-white/10 bg-white/5 flex items-center justify-center text-white/80">
                                                <FileText className="w-4 h-4" />
                                            </div>
                                            <div className="min-w-0">
                                                <p className="text-sm font-medium text-white truncate flex items-center gap-2">
                                                    {proposal.prospectName}
                                                    {proposal.status === 'sent' && (
                                                        <BadgeCheck className="w-4 h-4 text-green-400" />
                                                    )}
                                                </p>
                                                <p className="text-xs text-[#9ca3af] truncate">{proposal.prospectUrl}</p>
                                            </div>
                                        </div>
                                        <div className="flex flex-wrap items-center gap-3">
                                            <span
                                                className={cn(
                                                    "text-[11px] px-3 py-1 rounded-full border uppercase tracking-wide",
                                                    proposal.status === 'sent'
                                                        ? "border-green-500/40 text-green-300 bg-green-500/5"
                                                        : "border-white/10 text-[#cbd5f5] bg-white/5"
                                                )}
                                            >
                                                {proposal.status}
                                            </span>
                                            <span className="text-xs text-[#6b7280]">{formatDate(proposal.createdAt)}</span>
                                        </div>
                                    </button>
                                ))
                            ) : (
                                <div className="px-6 py-16 text-center text-[#6b7280] space-y-2">
                                    <Filter className="w-5 h-5 mx-auto text-[#4b5563]" />
                                    <p className="text-sm">No proposals match the current filters.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </section>

                <section className="space-y-6 xl:sticky xl:top-8">
                    <div className="rounded-3xl border border-white/5 bg-gradient-to-br from-[#11121f] via-[#0a0c16] to-[#07070c] p-6 shadow-[0_40px_120px_rgba(0,0,0,0.55)]">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-xs uppercase tracking-[0.3em] text-[#64748b]">Quick compose</p>
                                <h3 className="text-xl font-semibold text-white mt-2">Start a fresh draft</h3>
                                <p className="text-sm text-[#94a3b8] mt-2">
                                    Pull context, set tone, and handoff to the editor in seconds.
                                </p>
                            </div>
                        </div>
                        <div className="mt-6 grid gap-3">
                            <Button
                                onClick={handleStartCreate}
                                className="w-full bg-white text-black hover:bg-white/90 py-6 justify-center"
                            >
                                <SparkleIcon className="w-4 h-4 mr-2" />
                                Open Composer
                            </Button>
                            <Button
                                variant="outline"
                                className="w-full border-white/15 bg-white/5 hover:bg-white/10 text-white"
                                onClick={() => setStatusFilter('draft')}
                            >
                                Jump to drafts
                            </Button>
                        </div>
                        <div className="mt-6 rounded-2xl border border-white/5 bg-black/20 p-4 text-sm text-[#94a3b8] space-y-3">
                            <div className="flex items-center gap-2 text-white">
                                <Clock className="w-4 h-4 text-[#3b82f6]" />
                                <span className="text-xs uppercase tracking-[0.3em] text-[#6b7280]">activity</span>
                            </div>
                            <ul className="space-y-3">
                                {filteredProposals.slice(0, 3).map((proposal) => (
                                    <li key={`activity-${proposal._id}`} className="flex items-center justify-between text-xs">
                                        <div className="text-[#e5e7eb] truncate">{proposal.prospectName}</div>
                                        <span className="text-[#6b7280]">{formatDate(proposal.createdAt)}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    <div className="rounded-3xl border border-white/5 bg-[#0d0f18]/90 backdrop-blur-xl p-6 space-y-4 shadow-[0_30px_120px_rgba(0,0,0,0.45)]">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-xs uppercase tracking-[0.3em] text-[#6b7280]">Insights</p>
                                <h3 className="text-base font-semibold text-white mt-1">Pipeline balance</h3>
                            </div>
                        </div>
                        <div className="space-y-3 text-sm text-[#94a3b8]">
                            <div className="flex items-center justify-between">
                                <span>Drafts</span>
                                <span className="font-medium text-white">{totalProposals - sentProposals}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span>Sent</span>
                                <span className="font-medium text-white">{sentProposals}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span>Win rate</span>
                                <span className="font-medium text-white">{successRate}%</span>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
}

function SparkleIcon(props: ComponentProps<'svg'>) {
    return (
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" {...props}>
            <path d="M12 2l1.5 4.5L18 8l-4.5 1.5L12 14l-1.5-4.5L6 8l4.5-1.5L12 2zm6 8l1 3 3 1-3 1-1 3-1-3-3-1 3-1 1-3zm-12 0l1 3 3 1-3 1-1 3-1-3-3-1 3-1 1-3z" />
        </svg>
    );
}
