'use server'

interface ProposalRequest {
    prospect_name: string;
    prospect_url: string;
    pain_points: string;
    // Phase 2: Enhanced options
    model?: string;
    template?: string;
    deep_scrape?: boolean;
}

interface GenerateResult {
    success: boolean;
    data: any;
    presentation_url?: string;
    pdf_url?: string;
    pptx_url?: string;
    model_used?: string;
    template_used?: string;
    deep_scrape_enabled?: boolean;
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

export async function getAvailableModels(): Promise<{ models: ModelOption[], default: string }> {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    try {
        const response = await fetch(`${API_URL}/agents/proposal/models`, {
            cache: 'force-cache',
        });
        
        if (!response.ok) {
            return { models: [], default: 'grok' };
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching models:', error);
        return { models: [], default: 'grok' };
    }
}

export async function getAvailableTemplates(): Promise<{ templates: TemplateOption[] }> {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    try {
        const response = await fetch(`${API_URL}/agents/proposal/templates`, {
            cache: 'force-cache',
        });
        
        if (!response.ok) {
            return { templates: [] };
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching templates:', error);
        return { templates: [] };
    }
}

export async function generateProposalAction(data: ProposalRequest): Promise<GenerateResult> {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const API_KEY = process.env.AGENT_SERVICE_KEY;

    try {
        const response = await fetch(`${API_URL}/agents/proposal/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': API_KEY || '',
            },
            body: JSON.stringify(data),
            cache: 'no-store',
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to generate proposal');
        }

        const result = await response.json();
        
        // Save to Convex via HTTP API (server-side)
        const convexUrl = process.env.NEXT_PUBLIC_CONVEX_URL;
        if (convexUrl && result.success) {
            try {
                await fetch(`${convexUrl}/api/mutation`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        path: 'proposals:create',
                        args: {
                            prospectName: data.prospect_name,
                            prospectUrl: data.prospect_url,
                            painPoints: data.pain_points,
                            content: result.data,
                            presentationUrl: result.presentation_url,
                            pdfUrl: result.pdf_url,
                            pptxUrl: result.pptx_url,
                            status: 'draft',
                        },
                    }),
                });
            } catch (saveError) {
                console.error('Failed to save proposal to Convex:', saveError);
                // Don't fail the whole operation if save fails
            }
        }

        return result;
    } catch (error) {
        console.error('Error generating proposal:', error);
        throw error;
    }
}
