import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, AlertTriangle, Info, TrendingUp, Clock } from 'lucide-react';

export function LiveAgentPanel({ analysis }) {
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

  return (
    <Card className="bg-gradient-to-br from-purple-900/30 to-indigo-900/30 border-purple-500/30" data-testid="live-agent-panel">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="relative">
              <Activity className="w-5 h-5 text-purple-400" />
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            </div>
            <CardTitle className="text-white">Autonomous Agent Status</CardTitle>
          </div>
          <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
            <span className="relative flex h-2 w-2 mr-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            {analysis.monitoring_status === 'active' ? 'LIVE MONITORING' : 'STANDBY'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Monitoring Info */}
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2 text-slate-300">
            <Clock className="w-4 h-4" />
            <span>Last market scan: <span className="text-white font-semibold">{analysis.last_market_scan}</span></span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <TrendingUp className="w-4 h-4" />
            <span>Auto-optimizing strategies</span>
          </div>
        </div>

        {/* Live Market Signals */}
        {analysis.market_signals && analysis.market_signals.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm font-semibold text-purple-300 flex items-center gap-2">
              <div className="h-px flex-1 bg-purple-500/30" />
              Live Market Signals
              <div className="h-px flex-1 bg-purple-500/30" />
            </div>
            {analysis.market_signals.map((signal, idx) => (
              <div 
                key={idx} 
                className={`rounded-lg p-3 border ${getSeverityColor(signal.severity)}`}
                data-testid={`market-signal-${idx}`}
              >
                <div className="flex items-start gap-3">
                  {getSeverityIcon(signal.severity)}
                  <div className="flex-1">
                    <div className="text-white text-sm font-medium mb-1">
                      {signal.message}
                    </div>
                    <div className="text-xs text-slate-400">
                      Detected {signal.detected_at}
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
              AI Learning Updates
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
                <div className="text-xs text-slate-400 mt-2">{update.timestamp}</div>
              </div>
            ))}
          </div>
        )}

        <div className="text-xs text-center text-slate-400 pt-2 border-t border-purple-500/20">
          🤖 AI Agent continuously monitors market conditions and auto-adjusts strategies
        </div>
      </CardContent>
    </Card>
  );
}
