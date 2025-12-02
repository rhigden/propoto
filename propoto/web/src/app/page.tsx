import Link from "next/link";
import { ArrowRight, Terminal, Cpu, Shield, Zap, Code2, Check, Keyboard } from "lucide-react";

export default function Home() {
    return (
        <div className="min-h-screen bg-[#040404] text-[#ededed] font-sans selection:bg-white/20 overflow-x-hidden">
            {/* Navigation */}
            <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-[#040404]/80 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm font-medium tracking-tight">
                        <div className="w-5 h-5 bg-white text-black rounded-[4px] flex items-center justify-center">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M21 21L12 12M12 12L3 3M12 12L21 3M12 12L3 21" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                        </div>
                        <span>Propoto</span>
                    </div>
                    <div className="flex items-center gap-6 text-sm text-[#a1a1aa]">
                        <Link href="#features" className="hover:text-white transition-colors">Features</Link>
                        <Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link>
                        <Link href="#blog" className="hover:text-white transition-colors">Blog</Link>
                        <Link
                            href="/dashboard"
                            className="px-3 py-1.5 text-xs font-medium bg-white text-black hover:bg-[#e5e5e5] rounded-md transition-colors"
                        >
                            Sign In
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="pt-32 pb-24 px-6 relative">
                {/* Glow Effects */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-gradient-to-b from-indigo-500/10 via-purple-500/5 to-transparent rounded-[100%] blur-3xl pointer-events-none" />
                
                <div className="max-w-4xl mx-auto text-center relative z-10">
                    <h1 className="text-6xl md:text-8xl font-bold tracking-tighter mb-8 bg-gradient-to-b from-white to-white/70 bg-clip-text text-transparent pb-2">
                        AI proposals that <br /> win deals.
                    </h1>
                    <p className="text-xl text-[#a1a1aa] max-w-2xl mx-auto mb-10 font-light leading-relaxed">
                        Turn a URL into a $10K proposal in 60 seconds. Propoto is the AI proposal generator that helps agencies close more deals, faster.
                    </p>
                    
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
                        <Link
                            href="/dashboard"
                            className="h-12 px-8 rounded-full bg-white text-black font-medium flex items-center gap-2 hover:bg-[#e5e5e5] transition-colors"
                        >
                            Get Started <ArrowRight className="w-4 h-4" />
                        </Link>
                        <button className="h-12 px-8 rounded-full bg-[#1a1a1a] text-white border border-white/10 font-medium hover:bg-[#2a2a2a] transition-colors flex items-center gap-2">
                            <Keyboard className="w-4 h-4 text-[#a1a1aa]" /> Command K to generate
                        </button>
                    </div>

                    {/* Terminal / Code Preview */}
                    <div className="rounded-xl border border-white/10 bg-[#0a0a0a] shadow-2xl shadow-indigo-500/10 overflow-hidden text-left max-w-3xl mx-auto">
                        <div className="h-10 border-b border-white/5 bg-[#111] flex items-center px-4 gap-2">
                            <div className="flex gap-1.5">
                                <div className="w-3 h-3 rounded-full bg-[#333]" />
                                <div className="w-3 h-3 rounded-full bg-[#333]" />
                                <div className="w-3 h-3 rounded-full bg-[#333]" />
                            </div>
                            <div className="ml-4 text-xs text-[#666] font-mono">generate_proposal.tsx</div>
                        </div>
                        <div className="p-6 font-mono text-sm overflow-x-auto">
                            <div className="text-[#a1a1aa]">
                                <span className="text-purple-400">const</span> proposal <span className="text-purple-400">=</span> <span className="text-blue-400">await</span> agent.<span className="text-yellow-300">generate</span>({`{`}
                                <br />
                                <div className="pl-4">
                                    client: <span className="text-green-400">"Acme Corp"</span>,
                                    <br />
                                    url: <span className="text-green-400">"acme.com"</span>,
                                    <br />
                                    style: <span className="text-green-400">"Enterprise"</span>
                                </div>
                                {`}`});
                                <br />
                                <br />
                                <span className="text-[#666]">// Generating PDF...</span>
                                <br />
                                <span className="text-[#666]">// Done in 1.2s</span>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Features Grid */}
            <section className="py-24 px-6 relative border-t border-white/5">
                <div className="max-w-6xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold tracking-tight mb-4">Built for speed</h2>
                        <p className="text-[#a1a1aa]">Designed to keep you in the flow.</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-6">
                        {[
                            {
                                title: "Privacy First",
                                desc: "Your data stays private. We offer a privacy mode where no code is stored on our servers.",
                                icon: Shield
                            },
                            {
                                title: "Instant Context",
                                desc: "Propoto scrapes your prospect's website to personalize every proposal automatically.",
                                icon: Zap
                            },
                            {
                                title: "Copilot++",
                                desc: "Predicts your next move. It suggests entire paragraphs of proposal text before you type them.",
                                icon: Code2
                            },
                            {
                                title: "Natural Language",
                                desc: "Edit proposals using simple english commands. 'Make this section more punchy'.",
                                icon: Terminal
                            },
                            {
                                title: "Tech Stack",
                                desc: "Seamlessly integrates with your existing CRM and tools via simple API keys.",
                                icon: Cpu
                            },
                            {
                                title: "One-Click Deck",
                                desc: "Turn any written proposal into a visual presentation slide deck instantly.",
                                icon: Keyboard
                            }
                        ].map((feature, i) => (
                            <div key={i} className="group p-6 rounded-xl bg-[#0a0a0a] border border-white/10 hover:border-white/20 transition-colors">
                                <feature.icon className="w-6 h-6 text-[#a1a1aa] mb-4 group-hover:text-white transition-colors" />
                                <h3 className="text-lg font-semibold mb-2 text-[#ededed]">{feature.title}</h3>
                                <p className="text-sm text-[#a1a1aa] leading-relaxed">{feature.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 border-t border-white/5 bg-[#040404]">
                <div className="max-w-6xl mx-auto px-6 grid md:grid-cols-4 gap-8 text-sm">
                    <div className="col-span-2">
                        <div className="font-bold mb-4 text-white">Propoto</div>
                        <p className="text-[#666] max-w-xs">
                            The AI-first operating system for modern agencies. Build faster, close more.
                        </p>
                    </div>
                    <div>
                        <div className="font-medium text-white mb-4">Product</div>
                        <ul className="space-y-2 text-[#888]">
                            <li><a href="#" className="hover:text-white transition-colors">Changelog</a></li>
                            <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                            <li><a href="#" className="hover:text-white transition-colors">Download</a></li>
                        </ul>
                    </div>
                    <div>
                        <div className="font-medium text-white mb-4">Company</div>
                        <ul className="space-y-2 text-[#888]">
                            <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                            <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                            <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                        </ul>
                    </div>
                </div>
            </footer>
        </div>
    );
}
