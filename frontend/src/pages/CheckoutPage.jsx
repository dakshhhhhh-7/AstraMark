import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from '@/components/navigation/Header';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { staggerContainer, staggerItem } from '@/lib/animations';
import { Check, CreditCard, Shield, Lock } from 'lucide-react';
import apiClient from '@/utils/apiClient';
import { toast } from 'sonner';

/**
 * CheckoutPage - Payment checkout page with Razorpay integration
 */
const CheckoutPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, isAuthenticated } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);

  const plans = {
    starter: {
      id: 'starter',
      name: 'Starter',
      price: 1499,
      currency: '₹',
      description: 'Perfect for getting started',
      features: ['Basic AI content', '5 campaigns/month', 'Email support', 'Market research'],
    },
    pro: {
      id: 'pro',
      name: 'Pro',
      price: 3999,
      currency: '₹',
      description: 'Most popular for growing businesses',
      features: ['Advanced AI content', 'Unlimited campaigns', 'Auto Mode', 'Priority support', 'Competitor analysis', 'Revenue projections'],
    },
    growth: {
      id: 'growth',
      name: 'Growth',
      price: 7999,
      currency: '₹',
      description: 'Full automation for scale',
      features: ['Everything in Pro', 'Dedicated account manager', 'Custom integrations', 'White-label options', 'API access'],
    },
  };

  useEffect(() => {
    // Redirect if not authenticated
    if (!isAuthenticated || !user) {
      toast.error('Please login to continue');
      navigate('/login');
      return;
    }

    // Get plan from URL
    const planId = searchParams.get('plan');
    if (planId && plans[planId]) {
      setSelectedPlan(plans[planId]);
    } else {
      toast.error('Invalid plan selected');
      navigate('/pricing');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, user, searchParams, navigate]);

  const handlePayment = async () => {
    if (!selectedPlan) return;

    setIsLoading(true);

    try {
      // Create Razorpay order
      const response = await apiClient.post('/api/payments/razorpay/create-order', {
        plan_id: selectedPlan.id,
      });

      if (!response.data.success) {
        throw new Error('Failed to create order');
      }

      const { order, razorpay_key } = response.data;

      // Load Razorpay script
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.async = true;
      document.body.appendChild(script);

      script.onload = () => {
        const options = {
          key: razorpay_key,
          amount: order.amount,
          currency: order.currency,
          name: 'AstraMark',
          description: `${selectedPlan.name} Plan Subscription`,
          order_id: order.order_id,
          prefill: {
            name: user.full_name || user.name || '',
            email: user.email || '',
          },
          theme: {
            color: '#6366f1',
          },
          handler: async (response) => {
            try {
              // Verify payment
              const verifyResponse = await apiClient.post('/api/payments/razorpay/verify', {
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              });

              if (verifyResponse.data.success) {
                toast.success('🎉 Payment successful! Welcome to ' + selectedPlan.name);
                navigate('/dashboard');
              } else {
                toast.error('Payment verification failed');
              }
            } catch (error) {
              console.error('Payment verification error:', error);
              toast.error('Payment verification failed');
            }
          },
          modal: {
            ondismiss: () => {
              setIsLoading(false);
              toast.info('Payment cancelled');
            },
          },
        };

        const razorpay = new window.Razorpay(options);
        razorpay.open();
        setIsLoading(false);
      };

      script.onerror = () => {
        setIsLoading(false);
        toast.error('Failed to load payment gateway');
      };
    } catch (error) {
      console.error('Payment error:', error);
      toast.error('Failed to initiate payment. Please try again.');
      setIsLoading(false);
    }
  };

  if (!selectedPlan) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-4 py-8 pt-24">
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="max-w-4xl mx-auto"
        >
          {/* Header */}
          <motion.div variants={staggerItem} className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-2 gradient-text">Complete Your Purchase</h1>
            <p className="text-muted-foreground">Secure checkout powered by Razorpay</p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Plan Summary */}
            <motion.div variants={staggerItem}>
              <Card variant="glass">
                <CardHeader>
                  <CardTitle>Order Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 rounded-lg bg-muted/30">
                    <h3 className="text-xl font-bold mb-1">{selectedPlan.name} Plan</h3>
                    <p className="text-sm text-muted-foreground mb-3">{selectedPlan.description}</p>
                    <div className="text-3xl font-bold">
                      {selectedPlan.currency}{selectedPlan.price.toLocaleString()}
                      <span className="text-sm text-muted-foreground font-normal">/month</span>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Included Features:</h4>
                    <ul className="space-y-2">
                      {selectedPlan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center gap-2 text-sm">
                          <Check className="h-4 w-4 text-success" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Payment Details */}
            <motion.div variants={staggerItem}>
              <Card variant="glass">
                <CardHeader>
                  <CardTitle>Payment Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 rounded-lg bg-muted/30">
                    <div className="flex items-center gap-2 mb-2">
                      <Shield className="h-5 w-5 text-success" />
                      <span className="font-semibold">Secure Payment</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Your payment information is encrypted and secure. We use Razorpay for payment processing.
                    </p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Subtotal</span>
                      <span className="font-semibold">{selectedPlan.currency}{selectedPlan.price.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Tax (18% GST)</span>
                      <span className="font-semibold">{selectedPlan.currency}{Math.round(selectedPlan.price * 0.18).toLocaleString()}</span>
                    </div>
                    <div className="border-t border-border pt-2 mt-2">
                      <div className="flex justify-between">
                        <span className="font-bold">Total</span>
                        <span className="font-bold text-lg">{selectedPlan.currency}{Math.round(selectedPlan.price * 1.18).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Lock className="h-3 w-3" />
                    <span>256-bit SSL encryption</span>
                  </div>
                </CardContent>
                <CardFooter className="flex flex-col gap-3">
                  <AnimatedButton
                    variant="premium"
                    className="w-full"
                    onClick={handlePayment}
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <LoadingSpinner size="sm" className="mr-2" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <CreditCard className="h-4 w-4 mr-2" />
                        Pay {selectedPlan.currency}{Math.round(selectedPlan.price * 1.18).toLocaleString()}
                      </>
                    )}
                  </AnimatedButton>
                  <AnimatedButton
                    variant="ghost"
                    className="w-full"
                    onClick={() => navigate('/pricing')}
                    disabled={isLoading}
                  >
                    Change Plan
                  </AnimatedButton>
                </CardFooter>
              </Card>
            </motion.div>
          </div>

          {/* Trust Badges */}
          <motion.div variants={staggerItem} className="mt-8 text-center">
            <p className="text-sm text-muted-foreground mb-4">Trusted by 1000+ businesses</p>
            <div className="flex justify-center gap-6 text-xs text-muted-foreground">
              <span>✓ 14-day money-back guarantee</span>
              <span>✓ Cancel anytime</span>
              <span>✓ No hidden fees</span>
            </div>
          </motion.div>
        </motion.div>
      </main>
    </div>
  );
};

export default CheckoutPage;
