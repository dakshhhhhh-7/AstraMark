/*
Analysis Page - Linear-Level Design
*/

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LinearLayout from '../components/LinearLayout';
import { Search, Sparkles, TrendingUp, Target, BarChart3, Zap } from 'lucide-react';
import { toast } from 'sonner';

export default function AnalysisPage() {
  const navigate = useNavigate();
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [analyzing, setAnalyzing] = useState(false);

  const handleAnalyze = async () => {
    if (!websiteUrl) {
      toast.error('Please enter a website URL');
      return;
    }

    setAnalyzing(true);
    toast.loading('Analyzing website...');
    
    // Simulate analysis
    setTimeout(() => {
      setAnalyzing(false);
      toast.success('Analysis complete!');
    }, 3000);
  };

  const tools = [
    {
      title: 'Website Analysis',
      description: 'Complete SEO and performance audit',
      icon: Search,
      color: 'blue',
    },
    {
      title: 'Content Generator',
      description: 'Create viral social media posts',
      icon: Sparkles,
      color: 'violet',
    },
    {
      title: 'Competitor Analysis',
      description: 'Track and analyze competitors',
      icon: Target,
      color: 'emerald',
    },
    {
      title: 'SEO Optimizer',
      description: 'Improve search rankings',
      icon: TrendingUp,
      color: 'amber',
    },
    {
      title: 'Performance Tracker',
      description: 'Monitor campaign metrics',
      icon: BarChart3,
      color: 'blue',
    },
    {
      title: 'AI Recommendations',
      description: 'Get personalized growth tips',
      icon: Zap,
      color: 'violet',
    },
  ];

  const actions = (
    <button
      onClick={() => navigate('/astramark')}
      className="px-4 py-2 rounded-lg bg-white text-black text-sm font-medium hover:bg-white/90 transition-all"
    >
      Back to Dashboard
    </button>
  );

  return (
    <LinearLayout 
      title="AI Studio" 
      subtitle="Analyze, optimize, and grow your business with AI"
      actions={actions}
    >
      <div className="space-y-6">
        {/* Analysis Input */}
        <div className="p-8 rounded-xl border border-white/5 bg-white/[0.02]">
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-semibold mb-2">AI Website Analysis</h2>
              <p className="text-white/50">
                Get comprehensive insights about any website in seconds
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2 text-white/70">
                  Website URL
                </label>
                <input
                  type="url"
                  value={websiteUrl}
                  onChange={(e) => setWebsiteUrl(e.target.value)}
                  placeholder="https://example.com"
                  className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all text-white placeholder:text-white/30"
                />
              </div>

              <button
                onClick={handleAnalyze}
                disabled={analyzing || !websiteUrl}
                className="w-full px-6 py-4 rounded-lg bg-white text-black font-medium hover:bg-white/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {analyzing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Analyze Website
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* AI Tools Grid */}
        <div>
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-1">AI Marketing Tools</h2>
            <p className="text-sm text-white/50">
              Powerful tools to grow your business
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {tools.map((tool) => (
              <button
                key={tool.title}
                onClick={() => toast.info(`${tool.title} coming soon!`)}
                className="p-6 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all text-left group"
              >
                <div className={`w-12 h-12 rounded-xl bg-${tool.color}-500/10 flex items-center justify-center mb-4 group-hover:bg-${tool.color}-500/20 transition-all`}>
                  <tool.icon className={`w-6 h-6 text-${tool.color}-400`} />
                </div>
                <h3 className="font-medium mb-2">{tool.title}</h3>
                <p className="text-sm text-white/50">{tool.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Recent Analyses */}
        <div className="p-6 rounded-xl border border-white/5 bg-white/[0.02]">
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-1">Recent Analyses</h2>
            <p className="text-sm text-white/50">Your analysis history</p>
          </div>

          <div className="text-center py-12">
            <Search className="w-12 h-12 text-white/20 mx-auto mb-4" />
            <p className="text-white/50 mb-4">No analyses yet</p>
            <button
              onClick={() => document.querySelector('input[type="url"]').focus()}
              className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-sm font-medium transition-all"
            >
              Start Your First Analysis
            </button>
          </div>
        </div>
      </div>
    </LinearLayout>
  );
}
