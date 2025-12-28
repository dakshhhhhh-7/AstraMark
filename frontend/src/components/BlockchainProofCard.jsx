import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Shield, CheckCircle2, Copy, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';

export function BlockchainProofCard({ blockchainProof }) {
  if (!blockchainProof) return null;

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard!`);
  };

  return (
    <Card className="bg-gradient-to-br from-cyan-900/30 to-blue-900/30 border-cyan-500/30" data-testid="blockchain-proof-card">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-cyan-400" />
            <CardTitle className="text-white">Blockchain Verification</CardTitle>
          </div>
          <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30">
            <CheckCircle2 className="w-3 h-3 mr-1" />
            {blockchainProof.verification_status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-slate-300 mb-4">
          Your marketing strategy is cryptographically verified and stored immutably for transparency and trust.
        </div>

        {/* Strategy Hash */}
        <div className="bg-slate-900/50 rounded-lg p-4 border border-cyan-500/20">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">Strategy Hash</span>
            <Button 
              size="sm" 
              variant="ghost" 
              className="h-6 px-2 text-cyan-400 hover:text-cyan-300"
              onClick={() => copyToClipboard(blockchainProof.strategy_hash, 'Strategy hash')}
              data-testid="copy-strategy-hash"
            >
              <Copy className="w-3 h-3" />
            </Button>
          </div>
          <div className="font-mono text-white text-sm break-all">
            {blockchainProof.strategy_hash}
          </div>
        </div>

        {/* KPI Snapshot Hash */}
        <div className="bg-slate-900/50 rounded-lg p-4 border border-cyan-500/20">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">KPI Snapshot Hash</span>
            <Button 
              size="sm" 
              variant="ghost" 
              className="h-6 px-2 text-cyan-400 hover:text-cyan-300"
              onClick={() => copyToClipboard(blockchainProof.kpi_snapshot_hash, 'KPI hash')}
              data-testid="copy-kpi-hash"
            >
              <Copy className="w-3 h-3" />
            </Button>
          </div>
          <div className="font-mono text-white text-sm break-all">
            {blockchainProof.kpi_snapshot_hash}
          </div>
        </div>

        {/* Verification Info */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-cyan-500/10 rounded p-3 text-center">
            <div className="text-xs text-slate-400 mb-1">Last Verified</div>
            <div className="text-white font-semibold text-sm">{blockchainProof.last_verified}</div>
          </div>
          <div className="bg-cyan-500/10 rounded p-3 text-center">
            <div className="text-xs text-slate-400 mb-1">Network</div>
            <div className="text-white font-semibold text-sm">Ethereum L2</div>
          </div>
        </div>

        {/* View on Explorer Button */}
        <Button 
          className="w-full bg-cyan-600 hover:bg-cyan-700 text-white"
          data-testid="view-on-explorer-btn"
        >
          <ExternalLink className="w-4 h-4 mr-2" />
          View on Block Explorer
        </Button>

        <div className="text-xs text-center text-slate-400 pt-2 border-t border-cyan-500/20">
          🔐 Immutable proof ensures strategy integrity and prevents tampering
        </div>
      </CardContent>
    </Card>
  );
}
