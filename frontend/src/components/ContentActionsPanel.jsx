import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    FileText,
    Download,
    Calendar,
    Mail,
    Presentation,
    Loader2,
    CheckCircle2,
    ExternalLink,
    Eye
} from 'lucide-react';
import { toast } from 'sonner';

export function ContentActionsPanel({ analysisId, isPremium }) {
    const [loading, setLoading] = useState({});
    const [generated, setGenerated] = useState({});

    const handleExportPDF = async () => {
        try {
            setLoading(prev => ({ ...prev, pdf: true }));

            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL !== undefined ? process.env.REACT_APP_BACKEND_URL : 'http://localhost:8001'}/api/export/pdf/${analysisId}`);

            if (!response.ok) throw new Error('PDF export failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `astramark_report_${analysisId.substring(0, 8)}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            toast.success('PDF report downloaded successfully!');
            setGenerated(prev => ({ ...prev, pdf: true }));
        } catch (error) {
            toast.error('Failed to export PDF: ' + error.message);
        } finally {
            setLoading(prev => ({ ...prev, pdf: false }));
        }
    };

    const handleGeneratePitchDeck = async () => {
        try {
            setLoading(prev => ({ ...prev, pitchDeck: true }));

            const response = await fetch(
                `${process.env.REACT_APP_BACKEND_URL !== undefined ? process.env.REACT_APP_BACKEND_URL : 'http://localhost:8001'}/api/generate/pitch-deck?analysis_id=${analysisId}`,
                { method: 'POST' }
            );

            if (!response.ok) throw new Error('Pitch deck generation failed');

            const data = await response.json();

            toast.success(`Pitch deck generated with ${data.total_slides} slides!`);
            setGenerated(prev => ({ ...prev, pitchDeck: data }));
        } catch (error) {
            toast.error('Failed to generate pitch deck: ' + error.message);
        } finally {
            setLoading(prev => ({ ...prev, pitchDeck: false }));
        }
    };

    const handleGenerateContentCalendar = async () => {
        try {
            setLoading(prev => ({ ...prev, calendar: true }));

            const response = await fetch(
                `${process.env.REACT_APP_BACKEND_URL !== undefined ? process.env.REACT_APP_BACKEND_URL : 'http://localhost:8001'}/api/generate/content-calendar?analysis_id=${analysisId}&weeks=4`,
                { method: 'POST' }
            );

            if (!response.ok) throw new Error('Content calendar generation failed');

            const data = await response.json();

            toast.success(`Content calendar generated with ${data.total_posts} posts!`);
            setGenerated(prev => ({ ...prev, calendar: data }));
        } catch (error) {
            toast.error('Failed to generate content calendar: ' + error.message);
        } finally {
            setLoading(prev => ({ ...prev, calendar: false }));
        }
    };

    const handleGenerateEmailSequence = async () => {
        try {
            setLoading(prev => ({ ...prev, email: true }));

            const response = await fetch(
                `${process.env.REACT_APP_BACKEND_URL !== undefined ? process.env.REACT_APP_BACKEND_URL : 'http://localhost:8001'}/api/generate/email-sequence?analysis_id=${analysisId}&sequence_type=onboarding`,
                { method: 'POST' }
            );

            if (!response.ok) throw new Error('Email sequence generation failed');

            const data = await response.json();

            toast.success(`Email sequence generated with ${data.total_emails} emails!`);
            setGenerated(prev => ({ ...prev, email: data }));
        } catch (error) {
            toast.error('Failed to generate email sequence: ' + error.message);
        } finally {
            setLoading(prev => ({ ...prev, email: false }));
        }
    };

    // Handler to simulate generation for locked items
    const handleLockedAction = (item) => {
        toast.promise(new Promise(resolve => setTimeout(resolve, 2000)), {
            loading: `Generating ${item.title} preview...`,
            success: () => {
                // Set fake generated data for preview
                if (item.id === 'pitchDeck') {
                    setGenerated(prev => ({ ...prev, pitchDeck: { total_slides: 9, pitch_deck: { slides: [{ slide_number: 1, title: 'Vision & Mission' }, { slide_number: 2, title: 'Problem Statement' }] } } }));
                } else if (item.id === 'calendar') {
                    setGenerated(prev => ({ ...prev, calendar: { total_posts: 12, duration_weeks: 4 } }));
                } else if (item.id === 'email') {
                    setGenerated(prev => ({ ...prev, email: { total_emails: 5, sequence_type: 'onboarding', email_sequence: { emails: [{ email_number: 1, subject_line: 'Welcome to the Future' }] } } }));
                }
                return `${item.title} Preview Ready!`;
            },
            error: 'Failed to generate preview'
        });
    };

    const actions = [
        {
            id: 'pdf',
            title: 'Export PDF Report',
            description: 'Download a professional PDF report with all insights',
            icon: FileText,
            color: 'from-blue-500 to-cyan-500',
            action: handleExportPDF,
            isPremium: false
        },
        {
            id: 'pitchDeck',
            title: 'Generate Pitch Deck',
            shortName: 'Deck',
            description: 'AI-generated investor presentation (9 slides)',
            icon: Presentation,
            color: 'from-purple-500 to-pink-500',
            action: handleGeneratePitchDeck,
            isPremium: true
        },
        {
            id: 'calendar',
            title: 'Content Calendar',
            shortName: 'Calendar',
            description: '4-week multi-channel posting schedule',
            icon: Calendar,
            color: 'from-green-500 to-emerald-500',
            action: handleGenerateContentCalendar,
            isPremium: true
        },
        {
            id: 'email',
            title: 'Email Sequence',
            shortName: 'Emails',
            description: 'Automated drip campaign (5 emails)',
            icon: Mail,
            color: 'from-orange-500 to-red-500',
            action: handleGenerateEmailSequence,
            isPremium: true
        }
    ];

    return (
        <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                    <Download className="w-5 h-5 text-purple-400" />
                    Content Generation & Export
                </CardTitle>
                <CardDescription className="text-slate-400">
                    Generate marketing materials and export your analysis
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {actions.map((item) => {
                        const Icon = item.icon;
                        const isLoading = loading[item.id];
                        const isGenerated = generated[item.id];
                        const isLocked = item.isPremium && !isPremium;

                        // Override action if locked
                        const effectiveAction = isLocked ? () => handleLockedAction(item) : item.action;

                        return (
                            <div
                                key={item.id}
                                className={`relative bg-slate-800/50 rounded-lg p-4 border ${isLocked ? 'border-slate-700' : 'border-slate-700 hover:border-purple-500/50'
                                    } transition-all`}
                            >
                                <div className="flex items-start gap-3">
                                    <div className={`p-2 rounded-lg bg-gradient-to-br ${item.color}`}>
                                        <Icon className="w-5 h-5 text-white" />
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                            <h4 className="text-white font-semibold text-sm">{item.title}</h4>
                                            {item.isPremium && (
                                                <Badge variant="outline" className="text-xs border-purple-400/30 text-purple-400">
                                                    Pro
                                                </Badge>
                                            )}
                                            {isGenerated && (
                                                <CheckCircle2 className="w-4 h-4 text-green-400" />
                                            )}
                                        </div>
                                        <p className="text-slate-400 text-xs mb-3">{item.description}</p>
                                        <Button
                                            size="sm"
                                            onClick={effectiveAction}
                                            disabled={isLoading}
                                            className={`w-full ${isLocked
                                                ? 'bg-slate-700/50 hover:bg-slate-700 border border-purple-500/30 text-purple-200'
                                                : `bg-gradient-to-r ${item.color} hover:opacity-90`
                                                }`}
                                        >
                                            {isLoading ? (
                                                <>
                                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                                    Generating...
                                                </>
                                            ) : isGenerated ? (
                                                item.id === 'pdf' ? (
                                                    <>
                                                        <Download className="w-4 h-4 mr-2" />
                                                        Download Again
                                                    </>
                                                ) : (
                                                    <>
                                                        <ExternalLink className="w-4 h-4 mr-2" />
                                                        View Generated
                                                    </>
                                                )
                                            ) : isLocked ? (
                                                <>
                                                    <Eye className="w-4 h-4 mr-2" />
                                                    Preview {item.shortName || 'Sample'}
                                                </>
                                            ) : (
                                                <>
                                                    <Icon className="w-4 h-4 mr-2" />
                                                    Generate
                                                </>
                                            )}
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Generated Content Preview */}
                {generated.pitchDeck && (
                    <div className="mt-6 p-4 bg-slate-800/30 rounded-lg border border-purple-500/30">
                        <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                            <Presentation className="w-4 h-4 text-purple-400" />
                            Pitch Deck Preview
                        </h4>
                        <p className="text-slate-300 text-sm mb-2">
                            {generated.pitchDeck.total_slides} slides generated
                        </p>
                        <div className="space-y-2">
                            {generated.pitchDeck.pitch_deck?.slides?.slice(0, 3).map((slide, idx) => (
                                <div key={idx} className="text-xs text-slate-400">
                                    Slide {slide.slide_number}: {slide.title}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {generated.calendar && (
                    <div className="mt-6 p-4 bg-slate-800/30 rounded-lg border border-green-500/30">
                        <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                            <Calendar className="w-4 h-4 text-green-400" />
                            Content Calendar Preview
                        </h4>
                        <p className="text-slate-300 text-sm">
                            {generated.calendar.total_posts} posts scheduled over {generated.calendar.duration_weeks} weeks
                        </p>
                    </div>
                )}

                {generated.email && (
                    <div className="mt-6 p-4 bg-slate-800/30 rounded-lg border border-orange-500/30">
                        <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                            <Mail className="w-4 h-4 text-orange-400" />
                            Email Sequence Preview
                        </h4>
                        <p className="text-slate-300 text-sm mb-2">
                            {generated.email.total_emails} emails in {generated.email.sequence_type} sequence
                        </p>
                        <div className="space-y-2">
                            {generated.email.email_sequence?.emails?.slice(0, 2).map((email, idx) => (
                                <div key={idx} className="text-xs text-slate-400">
                                    Email {email.email_number}: {email.subject_line}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
