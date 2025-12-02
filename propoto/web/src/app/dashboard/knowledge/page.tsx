'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Brain, Link2, Search, Loader2, ExternalLink, Tag, Sparkles } from 'lucide-react';

export default function KnowledgePage() {
    const [url, setUrl] = useState('');
    const [isIngesting, setIsIngesting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleIngest = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!url) return;

        setIsIngesting(true);
        setError(null);

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${API_URL}/agents/knowledge/ingest`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': process.env.NEXT_PUBLIC_AGENT_SERVICE_KEY || '',
                },
                body: JSON.stringify({ url }),
            });

            if (!response.ok) {
                throw new Error('Failed to ingest URL');
            }

            setUrl('');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to ingest');
        } finally {
            setIsIngesting(false);
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex flex-col gap-2">
                <h1 className="text-2xl font-semibold text-[#ededed] tracking-tight">Knowledge Base</h1>
                <p className="text-[#a1a1aa] text-sm">Ingest URLs to build your organizational intelligence graph.</p>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Ingest Form */}
                <Card className="lg:col-span-1 border-[#262626] bg-[#121212]">
                    <CardHeader>
                        <CardTitle className="text-lg text-[#ededed] flex items-center gap-2">
                            <Link2 className="h-5 w-5 text-[#a1a1aa]" />
                            Add Source
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleIngest} className="space-y-4">
                            <Input
                                type="url"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                placeholder="https://example.com/article"
                                className="bg-[#0a0a0a] border-[#262626] text-[#ededed] placeholder:text-[#525252] focus:border-[#3b82f6] focus:ring-0 rounded-lg"
                            />
                            {error && (
                                <p className="text-sm text-red-400 bg-red-900/10 p-3 rounded-lg border border-red-900/20">{error}</p>
                            )}
                            <Button
                                type="submit"
                                disabled={isIngesting || !url}
                                className="w-full bg-[#ededed] text-black hover:bg-white font-medium py-2 rounded-lg shadow-lg shadow-white/5 disabled:opacity-50"
                            >
                                {isIngesting ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Analyzing...
                                    </>
                                ) : (
                                    <>
                                        <Sparkles className="mr-2 h-4 w-4" />
                                        Ingest URL
                                    </>
                                )}
                            </Button>
                        </form>
                    </CardContent>
                </Card>

                {/* Knowledge Entries */}
                <Card className="lg:col-span-2 border-[#262626] bg-[#121212]">
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-lg text-[#ededed] flex items-center gap-2">
                                <Brain className="h-5 w-5 text-[#a1a1aa]" />
                                Recent Knowledge
                            </CardTitle>
                            <div className="relative w-64">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#525252]" />
                                <input
                                    type="text"
                                    placeholder="Search sources..."
                                    className="w-full bg-[#0a0a0a] border border-[#262626] rounded-lg pl-9 pr-4 py-1.5 text-sm text-[#ededed] placeholder-[#525252] focus:outline-none focus:border-[#3b82f6] transition-colors"
                                />
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-1">
                            {[
                                { title: 'AI Agent Market Report 2025', url: 'mckinsey.com', entities: 12, score: 9 },
                                { title: 'Competitor Analysis: Jasper', url: 'jasper.ai', entities: 8, score: 7 },
                                { title: 'n8n Workflow Patterns', url: 'docs.n8n.io', entities: 15, score: 8 },
                            ].map((entry, i) => (
                                <div
                                    key={i}
                                    className="p-3 rounded-lg hover:bg-[#262626] border border-transparent hover:border-[#262626] transition-all group cursor-pointer flex items-center justify-between"
                                >
                                    <div className="flex items-center gap-3 min-w-0">
                                        <div className="w-8 h-8 rounded-md bg-[#0a0a0a] flex items-center justify-center border border-[#262626] text-[#a1a1aa]">
                                            <Tag className="h-4 w-4" />
                                        </div>
                                        <div className="min-w-0">
                                            <div className="font-medium text-[#ededed] text-sm truncate">{entry.title}</div>
                                            <div className="text-xs text-[#525252] flex items-center gap-1 truncate">
                                                <ExternalLink className="h-3 w-3" />
                                                {entry.url}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2 pl-4">
                                        <span className="px-2 py-0.5 text-[10px] bg-[#262626] text-[#a1a1aa] rounded border border-[#404040]">
                                            {entry.entities} entities
                                        </span>
                                        <span className="px-2 py-0.5 text-[10px] bg-green-900/10 text-green-400 rounded border border-green-900/20">
                                            Score: {entry.score}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
