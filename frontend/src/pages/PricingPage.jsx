import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { fadeInUp, staggerContainer, staggerItem } from '@/lib/animations';
import { Check } from 'lucide-react';

/**
 * PricingPage - High-conversion pricing page
 * Placeholder for Phase 7 implementation
 */
const PricingPage = () => {
  const navigate = useNavigate();

  const plans = [
    {
      name: 'Starter',
      price: '₹1,999',
      description: 'Perfect for getting started',
      features: ['Basic AI content', '5 campaigns/month', 'Email support'],
    },
    {
      name: 'Pro',
      price: '₹3,999',
      description: 'Most popular for growing businesses',
      popular: true,
      features: ['Advanced AI content', 'Unlimited campaigns', 'Auto Mode', 'Priority support'],
    },
    {
      name: 'Growth',
      price: '₹9,999',
      description: 'Full automation for scale',
      features: ['Everything in Pro', 'Dedicated account manager', 'Custom integrations', 'White-label options'],
    },
  ];

  return (
    <div className="min-h-screen bg-background py-20 px-4">
      <motion.div
        className="container mx-auto"
        variants={staggerContainer}
        initial="initial"
        animate="animate"
      >
        <motion.div variants={staggerItem} className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4 gradient-text">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Choose the plan that fits your business. Cancel anytime.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => (
            <motion.div key={plan.name} variants={staggerItem}>
              <Card
                variant={plan.popular ? "premium" : "glass"}
                className="relative h-full"
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="px-4 py-1 rounded-full bg-gradient-primary text-white text-sm font-semibold">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <CardHeader>
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                
                <CardContent>
                  <div className="mb-6">
                    <span className="text-4xl font-bold">{plan.price}</span>
                    <span className="text-muted-foreground">/month</span>
                  </div>
                  
                  <ul className="space-y-3">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-center gap-2">
                        <Check className="h-5 w-5 text-success" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                
                <CardFooter>
                  <AnimatedButton
                    variant={plan.popular ? "premium" : "default"}
                    className="w-full"
                    onClick={() => navigate('/register')}
                  >
                    Get Started
                  </AnimatedButton>
                </CardFooter>
              </Card>
            </motion.div>
          ))}
        </div>

        <motion.div variants={staggerItem} className="text-center mt-12">
          <p className="text-muted-foreground">
            All plans include 14-day money-back guarantee
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default PricingPage;
