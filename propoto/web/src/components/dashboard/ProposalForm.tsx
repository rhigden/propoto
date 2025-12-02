'use client';

import { useState, useTransition, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Loader2, Sparkles, Cpu, Palette, Globe, Settings2, Zap, ChevronRight } from 'lucide-react';
import { generateProposalAction, getAvailableModels, getAvailableTemplates } from '@/app/actions';
import { cn } from "@/lib/utils";

interface ProposalFormProps {
    onSuccess: (data: any) => void;
}

interface ModelOption {
    key: string;
    name: string;
}

interface TemplateOption {
    key: string;
    name: string;
    description: string;
    tone: string;
}

// Loading skeleton shown during proposal generation
function ProposalSkeleton({ deepScrape = false }: { deepScrape?: boolean }) {
    const steps = deepScrape 
        ? [
            { icon: Globe, label: 'Analyzing', delay: '0ms' },
            { icon: Cpu, label: 'Reasoning', delay: '300ms' },
            { icon: Palette, label: 'Designing', delay: '600ms' },
        ]
        : [
            { icon: Cpu, label: 'Reasoning', delay: '0ms' },
            { icon: Palette, label: 'Designing', delay: '300ms' },
        ];

    return (
        <div className="w-full max-w-3xl mx-auto mt-20 space-y-8 animate-in fade-in duration-500">
            <div className="text-center space-y-2">
                <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-[#121212] border border-[#262626] shadow-2xl">
                    <Loader2 className="w-6 h-6 text-[#3b82f6] animate-spin" />
                </div>
                <h3 className="text-lg font-medium text-[#ededed]">Generating Proposal...</h3>
                <p className="text-sm text-[#a1a1aa]">{deepScrape ? 'Analyzing website intelligence & crafting strategy' : 'Crafting a personalized strategy'}</p>
            </div>

            <div className="grid grid-cols-3 gap-4">
                {steps.map((step, i) => (
                    <div key={i} className="flex flex-col items-center gap-3 p-4 rounded-xl bg-[#121212] border border-[#262626]" style={{ animationDelay: step.delay }}>
                        <step.icon className="w-5 h-5 text-[#3b82f6] animate-pulse" />
                        <span className="text-xs font-medium text-[#a1a1aa]">{step.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

export function ProposalForm({ onSuccess }: ProposalFormProps) {
    const [isPending, startTransition] = useTransition();
    const [error, setError] = useState<string | null>(null);
    const [showSettings, setShowSettings] = useState(false);
    
    // Inputs
    const [prospectName, setProspectName] = useState('');
    const [prospectUrl, setProspectUrl] = useState('');
    const [painPoints, setPainPoints] = useState('');
    
    // Options
    const [models, setModels] = useState<ModelOption[]>([]);
    const [templates, setTemplates] = useState<TemplateOption[]>([]);
    const [selectedModel, setSelectedModel] = useState<string>('');
    const [selectedTemplate, setSelectedTemplate] = useState<string>('default');
    const [deepScrape, setDeepScrape] = useState(false);

    // Load models and templates on mount
    useEffect(() => {
        async function loadOptions() {
            const [modelsData, templatesData] = await Promise.all([
                getAvailableModels(),
                getAvailableTemplates()
            ]);
            
            if (modelsData.models.length > 0) {
                setModels(modelsData.models);
                setSelectedModel(modelsData.default || modelsData.models[0].key);
            }
            
            if (templatesData.templates.length > 0) {
                setTemplates(templatesData.templates);
            }
        }
        loadOptions();
    }, []);

    const handleSubmit = () => {
        if (!prospectName || !prospectUrl || !painPoints) return;
        
        setError(null);
        const data = {
            prospect_name: prospectName,
            prospect_url: prospectUrl,
            pain_points: painPoints,
            model: selectedModel || undefined,
            template: selectedTemplate || undefined,
            deep_scrape: deepScrape,
        };

        startTransition(async () => {
            try {
                const result = await generateProposalAction(data);
                if (result.success) {
                    onSuccess({
                        ...result,
                        prospect_name: data.prospect_name,
                        prospect_url: data.prospect_url,
                        pain_points: data.pain_points,
                        generated_at: Date.now(),
                    });
                } else {
                    setError('Failed to generate proposal. Please try again.');
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'An unexpected error occurred');
            }
        });
    };

    if (isPending) {
        return <ProposalSkeleton deepScrape={deepScrape} />;
    }

    return (
        <div className="w-full max-w-3xl mx-auto mt-12">
            <div className="space-y-8">
                {/* Main Input Flow */}
                <div className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-[#a1a1aa] ml-1">Project Title</label>
                        <input
                            type="text"
                            value={prospectName}
                            onChange={(e) => setProspectName(e.target.value)}
                            placeholder="Proposal for Acme Corp..."
                            className="w-full bg-transparent text-4xl font-semibold text-[#ededed] placeholder-[#262626] border-none focus:ring-0 p-0 tracking-tight"
                            autoFocus
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-[#a1a1aa] uppercase tracking-wider ml-1">Target URL</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                                    <Globe className="w-4 h-4 text-[#525252] group-focus-within:text-[#3b82f6] transition-colors" />
                                </div>
                                <input
                                    type="url"
                                    value={prospectUrl}
                                    onChange={(e) => setProspectUrl(e.target.value)}
                                    placeholder="https://example.com"
                                    className="w-full bg-[#121212] border border-[#262626] rounded-xl py-3 pl-10 pr-4 text-sm text-[#ededed] placeholder-[#525252] focus:border-[#3b82f6] focus:ring-1 focus:ring-[#3b82f6] transition-all"
                                />
                            </div>
                        </div>
                        
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-[#a1a1aa] uppercase tracking-wider ml-1">Context / Pain Points</label>
                            <textarea
                                value={painPoints}
                                onChange={(e) => setPainPoints(e.target.value)}
                                placeholder="e.g. Low conversion, outdated brand..."
                                className="w-full bg-[#121212] border border-[#262626] rounded-xl py-3 px-4 text-sm text-[#ededed] placeholder-[#525252] focus:border-[#3b82f6] focus:ring-1 focus:ring-[#3b82f6] transition-all resize-none h-[46px] overflow-hidden focus:h-24"
                            />
                        </div>
                    </div>
                </div>

                {/* Settings Toggle */}
                <div className="flex items-center justify-between pt-4">
                    <button
                        onClick={() => setShowSettings(!showSettings)}
                        className={cn(
                            "flex items-center gap-2 text-sm font-medium transition-colors px-3 py-2 rounded-lg",
                            showSettings ? "bg-[#262626] text-[#ededed]" : "text-[#a1a1aa] hover:bg-[#121212] hover:text-[#ededed]"
                        )}
                    >
                        <Settings2 className="w-4 h-4" />
                        <span>Configuration</span>
                        <ChevronRight className={cn("w-3 h-3 transition-transform", showSettings && "rotate-90")} />
                    </button>

                    <div className="flex items-center gap-2">
                        {deepScrape && (
                            <span className="text-xs text-[#3b82f6] bg-[#3b82f6]/10 px-2 py-1 rounded-md flex items-center gap-1">
                                <Zap className="w-3 h-3" /> Deep Analysis
                            </span>
                        )}
                    </div>
                </div>

                {/* Settings Panel */}
                {showSettings && (
                    <div className="p-6 rounded-xl bg-[#121212] border border-[#262626] animate-in fade-in slide-in-from-top-2">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-4">
                                <h4 className="text-sm font-medium text-[#ededed] border-b border-[#262626] pb-2">Intelligence</h4>
                                <label htmlFor="deep-scrape-toggle" className="flex items-start gap-3 p-3 rounded-lg hover:bg-[#262626] cursor-pointer transition-colors group">
                                    <div className="mt-0.5 relative">
                                        <input
                                            id="deep-scrape-toggle"
                                            type="checkbox"
                                            checked={deepScrape}
                                            onChange={(e) => setDeepScrape(e.target.checked)}
                                            className="sr-only peer"
                                            aria-label="Enable deep website analysis"
                                            aria-describedby="deep-scrape-description"
                                        />
                                        <div 
                                            className="w-9 h-5 bg-[#262626] rounded-full peer-checked:bg-[#3b82f6] transition-colors border border-[#404040] peer-checked:border-[#3b82f6]" 
                                            aria-hidden="true"
                                        />
                                        <div 
                                            className="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-4 shadow-sm" 
                                            aria-hidden="true"
                                        />
                                    </div>
                                    <div className="flex-1">
                                        <div className="text-sm font-medium text-[#ededed] group-hover:text-white">Deep Analysis</div>
                                        <div id="deep-scrape-description" className="text-xs text-[#a1a1aa]">Crawl website for comprehensive intelligence extraction</div>
                                    </div>
                                </label>
                            </div>

                            <div className="space-y-4">
                                <h4 className="text-sm font-medium text-[#ededed] border-b border-[#262626] pb-2">Model & Style</h4>
                                <div className="space-y-3">
                                    <div className="flex flex-col gap-1">
                                        <label className="text-xs text-[#a1a1aa]">AI Model</label>
                                        <select 
                                            value={selectedModel}
                                            onChange={(e) => setSelectedModel(e.target.value)}
                                            className="bg-[#0a0a0a] border border-[#262626] rounded-lg px-3 py-2 text-sm text-[#ededed] focus:border-[#3b82f6] outline-none"
                                        >
                                            {models.map(m => <option key={m.key} value={m.key}>{m.name}</option>)}
                                        </select>
                                    </div>
                                    <div className="flex flex-col gap-1">
                                        <label className="text-xs text-[#a1a1aa]">Template Style</label>
                                        <select 
                                            value={selectedTemplate}
                                            onChange={(e) => setSelectedTemplate(e.target.value)}
                                            className="bg-[#0a0a0a] border border-[#262626] rounded-lg px-3 py-2 text-sm text-[#ededed] focus:border-[#3b82f6] outline-none"
                                        >
                                            {templates.map(t => <option key={t.key} value={t.key}>{t.name} ({t.tone})</option>)}
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="p-4 rounded-xl bg-red-900/10 border border-red-900/20 text-sm text-red-400 flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                        {error}
                    </div>
                )}

                <div className="pt-4 flex justify-end">
                    <Button
                        onClick={handleSubmit}
                        disabled={!prospectName || !prospectUrl || !painPoints || isPending}
                        className="bg-[#ededed] text-black hover:bg-white px-8 py-6 rounded-full text-base font-medium shadow-[0_0_20px_rgba(255,255,255,0.1)] hover:shadow-[0_0_25px_rgba(255,255,255,0.2)] transition-all disabled:opacity-50 disabled:shadow-none"
                    >
                        {isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                            <span className="flex items-center gap-2">
                                <Sparkles className="w-4 h-4" /> Generate Proposal
                            </span>
                        )}
                    </Button>
                </div>
            </div>
        </div>
    );
}
