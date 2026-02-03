import { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL !== undefined ? process.env.REACT_APP_BACKEND_URL : 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

export function BusinessInputForm({ onAnalysisComplete, isLoading, setIsLoading }) {
  const [formData, setFormData] = useState({
    business_type: '',
    target_market: '',
    monthly_budget: '',
    primary_goal: '',
    additional_info: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.business_type || !formData.target_market || !formData.monthly_budget || !formData.primary_goal) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/analyze`, formData);
      toast.success('Analysis complete!');
      onAnalysisComplete(response.data);
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error(error.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-white mb-3">
          AI-Powered Marketing <span className="gradient-text">Intelligence</span>
        </h2>
        <p className="text-slate-400 text-lg">
          Get comprehensive marketing strategies, user insights, and revenue projections in seconds
        </p>
      </div>

      <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm" data-testid="business-input-form">
        <CardHeader>
          <CardTitle className="text-white">Tell Us About Your Business</CardTitle>
          <CardDescription className="text-slate-400">
            Provide details to receive personalized marketing intelligence
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="business_type" className="text-slate-200">
                Business Type <span className="text-red-500">*</span>
              </Label>
              <Input
                id="business_type"
                name="business_type"
                data-testid="business-type-input"
                placeholder="e.g., SaaS, E-commerce, Consulting, Agency"
                value={formData.business_type}
                onChange={handleChange}
                className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="target_market" className="text-slate-200">
                Target Market <span className="text-red-500">*</span>
              </Label>
              <Input
                id="target_market"
                name="target_market"
                data-testid="target-market-input"
                placeholder="e.g., Small business owners in USA, B2B companies, Young professionals"
                value={formData.target_market}
                onChange={handleChange}
                className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="monthly_budget" className="text-slate-200">
                Monthly Marketing Budget <span className="text-red-500">*</span>
              </Label>
              <Input
                id="monthly_budget"
                name="monthly_budget"
                data-testid="monthly-budget-input"
                placeholder="e.g., ₹50,000, $5,000, €3,000"
                value={formData.monthly_budget}
                onChange={handleChange}
                className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="primary_goal" className="text-slate-200">
                Primary Goal <span className="text-red-500">*</span>
              </Label>
              <Input
                id="primary_goal"
                name="primary_goal"
                data-testid="primary-goal-input"
                placeholder="e.g., Increase leads by 50%, Build brand awareness, Drive sales"
                value={formData.primary_goal}
                onChange={handleChange}
                className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="additional_info" className="text-slate-200">
                Additional Information (Optional)
              </Label>
              <Textarea
                id="additional_info"
                name="additional_info"
                data-testid="additional-info-input"
                placeholder="Any other details about your business, challenges, or specific needs..."
                value={formData.additional_info}
                onChange={handleChange}
                rows={4}
                className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
              />
            </div>

            <Button
              type="submit"
              data-testid="generate-analysis-btn"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-6 text-lg"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Analyzing with AI...
                </>
              ) : (
                '🚀 Generate AI Marketing Strategy'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900/30 border border-slate-800 rounded-lg p-4 text-center">
          <div className="text-purple-400 text-2xl mb-2">⚡</div>
          <div className="text-white font-semibold">AI-Powered Analysis</div>
          <div className="text-slate-400 text-sm">Gemini 2.0 Intelligence</div>
        </div>
        <div className="bg-slate-900/30 border border-slate-800 rounded-lg p-4 text-center">
          <div className="text-pink-400 text-2xl mb-2">📊</div>
          <div className="text-white font-semibold">Multi-Channel Strategy</div>
          <div className="text-slate-400 text-sm">SEO, Content, Ads, Social</div>
        </div>
        <div className="bg-slate-900/30 border border-slate-800 rounded-lg p-4 text-center">
          <div className="text-purple-400 text-2xl mb-2">💰</div>
          <div className="text-white font-semibold">Revenue Projections</div>
          <div className="text-slate-400 text-sm">Data-Driven Forecasts</div>
        </div>
      </div>
    </div>
  );
}
