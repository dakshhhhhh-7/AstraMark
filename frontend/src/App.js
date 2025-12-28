import { useState } from 'react';
import '@/App.css';
import { BusinessInputForm } from '@/components/BusinessInputForm';
import { AnalysisDashboard } from '@/components/AnalysisDashboard';
import { Toaster } from '@/components/ui/sonner';
import { toast } from 'sonner';

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalysisComplete = (result) => {
    setAnalysisResult(result);
  };

  const handleNewAnalysis = () => {
    setAnalysisResult(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <Toaster position="top-right" richColors />
      
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">AstraMark</h1>
                <p className="text-xs text-slate-400">AI Marketing Intelligence Platform</p>
              </div>
            </div>
            {analysisResult && (
              <button
                data-testid="new-analysis-btn"
                onClick={handleNewAnalysis}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                New Analysis
              </button>
            )}
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
          <p>Powered by AI • Built on Emergent Platform</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
