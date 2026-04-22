import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useDashboardStore, useAutoModeStore, useUserStore } from '@/lib/store';
import { Header } from '@/components/navigation/Header';
import { MetricCard, GrowthScore } from '@/components/ui/animated-counter';
import { AnimatedButton } from '@/components/ui/animated-button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Switch } from '@/components/ui/switch';
import { AIChatPanel } from '@/components/AIChatPanel';
import { fadeInUp, staggerContainer, staggerItem } from '@/lib/animations';
import {
  DollarSign, Users, TrendingUp, Zap, Sparkles, Target,
  BarChart3, Clock, CheckCircle2, ArrowRight, Rocket, Bell
} from 'lucide-react';

export function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { metrics, insights, liveFeed, setMetrics, addLiveFeedItem } = useDashboardStore();
  const { isEnabled: autoModeEnabled, enableAutoMode, disableAutoMode } = useAutoModeStore();
  const { canUseAutoMode } = useUserStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading dashboard data
    setTimeout(() => {
      setMetrics({
        revenue: 12000,
        leads: 42,
        engagement: 23,
        growthScore: 87,
      });
      setIsLoading(false);
    }, 1000);

    // Simulate live feed updates
    const feedInterval = setInterval(() => {
      const updates = [
        { type: 'content', message: 'AI created 5 social media posts', icon: 'sparkles' },
        { type: 'ad', message: 'Ad campaign performing well (+15% CTR)', icon: 'trending' },
        { type: 'seo', message: 'SEO ranking improved for 3 keywords', icon: 'target' },
        { type: 'lead', message: 'New lead captured from Facebook', icon: 'users' },
      ];
      const randomUpdate = updates[Math.floor(Math.random() * updates.length)];
      addLiveFeedItem(randomUpdate);
    }, 5000);

    return () => clearInterval(feedInterval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleAutoModeToggle = () => {
    if (autoModeEnabled) {
      disableAutoMode();
    } else {
      if (canUseAutoMode()) {
        enableAutoMode();
      } else {
        navigate('/pricing');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <LoadingSpinner size="xl" />
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
          className="space-y-8"
        >
          {/* Welcome Section */}
          <motion.div variants={staggerItem}>
            <h1 className="text-3xl md:text-4xl font-bold mb-2">
              Welcome back, {user?.name || 'User'}! 👋
            </h1>
            <p className="text-muted-foreground">
              Here's your growth overview for this week
            </p>
          </motion.div>

          {/* Auto Mode Toggle */}
          <motion.div variants={staggerItem}>
            <Card variant="premium" className="relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-primary opacity-10" />
              <CardContent className="relative p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-gradient-primary">
                      <Zap className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold mb-1">Auto Growth Mode</h3>
                      <p className="text-sm text-muted-foreground">
                        {autoModeEnabled
                          ? 'AI is handling your marketing automatically'
                          : 'Let AI handle everything on autopilot'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    {!canUseAutoMode() && (
                      <span className="text-sm text-muted-foreground">Pro plan required</span>
                    )}
                    <Switch
                      checked={autoModeEnabled}
                      onCheckedChange={handleAutoModeToggle}
                      className="data-[state=checked]:bg-gradient-primary"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Growth Metrics */}
          <motion.div variants={staggerItem}>
            <h2 className="text-2xl font-semibold mb-4">Your Growth This Week</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <MetricCard
                title="Revenue"
                value={metrics.revenue}
                change={23}
                icon={DollarSign}
                variant="currency"
              />
              <MetricCard
                title="New Leads"
                value={metrics.leads}
                change={18}
                icon={Users}
                variant="number"
              />
              <MetricCard
                title="Engagement Rate"
                value={metrics.engagement}
                change={15}
                icon={TrendingUp}
                variant="percentage"
              />
            </div>
          </motion.div>

          {/* Action Panel & Live Feed & AI Chat */}
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Action Panel */}
            <motion.div variants={staggerItem}>
              <Card variant="glass">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Rocket className="h-5 w-5 text-primary" />
                    Quick Actions
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <ActionButton
                    icon={Sparkles}
                    title="Generate Content"
                    description="Create 10 social media posts instantly"
                    onClick={() => {}}
                  />
                  <ActionButton
                    icon={Target}
                    title="Run Ads"
                    description="Launch optimized ad campaigns"
                    onClick={() => {}}
                  />
                  <ActionButton
                    icon={BarChart3}
                    title="Optimize Campaign"
                    description="Improve performance with AI insights"
                    onClick={() => {}}
                  />
                </CardContent>
              </Card>
            </motion.div>

            {/* Live Feed */}
            <motion.div variants={staggerItem}>
              <Card variant="glass">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bell className="h-5 w-5 text-accent" />
                    Live Feed
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 max-h-96 overflow-y-auto">
                  {liveFeed.slice(0, 10).map((item) => (
                    <motion.div
                      key={item.id}
                      className="flex items-start gap-3 p-3 rounded-lg bg-muted/30"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                    >
                      <div className="p-2 rounded-lg bg-primary/10">
                        {item.icon === 'sparkles' && <Sparkles className="h-4 w-4 text-primary" />}
                        {item.icon === 'trending' && <TrendingUp className="h-4 w-4 text-success" />}
                        {item.icon === 'target' && <Target className="h-4 w-4 text-accent" />}
                        {item.icon === 'users' && <Users className="h-4 w-4 text-primary" />}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm">{item.message}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Date(item.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>

            {/* AI Chat Panel */}
            <motion.div variants={staggerItem} className="lg:row-span-2">
              <div className="h-[600px]">
                <AIChatPanel />
              </div>
            </motion.div>
          </div>

          {/* AI Insights */}
          <motion.div variants={staggerItem}>
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  AI Insights & Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <InsightCard
                  title="Quick Win"
                  description="Your audience prefers video content. Create 3 reels this week for 2x engagement."
                  action="Create Reels"
                />
                <InsightCard
                  title="Optimization"
                  description="Run ads at 8PM for 25% better conversion rates based on your audience data."
                  action="Schedule Ads"
                />
                <InsightCard
                  title="Growth Opportunity"
                  description="Expand to Instagram Stories - 40% of your audience is active there."
                  action="Start Campaign"
                />
              </CardContent>
            </Card>
          </motion.div>

          {/* Growth Score */}
          <motion.div variants={staggerItem} className="flex justify-center">
            <GrowthScore score={metrics.growthScore} />
          </motion.div>
        </motion.div>
      </main>
    </div>
  );
}

// Action Button Component
const ActionButton = ({ icon: Icon, title, description, onClick }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async () => {
    setIsLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsLoading(false);
  };

  return (
    <motion.button
      className="w-full p-4 rounded-lg border-2 border-border hover:border-primary bg-background/50 transition-all text-left group"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={handleClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
            <Icon className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h4 className="font-semibold">{title}</h4>
            <p className="text-sm text-muted-foreground">{description}</p>
          </div>
        </div>
        {isLoading ? (
          <LoadingSpinner size="sm" />
        ) : (
          <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
        )}
      </div>
    </motion.button>
  );
};

// Insight Card Component
const InsightCard = ({ title, description, action }) => {
  return (
    <div className="flex items-start justify-between p-4 rounded-lg bg-muted/30">
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2 py-1 rounded-full bg-accent/10 text-accent text-xs font-medium">
            {title}
          </span>
        </div>
        <p className="text-sm mb-3">{description}</p>
        <AnimatedButton size="sm" variant="outline">
          {action}
        </AnimatedButton>
      </div>
    </div>
  );
};

export default Dashboard;
