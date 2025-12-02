'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Key, User, Building, Bell, Save, Check, Shield, CreditCard } from 'lucide-react';

export default function SettingsPage() {
    const [saved, setSaved] = useState(false);

    const handleSave = () => {
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    return (
        <div className="space-y-8">
            <div className="flex flex-col gap-2">
                <h1 className="text-2xl font-semibold text-[#ededed] tracking-tight">Settings</h1>
                <p className="text-[#a1a1aa] text-sm">Manage your workspace and preferences.</p>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
                {/* Profile */}
                <Card className="border-[#262626] bg-[#121212]">
                    <CardHeader>
                        <CardTitle className="text-lg text-[#ededed] flex items-center gap-2">
                            <User className="h-5 w-5 text-[#a1a1aa]" />
                            Profile
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs text-[#a1a1aa]">First Name</label>
                                <Input defaultValue="Demo" className="bg-[#0a0a0a] border-[#262626] text-[#ededed] focus:border-[#3b82f6] rounded-lg" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs text-[#a1a1aa]">Last Name</label>
                                <Input defaultValue="User" className="bg-[#0a0a0a] border-[#262626] text-[#ededed] focus:border-[#3b82f6] rounded-lg" />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs text-[#a1a1aa]">Email Address</label>
                            <Input defaultValue="demo@propoto.app" className="bg-[#0a0a0a] border-[#262626] text-[#ededed] focus:border-[#3b82f6] rounded-lg" />
                        </div>
                        <div className="pt-2">
                            <Button onClick={handleSave} className="w-full bg-[#ededed] text-black hover:bg-white font-medium shadow-lg shadow-white/5">
                                {saved ? <Check className="mr-2 h-4 w-4" /> : <Save className="mr-2 h-4 w-4" />}
                                {saved ? 'Changes Saved' : 'Update Profile'}
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* Organization */}
                <Card className="border-[#262626] bg-[#121212]">
                    <CardHeader>
                        <CardTitle className="text-lg text-[#ededed] flex items-center gap-2">
                            <Building className="h-5 w-5 text-[#a1a1aa]" />
                            Workspace
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs text-[#a1a1aa]">Workspace Name</label>
                            <Input defaultValue="Demo Agency" className="bg-[#0a0a0a] border-[#262626] text-[#ededed] focus:border-[#3b82f6] rounded-lg" />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs text-[#a1a1aa]">Workspace ID</label>
                            <div className="flex gap-2">
                                <Input value="org_demo_12345" readOnly className="bg-[#0a0a0a] border-[#262626] text-[#525252] font-mono text-xs rounded-lg" />
                                <Button variant="outline" size="icon" className="border-[#262626] bg-[#0a0a0a] text-[#a1a1aa] hover:text-[#ededed]">
                                    <Check className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                        <div className="p-3 rounded-lg bg-[#262626] border border-[#404040] flex items-start gap-3">
                            <Shield className="h-4 w-4 text-yellow-500 mt-0.5" />
                            <div>
                                <p className="text-xs text-[#ededed] font-medium">Pro Plan</p>
                                <p className="text-[10px] text-[#a1a1aa]">Your plan renews on Dec 1, 2025.</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* API Keys */}
                <Card className="border-[#262626] bg-[#121212]">
                    <CardHeader>
                        <CardTitle className="text-lg text-[#ededed] flex items-center gap-2">
                            <Key className="h-5 w-5 text-[#a1a1aa]" />
                            API Integration
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <div className="flex justify-between">
                                <label className="text-xs text-[#a1a1aa]">OpenRouter Key</label>
                                <span className="text-[10px] text-green-400">Active</span>
                            </div>
                            <Input type="password" value="sk-or-v1-........................" readOnly className="bg-[#0a0a0a] border-[#262626] text-[#ededed] font-mono text-xs rounded-lg" />
                        </div>
                        <div className="space-y-2">
                            <div className="flex justify-between">
                                <label className="text-xs text-[#a1a1aa]">Gamma App Key</label>
                                <span className="text-[10px] text-[#525252]">Not Connected</span>
                            </div>
                            <Input placeholder="sk-gamma-..." className="bg-[#0a0a0a] border-[#262626] text-[#ededed] font-mono text-xs rounded-lg focus:border-[#3b82f6]" />
                        </div>
                    </CardContent>
                </Card>

                {/* Preferences */}
                <Card className="border-[#262626] bg-[#121212]">
                    <CardHeader>
                        <CardTitle className="text-lg text-[#ededed] flex items-center gap-2">
                            <Bell className="h-5 w-5 text-[#a1a1aa]" />
                            Preferences
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-1">
                        {[
                            { label: 'Email Notifications', desc: 'Receive daily summaries', enabled: true },
                            { label: 'Desktop Alerts', desc: 'Get notified when jobs complete', enabled: true },
                            { label: 'Marketing Updates', desc: 'News about product features', enabled: false },
                        ].map((item, i) => (
                            <div key={i} className="flex items-center justify-between p-3 rounded-lg hover:bg-[#0a0a0a] transition-colors">
                                <div>
                                    <div className="text-sm text-[#ededed]">{item.label}</div>
                                    <div className="text-xs text-[#525252]">{item.desc}</div>
                                </div>
                                <button
                                    className={`w-10 h-6 rounded-full transition-colors border ${
                                        item.enabled ? 'bg-[#3b82f6] border-[#3b82f6]' : 'bg-[#262626] border-[#404040]'
                                    }`}
                                >
                                    <div
                                        className={`w-4 h-4 bg-white rounded-full transition-transform shadow-sm ${
                                            item.enabled ? 'translate-x-5' : 'translate-x-1'
                                        }`}
                                    />
                                </button>
                            </div>
                        ))}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
