import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Sparkles,
  Lock,
  FileText,
  Megaphone,
  Download,
  Eye,
  Play,
  Rocket,
  Settings,
  CheckCircle2
} from 'lucide-react';
import { toast } from 'sonner';
import { useState } from 'react';

export function ExecutionActions({ actions, isPremium }) {
  const [selectedAction, setSelectedAction] = useState(null);
  const [simulationStep, setSimulationStep] = useState('config'); // config, simulating, result

  const getIcon = (actionType) => {
    switch (actionType) {
      case 'content': return <FileText className="w-4 h-4" />;
      case 'execution': return <Play className="w-4 h-4" />;
      case 'integration': return <Download className="w-4 h-4" />;
      case 'monitoring': return <Eye className="w-4 h-4" />;
      default: return <Rocket className="w-4 h-4" />;
    }
  };

  const handleActionClick = (action) => {
    setSelectedAction(action);
    setSimulationStep('config');
  };

  const handleExecute = (isSimulation = false) => {
    setSimulationStep('simulating');
    setTimeout(() => {
      setSimulationStep('result');
      if (!isSimulation) {
        toast.success(`Action Executed: ${selectedAction.action_name}`, {
          description: 'The agent has started working on this task.'
        });
      }
    }, 1500);
  };

  const ActionDialog = () => {
    if (!selectedAction) return null;
    const isLocked = selectedAction.status === 'locked' && !isPremium;

    return (
      <Dialog open={!!selectedAction} onOpenChange={(open) => !open && setSelectedAction(null)}>
        <DialogContent className="max-w-2xl bg-slate-950 border-slate-800 text-white">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {getIcon(selectedAction.action_type)}
              {selectedAction.action_name}
            </DialogTitle>
            <DialogDescription className="text-slate-400">
              {selectedAction.description}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 mt-4">
            {/* Step 1: Configuration */}
            {simulationStep === 'config' && (
              <div className="space-y-4">
                <div className="p-4 bg-purple-900/10 border border-purple-500/20 rounded-lg">
                  <h4 className="text-sm font-semibold text-purple-300 mb-3 flex items-center gap-2">
                    <Settings className="w-4 h-4" /> Action Parameters
                  </h4>
                  <div className="grid gap-4 py-2">
                    <div className="grid gap-2">
                      <Label>Campaign Name / Identifier</Label>
                      <Input defaultValue={`Auto-${selectedAction.action_name}-001`} className="bg-slate-900 border-slate-700" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="grid gap-2">
                        <Label>Daily Budget Limit</Label>
                        <Input defaultValue="$50.00" className="bg-slate-900 border-slate-700" />
                      </div>
                      <div className="grid gap-2">
                        <Label>Target Audience</Label>
                        <Input defaultValue="Lookalike 1%" className="bg-slate-900 border-slate-700" />
                      </div>
                    </div>
                    <div className="grid gap-2">
                      <Label>Optimization Goal</Label>
                      <Textarea defaultValue="Maximize conversions while maintaining ROAS > 2.5" className="bg-slate-900 border-slate-700 h-20" />
                    </div>
                  </div>
                </div>

                {isLocked && (
                  <div className="text-xs text-center text-slate-400">
                    <Badge variant="outline" className="text-yellow-400 border-yellow-500/30 mb-2">Free Preview Mode</Badge>
                    <p>You can configure and simulate this action to see expected results.</p>
                  </div>
                )}
              </div>
            )}

            {/* Step 2: Simulating */}
            {simulationStep === 'simulating' && (
              <div className="py-12 flex flex-col items-center justify-center text-center space-y-4">
                <div className="relative w-16 h-16">
                  <div className="absolute inset-0 border-4 border-slate-800 rounded-full"></div>
                  <div className="absolute inset-0 border-4 border-t-purple-500 rounded-full animate-spin"></div>
                  <Sparkles className="absolute inset-0 m-auto text-purple-400 animate-pulse" />
                </div>
                <p className="text-slate-300">AI Agents are analyzing parameters...</p>
              </div>
            )}

            {/* Step 3: Result Preview */}
            {simulationStep === 'result' && (
              <div className="space-y-4">
                <div className="p-4 bg-green-900/10 border border-green-500/20 rounded-lg">
                  <h4 className="text-sm font-semibold text-green-300 mb-3 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    {isLocked ? 'Simulation Complete (Preview)' : 'Action Initiated Successfully'}
                  </h4>
                  <div className={`space-y-3 ${isLocked ? 'blur-sm select-none opacity-60' : ''}`}>
                    <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
                      <span className="text-slate-400">Estimated Reach</span>
                      <span className="text-white font-mono">12,500 - 15,000</span>
                    </div>
                    <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
                      <span className="text-slate-400">Projected ROAS</span>
                      <span className="text-white font-mono">3.2x</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-400">Ad Sets Created</span>
                      <span className="text-white font-mono">4 Variants</span>
                    </div>
                  </div>
                  {isLocked && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="bg-slate-900/90 p-4 rounded-lg border border-purple-500/50 text-center shadow-2xl">
                        <Lock className="w-6 h-6 text-purple-400 mx-auto mb-2" />
                        <h4 className="text-white font-semibold mb-1">Results Locked</h4>
                        <p className="text-slate-400 text-sm mb-3">Upgrade to Pro to execute this campaign live</p>
                        <Button size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600">
                          Upgrade Now
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
                {!isLocked && (
                  <p className="text-sm text-slate-400 text-center">
                    You can track the progress in the Live Agent Status panel.
                  </p>
                )}
              </div>
            )}
          </div>

          <DialogFooter className="gap-2 sm:gap-0">
            {simulationStep === 'config' && (
              <Button
                className="w-full sm:w-auto bg-gradient-to-r from-purple-600 to-pink-600 hover:opacity-90 transition-opacity"
                onClick={() => handleExecute(isLocked)}
              >
                {isLocked ? 'Simulate Output' : 'Execute Campaign'}
                <Play className="w-4 h-4 ml-2" />
              </Button>
            )}
            {simulationStep === 'result' && isLocked && (
              <Button variant="outline" onClick={() => setSimulationStep('config')}>Back to Config</Button>
            )}
            {simulationStep === 'result' && !isLocked && (
              <Button onClick={() => setSelectedAction(null)}>Close</Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  };

  return (
    <Card className="bg-slate-900/50 border-slate-800" data-testid="execution-actions-card">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          <CardTitle className="text-white">AI Execution Center</CardTitle>
        </div>
        <CardDescription className="text-slate-400">
          Let AI do the heavy lifting - execute marketing tasks automatically
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {actions && actions.map((action, idx) => (
            <div
              key={idx}
              className={`relative rounded-lg p-4 border transition-all ${action.status === 'locked'
                  ? 'border-slate-700 bg-slate-800/30'
                  : 'border-purple-500/30 bg-gradient-to-br from-purple-900/20 to-pink-900/20 hover:border-purple-500/50'
                }`}
              data-testid={`execution-action-${action.action_id}`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getIcon(action.action_type)}
                  <h4 className="text-white font-semibold text-sm">{action.action_name}</h4>
                </div>
                {action.is_premium && (
                  <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
                    <Lock className="w-3 h-3 mr-1" />
                    Pro
                  </Badge>
                )}
              </div>
              <p className="text-slate-300 text-xs mb-3">{action.description}</p>
              <Button
                size="sm"
                onClick={() => handleActionClick(action)}
                className={`w-full ${action.status === 'locked' && !isPremium // Even if locked, we allow clicking to open the preview modal
                    ? 'bg-slate-700 hover:bg-slate-600 text-slate-300'
                    : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                  }`}
                data-testid={`execute-${action.action_id}-btn`}
              >
                {action.status === 'locked' && !isPremium ? (
                  <>
                    <Eye className="w-3 h-3 mr-2" />
                    Preview & Simulate
                  </>
                ) : (
                  <>
                    <Play className="w-3 h-3 mr-2" />
                    Configure & Run
                  </>
                )}
              </Button>
            </div>
          ))}
        </div>

        <div className="mt-4 p-3 bg-purple-500/10 border border-purple-500/30 rounded-lg">
          <div className="flex items-start gap-2">
            <Megaphone className="w-4 h-4 text-purple-400 mt-0.5" />
            <div className="text-sm">
              <div className="text-white font-semibold mb-1">Unlock Full Automation</div>
              <div className="text-slate-300 text-xs">
                Pro users get unlimited execution actions + real-time competitor tracking + live CPC monitoring.
                <span className="text-purple-400 ml-1 cursor-pointer hover:underline">Compare plans</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>

      {/* Dialog */}
      <ActionDialog />
    </Card>
  );
}
