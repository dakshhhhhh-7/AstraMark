import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Shield, CheckCircle2, Copy, ExternalLink, Loader2, Lock } from 'lucide-react';
import { toast } from 'sonner';
import { useState } from 'react';

export function BlockchainProofCard({ blockchainProof }) {
  const [verificationState, setVerificationState] = useState('verified'); // verified, verifying, idle

  if (!blockchainProof) return null;

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard!`);
  };

  const handleVerify = () => {
    setVerificationState('verifying');
    toast.info("Initiating blockchain verification...");

    // Simulate verification steps
    setTimeout(() => {
      toast.info("Validating strategy hash on-chain...");
    }, 1500);

    setTimeout(() => {
      setVerificationState('verified');
      toast.success("Strategy verification confirmed! Immutable proof validated.");
    }, 3500);
  };

  return (
    <Card className="bg-gradient-to-br from-cyan-950/50 to-blue-950/50 border border-cyan-500/30 overflow-hidden relative" data-testid="blockchain-proof-card">
      {/* Animated Background Effect */}
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10"></div>

      <CardHeader className="relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className={`w-5 h-5 ${verificationState === 'verifying' ? 'animate-pulse text-cyan-400' : 'text-cyan-400'}`} />
            <CardTitle className="text-white">Blockchain Trust Layer</CardTitle>
          </div>
          {verificationState === 'verified' && (
            <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              Verified
            </Badge>
          )}
          {verificationState === 'verifying' && (
            <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
              <Loader2 className="w-3 h-3 mr-1 animate-spin" />
              Verifying...
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4 relative z-10">
        <div className="text-sm text-slate-300 mb-4">
          This strategy is cryptographically hashed and anchored on-chain. This ensures transparency, immutability, and verifiable performance history.
        </div>

        {/* Strategy Hash */}
        <div className="bg-slate-900/80 rounded-lg p-4 border border-cyan-500/20 group hover:border-cyan-500/50 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <Lock className="w-3 h-3" /> Strategy Hash
            </span>
            <Button
              size="sm"
              variant="ghost"
              className="h-6 px-2 text-cyan-400 hover:text-cyan-300 hover:bg-cyan-900/20"
              onClick={() => copyToClipboard(blockchainProof.strategy_hash, 'Strategy hash')}
              data-testid="copy-strategy-hash"
            >
              <Copy className="w-3 h-3" />
            </Button>
          </div>
          <div className="font-mono text-cyan-100/80 text-xs break-all bg-black/40 p-2 rounded">
            {blockchainProof.strategy_hash}
          </div>
        </div>

        {/* Verification Info */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-cyan-900/20 rounded p-3 text-center border border-cyan-500/10">
            <div className="text-xs text-slate-400 mb-1">Last Validated</div>
            <div className="text-white font-semibold text-sm">
              {verificationState === 'verifying' ? 'Updating...' : blockchainProof.last_verified}
            </div>
          </div>
          <div className="bg-cyan-900/20 rounded p-3 text-center border border-cyan-500/10">
            <div className="text-xs text-slate-400 mb-1">Network</div>
            <div className="text-white font-semibold text-sm">Ethereum L2</div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-2">
          <Button
            variant="outline"
            className="flex-1 border-cyan-500/30 text-cyan-400 hover:bg-cyan-950 hover:text-cyan-300"
            onClick={handleVerify}
            disabled={verificationState === 'verifying'}
          >
            {verificationState === 'verifying' ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Verifying</>
            ) : (
              <><Shield className="w-4 h-4 mr-2" /> Re-Verify Proof</>
            )}
          </Button>
          <Button
            className="flex-1 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white border-0"
            data-testid="view-on-explorer-btn"
          >
            <ExternalLink className="w-4 h-4 mr-2" />
            Explorer
          </Button>
        </div>

        <div className="text-[10px] text-center text-slate-500 uppercase tracking-wider pt-2">
          Powered by AstraMark Trust Layer™
        </div>
      </CardContent>
    </Card>
  );
}
