'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Target, Search, Loader2, Building2, Globe, Mail, Phone, Zap } from 'lucide-react';

interface Lead {
    company_name: string;
    website: string | null;
    description: string;
    score: number;
    status: string;
}

export default function SalesPage() {
    const [query, setQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [leads, setLeads] = useState<Lead[]>([]);
    const [marketSummary, setMarketSummary] = useState<string | null>(null);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query) return;

        setIsSearching(true);
        setError(null);

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${API_URL}/agents/sales/find_leads`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': process.env.NEXT_PUBLIC_AGENT_SERVICE_KEY || '',
                },
                body: JSON.stringify({ prompt: query, context: {} }),
            });

            if (!response.ok) {
                throw new Error('Failed to find leads');
            }

            const data = await response.json();
            if (data.success && data.data) {
                setLeads(data.data.leads || []);
                setMarketSummary(data.data.market_summary || null);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to find leads');
        } finally {
            setIsSearching(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-green-400 border-green-900/30 bg-green-900/10';
        if (score >= 60) return 'text-yellow-400 border-yellow-900/30 bg-yellow-900/10';
        return 'text-[#a1a1aa] border-[#404040] bg-[#262626]';
    };

    return (
        <div className="space-y-8">
            <div className="flex flex-col gap-2">
                <h1 className="text-2xl font-semibold text-[#ededed] tracking-tight">Sales Intelligence</h1>
                <p className="text-[#a1a1aa] text-sm">Discover and qualify leads with AI-powered search.</p>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Search Panel */}
                <Card className="lg:col-span-1 border-[#262626] bg-[#121212]">
                    <CardHeader>
                        <CardTitle className="text-lg text-[#ededed] flex items-center gap-2">
                            <Search className="h-5 w-5 text-[#a1a1aa]" />
                            Find Leads
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSearch} className="space-y-4">
                            <Input
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="E.g., Digital marketing agencies in Austin, Texas"
                                className="bg-[#0a0a0a] border-[#262626] text-[#ededed] placeholder:text-[#525252] focus:border-[#3b82f6] focus:ring-0 rounded-lg"
                            />
                            {error && (
                                <p className="text-sm text-red-400 bg-red-900/10 p-3 rounded-lg border border-red-900/20">{error}</p>
                            )}
                            <Button
                                type="submit"
                                disabled={isSearching || !query}
                                className="w-full bg-[#ededed] text-black hover:bg-white font-medium py-2 rounded-lg shadow-lg shadow-white/5 disabled:opacity-50"
                            >
                                {isSearching ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Searching...
                                    </>
                                ) : (
                                    <>
                                        <Zap className="mr-2 h-4 w-4" />
                                        Find Leads
                                    </>
                                )}
                            </Button>
                        </form>

                        {/* Stats */}
                        <div className="mt-6 pt-6 border-t border-[#262626] space-y-3">
                            {[
                                { label: 'Total Leads', value: leads.length || 24, color: 'text-[#ededed]' },
                                { label: 'Qualified', value: leads.filter(l => l.score >= 70).length || 12, color: 'text-green-400' },
                                { label: 'Contacted', value: 5, color: 'text-[#3b82f6]' }
                            ].map((stat, i) => (
                                <div key={i} className="flex justify-between text-sm">
                                    <span className="text-[#a1a1aa]">{stat.label}</span>
                                    <span className={`font-medium ${stat.color}`}>{stat.value}</span>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* Leads List */}
                <Card className="lg:col-span-2 border-[#262626] bg-[#121212] flex flex-col h-[calc(100vh-12rem)]">
                    <CardHeader className="shrink-0">
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-lg text-[#ededed] flex items-center gap-2">
                                <Target className="h-5 w-5 text-[#a1a1aa]" />
                                {leads.length > 0 ? `Found ${leads.length} Leads` : 'Lead Pipeline'}
                            </CardTitle>
                            <Button variant="outline" size="sm" className="border-[#262626] bg-[#0a0a0a] text-[#a1a1aa] hover:text-[#ededed] hover:bg-[#171717] text-xs">
                                <Mail className="h-3 w-3 mr-2" /> Export CSV
                            </Button>
                        </div>
                        {marketSummary && (
                            <p className="text-sm text-[#a1a1aa] mt-2">{marketSummary}</p>
                        )}
                    </CardHeader>
                    <CardContent className="flex-1 overflow-y-auto custom-scrollbar pr-2">
                        <div className="space-y-2">
                            {(leads.length > 0 ? leads : [
                                { company_name: 'TechFlow Marketing', website: 'techflow.io', description: 'Full-service digital agency', score: 85, status: 'new' },
                                { company_name: 'Growth Partners Co', website: 'growthpartners.com', description: 'B2B marketing specialists', score: 72, status: 'contacted' },
                                { company_name: 'Digital Spark Agency', website: 'digitalspark.co', description: 'Performance marketing', score: 68, status: 'new' },
                                { company_name: 'NextGen Solutions', website: 'nextgen.io', description: 'Enterprise software development', score: 92, status: 'new' },
                                { company_name: 'Creative Pulse', website: 'creativepulse.design', description: 'Branding and UI/UX studio', score: 64, status: 'contacted' },
                            ]).map((lead, i) => (
                                <div
                                    key={i}
                                    className="p-3 rounded-lg hover:bg-[#262626] border border-transparent hover:border-[#262626] transition-all group cursor-pointer"
                                >
                                    <div className="flex items-start justify-between gap-4">
                                        <div className="space-y-1 min-w-0 flex-1">
                                            <div className="flex items-center gap-2">
                                                <Building2 className="h-4 w-4 text-[#525252]" />
                                                <h4 className="font-medium text-[#ededed] text-sm truncate">{lead.company_name}</h4>
                                                <span className={`px-1.5 py-0.5 text-[10px] font-medium border rounded ${getScoreColor(lead.score)}`}>
                                                    {lead.score}%
                                                </span>
                                            </div>
                                            {lead.website && (
                                                <div className="flex items-center gap-1 text-xs text-[#3b82f6]">
                                                    <Globe className="h-3 w-3" />
                                                    {lead.website}
                                                </div>
                                            )}
                                            <p className="text-xs text-[#525252] line-clamp-1">{lead.description}</p>
                                        </div>
                                        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button className="p-1.5 rounded hover:bg-[#171717] text-[#a1a1aa] hover:text-[#ededed]">
                                                <Phone className="h-3.5 w-3.5" />
                                            </button>
                                            <button className="p-1.5 rounded hover:bg-[#171717] text-[#a1a1aa] hover:text-[#ededed]">
                                                <Mail className="h-3.5 w-3.5" />
                                            </button>
                                        </div>
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
