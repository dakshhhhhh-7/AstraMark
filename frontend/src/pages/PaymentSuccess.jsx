import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { CheckCircle, ArrowRight, Download, Calendar } from 'lucide-react';
import axios from 'axios';

const PaymentSuccess = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSubscriptionDetails();
  }, []);

  const fetchSubscriptionDetails = async () => {
    try {
      const response = await axios.get('/api/payments/subscription');
      setSubscription(response.data);
    } catch (error) {
      console.error('Failed to fetch subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGoToDashboard = () => {
    navigate('/dashboard');
  };

  const handleManageSubscription = async () => {
    try {
      const response = await axios.post('/api/payments/portal', {
        return_url: window.location.origin + '/dashboard'
      });
      window.location.href = response.data.portal_url;
    } catch (error) {
      console.error('Failed to open portal:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-white/10 backdrop-blur-lg border-white/20 text-white">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-16 h-16 bg-green-500 rounded-full flex items-center justify-center">
            <CheckCircle className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold">Payment Successful!</CardTitle>
          <p className="text-slate-300 mt-2">
            Welcome to AstraMark {subscription?.plan ? subscription.plan.charAt(0).toUpperCase() + subscription.plan.slice(1) : 'Premium'}!
          </p>
        </CardHeader>

        <CardContent className="space-y-6">
          {subscription && (
            <div className="bg-white/5 rounded-lg p-4 space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-300">Plan:</span>
                <span className="font-semibold">
                  {subscription.plan ? subscription.plan.charAt(0).toUpperCase() + subscription.plan.slice(1) : 'Premium'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Status:</span>
                <span className="text-green-400 font-semibold">
                  {subscription.status || 'Active'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Gateway:</span>
                <span className="font-semibold">
                  {subscription.gateway ? subscription.gateway.charAt(0).toUpperCase() + subscription.gateway.slice(1) : 'Payment Gateway'}
                </span>
              </div>
            </div>
          )}

          <div className="space-y-3">
            <h3 className="font-semibold text-lg">What's Next?</h3>
            <ul className="space-y-2 text-sm text-slate-300">
              <li className="flex items-center gap-2">
                <ArrowRight className="w-4 h-4 text-purple-400" />
                Access advanced AI marketing strategies
              </li>
              <li className="flex items-center gap-2">
                <Download className="w-4 h-4 text-purple-400" />
                Export professional PDF reports
              </li>
              <li className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-purple-400" />
                Generate content calendars and pitch decks
              </li>
            </ul>
          </div>

          <div className="space-y-3">
            <Button 
              onClick={handleGoToDashboard}
              className="w-full bg-purple-600 hover:bg-purple-700"
            >
              Go to Dashboard
            </Button>
            
            <Button 
              onClick={handleManageSubscription}
              variant="outline"
              className="w-full border-white/20 text-white hover:bg-white/10"
            >
              Manage Subscription
            </Button>
          </div>

          <div className="text-center text-xs text-slate-400">
            <p>
              Need help? Contact us at{' '}
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

export default PaymentSuccess;