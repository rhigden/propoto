"use client";

import { useState } from "react";
import { useAction } from "convex/react";
import { api } from "../../../convex/_generated/api";
import { Loader2, AlertCircle, Sparkles } from "lucide-react";

export function KnowledgeWidget() {
    const [url, setUrl] = useState("");
    const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
    const [errorMessage, setErrorMessage] = useState("");

    const callAgent = useAction(api.actions.agents.callAgentService);

    const handleIngest = async () => {
        if (!url) return;

        setStatus("loading");
        setErrorMessage("");

        try {
            await callAgent({
                agent: "knowledge",
                action: "ingest",
                payload: { url },
                orgId: "demo-org-1", // Temporary hardcoded orgId for testing
            });

            setStatus("success");
            setUrl("");
            setTimeout(() => setStatus("idle"), 3000);
        } catch (e: unknown) {
            console.error(e);
            setStatus("error");
            setErrorMessage(e instanceof Error ? e.message : "Failed to ingest URL");
        }
    };

    return (
        <div className="bg-[#121212] p-5 rounded-xl border border-[#262626] hover:border-[#404040] transition-colors">
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-[#ededed] flex items-center gap-2 text-sm">
                    <Sparkles className="w-4 h-4 text-[#a1a1aa]" />
                    Knowledge Base
                </h3>
                <span className={`px-2 py-0.5 text-[10px] uppercase font-medium tracking-wider rounded-sm ${status === 'loading' ? 'bg-yellow-900/20 text-yellow-400' :
                    status === 'success' ? 'bg-green-900/20 text-green-400' :
                        status === 'error' ? 'bg-red-900/20 text-red-400' :
                            'bg-[#262626] text-[#a1a1aa]'
                    }`}>
                    {status === 'idle' ? 'Ready' :
                        status === 'loading' ? 'Learning...' :
                            status === 'success' ? 'Active' : 'Error'}
                </span>
            </div>

            <p className="text-xs text-[#a1a1aa] mb-4 min-h-[1.5em]">
                {status === 'success'
                    ? "Successfully queued for ingestion!"
                    : "Feed URLs to train your organizational brain."}
            </p>

            <div className="space-y-3">
                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="Paste URL..."
                    disabled={status === 'loading'}
                    className="w-full px-3 py-2 text-sm bg-[#0a0a0a] border border-[#262626] text-[#ededed] rounded-lg focus:outline-none focus:border-[#3b82f6] disabled:opacity-50 placeholder-[#525252] transition-colors"
                    onKeyDown={(e) => e.key === 'Enter' && handleIngest()}
                />
                <button
                    onClick={handleIngest}
                    disabled={!url || status === 'loading'}
                    className="w-full py-2 text-sm text-[#ededed] bg-[#262626] border border-[#404040] rounded-lg hover:bg-[#333] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex justify-center items-center gap-2 font-medium"
                >
                    {status === 'loading' ? <Loader2 className="w-3 h-3 animate-spin" /> : "Ingest"}
                </button>

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
