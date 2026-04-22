import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useOnboardingStore } from '@/lib/store';
import { ProgressIndicator } from '@/components/ui/progress-indicator';
import { AnimatedButton } from '@/components/ui/animated-button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AIAnalysisEffect } from '@/components/ui/particle-effect';
import { fadeInUp, slideInUp } from '@/lib/animations';
import { 
  Sparkles, ArrowRight, ArrowLeft, CheckCircle2, 
  Target, Users, TrendingUp, Zap, Rocket 
} from 'lucide-react';
import { z } from 'zod';

/**
 * OnboardingPage - Three-step onboarding flow with WOW moment
 * Step 1: Business Setup
 * Step 2: AI Analysis (10-second countdown)
 * Step 3: Instant Output (Strategy + Growth Plan)
 */
const OnboardingPage = () => {
  const navigate = useNavigate();
  const {
    currentStep,
    totalSteps,
    getProgress,
    nextStep,
    previousStep,
    completeOnboarding,
  } = useOnboardingStore();

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <motion.div
        className="w-full max-w-3xl"
        {...fadeInUp}
      >
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-4">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">AI-Powered Setup</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-2">Welcome to AstraMark</h1>
          <p className="text-muted-foreground">
            Let's set up your business for AI-powered growth
          </p>
        </div>

        {/* Progress Bar */}
        <ProgressIndicator
          value={getProgress()}
          variant="gradient"
          className="mb-8"
        />

        {/* Step Content */}
        <AnimatePresence mode="wait">
          {currentStep === 1 && <Step1BusinessSetup key="step1" />}
          {currentStep === 2 && <Step2AIAnalysis key="step2" />}
          {currentStep === 3 && <Step3InstantOutput key="step3" navigate={navigate} />}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

// Step 1: Business Setup
const Step1BusinessSetup = () => {
  const { businessSetup, updateBusinessSetup, nextStep, canProceed } = useOnboardingStore();
  const [formData, setFormData] = useState(businessSetup);
  const [errors, setErrors] = useState({});

  const businessTypes = [
    { value: 'ecommerce', label: 'E-commerce', icon: '🛒' },
    { value: 'saas', label: 'SaaS', icon: '💻' },
    { value: 'agency', label: 'Agency', icon: '🎯' },
    { value: 'consulting', label: 'Consulting', icon: '💼' },
    { value: 'other', label: 'Other', icon: '✨' },
  ];

  const goals = [
    { value: 'leads', label: 'Generate More Leads', icon: Users },
    { value: 'revenue', label: 'Increase Revenue', icon: TrendingUp },
    { value: 'brand', label: 'Build Brand Awareness', icon: Target },
    { value: 'automation', label: 'Automate Marketing', icon: Zap },
  ];

  const schema = z.object({
    businessType: z.string().min(1, 'Please select a business type'),
    targetAudience: z.string().min(3, 'Please describe your target audience'),
    goals: z.array(z.string()).min(1, 'Please select at least one goal'),
  });

  const handleSubmit = () => {
    try {
      schema.parse(formData);
      updateBusinessSetup(formData);
      nextStep();
    } catch (error) {
      if (error instanceof z.ZodError) {
        const newErrors = {};
        error.errors.forEach((err) => {
          newErrors[err.path[0]] = err.message;
        });
        setErrors(newErrors);
      }
    }
  };

  const toggleGoal = (goalValue) => {
    const currentGoals = formData.goals || [];
    const newGoals = currentGoals.includes(goalValue)
      ? currentGoals.filter((g) => g !== goalValue)
      : [...currentGoals, goalValue];
    setFormData({ ...formData, goals: newGoals });
    setErrors({ ...errors, goals: null });
  };

  return (
    <motion.div {...slideInUp}>
      <Card variant="glass" className="p-8">
        <CardContent className="space-y-6 p-0">
          <div>
            <h2 className="text-2xl font-semibold mb-2">Tell us about your business</h2>
            <p className="text-muted-foreground">
              This helps our AI create a personalized growth strategy
            </p>
          </div>

          {/* Business Type */}
          <div className="space-y-3">
            <Label>What type of business do you have?</Label>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {businessTypes.map((type) => (
                <motion.button
                  key={type.value}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    formData.businessType === type.value
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50'
                  }`}
                  onClick={() => {
                    setFormData({ ...formData, businessType: type.value });
                    setErrors({ ...errors, businessType: null });
                  }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <div className="text-3xl mb-2">{type.icon}</div>
                  <div className="text-sm font-medium">{type.label}</div>
                </motion.button>
              ))}
            </div>
            {errors.businessType && (
              <p className="text-sm text-destructive">{errors.businessType}</p>
            )}
          </div>

          {/* Target Audience */}
          <div className="space-y-3">
            <Label htmlFor="targetAudience">Who is your target audience?</Label>
            <Input
              id="targetAudience"
              placeholder="e.g., Small business owners, Tech startups, E-commerce brands"
              value={formData.targetAudience || ''}
              onChange={(e) => {
                setFormData({ ...formData, targetAudience: e.target.value });
                setErrors({ ...errors, targetAudience: null });
              }}
            />
            {errors.targetAudience && (
              <p className="text-sm text-destructive">{errors.targetAudience}</p>
            )}
          </div>

          {/* Goals */}
          <div className="space-y-3">
            <Label>What are your main goals? (Select all that apply)</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {goals.map((goal) => {
                const Icon = goal.icon;
                const isSelected = (formData.goals || []).includes(goal.value);
                return (
                  <motion.button
                    key={goal.value}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      isSelected
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/50'
                    }`}
                    onClick={() => toggleGoal(goal.value)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className={`h-5 w-5 ${isSelected ? 'text-primary' : 'text-muted-foreground'}`} />
                      <span className="font-medium">{goal.label}</span>
                      {isSelected && <CheckCircle2 className="h-5 w-5 text-primary ml-auto" />}
                    </div>
                  </motion.button>
                );
              })}
            </div>
            {errors.goals && (
              <p className="text-sm text-destructive">{errors.goals}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end pt-4">
            <AnimatedButton
              size="lg"
              variant="premium"
              onClick={handleSubmit}
              className="group"
            >
              Continue to AI Analysis
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </AnimatedButton>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Step 2: AI Analysis
const Step2AIAnalysis = () => {
  const { nextStep } = useOnboardingStore();
  const [countdown, setCountdown] = useState(10);
  const [analysisSteps, setAnalysisSteps] = useState([
    { label: 'Analyzing your business model', completed: false },
    { label: 'Identifying growth opportunities', completed: false },
    { label: 'Creating content strategy', completed: false },
    { label: 'Optimizing ad campaigns', completed: false },
    { label: 'Generating growth plan', completed: false },
  ]);

  useEffect(() => {
    // Countdown timer
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          nextStep();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    // Complete analysis steps progressively
    const stepTimers = analysisSteps.map((_, index) => {
      return setTimeout(() => {
        setAnalysisSteps((prev) =>
          prev.map((step, i) => (i === index ? { ...step, completed: true } : step))
        );
      }, (index + 1) * 2000);
    });

    return () => {
      clearInterval(timer);
      stepTimers.forEach(clearTimeout);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <motion.div {...slideInUp}>
      <Card variant="glass" className="p-8">
        <CardContent className="space-y-8 p-0">
          <div className="text-center">
            <h2 className="text-2xl font-semibold mb-2">AI is Analyzing Your Business</h2>
            <p className="text-muted-foreground">
              Creating your personalized growth strategy...
            </p>
          </div>

          {/* AI Animation */}
          <AIAnalysisEffect />

          {/* Countdown */}
          <div className="text-center">
            <motion.div
              className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-primary text-white text-3xl font-bold"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              {countdown}
            </motion.div>
            <p className="text-sm text-muted-foreground mt-2">seconds remaining</p>
          </div>

          {/* Analysis Steps */}
          <div className="space-y-3">
            {analysisSteps.map((step, index) => (
              <motion.div
                key={step.label}
                className="flex items-center gap-3 p-3 rounded-lg bg-muted/30"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                {step.completed ? (
                  <CheckCircle2 className="h-5 w-5 text-success flex-shrink-0" />
                ) : (
                  <motion.div
                    className="h-5 w-5 border-2 border-primary rounded-full flex-shrink-0"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  />
                )}
                <span className={step.completed ? 'text-foreground' : 'text-muted-foreground'}>
                  {step.label}
                </span>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Step 3: Instant Output
const Step3InstantOutput = ({ navigate }) => {
  const { completeOnboarding, businessSetup } = useOnboardingStore();

  const strategy = {
    title: 'Your Personalized Growth Strategy',
    insights: [
      `Focus on ${businessSetup.targetAudience || 'your target audience'} with value-driven content`,
      'Run targeted ad campaigns on social media platforms',
      'Implement email automation for lead nurturing',
      'Create SEO-optimized blog content weekly',
    ],
  };

  const growthPlan = {
    title: '30-Day Growth Plan',
    weeks: [
      { week: 1, focus: 'Content Foundation', tasks: ['Create 10 social posts', 'Set up email sequences'] },
      { week: 2, focus: 'Ad Launch', tasks: ['Launch Facebook ads', 'Optimize targeting'] },
      { week: 3, focus: 'Optimization', tasks: ['A/B test campaigns', 'Refine messaging'] },
      { week: 4, focus: 'Scale', tasks: ['Increase ad budget', 'Expand to new channels'] },
    ],
  };

  const handleComplete = () => {
    completeOnboarding();
    navigate('/dashboard');
  };

  return (
    <motion.div {...slideInUp}>
      <Card variant="premium" className="p-8">
        <CardContent className="space-y-8 p-0">
          {/* Success Header */}
          <div className="text-center">
            <motion.div
              className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-success/20 mb-4"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', duration: 0.5 }}
            >
              <Rocket className="h-8 w-8 text-success" />
            </motion.div>
            <h2 className="text-3xl font-bold mb-2 gradient-text">You're All Set!</h2>
            <p className="text-muted-foreground">
              Here's your AI-generated growth strategy
            </p>
          </div>

          {/* Strategy */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              {strategy.title}
            </h3>
            <div className="space-y-2">
              {strategy.insights.map((insight, index) => (
                <motion.div
                  key={index}
                  className="flex items-start gap-3 p-3 rounded-lg bg-muted/30"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <CheckCircle2 className="h-5 w-5 text-success flex-shrink-0 mt-0.5" />
                  <span>{insight}</span>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Growth Plan */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              {growthPlan.title}
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {growthPlan.weeks.map((week, index) => (
                <motion.div
                  key={week.week}
                  className="p-4 rounded-lg bg-muted/30"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="font-semibold mb-2">Week {week.week}: {week.focus}</div>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    {week.tasks.map((task, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                        {task}
                      </li>
                    ))}
                  </ul>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-center pt-4">
            <AnimatedButton
              size="xl"
              variant="premium"
              onClick={handleComplete}
              className="group"
            >
              Go to Dashboard
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </AnimatedButton>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default OnboardingPage;
