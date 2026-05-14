/*
Dashboard - Linear-Level Design
*/

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LinearLayout from '../components/LinearLayout';
import { 
  TrendingUp, Users, Target, Zap, Sparkles, BarChart3,
  ArrowUpRight, Activity, Play
} from 'lucide-react';
import { toast } from 'sonner';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [metrics, setMetrics] = useState({
    revenue: 12000,
    leads: 42,
    engagement: 23,
    campaigns: 8,
  });

  const [activities, setActivities] = useState([
    { action: 'Content generated', detail: '5 social media posts created', time: '5m ago', icon: Sparkles },
    { action: 'Ad optimized', detail: 'Campaign CTR increased by 15%', time: '1h ago', icon: TrendingUp },
    { action: 'SEO improved', detail: '3 keywords ranking improved', time: '2h ago', icon: Target },
    { action: 'Lead captured', detail: 'New lead from Facebook', time: '3h ago', icon: Users },
  ]);

  const stats = [
    { 
      label: 'Revenue', 
      value: `₹${(metrics.revenue / 1000).toFixed(1)}K`, 
      change: '+23%',
      icon: TrendingUp,
      color: 'emerald'
    },
    { 
      label: 'New Leads', 
      value: metrics.leads, 
      change: '+18%',
      icon: Users,
      color: 'blue'
    },
    { 
      label: 'Engagement', 
      value: `${metrics.engagement}%`, 
      change: '+15%',
      icon: Activity,
      color: 'violet'
    },
    { 
      label: 'Active Campaigns', 
      value: metrics.campaigns, 
      change: '+2',
      icon: Target,
      color: 'amber'
    },
  ];

  const insights = [
    {
      title: 'Quick Win',
      description: 'Your audience prefers video content. Create 3 reels this week for 2x engagement.',
      action: 'Create Reels',
    },
    {
      title: 'Optimization',
      description: 'Run ads at 8PM for 25% better conversion rates based on your audience data.',
      action: 'Schedule Ads',
    },
    {
      title: 'Growth Opportunity',
      description: 'Expand to Instagram Stories - 40% of your audience is active there.',
      action: 'Start Campaign',
    },
  ];

  const actions = (
    <>
      <button
        onClick={() => navigate('/analysis')}
        className="px-4 py-2 rounded-lg text-sm font-medium text-white/80 hover:text-white hover:bg-white/5 transition-all"
      >
        AI Analysis
      </button>
      <button
        onClick={() => navigate('/astramark')}
        className="px-4 py-2 rounded-lg bg-white text-black text-sm font-medium hover:bg-white/90 transition-all flex items-center gap-2"
      >
        <Play className="w-4 h-4" />
        New Campaign
      </button>
    </>
  );

  return (
    <LinearLayout 
      title="Dashboard" 
      subtitle={`Welcome back, ${user?.name || 'User'}`}
      actions={actions}
    >
      <div className="space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-4">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="p-6 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all cursor-pointer"
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
          {/* AI Insights */}
          <div className="col-span-2 p-6 rounded-xl border border-white/5 bg-white/[0.02]">
            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-1">AI Insights & Recommendations</h2>
              <p className="text-sm text-white/50">Personalized growth opportunities</p>
            </div>

            <div className="space-y-4">
              {insights.map((insight, index) => (
                <div
                  key={index}
                  className="p-4 rounded-lg border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all"
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-xs font-medium px-2 py-1 rounded-md bg-violet-500/10 text-violet-400">
                      {insight.title}
                    </span>
                  </div>
                  <p className="text-sm text-white/70 mb-3">{insight.description}</p>
                  <button className="text-sm font-medium text-white/80 hover:text-white transition-all flex items-center gap-1">
                    {insight.action}
                    <ArrowUpRight className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Activity Feed */}
          <div className="p-6 rounded-xl border border-white/5 bg-white/[0.02]">
            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-1">Recent Activity</h2>
              <p className="text-sm text-white/50">Live updates</p>
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
              description: 'Create 10 social posts instantly',
              icon: Sparkles,
              action: () => navigate('/analysis')
            },
            { 
              title: 'Run Ads', 
              description: 'Launch optimized campaigns',
              icon: Target,
              action: () => navigate('/astramark')
            },
            { 
              title: 'View Analytics', 
              description: 'Track performance metrics',
              icon: BarChart3,
              action: () => toast.info('Analytics coming soon!')
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

        {/* Growth Score */}
        <div className="p-8 rounded-xl border border-white/5 bg-white/[0.02] text-center">
          <div className="inline-flex items-center justify-center w-32 h-32 rounded-full border-4 border-emerald-500/20 bg-emerald-500/5 mb-4">
            <div className="text-center">
              <div className="text-4xl font-bold text-emerald-400">87</div>
              <div className="text-xs text-white/50">Growth Score</div>
            </div>
          </div>
          <h3 className="text-lg font-semibold mb-2">Excellent Performance!</h3>
          <p className="text-sm text-white/50 max-w-md mx-auto">
            Your marketing is performing above average. Keep up the great work!
          </p>
        </div>
      </div>
    </LinearLayout>
  );
}
