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
  Sparkles
} from 'lucide-react';
import { useState } from 'react';

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

  const PremiumLock = ({ feature }) => (
    <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm rounded-lg flex flex-col items-center justify-center z-10">
      <Lock className="w-12 h-12 text-purple-400 mb-3" />
      <h3 className="text-white font-semibold mb-2">{feature}</h3>
      <p className="text-slate-400 text-sm mb-4 text-center px-4">Unlock with Pro</p>
      <Button data-testid="upgrade-to-pro-btn" className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
        <Sparkles className="w-4 h-4 mr-2" />
        Upgrade to Pro
      </Button>
    </div>
  );

  return (
    <div className="space-y-6" data-testid="analysis-dashboard">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 border border-purple-500/30 rounded-lg p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">Marketing Intelligence Report</h2>
            <p className="text-slate-300">{analysis.overview}</p>
          </div>
          <VerdictBadge />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">Confidence Score</div>
            <div className="flex items-center gap-3">
              <div className="text-3xl font-bold text-white">{analysis.confidence_score}%</div>
              <Progress value={analysis.confidence_score} className="flex-1 h-2" />
            </div>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">Virality Score</div>
            <div className="flex items-center gap-3">
              <div className="text-3xl font-bold text-purple-400">{analysis.virality_score}/100</div>
              <Progress value={analysis.virality_score} className="flex-1 h-2" />
            </div>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-1">Retention Score</div>
            <div className="flex items-center gap-3">
              <div className="text-3xl font-bold text-pink-400">{analysis.retention_score}/100</div>
              <Progress value={analysis.retention_score} className="flex-1 h-2" />
            </div>
          </div>
        </div>
      </div>

      {/* Market Analysis */}
      <Card className="bg-slate-900/50 border-slate-800" data-testid="market-analysis-card">
        <CardHeader>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-400" />
            <CardTitle className="text-white">Market Opportunity</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-slate-400 text-sm mb-1">Market Size</div>
              <div className="text-white font-semibold">{analysis.market_analysis.market_size}</div>
            </div>
            <div>
              <div className="text-slate-400 text-sm mb-1">Growth Rate</div>
              <div className="text-white font-semibold">{analysis.market_analysis.growth_rate}</div>
            </div>
          </div>
          <div>
            <div className="text-slate-400 text-sm mb-2">Entry Barriers</div>
            <div className="text-white">{analysis.market_analysis.entry_barriers}</div>
          </div>
          <div>
            <div className="text-slate-400 text-sm mb-2">Key Opportunities</div>
            <ul className="space-y-2">
              {analysis.market_analysis.opportunities.map((opp, idx) => (
                <li key={idx} className="flex items-start gap-2 text-white">
                  <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                  <span>{opp}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <div className="text-slate-400 text-sm mb-2">Potential Risks</div>
            <ul className="space-y-2">
              {analysis.market_analysis.risks.map((risk, idx) => (
                <li key={idx} className="flex items-start gap-2 text-white">
                  <AlertTriangle className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                  <span>{risk}</span>
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* User Personas */}
      <Card className="bg-slate-900/50 border-slate-800" data-testid="user-personas-card">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-pink-400" />
            <CardTitle className="text-white">Target User Personas</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analysis.user_personas.map((persona, idx) => (
              <div key={idx} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <h4 className="text-white font-semibold mb-3">{persona.name}</h4>
                <div className="space-y-3 text-sm">
                  <div>
                    <span className="text-slate-400">Demographics:</span>
                    <p className="text-white mt-1">{persona.demographics}</p>
                  </div>
                  <div>
                    <span className="text-slate-400">Psychographics:</span>
                    <p className="text-white mt-1">{persona.psychographics}</p>
                  </div>
                  <div>
                    <span className="text-slate-400">Pain Points:</span>
                    <ul className="mt-1 space-y-1">
                      {persona.pain_points.map((point, i) => (
                        <li key={i} className="text-white">• {point}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <span className="text-slate-400">Buying Triggers:</span>
                    <ul className="mt-1 space-y-1">
                      {persona.buying_triggers.map((trigger, i) => (
                        <li key={i} className="text-green-400">• {trigger}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* AI Insights */}
      <Card className="bg-slate-900/50 border-slate-800" data-testid="ai-insights-card">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-yellow-400" />
            <CardTitle className="text-white">AI-Powered Insights</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {analysis.ai_insights.map((insight, idx) => (
              <div key={idx} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <div className="flex items-start justify-between mb-2">
                  <Badge variant="outline" className="text-purple-400 border-purple-400/30">
                    {insight.insight_type}
                  </Badge>
                  <div className="text-slate-400 text-sm">
                    Confidence: <span className="text-white font-semibold">{insight.confidence}%</span>
                  </div>
                </div>
                <p className="text-white">{insight.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Marketing Strategies */}
      <Card className="bg-slate-900/50 border-slate-800" data-testid="strategies-card">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-purple-400" />
            <CardTitle className="text-white">Multi-Channel Marketing Strategies</CardTitle>
          </div>
          <CardDescription className="text-slate-400">
            Actionable strategies for each marketing channel
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
                <div>
                  <h4 className="text-white font-semibold mb-2">Strategy</h4>
                  <p className="text-slate-300">{strategy.strategy}</p>
                </div>
                <div>
                  <h4 className="text-white font-semibold mb-2">Content Ideas</h4>
                  <ul className="space-y-2">
                    {strategy.content_ideas.map((idea, i) => (
                      <li key={i} className="flex items-start gap-2 text-slate-300">
                        <ArrowRight className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
                        <span>{idea}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="text-white font-semibold mb-2">Posting Schedule</h4>
                  <p className="text-slate-300">{strategy.posting_schedule}</p>
                </div>
                <div>
                  <h4 className="text-white font-semibold mb-2">KPI Benchmarks</h4>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(strategy.kpi_benchmarks).map(([key, value], i) => (
                      <div key={i} className="bg-slate-800/50 rounded p-3">
                        <div className="text-slate-400 text-xs mb-1">
                          {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                        </div>
                        <div className="text-white font-semibold">{value}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      {/* Revenue Projection */}
      <Card className="bg-slate-900/50 border-slate-800" data-testid="revenue-projection-card">
        <CardHeader>
          <div className="flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-green-400" />
            <CardTitle className="text-white">Revenue Projections</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-green-900/30 to-emerald-900/30 border border-green-500/30 rounded-lg p-4">
              <div className="text-slate-400 text-sm mb-1">Minimum Monthly</div>
              <div className="text-2xl font-bold text-white">{analysis.revenue_projection.min_monthly}</div>
            </div>
            <div className="bg-gradient-to-br from-green-900/30 to-emerald-900/30 border border-green-500/30 rounded-lg p-4">
              <div className="text-slate-400 text-sm mb-1">Maximum Monthly</div>
              <div className="text-2xl font-bold text-white">{analysis.revenue_projection.max_monthly}</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="text-slate-400 text-sm mb-1">Timeline</div>
              <div className="text-lg font-semibold text-white">{analysis.revenue_projection.growth_timeline}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Competitor Analysis - Premium Feature */}
      <Card className="bg-slate-900/50 border-slate-800 relative" data-testid="competitor-analysis-card">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-purple-400" />
              <CardTitle className="text-white">Competitor Deep-Dive</CardTitle>
            </div>
            <Badge className="bg-purple-500/10 text-purple-400 border-purple-500/30">
              <Lock className="w-3 h-3 mr-1" />
              Pro
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="min-h-[200px]">
          <div className="text-slate-300 blur-sm">
            Detailed competitor analysis, market positioning, and competitive advantages...
          </div>
        </CardContent>
        {!isPremium && <PremiumLock feature="Competitor Analysis" />}
      </Card>

      {/* Action Items */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-gradient-to-br from-green-900/30 to-emerald-900/30 border-green-500/30">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-400" />
              Biggest Opportunity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-white">{analysis.biggest_opportunity}</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-900/30 to-orange-900/30 border-yellow-500/30">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-400" />
              Biggest Risk
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-white">{analysis.biggest_risk}</p>
          </CardContent>
        </Card>
      </div>

      {/* Next Action */}
      <Card className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 border-purple-500/30">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400" />
            Next Best Action
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-white text-lg mb-4">{analysis.next_action}</p>
          <Button 
            data-testid="take-action-btn"
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
          >
            Take Action
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
