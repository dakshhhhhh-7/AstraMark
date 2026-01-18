import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Activity, AlertTriangle, Info, TrendingUp, Clock, PauseCircle, PlayCircle, Check, X, Sliders } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

export function LiveAgentPanel({ analysis }) {
  const [isPaused, setIsPaused] = useState(false);
  const [aggressiveness, setAggressiveness] = useState('balanced');
  const [goal, setGoal] = useState('roas');

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <AlertTriangle className="w-4 h-4 text-red-400" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      default: return <Info className="w-4 h-4 text-blue-400" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'border-red-500/30 bg-red-500/10';
      case 'warning': return 'border-yellow-500/30 bg-yellow-500/10';
      default: return 'border-blue-500/30 bg-blue-500/10';
    }
  };

  const handleAction = (id, action) => {
    toast.success(`Action ${action} for item ${id}`);
  };

  return (
    <Card className="bg-gradient-to-br from-purple-900/30 to-indigo-900/30 border-purple-500/30" data-testid="live-agent-panel">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="relative">
              {isPaused ? (
                <PauseCircle className="w-5 h-5 text-yellow-400" />
              ) : (
                <>
                  <Activity className="w-5 h-5 text-purple-400" />
                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                </>
              )}
            </div>
            <CardTitle className="text-white">Autonomous Agent Status</CardTitle>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-slate-900/50 rounded-full px-3 py-1 border border-slate-700">
              <span className="text-xs text-slate-400">Autopilot</span>
              <Switch
                checked={!isPaused}
                onCheckedChange={(checked) => setIsPaused(!checked)}
                className="data-[state=checked]:bg-green-500"
              />
            </div>
            <Badge className={`${isPaused ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' : 'bg-green-500/20 text-green-400 border-green-500/30'}`}>
              {isPaused ? 'PAUSED' : 'ACTIVE'}
            </Badge>
          </div>
        </div>

        {/* Agent Controls */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4 p-4 bg-slate-900/40 rounded-lg border border-purple-500/20">
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Aggressiveness</label>
            <div className="flex gap-1">
              {['Low', 'Balanced', 'High'].map((level) => (
                <button
                  key={level}
                  onClick={() => setAggressiveness(level.toLowerCase())}
                  className={`px-2 py-1 rounded text-xs transition-colors border ${aggressiveness === level.toLowerCase()
                      ? 'bg-purple-600 text-white border-purple-500'
                      : 'bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700'
                    }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Optimization Goal</label>
            <div className="flex gap-1">
              {['Leads', 'ROAS', 'CAC'].map((g) => (
                <button
                  key={g}
                  onClick={() => setGoal(g.toLowerCase())}
                  className={`px-2 py-1 rounded text-xs transition-colors border ${goal === g.toLowerCase()
                      ? 'bg-blue-600 text-white border-blue-500'
                      : 'bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700'
                    }`}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center justify-end">
            <div className="text-right">
              <div className="text-xs text-slate-400">Next Optimization</div>
              <div className="text-sm text-white font-mono flex items-center justify-end gap-1">
                <Clock className="w-3 h-3 text-purple-400" /> 04:12:30
              </div>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Live Market Signals - Now Actionable */}
        {analysis.market_signals && analysis.market_signals.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm font-semibold text-purple-300 flex items-center gap-2">
              <div className="h-px flex-1 bg-purple-500/30" />
              Pending Decisions
              <div className="h-px flex-1 bg-purple-500/30" />
            </div>
            {analysis.market_signals.map((signal, idx) => (
              <div
                key={idx}
                className={`rounded-lg p-3 border ${getSeverityColor(signal.severity)} transition-all hover:bg-opacity-20`}
                data-testid={`market-signal-${idx}`}
              >
                <div className="flex items-start gap-3">
                  {getSeverityIcon(signal.severity)}
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <div className="text-white text-sm font-medium mb-1">
                        {signal.message}
                      </div>
                      <Badge variant="outline" className="text-[10px] border-slate-600 text-slate-400">
                        {signal.detected_at}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-300 mb-3">
                      Suggested Action: Adjust ad spend distribution to reflect new trend.
                    </p>

                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" className="h-7 text-xs border-green-500/30 text-green-400 hover:bg-green-950 hover:text-green-300" onClick={() => handleAction(idx, 'Approve')}>
                        <Check className="w-3 h-3 mr-1" /> Approve
                      </Button>
                      <Button size="sm" variant="outline" className="h-7 text-xs border-red-500/30 text-red-400 hover:bg-red-950 hover:text-red-300" onClick={() => handleAction(idx, 'Reject')}>
                        <X className="w-3 h-3 mr-1" /> Reject
                      </Button>
                      <Button size="sm" variant="ghost" className="h-7 text-xs text-slate-400 hover:text-white">
                        Modify
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* AI Learning Updates */}
        {analysis.ai_learning_updates && analysis.ai_learning_updates.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm font-semibold text-green-300 flex items-center gap-2">
              <div className="h-px flex-1 bg-green-500/30" />
              Recent Auto-Optimizations
              <div className="h-px flex-1 bg-green-500/30" />
            </div>
            {analysis.ai_learning_updates.map((update, idx) => (
              <div
                key={idx}
                className="rounded-lg p-3 border border-green-500/30 bg-green-500/10"
                data-testid={`learning-update-${idx}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <Badge variant="outline" className="text-green-400 border-green-400/30 text-xs">
                    {update.update_type}
                  </Badge>
                  <span className="text-xs text-green-400 font-semibold">{update.improvement_metric}</span>
                </div>
                <p className="text-white text-sm">{update.learning_description}</p>
              </div>
            ))}
          </div>
        )}

        <div className="text-xs text-center text-slate-400 pt-2 border-t border-purple-500/20 flex justify-center items-center gap-2">
          <Activity className="w-3 h-3" />
          Agent is continuously monitoring market conditions
        </div>
      </CardContent>
    </Card>
  );
}
