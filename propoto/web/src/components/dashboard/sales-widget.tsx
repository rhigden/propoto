"use client";

import { useState } from "react";
import { useAction } from "convex/react";
import { api } from "../../../convex/_generated/api";
import { Loader2, AlertCircle, Zap } from "lucide-react";

export function SalesWidget() {
    const [prompt, setPrompt] = useState("");
    const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
    const [errorMessage, setErrorMessage] = useState("");
    const [leadsFound, setLeadsFound] = useState(0);

    const callAgent = useAction(api.actions.agents.callAgentService);

    const handleFindLeads = async () => {
        if (!prompt) return;

        setStatus("loading");
        setErrorMessage("");
        setLeadsFound(0);

        try {
            const result = await callAgent({
                agent: "sales",
                action: "find_leads",
                payload: {
                    prompt,
                },
                orgId: "demo-org-1",
            });

            if (result.success && result.data && result.data.leads) {
                setLeadsFound(result.data.leads.length);
                setStatus("success");
                setPrompt("");
                setTimeout(() => setStatus("idle"), 5000);
            } else {
                throw new Error("No leads returned from service");
            }
        } catch (e: unknown) {
            console.error(e);
            setStatus("error");
            setErrorMessage(e instanceof Error ? e.message : "Failed to find leads");
        }
    };

    return (
        <div className="bg-[#121212] p-5 rounded-xl border border-[#262626] hover:border-[#404040] transition-colors">
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-[#ededed] flex items-center gap-2 text-sm">
                    <Zap className="w-4 h-4 text-[#a1a1aa]" />
                    Sales Scout
                </h3>
                <span className={`px-2 py-0.5 text-[10px] uppercase font-medium tracking-wider rounded-sm ${status === 'loading' ? 'bg-green-900/20 text-green-400' :
                    status === 'success' ? 'bg-green-900/20 text-green-400' :
                        status === 'error' ? 'bg-red-900/20 text-red-400' :
                            'bg-[#262626] text-[#a1a1aa]'
                    }`}>
                    {status === 'idle' ? 'Ready' :
                        status === 'loading' ? 'Hunting...' :
                            status === 'success' ? 'Found!' : 'Error'}
                </span>
            </div>

            <div className="space-y-4">
                <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                        <span className="text-[#a1a1aa]">New Leads</span>
                        <span className="font-medium text-[#ededed]">{leadsFound > 0 ? `+${leadsFound}` : "0"}</span>
                    </div>
                    <div className="w-full bg-[#262626] h-1 rounded-full overflow-hidden">
                        <div className="bg-[#10b981] h-full rounded-full transition-all duration-500" style={{ width: `${Math.min(leadsFound * 10, 100)}%` }} />
                    </div>
                </div>

                <div className="space-y-3">
                    <input
                        type="text"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="e.g. SaaS in NYC..."
                        disabled={status === 'loading'}
                        className="w-full px-3 py-2 text-sm bg-[#0a0a0a] border border-[#262626] text-[#ededed] rounded-lg focus:outline-none focus:border-[#3b82f6] disabled:opacity-50 placeholder-[#525252] transition-colors"
                        onKeyDown={(e) => e.key === 'Enter' && handleFindLeads()}
                    />
                    <button
                        onClick={handleFindLeads}
                        disabled={!prompt || status === 'loading'}
                        className="w-full py-2 text-sm text-[#ededed] bg-[#262626] border border-[#404040] rounded-lg hover:bg-[#333] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex justify-center items-center gap-2 font-medium"
                    >
                        {status === 'loading' ? <Loader2 className="w-3 h-3 animate-spin" /> : "Find Leads"}
                    </button>
                </div>

                {status === 'error' && (
                    <div className="flex items-center gap-2 text-xs text-red-400">
                        <AlertCircle className="w-3 h-3" />
                        <span className="truncate">{errorMessage}</span>
                    </div>
                )}
            </div>
        </div>
    );
}
