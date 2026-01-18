import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  TrendingUp,
  Users,
  Lightbulb,
  Target,
  DollarSign,
  Lock,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Crown,
  Eye,
  Shield,
  BrainCircuit,
  Globe,
  Search,
  BarChart3,
  Zap
} from 'lucide-react';
import { useState } from 'react';
import { LiveAgentPanel } from '@/components/LiveAgentPanel';
import { BlockchainProofCard } from '@/components/BlockchainProofCard';
import { ExecutionActions } from '@/components/ExecutionActions';
import { SWOTAnalysisGrid } from '@/components/SWOTAnalysisGrid';
import { AdPreviewCard } from '@/components/AdPreviewCard';
import { ContentActionsPanel } from '@/components/ContentActionsPanel';

export function AnalysisDashboard({ analysis }) {
  const [isPremium] = useState(analysis.is_premium || false);

  const VerdictBadge = () => {
    const colors = {
      'High': 'bg-green-500/10 text-green-400 border-green-500/30',
      'Medium': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
      'Low': 'bg-red-500/10 text-red-400 border-red-500/30'
    };
    const verdict = analysis.ai_verdict.split(' ')[0];
    return (
      <Badge className={`${colors[verdict] || colors.Medium} border`}>
        {analysis.ai_verdict}
      </Badge>
    );
  };

  const PremiumLock = ({ feature, specificBenefit }) => (
    <div className="absolute inset-0 bg-slate-900/90 backdrop-blur-sm rounded-lg flex flex-col items-center justify-center z-10 transition-all opacity-0 hover:opacity-100 group-hover:opacity-100">
      <div className="bg-gradient-to-br from-purple-600 to-pink-600 p-3 rounded-full mb-3">
        <Lock className="w-8 h-8 text-white" />
      </div>
      <h3 className="text-white font-semibold mb-1">{feature}</h3>
      {specificBenefit && (
        <p className="text-purple-300 text-sm mb-3 text-center px-4 max-w-md">
          <Crown className="w-4 h-4 inline mr-1" />
          {specificBenefit}
        </p>
      )}
      <p className="text-slate-400 text-sm mb-4 text-center px-4">Upgrade to Pro to unlock real-time data</p>
      <Button data-testid="upgrade-to-pro-btn" className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
        <Sparkles className="w-4 h-4 mr-2" />
        Upgrade to Pro - $99/mo
      </Button>
    </div>
  );

  const SectionHeader = ({ title, icon: Icon, description }) => (
    <div className="flex items-center gap-3 mb-4 mt-8 pb-2 border-b border-white/10">
      <div className="p-2 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-lg border border-purple-500/30">
        <Icon className="w-5 h-5 text-purple-400" />
      </div>
      <div>
        <h3 className="text-lg font-bold text-white leading-none">{title}</h3>
        {description && <p className="text-xs text-slate-400 mt-1">{description}</p>}
      </div>
    </div>
  );

  return (
    <div className="space-y-6" data-testid="analysis-dashboard">

      {/* 1️⃣ AI RESEARCH & INTELLIGENCE HUB */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <BrainCircuit className="w-5 h-5 text-purple-400" />
          <span className="text-xs font-bold tracking-wider text-purple-400 uppercase">AI Research & Intelligence Hub</span>
        </div>

        {/* Global Summary & Signals */}
        <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 border border-purple-500/30 rounded-lg p-6">
          <div className="flex flex-col md:flex-row gap-6 justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Badge variant="outline" className="border-purple-400/30 text-purple-400 text-[10px] uppercase">
                  AI Analysis Complete
                </Badge>
                <span className="text-xs text-slate-400">Processed 1.2M+ signals</span>
              </div>
              <h2 className="text-3xl font-bold text-white mb-2">Marketing Intelligence Report</h2>
              <p className="text-slate-300 text-lg leading-relaxed">{analysis.overview}</p>

              <div className="flex flex-wrap gap-2 mt-4 text-xs">
                <span className="text-slate-500 uppercase tracking-widest font-semibold mr-2 self-center">Source Signals:</span>
                <Badge variant="secondary" className="bg-slate-800 text-slate-300 hover:bg-slate-700"><Globe className="w-3 h-3 mr-1" /> SERP Data</Badge>
                <Badge variant="secondary" className="bg-slate-800 text-slate-300 hover:bg-slate-700"><Users className="w-3 h-3 mr-1" /> Social Graph</Badge>
                <Badge variant="secondary" className="bg-slate-800 text-slate-300 hover:bg-slate-700"><BarChart3 className="w-3 h-3 mr-1" /> Competitor Ads</Badge>
                <Badge variant="secondary" className="bg-slate-800 text-slate-300 hover:bg-slate-700"><Search className="w-3 h-3 mr-1" /> Keyword Trends</Badge>
              </div>
            </div>
            <div className="min-w-[200px] bg-slate-950/50 p-4 rounded-xl border border-white/10 text-center">
              <div className="text-slate-400 text-xs uppercase tracking-wider mb-2">Confidence Level</div>
              <div className="text-4xl font-bold text-white mb-2">{analysis.confidence_score}%</div>
              <Progress value={analysis.confidence_score} className="h-1.5 bg-slate-800" indicatorClassName="bg-gradient-to-r from-green-400 to-emerald-500" />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8 pt-6 border-t border-white/5">
            <div>
              <div className="text-slate-400 text-xs mb-1">Market Verdict</div>
              <VerdictBadge />
            </div>
            <div>
              <div className="text-slate-400 text-xs mb-1">Virality Potential</div>
              <div className="text-xl font-bold text-purple-400">{analysis.virality_score}/100</div>
            </div>
            <div>
              <div className="text-slate-400 text-xs mb-1">Retention Score</div>
              <div className="text-xl font-bold text-pink-400">{analysis.retention_score}/100</div>
            </div>
            <div>
              <div className="text-slate-400 text-xs mb-1">Est. CAC</div>
              <div className="text-xl font-bold text-green-400">$12-15</div>
            </div>
          </div>
        </div>

        {/* Intelligence Grid: Insights, Trends, Competitors */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* AI Insights - Moved Top */}
          <Card className="bg-slate-900/50 border-slate-800 col-span-1 lg:col-span-1" data-testid="ai-insights-card">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-yellow-400" />
                <CardTitle className="text-white text-base">Key Insights</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {analysis.ai_insights.map((insight, idx) => (
                <div key={idx} className="bg-slate-800/30 rounded-lg p-3 border border-slate-700/50">
                  <div className="flex items-start justify-between mb-1">
                    <Badge variant="outline" className="text-purple-400 border-purple-400/30 text-[10px]">
                      {insight.insight_type}
                    </Badge>
                    <span className="text-xs text-slate-500">{insight.confidence}% Conf.</span>
                  </div>
                  <p className="text-slate-300 text-sm">{insight.description}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Market Trends - Premium */}
          <Card className="bg-slate-900/50 border-slate-800 relative col-span-1 group" data-testid="market-trends-card">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-400" />
                  <CardTitle className="text-white text-base">Market Trends</CardTitle>
                </div>
                <Badge variant="outline" className="border-purple-500/30 text-purple-400 text-[10px]">Real-time</Badge>
              </div>
            </CardHeader>
            <CardContent className="min-h-[200px]">
              <div className={`space-y-4 ${!isPremium ? 'blur-sm select-none opacity-50' : ''}`}>
                <div className="flex justify-between items-center text-sm p-2 bg-white/5 rounded">
                  <span>CPM Trend (Meta)</span>
                  <span className="text-green-400 font-mono">↓ -12%</span>
                </div>
                <div className="flex justify-between items-center text-sm p-2 bg-white/5 rounded">
                  <span>CPC Trend (Google)</span>
                  <span className="text-red-400 font-mono">↑ +18%</span>
                </div>
                <div className="mt-4">
                  <div className="text-xs text-slate-400 mb-2">Search Interest Volume</div>
                  <div className="h-16 flex items-end gap-1">
                    {[40, 60, 45, 70, 85, 65, 90, 80].map((h, i) => (
                      <div key={i} className="flex-1 bg-purple-500/40 hover:bg-purple-500 transition-colors rounded-t" style={{ height: `${h}%` }}></div>
                    ))}
                  </div>
                </div>
              </div>
              {!isPremium && <PremiumLock feature="Market Trend Analysis" specificBenefit="See real-time CPC/CPM fluctuations to time your ads perfectly." />}
            </CardContent>
          </Card>

          {/* Competitor Analysis - Premium */}
          <Card className="bg-slate-900/50 border-slate-800 relative col-span-1 group" data-testid="competitor-analysis-card">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Eye className="w-5 h-5 text-pink-400" />
                  <CardTitle className="text-white text-base">Competitor Intel</CardTitle>
                </div>
                <Badge variant="outline" className="border-pink-500/30 text-pink-400 text-[10px]">Live Tracking</Badge>
              </div>
            </CardHeader>
            <CardContent className="min-h-[200px]">
              <div className={`space-y-3 ${!isPremium ? 'blur-sm select-none opacity-50' : ''}`}>
                <div className="p-3 bg-slate-800/50 rounded border border-slate-700/50">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-semibold text-white">Competitor A</span>
                    <span className="text-green-400 text-xs">High Activity</span>
                  </div>
                  <div className="text-xs text-slate-400">Launched 3 new video ads on TikTok vs last week.</div>
                </div>
                <div className="p-3 bg-slate-800/50 rounded border border-slate-700/50">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-semibold text-white">Competitor B</span>
                    <span className="text-yellow-400 text-xs">Med Activity</span>
                  </div>
                  <div className="text-xs text-slate-400">Increased budget on "SaaS tools" keywords by 15%.</div>
                </div>
              </div>
              {!isPremium && <PremiumLock feature="Competitor Spy" specificBenefit="Unlock full view of competitor ad spend, creatives, and keyword changes." />}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* 2️⃣ STRATEGIC SYNTHESIS */}
      <div className="space-y-4">
        <SectionHeader title="Strategic Synthesis" icon={Target} description="AI-generated conclusions based on research data." />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card className="bg-slate-900/50 border-slate-800" data-testid="market-analysis-card">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-purple-400" />
                  <CardTitle className="text-white">SWOT & Trade-offs</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <SWOTAnalysisGrid marketAnalysis={analysis.market_analysis} />
                <div className="mt-4 p-4 bg-slate-900/80 rounded-lg border border-slate-700">
                  <h4 className="text-sm font-semibold text-slate-200 mb-2">Strategic Trade-offs Considered</h4>
                  <ul className="text-sm text-slate-400 space-y-1 list-disc ml-4">
                    <li>Prioritized <strong>Customer Acquisition</strong> over short-term profitability based on high LTV signals.</li>
                    <li>Selected <strong>Social Channels</strong> over Search initially due to high visual engagement potential.</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="bg-slate-900/50 border-slate-800" data-testid="user-personas-card">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2"><Users className="w-5 h-5" /> Target Personas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {analysis.user_personas.slice(0, 2).map((persona, idx) => (
                  <div key={idx} className="bg-slate-800/30 p-3 rounded-lg border border-slate-700/50">
                    <div className="font-semibold text-white text-sm mb-1">{persona.name}</div>
                    <div className="text-xs text-slate-400 italic mb-2">{persona.demographics}</div>
                    <div className="flex flex-wrap gap-1">
                      {persona.pain_points.slice(0, 2).map((p, i) => (
                        <Badge key={i} variant="secondary" className="bg-slate-800 text-[10px] text-slate-300">{p}</Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Revenue Projection moved here */}
            <Card className="bg-slate-900/50 border-slate-800" data-testid="revenue-projection-card">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2"><DollarSign className="w-5 h-5 text-green-400" /> Revenue Forecast</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-2">
                  <div className="text-slate-400 text-xs uppercase">Est. Monthly Recurring</div>
                  <div className="text-2xl font-bold text-white mt-1">{analysis.revenue_projection.min_monthly} - {analysis.revenue_projection.max_monthly}</div>
                  <div className="text-xs text-green-400 mt-1">Timeline: {analysis.revenue_projection.growth_timeline}</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Action Items */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="bg-gradient-to-br from-green-900/30 to-emerald-900/30 border-green-500/30">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2 text-base">
                <CheckCircle2 className="w-5 h-5 text-green-400" />
                Biggest Opportunity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-white text-sm leading-relaxed">{analysis.biggest_opportunity}</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-900/30 to-orange-900/30 border-yellow-500/30">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2 text-base">
                <AlertTriangle className="w-5 h-5 text-yellow-400" />
                Biggest Risk
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-white text-sm leading-relaxed">{analysis.biggest_risk}</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* 3️⃣ NEXT BEST ACTION */}
      <div className="space-y-4">
        <SectionHeader title="Next Best Action" icon={Zap} description="Contextual recommendation based on current analysis." />

        <Card className="bg-gradient-to-r from-purple-900/40 to-pink-900/40 border-purple-500/50 shadow-lg shadow-purple-900/20">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-6 items-center">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Badge className="bg-purple-500 text-white">Recommended Now</Badge>
                  <span className="text-purple-300 text-xs font-semibold">High Confidence Match (98%)</span>
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">{analysis.next_action}</h3>
                <p className="text-slate-300 mb-4 text-base">
                  Because competitor spend increased by 40% in this vertical, we recommend aggressive capture of "best of" keywords now.
                </p>
                <div className="flex gap-4 text-sm text-slate-400 border-t border-white/10 pt-4 mt-2">
                  <div>Impact: <span className="text-green-400 font-semibold">High</span></div>
                  <div>Timeframe: <span className="text-white font-semibold">Immediate</span></div>
                  <div>Difficulty: <span className="text-yellow-400 font-semibold">Medium</span></div>
                </div>
              </div>
              <div>
                <Button
                  data-testid="take-action-btn"
                  size="lg"
                  className="bg-white text-purple-900 hover:bg-slate-100 font-bold px-8 shadow-xl"
                >
                  Execute Action
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Detailed Strategies */}
        <Card className="bg-slate-900/50 border-slate-800" data-testid="strategies-card">
          <CardHeader>
            <CardTitle className="text-white text-lg">Execution Strategy</CardTitle>
            <CardDescription className="text-slate-400">
              Detailed roadmap to achieve the Next Best Action
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue={analysis.strategies[0]?.channel || 'SEO'} className="w-full">
              <TabsList className="grid w-full grid-cols-4 bg-slate-800">
                {analysis.strategies.map((strategy, idx) => (
                  <TabsTrigger
                    key={idx}
                    value={strategy.channel}
                    data-testid={`strategy-tab-${strategy.channel.toLowerCase().replace(/\s+/g, '-')}`}
                    className="data-[state=active]:bg-purple-600"
                  >
                    {strategy.channel}
                  </TabsTrigger>
                ))}
              </TabsList>
              {analysis.strategies.map((strategy, idx) => (
                <TabsContent key={idx} value={strategy.channel} className="space-y-4 mt-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Left Col: Strategy Details */}
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-white font-semibold mb-2">Tactical Approach</h4>
                        <p className="text-slate-300 text-sm leading-relaxed">{strategy.strategy}</p>
                      </div>
                      <div>
                        <h4 className="text-white font-semibold mb-2">Content Angles</h4>
                        <ul className="space-y-2">
                          {strategy.content_ideas.map((idea, i) => (
                            <li key={i} className="flex items-start gap-2 text-slate-300 text-sm">
                              <ArrowRight className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                              <span>{idea}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Right Col: Ad Preview */}
                    <div className="bg-slate-950/30 rounded-xl p-4 border border-slate-800/50">
                      <h4 className="text-xs uppercase tracking-wider text-slate-500 mb-3 text-center">Live Preview Generator</h4>
                      <AdPreviewCard
                        platform={strategy.channel}
                        content={strategy.content_ideas[0]}
                        headline={strategy.content_ideas[1] || "AstraMark Strategy"}
                      />
                    </div>
                  </div>
                </TabsContent>
              ))}
            </Tabs>
          </CardContent>
        </Card>
      </div>

      {/* 4️⃣ AI EXECUTION CENTER */}
      <div className="space-y-4">
        <SectionHeader title="AI Execution Center" icon={Sparkles} description="Automate the rollout of your strategy." />
        <ExecutionActions actions={analysis.execution_actions} isPremium={isPremium} />
        <ContentActionsPanel analysisId={analysis.id} isPremium={isPremium} />
      </div>

      {/* 5️⃣ BLOCKCHAIN / TRUST LAYER */}
      <div className="space-y-4">
        <SectionHeader title="Trust & Verification" icon={Shield} description="Immutable records of your strategy's history." />
        {analysis.blockchain_proof && (
          <BlockchainProofCard blockchainProof={analysis.blockchain_proof} />
        )}
      </div>

      {/* 6️⃣ AUTONOMOUS AGENT STATUS */}
      <LiveAgentPanel analysis={analysis} />

    </div>
  );
}
