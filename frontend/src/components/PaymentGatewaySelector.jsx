import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Check, CreditCard, Smartphone, Building, Globe } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const PaymentGatewaySelector = ({ selectedPlan, onPaymentInitiate }) => {
  const [gateways, setGateways] = useState([]);
  const [plans, setPlans] = useState({});
  const [selectedGateway, setSelectedGateway] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPaymentData();
  }, []);

  const fetchPaymentData = async () => {
    try {
      const [gatewaysRes, plansRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/payments/gateways`),
        axios.get(`${BACKEND_URL}/api/payments/plans`)
      ]);
      
      setGateways(gatewaysRes.data.gateways);
      setPlans(plansRes.data);
      
      // Auto-select default gateway
      const defaultGateway = gatewaysRes.data.gateways.find(g => 
        g.id === gatewaysRes.data.default
      );
      if (defaultGateway) {
        setSelectedGateway(defaultGateway.id);
      }
    } catch (error) {
      console.error('Failed to fetch payment data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGatewayIcon = (gatewayId) => {
    switch (gatewayId) {
      case 'stripe':
        return <CreditCard className="h-6 w-6" />;
      case 'razorpay':
        return <Smartphone className="h-6 w-6" />;
      default:
        return <Building className="h-6 w-6" />;
    }
  };

  const getMethodIcons = (methods) => {
    const icons = {
      card: <CreditCard className="h-4 w-4" />,
      upi: <Smartphone className="h-4 w-4" />,
      netbanking: <Building className="h-4 w-4" />,
      wallet: <Smartphone className="h-4 w-4" />,
      apple_pay: <Smartphone className="h-4 w-4" />,
      google_pay: <Smartphone className="h-4 w-4" />
    };
    
    return methods.slice(0, 3).map((method, index) => (
      <span key={index} className="inline-flex items-center">
        {icons[method] || <CreditCard className="h-4 w-4" />}
      </span>
    ));
  };

  const getPlanForGateway = (gatewayId) => {
    const gatewayPlans = plans[gatewayId] || [];
    return gatewayPlans.find(plan => plan.id === selectedPlan?.id);
  };

  const handleProceedToPayment = () => {
    if (selectedGateway && selectedPlan) {
      const plan = getPlanForGateway(selectedGateway);
      onPaymentInitiate(selectedGateway, plan);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (gateways.length === 0) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <p className="text-gray-500">No payment gateways available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Choose Payment Method</h3>
        <p className="text-sm text-gray-600">
          Select your preferred payment gateway based on your location and payment preferences.
        </p>
      </div>

      <div className="grid gap-4">
        {gateways.map((gateway) => {
          const plan = getPlanForGateway(gateway.id);
          const isSelected = selectedGateway === gateway.id;
          
          return (
            <Card 
              key={gateway.id}
              className={`cursor-pointer transition-all ${
                isSelected 
                  ? 'ring-2 ring-blue-500 border-blue-500' 
                  : 'hover:border-gray-300'
              }`}
              onClick={() => setSelectedGateway(gateway.id)}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      {getGatewayIcon(gateway.id)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium">{gateway.name}</h4>
                        {isSelected && (
                          <Check className="h-4 w-4 text-blue-500" />
                        )}
                      </div>
                      
                      <p className="text-sm text-gray-600 mt-1">
                        {gateway.description}
                      </p>
                      
                      <div className="flex items-center space-x-4 mt-2">
                        <div className="flex items-center space-x-1">
                          <Globe className="h-3 w-3 text-gray-400" />
                          <span className="text-xs text-gray-500">
                            {gateway.regions.join(', ')}
                          </span>
                        </div>
                        
                        <div className="flex items-center space-x-1">
                          {getMethodIcons(gateway.methods)}
                          {gateway.methods.length > 3 && (
                            <span className="text-xs text-gray-500">
                              +{gateway.methods.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex flex-wrap gap-1 mt-2">
                        {gateway.currencies.map((currency) => (
                          <Badge key={currency} variant="secondary" className="text-xs">
                            {currency}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  {plan && (
                    <div className="text-right">
                      <div className="font-semibold">
                        {plan.currency === 'INR' ? '₹' : '$'}{plan.price}
                      </div>
                      <div className="text-xs text-gray-500">
                        per {plan.interval}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {selectedGateway && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              {getGatewayIcon(selectedGateway)}
            </div>
            <div>
              <h4 className="font-medium text-blue-900">
                {gateways.find(g => g.id === selectedGateway)?.name} Selected
              </h4>
              <p className="text-sm text-blue-700 mt-1">
                You'll be redirected to {gateways.find(g => g.id === selectedGateway)?.name} to complete your payment securely.
              </p>
            </div>
          </div>
        </div>
      )}

      <Button 
        onClick={handleProceedToPayment}
        disabled={!selectedGateway || !selectedPlan}
        className="w-full"
        size="lg"
      >
        Proceed to Payment
      </Button>
    </div>
  );
};

export default PaymentGatewaySelector;