import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { XCircle, ArrowLeft, RefreshCw } from 'lucide-react';

const PaymentCancel = () => {
  const navigate = useNavigate();

  const handleGoBack = () => {
    navigate('/dashboard');
  };

  const handleTryAgain = () => {
    navigate('/dashboard');
    // You could also trigger the pricing modal here
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-900 to-slate-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-white/10 backdrop-blur-lg border-white/20 text-white">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-16 h-16 bg-red-500 rounded-full flex items-center justify-center">
            <XCircle className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold">Payment Cancelled</CardTitle>
          <p className="text-slate-300 mt-2">
            Your payment was cancelled. No charges were made to your account.
          </p>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="bg-white/5 rounded-lg p-4">
            <h3 className="font-semibold mb-2">What happened?</h3>
            <p className="text-sm text-slate-300">
              You cancelled the payment process before it was completed. This is completely normal and no charges were made.
            </p>
          </div>

          <div className="space-y-3">
            <h3 className="font-semibold text-lg">What would you like to do?</h3>
            <ul className="space-y-2 text-sm text-slate-300">
              <li>• Continue using AstraMark with free features</li>
              <li>• Try the payment process again</li>
              <li>• Contact support if you experienced issues</li>
            </ul>
          </div>

          <div className="space-y-3">
            <Button 
              onClick={handleTryAgain}
              className="w-full bg-purple-600 hover:bg-purple-700"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
            
            <Button 
              onClick={handleGoBack}
              variant="outline"
              className="w-full border-white/20 text-white hover:bg-white/10"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </div>

          <div className="text-center text-xs text-slate-400">
            <p>
              Having trouble? Contact us at{' '}
              <a href="mailto:support@astramark.ai" className="text-purple-400 hover:underline">
                support@astramark.ai
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentCancel;