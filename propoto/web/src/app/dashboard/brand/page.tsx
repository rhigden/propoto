'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Palette, Presentation, FileText, Globe, Loader2, ExternalLink, Sparkles, Wand2 } from 'lucide-react';

type AssetFormat = 'presentation' | 'document' | 'webpage';

export default function BrandPage() {
    const [prompt, setPrompt] = useState('');
    const [format, setFormat] = useState<AssetFormat>('presentation');
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [generatedUrl, setGeneratedUrl] = useState<string | null>(null);

    const handleGenerate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt) return;

        setIsGenerating(true);
        setError(null);
        setGeneratedUrl(null);

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${API_URL}/agents/brand/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': process.env.NEXT_PUBLIC_AGENT_SERVICE_KEY || '',
                },
                body: JSON.stringify({
                    prompt,
                    format,
                    num_cards: 10,
                    tone: 'professional, innovative',
                    image_style: 'photorealistic, modern',
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to generate asset');
            }

            const data = await response.json();
            if (data.success && data.data?.url) {
                setGeneratedUrl(data.data.url);
                setPrompt('');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to generate');
        } finally {
            setIsGenerating(false);
        }
    };

    const formatOptions = [
        { value: 'presentation', label: 'Presentation', icon: Presentation },
        { value: 'document', label: 'Document', icon: FileText },
        { value: 'webpage', label: 'Webpage', icon: Globe },
    ] as const;

    return (
        <div className="space-y-8">
            <div className="flex flex-col gap-2">
                <h1 className="text-2xl font-semibold text-[#ededed] tracking-tight">Brand Studio</h1>
                <p className="text-[#a1a1aa] text-sm">Generate assets with consistent brand identity.</p>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
                {/* Generator Form */}
                <Card className="border-[#262626] bg-[#121212]">
                    <CardHeader>
                        <CardTitle className="text-lg text-[#ededed] flex items-center gap-2">
                            <Wand2 className="h-5 w-5 text-[#a1a1aa]" />
                            Create Asset
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleGenerate} className="space-y-6">
                            {/* Format Selection */}
                            <div className="flex gap-2">
                                {formatOptions.map((opt) => (
                                    <button
                                        key={opt.value}
                                        type="button"
                                        onClick={() => setFormat(opt.value)}
                                        className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm transition-all ${
                                            format === opt.value
                                                ? 'bg-[#ededed] text-black font-medium'
                                                : 'bg-[#0a0a0a] border border-[#262626] text-[#a1a1aa] hover:text-[#ededed]'
                                        }`}
                                    >
                                        <opt.icon className="h-4 w-4" />
                                        {opt.label}
                                    </button>
                                ))}
                            </div>

                            <Textarea
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                placeholder="Describe what you want to create..."
                                className="min-h-[120px] bg-[#0a0a0a] border-[#262626] text-[#ededed] placeholder:text-[#525252] focus:border-[#3b82f6] focus:ring-0 rounded-xl resize-none"
                            />

                            {error && (
                                <p className="text-sm text-red-400 bg-red-900/10 p-3 rounded-lg border border-red-900/20">{error}</p>
                            )}

                            <div className="flex justify-end">
                                <Button
                                    type="submit"
                                    disabled={isGenerating || !prompt}
                                    className="bg-[#3b82f6] hover:bg-[#2563eb] text-white font-medium px-6 py-2 rounded-lg transition-colors disabled:opacity-50"
                                >
                                    {isGenerating ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            Generating...
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles className="mr-2 h-4 w-4" />
                                            Generate Asset
                                        </>
                                    )}
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>

                {/* Preview / Recent Assets */}
                <Card className="border-[#262626] bg-[#121212] flex flex-col">
                    <CardHeader>
                        <CardTitle className="text-lg text-[#ededed]">
                            {generatedUrl ? 'Generated Asset' : 'Recent History'}
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex-1">
                        {generatedUrl ? (
                            <div className="space-y-4 h-full flex flex-col">
                                <div className="flex-1 rounded-xl overflow-hidden bg-[#0a0a0a] border border-[#262626] relative group">
                                    <iframe
                                        src={generatedUrl}
                                        className="w-full h-full border-0"
                                        allowFullScreen
                                    />
                                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                                        <span className="text-white text-sm font-medium">Click to interact</span>
                                    </div>
                                </div>
                                <a
                                    href={generatedUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center justify-center gap-2 text-[#ededed] hover:text-white text-sm bg-[#262626] py-3 rounded-lg border border-[#262626] hover:bg-[#333] transition-all"
                                >
                                    <ExternalLink className="h-4 w-4" />
                                    Open in new tab
                                </a>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                {[
                                    { name: 'Q4 Strategy Deck', type: 'presentation', date: 'Today' },
                                    { name: 'Client Proposal - Acme', type: 'document', date: 'Yesterday' },
                                    { name: 'Product Launch Page', type: 'webpage', date: '2 days ago' },
                                ].map((asset, i) => (
                                    <div
                                        key={i}
                                        className="p-3 rounded-lg hover:bg-[#262626] transition-colors cursor-pointer group flex items-center justify-between border border-transparent hover:border-[#262626]"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-md bg-[#0a0a0a] flex items-center justify-center border border-[#262626] text-[#a1a1aa]">
                                                {asset.type === 'presentation' && <Presentation className="h-4 w-4" />}
                                                {asset.type === 'document' && <FileText className="h-4 w-4" />}
                                                {asset.type === 'webpage' && <Globe className="h-4 w-4" />}
                                            </div>
                                            <div>
                                                <div className="text-sm font-medium text-[#ededed] group-hover:text-white">{asset.name}</div>
                                                <div className="text-xs text-[#525252] capitalize">{asset.type}</div>
                                            </div>
                                        </div>
                                        <span className="text-xs text-[#525252]">{asset.date}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
