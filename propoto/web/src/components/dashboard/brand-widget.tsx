"use client";

import { useState } from "react";
import { useAction } from "convex/react";
import { api } from "../../../convex/_generated/api";
import { Loader2, AlertCircle, Wand2 } from "lucide-react";

export function BrandWidget() {
    const [prompt, setPrompt] = useState("");
    const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
    const [errorMessage, setErrorMessage] = useState("");
    const [assetUrl, setAssetUrl] = useState("");

    const callAgent = useAction(api.actions.agents.callAgentService);

    const handleGenerate = async () => {
        if (!prompt) return;

        setStatus("loading");
        setErrorMessage("");
        setAssetUrl("");

        try {
            const result = await callAgent({
                agent: "brand",
                action: "generate",
                payload: {
                    prompt,
                    format: "presentation",
                    tone: "professional, innovative",
                    image_style: "photorealistic, modern"
                },
                orgId: "demo-org-1", // Temporary hardcoded orgId
            });

            if (result.success && result.data && result.data.url) {
                setAssetUrl(result.data.url);
                setStatus("success");
                setPrompt("");
            } else {
                throw new Error("No URL returned from service");
            }
        } catch (e: unknown) {
            console.error(e);
            setStatus("error");
            setErrorMessage(e instanceof Error ? e.message : "Failed to generate asset");
        }
    };

    return (
        <div className="bg-[#121212] p-5 rounded-xl border border-[#262626] hover:border-[#404040] transition-colors">
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-[#ededed] flex items-center gap-2 text-sm">
                    <Wand2 className="w-4 h-4 text-[#a1a1aa]" />
                    Brand Asset
                </h3>
                <span className={`px-2 py-0.5 text-[10px] uppercase font-medium tracking-wider rounded-sm ${status === 'loading' ? 'bg-blue-900/20 text-blue-400' :
                        status === 'success' ? 'bg-green-900/20 text-green-400' :
                            status === 'error' ? 'bg-red-900/20 text-red-400' :
                                'bg-[#262626] text-[#a1a1aa]'
                    }`}>
                    {status === 'idle' ? 'Ready' :
                        status === 'loading' ? 'Creating...' :
                            status === 'success' ? 'Done' : 'Error'}
                </span>
            </div>

            <p className="text-xs text-[#a1a1aa] mb-4 min-h-[1.5em]">
                {status === 'success'
                    ? "Asset generated successfully!"
                    : "Generate brand consistent assets for your campaigns."}
            </p>

            {status === 'success' && assetUrl && (
                <div className="mb-4 p-3 bg-[#0a0a0a] rounded-lg border border-[#262626]">
                    <a
                        href={assetUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs font-medium text-[#3b82f6] hover:text-blue-400 flex items-center gap-2"
                    >
                        View Generated Asset →
                    </a>
                </div>
            )}

            <div className="space-y-3">
                <input
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Describe asset..."
                    disabled={status === 'loading'}
                    className="w-full px-3 py-2 text-sm bg-[#0a0a0a] border border-[#262626] text-[#ededed] rounded-lg focus:outline-none focus:border-[#3b82f6] disabled:opacity-50 placeholder-[#525252] transition-colors"
                    onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
                />
                <button
                    onClick={handleGenerate}
                    disabled={!prompt || status === 'loading'}
                    className="w-full py-2 text-sm text-[#ededed] bg-[#262626] border border-[#404040] rounded-lg hover:bg-[#333] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex justify-center items-center gap-2 font-medium"
                >
                    {status === 'loading' ? <Loader2 className="w-3 h-3 animate-spin" /> : "Generate"}
                </button>

                {status === 'error' && (
                    <div className="flex items-center gap-2 text-xs text-red-400 mt-2">
                        <AlertCircle className="w-3 h-3" />
                        <span className="truncate">{errorMessage}</span>
                    </div>
                )}
            </div>
        </div>
    );
}
