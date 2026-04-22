import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useInView } from 'react-intersection-observer';
import { AnimatedButton } from '@/components/ui/animated-button';
import { MetricCard, AnimatedCounter } from '@/components/ui/animated-counter';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Header } from '@/components/navigation/Header';
import { fadeInUp, staggerContainer, staggerItem } from '@/lib/animations';
import { 
  ArrowRight, Sparkles, TrendingUp, Zap, Target, 
  BarChart3, Users, DollarSign, CheckCircle2, Star,
  Rocket, Shield, Clock
} from 'lucide-react';

/**
 * LandingPage - High-conversion landing page for AstraMark
 * Premium $100M SaaS design with conversion-focused elements
 */
const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      <Header transparent />
      
      {/* Hero Section */}
      <HeroSection navigate={navigate} />
      
      {/* Problem Section */}
      <ProblemSection />
      
      {/* Solution Section */}
      <SolutionSection />
      
      {/* Demo Dashboard Preview */}
      <DemoDashboardSection />
      
      {/* Social Proof */}
      <SocialProofSection />
      
      {/* Features Grid */}
      <FeaturesSection />
      
      {/* Pricing Preview */}
      <PricingPreviewSection navigate={navigate} />
      
      {/* Final CTA */}
      <FinalCTASection navigate={navigate} />
    </div>
  );
};

// Hero Section Component
const HeroSection = ({ navigate }) => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-radial from-primary/20 via-background to-background" />
      
      {/* Particle effects */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(30)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-primary/30 rounded-full blur-sm"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [-20, 20],
              opacity: [0.2, 0.8, 0.2],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      <motion.div
        className="relative z-10 container mx-auto px-4 text-center"
        variants={staggerContainer}
        initial="initial"
        animate="animate"
      >
        <motion.div variants={staggerItem} className="mb-6">
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-sm font-medium text-primary">
            <Sparkles className="h-4 w-4" />
            AI-Powered Growth Platform
          </span>
        </motion.div>

        <motion.h1
          variants={staggerItem}
          className="text-5xl md:text-7xl lg:text-8xl font-bold mb-6 gradient-text leading-tight"
        >
          AI That Brings You
          <br />
          Customers Automatically
        </motion.h1>

        <motion.p
          variants={staggerItem}
          className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto"
        >
          Replace your marketing team with AstraMark AI. Generate content, run ads,
          and grow your business on autopilot.
        </motion.p>

        <motion.div
          variants={staggerItem}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12"
        >
          <AnimatedButton
            size="xl"
            variant="premium"
            onClick={() => navigate('/register')}
            className="group"
          >
            Start Growing Free
            <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
          </AnimatedButton>
          
          <AnimatedButton
            size="xl"
            variant="outline"
            onClick={() => navigate('/pricing')}
          >
            View Pricing
          </AnimatedButton>
        </motion.div>

        <motion.div
          variants={staggerItem}
          className="flex flex-wrap items-center justify-center gap-6 md:gap-8 text-sm text-muted-foreground"
        >
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-success" />
            <span>₹50Cr+ Revenue Generated</span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-accent" />
            <span>1000+ Businesses Growing</span>
          </div>
          <div className="flex items-center gap-2">
            <Star className="h-4 w-4 text-warning" />
            <span>4.9/5 Rating</span>
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
};

// Problem Section
const ProblemSection = () => {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });

  const problems = [
    { icon: DollarSign, title: "Marketing is Expensive", description: "Agencies charge ₹50K-₹2L/month" },
    { icon: Clock, title: "Takes Too Much Time", description: "Hours spent on content & campaigns" },
    { icon: Target, title: "Results Are Unclear", description: "Hard to track ROI and growth" },
  ];

  return (
    <section ref={ref} className="py-20 px-4 bg-muted/30">
      <motion.div
        className="container mx-auto"
        initial={{ opacity: 0, y: 40 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6 }}
      >
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Marketing is <span className="text-destructive">Expensive</span> & <span className="text-destructive">Confusing</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Most businesses struggle with these challenges
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {problems.map((problem, index) => (
            <motion.div
              key={problem.title}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: index * 0.2 }}
            >
              <Card variant="glass" className="text-center h-full">
                <CardContent className="pt-6">
                  <div className="inline-flex p-4 rounded-2xl bg-destructive/10 mb-4">
                    <problem.icon className="h-8 w-8 text-destructive" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{problem.title}</h3>
                  <p className="text-muted-foreground">{problem.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  );
};

// Solution Section
const SolutionSection = () => {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });

  return (
    <section ref={ref} className="py-20 px-4">
      <motion.div
        className="container mx-auto text-center"
        initial={{ opacity: 0, y: 40 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6 }}
      >
        <h2 className="text-4xl md:text-5xl font-bold mb-6">
          AstraMark Does <span className="gradient-text">Everything Automatically</span>
        </h2>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-12">
          One platform that handles all your marketing needs with AI
        </p>

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {[
            { icon: Sparkles, title: "AI Content Generation", desc: "Posts, ads, emails created instantly" },
            { icon: Target, title: "Smart Ad Management", desc: "Optimize campaigns automatically" },
            { icon: BarChart3, title: "Growth Analytics", desc: "Track revenue and ROI in real-time" },
          ].map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={inView ? { opacity: 1, scale: 1 } : {}}
              transition={{ delay: index * 0.15 }}
            >
              <Card variant="premium" className="h-full">
                <CardContent className="pt-6 text-center">
                  <div className="inline-flex p-4 rounded-2xl bg-gradient-primary mb-4">
                    <feature.icon className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.desc}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  );
};

// Demo Dashboard Section
const DemoDashboardSection = () => {
  const { ref, inView } = useInView({ threshold: 0.1, triggerOnce: true });

  return (
    <section ref={ref} className="py-20 px-4 bg-muted/30">
      <motion.div
        className="container mx-auto"
        initial={{ opacity: 0, y: 40 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6 }}
      >
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            See Your <span className="gradient-text">Growth in Real-Time</span>
          </h2>
          <p className="text-xl text-muted-foreground">
            Track what matters: Revenue, Leads, and Engagement
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <MetricCard
            title="Revenue This Week"
            value={12000}
            change={23}
            icon={DollarSign}
            variant="currency"
          />
          <MetricCard
            title="New Leads"
            value={42}
            change={18}
            icon={Users}
            variant="number"
          />
          <MetricCard
            title="Engagement Rate"
            value={23}
            change={15}
            icon={TrendingUp}
            variant="percentage"
          />
        </div>
      </motion.div>
    </section>
  );
};

// Social Proof Section
const SocialProofSection = () => {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });

  const testimonials = [
    {
      name: "Rajesh Kumar",
      role: "E-commerce Owner",
      content: "AstraMark increased our revenue by 300% in just 3 months. The AI does everything!",
      rating: 5,
    },
    {
      name: "Priya Sharma",
      role: "SaaS Founder",
      content: "Best investment we made. Replaced our entire marketing team and saved ₹5L/year.",
      rating: 5,
    },
    {
      name: "Amit Patel",
      role: "Agency Owner",
      content: "We use AstraMark for all our clients. Results are incredible and consistent.",
      rating: 5,
    },
  ];

  return (
    <section ref={ref} className="py-20 px-4">
      <motion.div
        className="container mx-auto"
        initial={{ opacity: 0, y: 40 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6 }}
      >
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Trusted by <span className="gradient-text">1000+ Businesses</span>
          </h2>
          <p className="text-xl text-muted-foreground">
            See what our customers are saying
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.name}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: index * 0.15 }}
            >
              <Card variant="glass" className="h-full">
                <CardContent className="pt-6">
                  <div className="flex gap-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 fill-warning text-warning" />
                    ))}
                  </div>
                  <p className="text-foreground mb-4 italic">"{testimonial.content}"</p>
                  <div>
                    <p className="font-semibold">{testimonial.name}</p>
                    <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  );
};

// Features Section
const FeaturesSection = () => {
  const { ref, inView } = useInView({ threshold: 0.1, triggerOnce: true });

  const features = [
    { icon: Rocket, title: "Launch in Minutes", desc: "Set up your AI marketing in under 10 minutes" },
    { icon: Shield, title: "100% Secure", desc: "Bank-level security for your data" },
    { icon: CheckCircle2, title: "Money-Back Guarantee", desc: "14-day no-questions-asked refund" },
  ];

  return (
    <section ref={ref} className="py-20 px-4 bg-muted/30">
      <div className="container mx-auto">
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              className="flex flex-col items-center text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: index * 0.15 }}
            >
              <div className="p-4 rounded-2xl bg-primary/10 mb-4">
                <feature.icon className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Pricing Preview Section
const PricingPreviewSection = ({ navigate }) => {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });

  return (
    <section ref={ref} className="py-20 px-4">
      <motion.div
        className="container mx-auto text-center"
        initial={{ opacity: 0, y: 40 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6 }}
      >
        <h2 className="text-4xl md:text-5xl font-bold mb-4">
          Simple, <span className="gradient-text">Transparent Pricing</span>
        </h2>
        <p className="text-xl text-muted-foreground mb-8">
          Start free, upgrade when you're ready
        </p>
        
        <AnimatedButton
          size="xl"
          variant="premium"
          onClick={() => navigate('/pricing')}
        >
          View All Plans
          <ArrowRight className="h-5 w-5" />
        </AnimatedButton>
      </motion.div>
    </section>
  );
};

// Final CTA Section
const FinalCTASection = ({ navigate }) => {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });

  return (
    <section ref={ref} className="py-20 px-4 bg-gradient-primary">
      <motion.div
        className="container mx-auto text-center"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={inView ? { opacity: 1, scale: 1 } : {}}
        transition={{ duration: 0.6 }}
      >
        <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
          Ready to Grow Your Business?
        </h2>
        <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
          Join 1000+ businesses using AstraMark AI to automate their growth
        </p>
        
        <AnimatedButton
          size="xl"
          variant="default"
          className="bg-white text-primary hover:bg-white/90"
          onClick={() => navigate('/register')}
        >
          Start Growing Free
          <ArrowRight className="h-5 w-5" />
        </AnimatedButton>
        
        <p className="text-white/80 mt-4 text-sm">
          No credit card required • 14-day money-back guarantee
        </p>
      </motion.div>
    </section>
  );
};

export default LandingPage;
