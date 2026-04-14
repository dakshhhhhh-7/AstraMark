import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Check, Sparkles, ArrowLeft, AlertCircle } from "lucide-react";
import { useState } from "react";
import PaymentGatewaySelector from "./PaymentGatewaySelector";
import { initiateRazorpayPayment } from "@/utils/razorpayPayment";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { getAccessToken } from "@/utils/apiClient";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const plans = [
    {
        id: "starter",
        name: "Starter",
        price: 19,
        period: "month",
        features: [
            "Basic marketing strategies",
            "Limited reports",
            "5 analyses/month"
        ],
        color: "from-green-400 to-emerald-500",
        buttonColor: "bg-green-600 hover:bg-green-700",
        popular: false
    },
    {
        id: "pro",
        name: "Pro",
        price: 49,
        period: "month",
        features: [
            "Full marketing + data analysis",
            "Business plans",
            "Competitor research",
            "30 analyses/month",
            "Live market data",
            "PDF exports"
        ],
        color: "from-blue-400 to-indigo-500",
        buttonColor: "bg-blue-600 hover:bg-blue-700",
        popular: true
    },
    {
        id: "growth",
        name: "Growth",
        price: 99,
        period: "month",
        features: [
            "Advanced analytics",
            "Revenue forecasting",
            "Automation planning",
            "Export reports (PDF/Excel)",
            "100 analyses/month",
            "Pitch deck generator",
            "Content calendar",
            "Email sequences"
        ],
        color: "from-purple-400 to-pink-500",
        buttonColor: "bg-purple-600 hover:bg-purple-700",
        popular: false
    },
    {
        id: "enterprise",
        name: "Enterprise",
        price: "Custom",
        period: "",
        features: [
            "API access",
            "Team accounts",
            "Custom AI tuning",
            "White-label reports",
            "Blockchain verification",
            "24/7 support"
        ],
        color: "from-slate-400 to-slate-500",
        buttonColor: "bg-slate-600 hover:bg-slate-700",
        popular: false
    }
];

export function PricingModal({ isOpen, onClose }) {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [selectedPlan, setSelectedPlan] = useState(null);
    const [showPaymentGateways, setShowPaymentGateways] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const handlePlanSelect = (plan) => {
        if (plan.id === 'enterprise') {
            // Handle enterprise contact
            window.open('mailto:sales@astramark.ai?subject=Enterprise Plan Inquiry', '_blank');
            return;
        }
        
        // CRITICAL: Check if user is logged in BEFORE showing payment gateway
        if (!user) {
            console.error('❌ User not logged in - showing error');
            setError('You must be logged in to subscribe. Redirecting to login...');
            setTimeout(() => {
                onClose();
                navigate('/login');
            }, 2000);
            return;
        }
        
        console.log('✅ User is logged in:', user.email);
        setSelectedPlan(plan);
        setShowPaymentGateways(true);
        setError(null); // Clear any previous errors
    };

    const handlePaymentInitiate = async (gateway, plan) => {
        setLoading(true);
        setError(null);
        
        try {
            // CRITICAL: Double-check authentication
            const token = getAccessToken();
            console.log('🔐 Pre-payment token check:', token ? 'Token exists' : 'No token');
            console.log('👤 User state:', user ? `Logged in as ${user.email}` : 'No user');
            
            if (!token || !user) {
                console.error('❌ Authentication check failed');
                setError('Your session has expired. Please log in again.');
                setLoading(false);
                setTimeout(() => {
                    navigate('/login');
                }, 2000);
                return;
            }
            
            console.log('💳 Initiating payment:', { gateway, plan: plan.id, user: user.email });
            
            if (gateway === 'razorpay') {
                // Use production-grade Razorpay handler
                await initiateRazorpayPayment(
                    plan.id,
                    // Success callback
                    (response) => {
                        console.log('✅ Payment successful:', response);
                        setSuccess(true);
                        setLoading(false);
                        
                        // Show success message
                        setTimeout(() => {
                            alert(`🎉 Payment successful! Your ${plan.name} plan is now active.`);
                            onClose();
                            window.location.reload(); // Refresh to update subscription status
                        }, 500);
                    },
                    // Failure callback
                    (error) => {
                        console.error('❌ Payment failed:', error);
                        setLoading(false);
                        
                        // User-friendly error messages
                        let errorMessage = 'Payment failed. Please try again.';
                        
                        switch (error.code) {
                            case 'AUTHENTICATION_REQUIRED':
                            case 'AUTHENTICATION_EXPIRED':
                                errorMessage = 'Your session has expired. Redirecting to login...';
                                setError(errorMessage);
                                setTimeout(() => {
                                    window.location.href = '/login';
                                }, 2000);
                                return;
                            case 'SCRIPT_LOAD_FAILED':
                                errorMessage = 'Unable to load payment gateway. Please check your internet connection.';
                                break;
                            case 'NETWORK_ERROR':
                                errorMessage = 'Network error. Please check your connection and try again.';
                                break;
                            case 'SERVICE_UNAVAILABLE':
                                errorMessage = 'Payment service is temporarily unavailable. Please try again later.';
                                break;
                            case 'PAYMENT_CANCELLED':
                                errorMessage = 'Payment was cancelled.';
                                break;
                            case 'PAYMENT_FAILED':
                                errorMessage = error.message || 'Payment failed. Please try again.';
                                break;
                            case 'VERIFICATION_FAILED':
                                errorMessage = 'Payment verification failed. Please contact support.';
                                break;
                            default:
                                errorMessage = error.message || 'An unexpected error occurred.';
                        }
                        
                        setError(errorMessage);
                    }
                );
            } else if (gateway === 'stripe') {
                // Stripe implementation (existing code)
                const axios = (await import('axios')).default;
                const response = await axios.post(
                    `${BACKEND_URL}/api/payments/checkout`,
                    {
                        plan_id: plan.id,
                        gateway: gateway,
                        success_url: `${window.location.origin}/payment/success`,
                        cancel_url: `${window.location.origin}/payment/cancel`
                    },
                    {
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                // Redirect to Stripe
                if (response.data.checkout_url) {
                    window.location.href = response.data.checkout_url;
                }
            }
        } catch (err) {
            console.error('Payment initiation error:', err);
            
            // Check if it's an authentication error
            if (err.response && err.response.status === 401) {
                setError('Your session has expired. Redirecting to login...');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                setError('Failed to initiate payment. Please try again.');
            }
            
            setLoading(false);
        }
    };

    const handleBack = () => {
        setShowPaymentGateways(false);
        setSelectedPlan(null);
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="max-w-4xl bg-slate-950 border-slate-800 text-white">
                <DialogHeader>
                    <div className="flex items-center gap-2">
                        {showPaymentGateways && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={handleBack}
                                className="text-slate-400 hover:text-white"
                            >
                                <ArrowLeft className="h-4 w-4" />
                            </Button>
                        )}
                        <div className="flex-1">
                            <DialogTitle className="text-3xl font-bold text-center mb-2">
                                {showPaymentGateways ? (
                                    <>Complete Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">Subscription</span></>
                                ) : (
                                    <>Choose Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">Growth Plan</span></>
                                )}
                            </DialogTitle>
                            <DialogDescription className="text-center text-slate-400 text-lg">
                                {showPaymentGateways ? (
                                    `Selected: ${selectedPlan?.name} Plan`
                                ) : (
                                    "Unlock the full power of AI marketing intelligence"
                                )}
                            </DialogDescription>
                        </div>
                    </div>
                </DialogHeader>

                {showPaymentGateways ? (
                    <div className="mt-6">
                        {error && (
                            <Alert variant="destructive" className="mb-4">
                                <AlertCircle className="h-4 w-4" />
                                <AlertDescription>{error}</AlertDescription>
                            </Alert>
                        )}
                        
                        {success && (
                            <Alert className="mb-4 bg-green-50 border-green-200">
                                <Check className="h-4 w-4 text-green-600" />
                                <AlertDescription className="text-green-800">
                                    Payment successful! Your subscription is now active.
                                </AlertDescription>
                            </Alert>
                        )}
                        
                        <PaymentGatewaySelector
                            selectedPlan={selectedPlan}
                            onPaymentInitiate={handlePaymentInitiate}
                        />
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
                        {plans.map((plan) => (
                            <div
                                key={plan.id}
                                className={`relative rounded-xl border ${plan.popular ? 'border-purple-500 bg-slate-900/80' : 'border-slate-800 bg-slate-900/40'} p-6 flex flex-col`}
                            >
                                {plan.popular && (
                                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-white text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
                                        <Sparkles className="w-3 h-3" /> BEST VALUE
                                    </div>
                                )}

                                <div className="mb-4">
                                    <h3 className={`text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r ${plan.color}`}>
                                        {plan.name}
                                    </h3>
                                    <div className="flex items-baseline gap-1 mt-2">
                                        <span className="text-3xl font-bold text-white">
                                            {typeof plan.price === 'number' ? `$${plan.price}` : plan.price}
                                        </span>
                                        {plan.period && <span className="text-slate-400">/{plan.period}</span>}
                                    </div>
                                </div>

                                <ul className="space-y-3 mb-6 flex-1">
                                    {plan.features.map((feature, i) => (
                                        <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                                            <Check className={`w-4 h-4 mt-0.5 shrink-0 text-white`} />
                                            {feature}
                                        </li>
                                    ))}
                                </ul>

                                <Button 
                                    className={`w-full ${plan.buttonColor} text-white font-semibold`}
                                    onClick={() => handlePlanSelect(plan)}
                                    disabled={loading}
                                >
                                    {plan.id === 'enterprise' ? 'Contact Sales' : 'Get Started'}
                                </Button>
                            </div>
                        ))}
                    </div>
                )}
            </DialogContent>
        </Dialog>
    );
}