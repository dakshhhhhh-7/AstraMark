import { useState } from 'react';
import { BusinessInputForm } from '@/components/BusinessInputForm';
import { AnalysisDashboard } from '@/components/AnalysisDashboard';
import { PricingModal } from '@/components/PricingModal';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';

export function Dashboard() {
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isPricingOpen, setIsPricingOpen] = useState(false);
    const { user, logout } = useAuth();

    const handleAnalysisComplete = (result) => {
        setAnalysisResult(result);
    };

    const handleNewAnalysis = () => {
        setAnalysisResult(null);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            <PricingModal isOpen={isPricingOpen} onClose={() => setIsPricingOpen(false)} />

            {/* Header */}
            <header className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-50">
                <div className="container mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center cursor-pointer" onClick={handleNewAnalysis}>
                                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <div className="cursor-pointer" onClick={handleNewAnalysis}>
                                <h1 className="text-2xl font-bold text-white">AstraMark</h1>
                                <p className="text-xs text-slate-400">AI Marketing Intelligence Platform</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="text-slate-400 text-sm hidden md:inline">
                                Welcome, {user?.full_name || 'User'}
                            </span>
                            <button
                                onClick={() => setIsPricingOpen(true)}
                                className="text-slate-300 hover:text-white transition-colors"
                            >
                                Pricing
                            </button>
                            {analysisResult && (
                                <button
                                    data-testid="new-analysis-btn"
                                    onClick={handleNewAnalysis}
                                    className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                                >
                                    New Analysis
                                </button>
                            )}
                            <Button onClick={logout} variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-800">
                                Logout
                            </Button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-8">
                {!analysisResult ? (
                    <BusinessInputForm
                        onAnalysisComplete={handleAnalysisComplete}
                        isLoading={isLoading}
                        setIsLoading={setIsLoading}
                    />
                ) : (
                    <AnalysisDashboard analysis={analysisResult} />
                )}
            </main>

            {/* Footer */}
            <footer className="border-t border-slate-800 mt-16 py-8">
                <div className="container mx-auto px-4 text-center text-slate-400 text-sm">
                    <p>Powered by AstraMark AI • Official Agentic Interface</p>
                </div>
            </footer>
        </div>
    );
}
