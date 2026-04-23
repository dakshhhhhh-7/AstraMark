import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Header } from '@/components/navigation/Header';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { AnimatedButton } from '@/components/ui/animated-button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { fadeInUp, staggerContainer, staggerItem } from '@/lib/animations';
import { Sparkles, TrendingUp, Users, DollarSign, Target, BarChart3, Download } from 'lucide-react';
import apiClient from '@/utils/apiClient';
import { toast } from 'sonner';

/**
 * AnalysisPage - Dedicated business analysis page (like old AstraMark)
 */
const AnalysisPage = () => {
  const [formData, setFormData] = useState({
    businessType: '',
    targetMarket: '',
    monthlyBudget: '',
    primaryGoal: '',
    additionalInfo: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.businessType || !formData.targetMarket || !formData.monthlyBudget || !formData.primaryGoal) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsLoading(true);
    setAnalysisResult(null);

    try {
      const response = await apiClient.post('/api/analyze', {
        business_type: formData.businessType,
        target_market: formData.targetMarket,
        monthly_budget: formData.monthlyBudget,
        primary_goal: formData.primaryGoal,
        additional_info: formData.additionalInfo || 'None',
      });

      setAnalysisResult(response.data);
      toast.success('✅ Analysis complete!');
      
      // Scroll to results
      setTimeout(() => {
        document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error('Failed to generate analysis. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

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
          {/* Header */}
          <motion.div variants={staggerItem} className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4 gradient-text">
              AI Business Analysis
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Get comprehensive market research, competitor analysis, and growth strategies powered by AI
            </p>
          </motion.div>

          {/* Input Form */}
          <motion.div variants={staggerItem}>
            <Card variant="glass" className="max-w-3xl mx-auto">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  Tell Us About Your Business
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="businessType">Business Type *</Label>
                    <Input
                      id="businessType"
                      name="businessType"
                      placeholder="e.g., SaaS platform for small businesses"
                      value={formData.businessType}
                      onChange={handleInputChange}
                      disabled={isLoading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="targetMarket">Target Market *</Label>
                    <Input
                      id="targetMarket"
                      name="targetMarket"
                      placeholder="e.g., Small businesses and startups in India"
                      value={formData.targetMarket}
                      onChange={handleInputChange}
                      disabled={isLoading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="monthlyBudget">Monthly Budget (₹) *</Label>
                    <Input
                      id="monthlyBudget"
                      name="monthlyBudget"
                      type="text"
                      placeholder="e.g., 50000"
                      value={formData.monthlyBudget}
                      onChange={handleInputChange}
                      disabled={isLoading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="primaryGoal">Primary Goal *</Label>
                    <Textarea
                      id="primaryGoal"
                      name="primaryGoal"
                      placeholder="e.g., Generate leads and increase brand awareness through digital marketing"
                      value={formData.primaryGoal}
                      onChange={handleInputChange}
                      disabled={isLoading}
                      rows={3}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="additionalInfo">Additional Information (Optional)</Label>
                    <Textarea
                      id="additionalInfo"
                      name="additionalInfo"
                      placeholder="Any other details about your business..."
                      value={formData.additionalInfo}
                      onChange={handleInputChange}
                      disabled={isLoading}
                      rows={3}
                    />
                  </div>

                  <AnimatedButton
                    type="submit"
                    variant="premium"
                    className="w-full"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <LoadingSpinner size="sm" className="mr-2" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4 mr-2" />
                        Generate Analysis
                      </>
                    )}
                  </AnimatedButton>
                </form>
              </CardContent>
            </Card>
          </motion.div>

          {/* Results */}
          {analysisResult && (
            <motion.div
              id="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Overview */}
              {analysisResult.overview && (
                <Card variant="glass">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Sparkles className="h-5 w-5 text-primary" />
                      Overview
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">{analysisResult.overview}</p>
                  </CardContent>
                </Card>
              )}

              {/* Market Analysis */}
              {analysisResult.market_analysis && (
                <Card variant="glass">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-success" />
                      Market Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-semibold mb-1">Market Size</h4>
                        <p className="text-muted-foreground">{analysisResult.market_analysis.market_size}</p>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-1">Growth Rate</h4>
                        <p className="text-muted-foreground">{analysisResult.market_analysis.growth_rate}</p>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold mb-1">Entry Barriers</h4>
                      <p className="text-muted-foreground">{analysisResult.market_analysis.entry_barriers}</p>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-semibold mb-2 text-success">Opportunities</h4>
                        <ul className="space-y-1">
                          {analysisResult.market_analysis.opportunities?.map((opp, idx) => (
                            <li key={idx} className="text-sm text-muted-foreground">• {opp}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2 text-destructive">Risks</h4>
                        <ul className="space-y-1">
                          {analysisResult.market_analysis.risks?.map((risk, idx) => (
                            <li key={idx} className="text-sm text-muted-foreground">• {risk}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* User Personas */}
              {analysisResult.user_personas?.length > 0 && (
                <Card variant="glass">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="h-5 w-5 text-accent" />
                      Target User Personas
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {analysisResult.user_personas.map((persona, idx) => (
                      <div key={idx} className="p-4 rounded-lg bg-muted/30">
                        <h4 className="font-semibold text-lg mb-2">{persona.name}</h4>
                        <div className="space-y-2 text-sm">
                          <p><strong>Demographics:</strong> {persona.demographics}</p>
                          <p><strong>Psychographics:</strong> {persona.psychographics}</p>
                          <div>
                            <strong>Pain Points:</strong>
                            <ul className="ml-4 mt-1">
                              {persona.pain_points?.map((point, i) => (
                                <li key={i}>• {point}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Marketing Strategies */}
              {analysisResult.strategies?.length > 0 && (
                <Card variant="glass">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-5 w-5 text-primary" />
                      Marketing Strategies
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {analysisResult.strategies.map((strategy, idx) => (
                      <div key={idx} className="p-4 rounded-lg bg-muted/30">
                        <h4 className="font-semibold text-lg mb-2">{strategy.channel}</h4>
                        <p className="text-sm text-muted-foreground mb-3">{strategy.strategy}</p>
                        <div className="space-y-2">
                          <div>
                            <strong className="text-sm">Content Ideas:</strong>
                            <ul className="ml-4 mt-1 text-sm">
                              {strategy.content_ideas?.map((idea, i) => (
                                <li key={i}>• {idea}</li>
                              ))}
                            </ul>
                          </div>
                          <p className="text-sm"><strong>Schedule:</strong> {strategy.posting_schedule}</p>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Revenue Projection */}
              {analysisResult.revenue_projection && (
                <Card variant="glass">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <DollarSign className="h-5 w-5 text-success" />
                      Revenue Projection
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-3 gap-4">
                      <div className="p-4 rounded-lg bg-muted/30 text-center">
                        <p className="text-sm text-muted-foreground mb-1">Minimum Monthly</p>
                        <p className="text-2xl font-bold text-success">{analysisResult.revenue_projection.min_monthly}</p>
                      </div>
                      <div className="p-4 rounded-lg bg-muted/30 text-center">
                        <p className="text-sm text-muted-foreground mb-1">Maximum Monthly</p>
                        <p className="text-2xl font-bold text-success">{analysisResult.revenue_projection.max_monthly}</p>
                      </div>
                      <div className="p-4 rounded-lg bg-muted/30 text-center">
                        <p className="text-sm text-muted-foreground mb-1">Growth Timeline</p>
                        <p className="text-lg font-semibold">{analysisResult.revenue_projection.growth_timeline}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* AI Verdict */}
              {analysisResult.ai_verdict && (
                <Card variant="premium">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5 text-primary" />
                      AI Verdict
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Growth Potential</p>
                        <p className="text-xl font-bold">{analysisResult.ai_verdict}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground mb-1">Confidence Score</p>
                        <p className="text-xl font-bold">{analysisResult.confidence_score}%</p>
                      </div>
                    </div>
                    
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="p-3 rounded-lg bg-success/10">
                        <p className="text-sm font-semibold text-success mb-1">Biggest Opportunity</p>
                        <p className="text-sm">{analysisResult.biggest_opportunity}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-destructive/10">
                        <p className="text-sm font-semibold text-destructive mb-1">Biggest Risk</p>
                        <p className="text-sm">{analysisResult.biggest_risk}</p>
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-primary/10">
                      <p className="text-sm font-semibold text-primary mb-1">Next Action</p>
                      <p className="text-sm">{analysisResult.next_action}</p>
                    </div>

                    <div className="flex gap-4 justify-center pt-4">
                      <div className="text-center">
                        <p className="text-sm text-muted-foreground mb-1">Virality Score</p>
                        <p className="text-2xl font-bold">{analysisResult.virality_score}/100</p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-muted-foreground mb-1">Retention Score</p>
                        <p className="text-2xl font-bold">{analysisResult.retention_score}/100</p>
                      </div>
                    </div>

                    <AnimatedButton variant="premium" className="w-full mt-4">
                      <Download className="h-4 w-4 mr-2" />
                      Download Full Report (Coming Soon)
                    </AnimatedButton>
                  </CardContent>
                </Card>
              )}
            </motion.div>
          )}
        </motion.div>
      </main>
    </div>
  );
};

export default AnalysisPage;
