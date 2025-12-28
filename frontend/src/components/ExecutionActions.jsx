import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Sparkles, 
  Lock, 
  FileText, 
  Megaphone, 
  Mail, 
  Download, 
  Eye,
  Play,
  Rocket
} from 'lucide-react';
import { toast } from 'sonner';

export function ExecutionActions({ actions, isPremium }) {
  const getIcon = (actionType) => {
    switch (actionType) {
      case 'content': return <FileText className="w-4 h-4" />;
      case 'execution': return <Play className="w-4 h-4" />;
      case 'integration': return <Download className="w-4 h-4" />;
      case 'monitoring': return <Eye className="w-4 h-4" />;
      default: return <Rocket className="w-4 h-4" />;
    }
  };

  const handleAction = (action) => {
    if (action.status === 'locked' && !isPremium) {
      toast.error('This action requires Pro subscription');
      return;
    }
    toast.success(`Starting: ${action.action_name}...`, {
      description: 'AI is working on this. You\'ll be notified when complete.'
    });
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
              className={`relative rounded-lg p-4 border transition-all ${
                action.status === 'locked'
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
                onClick={() => handleAction(action)}
                disabled={action.status === 'locked' && !isPremium}
                className={`w-full ${
                  action.status === 'locked'
                    ? 'bg-slate-700 hover:bg-slate-600 text-slate-400'
                    : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                }`}
                data-testid={`execute-${action.action_id}-btn`}
              >
                {action.status === 'locked' && !isPremium ? (
                  <>
                    <Lock className="w-3 h-3 mr-2" />
                    Unlock with Pro
                  </>
                ) : (
                  <>
                    <Play className="w-3 h-3 mr-2" />
                    Execute Now
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
                Pro users get unlimited execution actions + real-time competitor tracking + live CPC monitoring
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
