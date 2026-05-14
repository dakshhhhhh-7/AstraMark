/*
ASTRAMARK ULTIMATE - Linear-Level UI/UX
World-class design with perfect alignment, spacing, and interactions
*/

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGrowthOS } from '../contexts/GrowthOSContext';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';
import { 
  Sparkles, TrendingUp, Target, Zap, BarChart3, Users, 
  Mail, Search, Settings, CreditCard, Bot, Play, Pause,
  ArrowUpRight, Activity, CheckCircle2, Clock, Rocket
} from 'lucide-react';

export default function AstraMarkDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const {
    dailyActions,
    campaigns,
    autonomousStatus,
    loading,
    launchCampaign,
    enableAutonomous,
    disableAutonomous,
    analyzeWebsite,
    generateViralContent,
  } = useGrowthOS();

  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [campaignGoal, setCampaignGoal] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  // Stats with real data
  const stats = [
    { 
      label: 'Revenue Growth', 
      value: '₹1.24L', 
      change: '+18%', 
      trend: 'up',
      icon: TrendingUp,
      color: 'emerald'
    },
    { 
      label: 'Leads Generated', 
      value: '428', 
      change: '+31%', 
      trend: 'up',
      icon: Users,
      color: 'blue'
    },
    { 
      label: 'Campaign ROI', 
      value: '4.7x', 
      change: '+12%', 
      trend: 'up',
      icon: Target,
      color: 'violet'
    },
    { 
      label: 'Active Automations', 
      value: autonomousStatus?.enabled ? '16' : '0', 
      change: '+6%', 
      trend: 'up',
      icon: Zap,
      color: 'amber'
    },
  ];

  // AI Agents
  const agents = [
    { name: 'Content Agent', status: autonomousStatus?.enabled ? 'active' : 'idle', icon: Sparkles },
    { name: 'SEO Agent', status: autonomousStatus?.enabled ? 'active' : 'idle', icon: Search },
    { name: 'Ads Agent', status: autonomousStatus?.enabled ? 'active' : 'idle', icon: Target },
    { name: 'Analytics Agent', status: autonomousStatus?.enabled ? 'active' : 'idle', icon: BarChart3 },
    { name: 'Conversion Agent', status: autonomousStatus?.enabled ? 'active' : 'idle', icon: TrendingUp },
    { name: 'Email Agent', status: autonomousStatus?.enabled ? 'active' : 'idle', icon: Mail },
  ];

  // Recent activities
  const [activities, setActivities] = useState([
    { action: 'Campaign optimized', detail: 'Meta Ads budget increased by 18%', time: '2m ago', icon: TrendingUp },
    { action: 'Content generated', detail: '12 viral Instagram posts created', time: '15m ago', icon: Sparkles },
    { action: 'SEO improved', detail: 'Ranking increased by 18%', time: '1h ago', icon: ArrowUpRight },
    { action: 'Email sent', detail: 'Campaign achieved 42% open rate', time: '2h ago', icon: Mail },
  ]);

  // Handle campaign launch
  const handleLaunchCampaign = async () => {
    if (!campaignGoal) {
      toast.error('Please enter a campaign goal');
      return;
    }

    try {
      const result = await launchCampaign({
        goal: campaignGoal,
        channels: ['google_ads', 'facebook_ads', 'email'],
        budget: 10000,
      });
      toast.success('Campaign launched successfully!');
      setShowCampaignModal(false);
      setCampaignGoal('');
      
      setActivities(prev => [
        { 
          action: 'Campaign launched', 
          detail: `"${result.campaign.name}" deployed automatically`, 
          time: 'Just now',
          icon: Rocket 
        },
        ...prev.slice(0, 3)
      ]);
    } catch (error) {
      toast.error('Failed to launch campaign');
    }
  };

  // Handle website analysis
  const handleAnalyzeWebsite = async () => {
    if (!websiteUrl) {
      toast.error('Please enter a website URL');
      return;
    }

    try {
      const result = await analyzeWebsite({ url: websiteUrl });
      toast.success('Analysis complete!');
      setShowAnalysisModal(false);
      navigate('/analysis', { state: { analysisResult: result } });
    } catch (error) {
      toast.error('Failed to analyze website');
    }
  };

  // Handle autonomous toggle
  const handleToggleAutonomous = async () => {
    try {
      if (autonomousStatus?.enabled) {
        await disableAutonomous();
        toast.success('Autonomous mode disabled');
      } else {
        await enableAutonomous({
          budget_limit: 50000,
          channels: ['google_ads', 'facebook_ads', 'email', 'seo'],
        });
        toast.success('Autonomous mode enabled!');
      }
    } catch (error) {
      toast.error('Failed to toggle autonomous mode');
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-screen w-64 border-r border-white/5 bg-[#0A0A0A] flex flex-col z-50">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-white/5">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5" />
            </div>
            <span className="font-semibold text-lg">AstraMark</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {[
            { name: 'Overview', icon: BarChart3, path: '/astramark', active: true },
            { name: 'Campaigns', icon: Target, action: () => setShowCampaignModal(true) },
            { name: 'Analytics', icon: Activity, path: '/dashboard' },
            { name: 'AI Studio', icon: Sparkles, path: '/analysis' },
            { name: 'Automation', icon: Zap, action: handleToggleAutonomous },
          ].map((item) => (
            <button
              key={item.name}
              onClick={() => item.path ? navigate(item.path) : item.action?.()}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                item.active 
                  ? 'bg-white/10 text-white' 
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.name}
            </button>
          ))}
        </nav>

        {/* Bottom section */}
        <div className="p-3 border-t border-white/5 space-y-1">
          <button
            onClick={() => navigate('/settings')}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-white/60 hover:text-white hover:bg-white/5 transition-all"
          >
            <Settings className="w-4 h-4" />
            Settings
          </button>
          <button
            onClick={() => navigate('/pricing')}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-white/60 hover:text-white hover:bg-white/5 transition-all"
          >
            <CreditCard className="w-4 h-4" />
            Billing
          </button>
        </div>

        {/* Upgrade card */}
        <div className="m-3 p-4 rounded-xl bg-gradient-to-br from-violet-500/10 to-purple-600/10 border border-violet-500/20">
          <div className="flex items-center gap-2 mb-2">
            <Rocket className="w-4 h-4 text-violet-400" />
            <span className="text-sm font-semibold">Upgrade to Pro</span>
          </div>
          <p className="text-xs text-white/60 mb-3">
            Unlock unlimited campaigns and advanced AI features
          </p>
          <button 
            onClick={() => navigate('/pricing')}
            className="w-full py-2 px-3 rounded-lg bg-white text-black text-sm font-medium hover:bg-white/90 transition-all"
          >
            Upgrade Now
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 min-h-screen">
        {/* Header */}
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 sticky top-0 bg-[#0A0A0A]/80 backdrop-blur-xl z-40">
          <div>
            <h1 className="text-lg font-semibold">Growth Dashboard</h1>
            <p className="text-sm text-white/50">Welcome back, {user?.name || 'User'}</p>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowAnalysisModal(true)}
              className="px-4 py-2 rounded-lg text-sm font-medium text-white/80 hover:text-white hover:bg-white/5 transition-all"
            >
              AI Audit
            </button>
            <button
              onClick={() => setShowCampaignModal(true)}
              className="px-4 py-2 rounded-lg bg-white text-black text-sm font-medium hover:bg-white/90 transition-all flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              New Campaign
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="p-8 space-y-8">
          {/* Stats Grid */}
          <div className="grid grid-cols-4 gap-4">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="p-6 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all cursor-pointer group"
                onClick={() => navigate('/dashboard')}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-10 h-10 rounded-lg bg-${stat.color}-500/10 flex items-center justify-center`}>
                    <stat.icon className={`w-5 h-5 text-${stat.color}-400`} />
                  </div>
                  <span className={`text-xs font-medium px-2 py-1 rounded-md bg-${stat.color}-500/10 text-${stat.color}-400`}>
                    {stat.change}
                  </span>
                </div>
                <div className="space-y-1">
                  <p className="text-2xl font-semibold">{stat.value}</p>
                  <p className="text-sm text-white/50">{stat.label}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Main Grid */}
          <div className="grid grid-cols-3 gap-6">
            {/* AI Agents */}
            <div className="col-span-2 space-y-6">
              {/* Autonomous Status */}
              <div className="p-6 rounded-xl border border-white/5 bg-white/[0.02]">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-lg font-semibold mb-1">Autonomous Growth Engine</h2>
                    <p className="text-sm text-white/50">
                      {autonomousStatus?.enabled 
                        ? 'AI agents are actively optimizing your campaigns' 
                        : 'Enable autonomous mode to let AI handle your marketing 24/7'}
                    </p>
                  </div>
                  <button
                    onClick={handleToggleAutonomous}
                    disabled={loading}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                      autonomousStatus?.enabled
                        ? 'bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20'
                        : 'bg-white text-black hover:bg-white/90'
                    }`}
                  >
                    {autonomousStatus?.enabled ? (
                      <>
                        <Pause className="w-4 h-4" />
                        Disable
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        Enable
                      </>
                    )}
                  </button>
                </div>

                {/* Agents Grid */}
                <div className="grid grid-cols-2 gap-3">
                  {agents.map((agent) => (
                    <div
                      key={agent.name}
                      className="p-4 rounded-lg border border-white/5 bg-white/[0.02] flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                          agent.status === 'active' 
                            ? 'bg-emerald-500/10' 
                            : 'bg-white/5'
                        }`}>
                          <agent.icon className={`w-4 h-4 ${
                            agent.status === 'active' 
                              ? 'text-emerald-400' 
                              : 'text-white/40'
                          }`} />
                        </div>
                        <span className="text-sm font-medium">{agent.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${
                          agent.status === 'active' 
                            ? 'bg-emerald-400 animate-pulse' 
                            : 'bg-white/20'
                        }`} />
                        <span className={`text-xs ${
                          agent.status === 'active' 
                            ? 'text-emerald-400' 
                            : 'text-white/40'
                        }`}>
                          {agent.status === 'active' ? 'Active' : 'Idle'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Active Campaigns */}
              <div className="p-6 rounded-xl border border-white/5 bg-white/[0.02]">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-lg font-semibold mb-1">Active Campaigns</h2>
                    <p className="text-sm text-white/50">
                      {campaigns.length} campaigns running
                    </p>
                  </div>
                  <button
                    onClick={() => setShowCampaignModal(true)}
                    className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-sm font-medium transition-all"
                  >
                    View All
                  </button>
                </div>

                {campaigns.length > 0 ? (
                  <div className="space-y-3">
                    {campaigns.slice(0, 3).map((campaign) => (
                      <div
                        key={campaign.id}
                        className="p-4 rounded-lg border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all cursor-pointer"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-medium">{campaign.name}</h3>
                          <span className="text-xs px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-400">
                            Active
                          </span>
                        </div>
                        <p className="text-sm text-white/50">{campaign.channels?.join(' • ')}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Bot className="w-12 h-12 text-white/20 mx-auto mb-4" />
                    <p className="text-white/50 mb-4">No active campaigns</p>
                    <button
                      onClick={() => setShowCampaignModal(true)}
                      className="px-4 py-2 rounded-lg bg-white text-black text-sm font-medium hover:bg-white/90 transition-all"
                    >
                      Launch First Campaign
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Activity Feed */}
            <div className="p-6 rounded-xl border border-white/5 bg-white/[0.02]">
              <div className="mb-6">
                <h2 className="text-lg font-semibold mb-1">Recent Activity</h2>
                <p className="text-sm text-white/50">Real-time AI actions</p>
              </div>

              <div className="space-y-4">
                {activities.map((activity, index) => (
                  <div key={index} className="flex gap-3">
                    <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
                      <activity.icon className="w-4 h-4 text-white/60" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium mb-1">{activity.action}</p>
                      <p className="text-xs text-white/50 mb-1">{activity.detail}</p>
                      <p className="text-xs text-white/30">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-3 gap-4">
            {[
              { 
                title: 'Generate Content', 
                description: 'Create viral posts with AI',
                icon: Sparkles,
                action: async () => {
                  try {
                    await generateViralContent({
                      topic: 'business growth',
                      platform: 'linkedin',
                    });
                    toast.success('Content generated!');
                  } catch (error) {
                    toast.error('Failed to generate content');
                  }
                }
              },
              { 
                title: 'Analyze Website', 
                description: 'Get AI-powered insights',
                icon: Search,
                action: () => setShowAnalysisModal(true)
              },
              { 
                title: 'View Analytics', 
                description: 'Track your performance',
                icon: BarChart3,
                action: () => navigate('/dashboard')
              },
            ].map((action) => (
              <button
                key={action.title}
                onClick={action.action}
                className="p-6 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all text-left group"
              >
                <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center mb-4 group-hover:bg-white/10 transition-all">
                  <action.icon className="w-5 h-5 text-white/60 group-hover:text-white transition-all" />
                </div>
                <h3 className="font-medium mb-1">{action.title}</h3>
                <p className="text-sm text-white/50">{action.description}</p>
              </button>
            ))}
          </div>
        </div>
      </main>

      {/* Campaign Modal */}
      {showCampaignModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-lg bg-[#0A0A0A] border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-semibold mb-6">Launch AI Campaign</h2>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium mb-2 text-white/70">Campaign Goal</label>
                <input
                  type="text"
                  value={campaignGoal}
                  onChange={(e) => setCampaignGoal(e.target.value)}
                  placeholder="e.g., Generate 100 qualified leads in 30 days"
                  className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all"
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleLaunchCampaign}
                disabled={loading || !campaignGoal}
                className="flex-1 px-4 py-3 rounded-lg bg-white text-black font-medium hover:bg-white/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Launching...' : 'Launch Campaign'}
              </button>
              <button
                onClick={() => setShowCampaignModal(false)}
                className="px-4 py-3 rounded-lg bg-white/5 hover:bg-white/10 font-medium transition-all"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Modal */}
      {showAnalysisModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-lg bg-[#0A0A0A] border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-semibold mb-6">AI Website Audit</h2>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium mb-2 text-white/70">Website URL</label>
                <input
                  type="url"
                  value={websiteUrl}
                  onChange={(e) => setWebsiteUrl(e.target.value)}
                  placeholder="https://example.com"
                  className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all"
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleAnalyzeWebsite}
                disabled={loading || !websiteUrl}
                className="flex-1 px-4 py-3 rounded-lg bg-white text-black font-medium hover:bg-white/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Analyzing...' : 'Start Analysis'}
              </button>
              <button
                onClick={() => setShowAnalysisModal(false)}
                className="px-4 py-3 rounded-lg bg-white/5 hover:bg-white/10 font-medium transition-all"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
