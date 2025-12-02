'use client';

import { useState, useCallback, useEffect } from 'react';
import { useMutation } from 'convex/react';
import type { Id } from '../../../convex/_generated/dataModel';
import { api } from '../../../convex/_generated/api';
import { CheckCircle2, ExternalLink, Download, Copy, Check, ArrowLeft, Zap, Pencil, Save, XCircle, Loader2, Info, Mail } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

interface PricingTier {
    name: string;
    price: string;
    features: string[];
}

interface ProposalData {
    executive_summary: string;
    current_situation: string;
    proposed_strategy: string;
    why_us: string;
    investment: PricingTier[];
    next_steps: string;
}

interface ProposalResultProps {
    data: ProposalData;
    presentationUrl?: string | null;
    pdfUrl?: string | null;
    pptxUrl?: string | null;
    prospectName?: string;
    prospectUrl?: string;
    proposalId?: Id<"proposals"> | null;
    status?: string;
    createdAt?: number;
    updatedAt?: number;
    onDataChange?: (data: ProposalData, meta?: { updatedAt?: number }) => void;
    onStatusChange?: (status: string, updatedAt?: number) => void;
    onReset: () => void;
}

const cloneProposalData = (proposal: ProposalData): ProposalData => ({
    ...proposal,
    investment: proposal.investment.map((tier) => ({
        ...tier,
        features: [...tier.features],
    })),
});

export function ProposalResult({
    data,
    presentationUrl,
    pdfUrl,
    pptxUrl,
    prospectName,
    prospectUrl,
    proposalId,
    status,
    createdAt,
    updatedAt,
    onDataChange,
    onStatusChange,
    onReset,
}: ProposalResultProps) {
    const [copied, setCopied] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [editableData, setEditableData] = useState<ProposalData>(() => cloneProposalData(data));
    const [saveState, setSaveState] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
    const updateProposal = useMutation(api.proposals.updateContent);
    const updateStatusMutation = useMutation(api.proposals.updateStatus);
    const trackExport = useMutation(api.proposals.trackExport);
    const [statusState, setStatusState] = useState(status || 'draft');
    const [statusUpdating, setStatusUpdating] = useState(false);
    const [downloadState, setDownloadState] = useState<'idle' | 'success' | 'error'>('idle');
    const [emailState, setEmailState] = useState<'idle' | 'sending' | 'success' | 'error'>('idle');

    useEffect(() => {
        setEditableData(cloneProposalData(data));
        setIsEditing(false);
        setSaveState('idle');
    }, [data]);

    useEffect(() => {
        setStatusState(status || 'draft');
    }, [status]);

    const formatRelativeTime = (timestamp?: number) => {
        if (!timestamp) return '—';
        const diffMs = Date.now() - timestamp;
        const minutes = Math.floor(diffMs / 60000);
        if (minutes < 1) return 'just now';
        if (minutes < 60) return `${minutes}m ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        const days = Math.floor(hours / 24);
        if (days < 7) return `${days}d ago`;
        return new Date(timestamp).toLocaleDateString();
    };

    const createdLabel = formatRelativeTime(createdAt);
    const updatedLabel = formatRelativeTime(updatedAt || createdAt);
    const statusBadgeClasses =
        statusState === 'sent'
            ? 'bg-green-500/10 text-green-300 border-green-500/30'
            : 'bg-[#1f2937] text-[#e5e7eb] border-[#374151]';

    const handleCopyToClipboard = useCallback(async () => {
        try {
            const textToCopy = proposalId
                ? `${window.location.origin}/api/p/${proposalId}`
                : JSON.stringify(editableData, null, 2);
            await navigator.clipboard.writeText(textToCopy);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error(err);
        }
    }, [editableData, proposalId]);

    const handleSectionChange = (field: keyof ProposalData, value: string) => {
        setEditableData((prev) => ({
            ...prev,
            [field]: value,
        }));
    };

    const handleTierFieldChange = (index: number, field: keyof PricingTier, value: string) => {
        setEditableData((prev) => {
            const updated = prev.investment.map((tier, tierIndex) => {
                if (tierIndex !== index) return tier;

                if (field === 'features') {
                    return {
                        ...tier,
                        features: value
                            .split('\n')
                            .map((feature) => feature.trim())
                            .filter(Boolean),
                    };
                }

                return {
                    ...tier,
                    [field]: value,
                };
            });

            return { ...prev, investment: updated };
        });
    };

    const handleCancelEdit = () => {
        setEditableData(cloneProposalData(data));
        setIsEditing(false);
        setSaveState('idle');
    };

    const handleSaveEdits = useCallback(async () => {
        if (!proposalId) return;
        setSaveState('saving');
        try {
            await updateProposal({
                id: proposalId,
                content: editableData,
            });
            setSaveState('success');
            setIsEditing(false);
            onDataChange?.(editableData, { updatedAt: Date.now() });
            setTimeout(() => setSaveState('idle'), 2500);
        } catch (error) {
            console.error(error);
            setSaveState('error');
            setTimeout(() => setSaveState('idle'), 3000);
        }
    }, [proposalId, editableData, updateProposal, onDataChange]);

    const handleStatusToggle = useCallback(async () => {
        if (!proposalId) return;
        const nextStatus = statusState === 'sent' ? 'draft' : 'sent';
        setStatusUpdating(true);
        try {
            await updateStatusMutation({
                id: proposalId,
                status: nextStatus,
            });
            const timestamp = Date.now();
            setStatusState(nextStatus);
            onStatusChange?.(nextStatus, timestamp);
        } catch (error) {
            console.error(error);
        } finally {
            setStatusUpdating(false);
        }
    }, [proposalId, statusState, updateStatusMutation, onStatusChange]);

    const handleDownload = useCallback(async () => {
        if (!proposalId || (!pdfUrl && !pptxUrl)) return;
        const targetUrl = pdfUrl || pptxUrl;
        const exportType = pdfUrl ? 'pdf' : 'pptx';
        try {
            window.open(targetUrl!, '_blank', 'noopener,noreferrer');
            await trackExport({
                proposalId,
                exportType,
            });
            setDownloadState('success');
            setTimeout(() => setDownloadState('idle'), 2000);
        } catch (error) {
            console.error(error);
            setDownloadState('error');
            setTimeout(() => setDownloadState('idle'), 3000);
        }
    }, [proposalId, pdfUrl, pptxUrl, trackExport]);

    const handleEmailExport = useCallback(async () => {
        if (!proposalId) return;
        setEmailState('sending');
        try {
            await trackExport({
                proposalId,
                exportType: 'email',
            });
            const subject = encodeURIComponent(`Proposal for ${prospectName ?? 'your prospect'}`);
            // Use tracking link if available, otherwise fallback to direct URL
            const trackingLink = proposalId ? `${window.location.origin}/api/p/${proposalId}` : (presentationUrl || pdfUrl || pptxUrl || '');
            const body = encodeURIComponent(
                `Hi,\n\nSharing the latest proposal.${trackingLink ? `\nDeck: ${trackingLink}\n` : '\n'}Let me know if you have any feedback.\n`
            );
            window.open(`mailto:?subject=${subject}&body=${body}`, '_blank');
            setEmailState('success');
            setTimeout(() => setEmailState('idle'), 2500);
        } catch (error) {
            console.error(error);
            setEmailState('error');
            setTimeout(() => setEmailState('idle'), 3000);
        }
    }, [proposalId, trackExport, prospectName, presentationUrl, pdfUrl, pptxUrl]);

    const renderTextValue = (text: string) => (
        <p className="text-base text-[#ededed] leading-relaxed whitespace-pre-wrap">{text}</p>
    );

    const editingDisabled = !proposalId;
    const statusButtonDisabled = !proposalId || statusUpdating;
    const downloadDisabled = !proposalId || (!pdfUrl && !pptxUrl);

    return (
        <div className="w-full h-full flex flex-col relative animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Top Action Bar */}
            <div className="sticky top-0 z-10 bg-[#0a0a0a]/80 backdrop-blur-md border-b border-[#262626] px-6 py-3 flex items-center justify-between gap-4 flex-wrap">
                <div className="flex items-center gap-4">
                    <button
                        onClick={onReset}
                        className="p-2 rounded-full hover:bg-[#262626] text-[#a1a1aa] hover:text-[#ededed] transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                    </button>
                    <div>
                        <h2 className="text-sm font-medium text-[#ededed]">{prospectName || 'New Proposal'}</h2>
                        <p className="text-xs text-[#a1a1aa]">{prospectUrl}</p>
                        <div className="flex flex-wrap items-center gap-2 mt-1">
                            <span className={`text-[10px] px-3 py-1 rounded-full border ${statusBadgeClasses}`}>
                                {statusState === 'sent' ? 'Sent' : 'Draft'}
                            </span>
                            <span className="text-[11px] text-[#a1a1aa]">Created {createdLabel}</span>
                            <span className="text-[11px] text-[#a1a1aa]">Updated {updatedLabel}</span>
                        </div>
                    </div>
                </div>

                <div className="flex flex-col items-end gap-2 w-full md:w-auto">
                    <div className="flex items-center gap-2 flex-wrap justify-end">
                        {presentationUrl && (
                            <a
                                href={presentationUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hidden md:flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-[#ededed] bg-[#262626] hover:bg-[#333] rounded-md border border-[#404040] transition-all"
                            >
                                <Zap className="w-3 h-3 text-purple-400" />
                                Open Deck
                            </a>
                        )}
                        <div className="h-4 w-px bg-[#262626] hidden md:block" />
                        <Button variant="ghost" size="icon" onClick={handleCopyToClipboard} className="h-8 w-8 text-[#a1a1aa] hover:text-[#ededed]">
                            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                        </Button>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={handleDownload}
                            disabled={downloadDisabled}
                            className="h-8 w-8 text-[#a1a1aa] hover:text-[#ededed] disabled:text-[#3f3f46]"
                        >
                            <Download className="w-4 h-4" />
                        </Button>
                        <Button
                            onClick={handleEmailExport}
                            disabled={!proposalId}
                            className="bg-[#ededed] text-black hover:bg-white text-xs font-medium px-4 h-8 rounded-md disabled:opacity-50"
                        >
                            <Mail className="w-3 h-3 mr-2" />
                            Email Draft
                        </Button>
                    </div>
                    {(downloadState !== 'idle' || emailState !== 'idle') && (
                        <div className="text-[11px] text-[#a1a1aa] flex flex-wrap gap-3 justify-end">
                            {downloadState === 'success' && <span className="text-green-400">Download logged</span>}
                            {downloadState === 'error' && <span className="text-red-400">Download failed</span>}
                            {emailState === 'success' && <span className="text-green-400">Email logged</span>}
                            {emailState === 'error' && <span className="text-red-400">Email logging failed</span>}
                            {emailState === 'sending' && <span>Logging email...</span>}
                        </div>
                    )}

                    <div className="flex items-center gap-2 flex-wrap justify-end">
                        {editingDisabled && (
                            <span className="text-[11px] uppercase tracking-wide text-[#a1a1aa] flex items-center gap-1">
                                <Info className="w-3 h-3" />
                                Syncing draft to enable edits...
                            </span>
                        )}
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleStatusToggle}
                            disabled={statusButtonDisabled}
                            className="text-xs font-medium bg-[#121212] border-[#333] text-[#ededed] hover:bg-[#1a1a1a]"
                        >
                            {statusUpdating ? (
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                                <CheckCircle2 className="w-4 h-4 mr-2" />
                            )}
                            {statusState === 'sent' ? 'Mark as Draft' : 'Mark as Sent'}
                        </Button>
                        {isEditing ? (
                            <>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={handleCancelEdit}
                                    className="text-xs text-[#a1a1aa] hover:text-[#ededed]"
                                >
                                    <XCircle className="w-4 h-4 mr-1" />
                                    Cancel
                                </Button>
                                <Button
                                    size="sm"
                                    onClick={handleSaveEdits}
                                    disabled={editingDisabled || saveState === 'saving'}
                                    className="bg-[#ededed] text-black hover:bg-white text-xs font-semibold"
                                >
                                    {saveState === 'saving' ? (
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    ) : (
                                        <Save className="w-4 h-4 mr-2" />
                                    )}
                                    Save changes
                                </Button>
                            </>
                        ) : (
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setIsEditing(true)}
                                disabled={editingDisabled}
                                className="text-xs font-medium bg-[#121212] border-[#333] text-[#ededed] hover:bg-[#1a1a1a]"
                            >
                                <Pencil className="w-4 h-4 mr-2" />
                                Edit
                            </Button>
                        )}
                        {saveState === 'success' && (
                            <span className="text-[11px] text-green-400 font-medium uppercase tracking-wide">Saved</span>
                        )}
                        {saveState === 'error' && (
                            <span className="text-[11px] text-red-400 font-medium uppercase tracking-wide">Save failed</span>
                        )}
                    </div>
                </div>
            </div>

            {/* Document Content */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
                <div className="max-w-3xl mx-auto py-12 px-8 space-y-12">
                    {/* Cover / Header */}
                    <div className="space-y-6 pb-8 border-b border-[#262626]">
                        <div className="space-y-2">
                            <h1 className="text-4xl font-bold text-[#ededed] tracking-tight">Strategic Proposal</h1>
                            <p className="text-xl text-[#a1a1aa] font-light">Prepared for {prospectName}</p>
                        </div>

                        {presentationUrl && (
                            <div className="mt-8 p-4 rounded-xl bg-[#121212] border border-[#262626] flex items-center justify-between group cursor-pointer hover:border-[#3b82f6] transition-all">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-900/50 to-blue-900/50 flex items-center justify-center border border-white/10">
                                        <ExternalLink className="w-5 h-5 text-white/80" />
                                    </div>
                                    <div>
                                        <div className="text-sm font-medium text-[#ededed]">Accompanying Presentation</div>
                                        <div className="text-xs text-[#a1a1aa]">View the visual deck generated for this proposal</div>
                                    </div>
                                </div>
                                <Button variant="ghost" className="text-xs text-[#3b82f6] opacity-0 group-hover:opacity-100 transition-opacity">
                                    Open in Gamma →
                                </Button>
                            </div>
                        )}
                    </div>

                    {/* Sections */}
                    <section className="space-y-3">
                        <div className="flex items-center justify-between">
                            <h3 className="text-sm font-medium text-[#a1a1aa] uppercase tracking-wider">Executive Summary</h3>
                        </div>
                        {isEditing ? (
                            <Textarea
                                value={editableData.executive_summary}
                                onChange={(e) => handleSectionChange('executive_summary', e.target.value)}
                                className="min-h-[140px] bg-[#0a0a0a] border border-[#262626] text-sm text-[#ededed]"
                            />
                        ) : (
                            renderTextValue(data.executive_summary)
                        )}
                    </section>

                    <section className="grid md:grid-cols-2 gap-8">
                        <div className="space-y-3">
                            <h3 className="text-sm font-medium text-[#a1a1aa] uppercase tracking-wider">Current State</h3>
                            {isEditing ? (
                                <Textarea
                                    value={editableData.current_situation}
                                    onChange={(e) => handleSectionChange('current_situation', e.target.value)}
                                    className="min-h-[200px] bg-[#0a0a0a] border border-[#262626] text-sm text-[#ededed]"
                                />
                            ) : (
                                <div className="p-4 rounded-lg bg-[#121212] border border-[#262626] text-sm text-[#ededed] leading-relaxed">
                                    {data.current_situation}
                                </div>
                            )}
                        </div>
                        <div className="space-y-3">
                            <h3 className="text-sm font-medium text-[#a1a1aa] uppercase tracking-wider">Proposed Strategy</h3>
                            {isEditing ? (
                                <Textarea
                                    value={editableData.proposed_strategy}
                                    onChange={(e) => handleSectionChange('proposed_strategy', e.target.value)}
                                    className="min-h-[200px] bg-[#0a0a0a] border border-[#262626] text-sm text-[#ededed]"
                                />
                            ) : (
                                <div className="p-4 rounded-lg bg-[#121212] border border-[#262626] text-sm text-[#ededed] leading-relaxed">
                                    {data.proposed_strategy}
                                </div>
                            )}
                        </div>
                    </section>

                    <section className="space-y-6">
                        <div className="flex items-center justify-between">
                            <h3 className="text-sm font-medium text-[#a1a1aa] uppercase tracking-wider">Investment Options</h3>
                            {isEditing && (
                                <span className="text-[11px] text-[#a1a1aa]">One tier per column • Features separated by new lines</span>
                            )}
                        </div>
                        <div className={`grid gap-4 ${isEditing ? 'md:grid-cols-1' : 'md:grid-cols-3'}`}>
                            {(isEditing ? editableData.investment : data.investment).map((tier, i) => (
                                <div key={i} className="flex flex-col p-5 rounded-xl border border-[#262626] bg-[#0a0a0a] gap-3">
                                    {isEditing ? (
                                        <>
                                            <Input
                                                value={tier.name}
                                                onChange={(e) => handleTierFieldChange(i, 'name', e.target.value)}
                                                placeholder="Tier name"
                                                className="bg-[#121212] border-[#262626] text-sm text-[#ededed]"
                                            />
                                            <Input
                                                value={tier.price}
                                                onChange={(e) => handleTierFieldChange(i, 'price', e.target.value)}
                                                placeholder="$X,XXX/mo"
                                                className="bg-[#121212] border-[#262626] text-sm text-[#ededed]"
                                            />
                                            <Textarea
                                                value={tier.features.join('\n')}
                                                onChange={(e) => handleTierFieldChange(i, 'features', e.target.value)}
                                                className="min-h-[140px] bg-[#121212] border-[#262626] text-sm text-[#ededed]"
                                                placeholder="Feature per line"
                                            />
                                        </>
                                    ) : (
                                        <>
                                            <div className="mb-4">
                                                <h4 className="font-medium text-[#ededed]">{tier.name}</h4>
                                                <div className="text-2xl font-semibold text-[#ededed] mt-1">{tier.price}</div>
                                            </div>
                                            <ul className="space-y-2 flex-1">
                                                {tier.features.map((feature, j) => (
                                                    <li key={j} className="text-xs text-[#a1a1aa] flex items-start gap-2">
                                                        <CheckCircle2 className="w-3 h-3 text-[#3b82f6] shrink-0 mt-0.5" />
                                                        <span>{feature}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </>
                                    )}
                                </div>
                            ))}
                        </div>
                    </section>

                    <section className="space-y-4 pt-8 border-t border-[#262626]">
                        <h3 className="text-sm font-medium text-[#a1a1aa] uppercase tracking-wider">Why Us & Next Steps</h3>
                        <div className="grid md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-xs text-[#a1a1aa] uppercase tracking-wider">Why Us</label>
                                {isEditing ? (
                                    <Textarea
                                        value={editableData.why_us}
                                        onChange={(e) => handleSectionChange('why_us', e.target.value)}
                                        className="min-h-[120px] bg-[#0a0a0a] border-[#262626] text-sm text-[#ededed]"
                                    />
                                ) : (
                                    <div className="text-sm text-[#ededed] leading-relaxed">{data.why_us}</div>
                                )}
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs text-[#a1a1aa] uppercase tracking-wider">Next Steps</label>
                                {isEditing ? (
                                    <Textarea
                                        value={editableData.next_steps}
                                        onChange={(e) => handleSectionChange('next_steps', e.target.value)}
                                        className="min-h-[120px] bg-[#0a0a0a] border-[#262626] text-sm text-[#ededed]"
                                    />
                                ) : (
                                    <div className="text-sm text-[#ededed] leading-relaxed font-medium">{data.next_steps}</div>
                                )}
                            </div>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
}
