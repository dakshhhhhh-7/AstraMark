import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AnimatedButton } from '@/components/ui/animated-button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Sparkles, Send, Bot, User, DollarSign, TrendingUp, Download } from 'lucide-react';
import apiClient from '@/utils/apiClient';
import { toast } from 'sonner';

/**
 * AIChatPanel - AI Business Analysis Chat with Market Research & Financial Projections
 */
export const AIChatPanel = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: "👋 Hi! I'm your AI business analyst. I can provide complete business analysis with:\n\n• **Market Research** - Detailed market size, growth rate, opportunities\n• **Competitor Analysis** - Real competitor data and insights\n• **User Personas** - Target audience profiles and pain points\n• **Marketing Strategies** - Channel-specific strategies with content ideas\n• **Revenue Projections** - Financial forecasts and growth timeline\n• **AI Insights** - Data-driven recommendations\n\n**To get a complete analysis:**\n1. Click 'Budget Planning' or add a budget\n2. Describe your business idea\n3. Hit send to get comprehensive research!\n\nExample: \"SaaS platform for small businesses\" with budget ₹50,000",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [budget, setBudget] = useState('');
  const [currency, setCurrency] = useState('INR');
  const [isLoading, setIsLoading] = useState(false);
  const [showBudgetInput, setShowBudgetInput] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input + (budget ? ` [Budget: ${currency} ${parseFloat(budget).toLocaleString()}]` : ''),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Check if this is a business analysis request
      const isBusinessAnalysis = input.toLowerCase().includes('business') || 
                                  input.toLowerCase().includes('analyze') || 
                                  input.toLowerCase().includes('market') ||
                                  input.toLowerCase().includes('startup') ||
                                  budget;

      let response;
      let analysisData = null;

      if (isBusinessAnalysis && budget) {
        // Call the full business analysis endpoint
        response = await apiClient.post('/api/analyze', {
          business_type: input,
          target_market: 'General market',
          monthly_budget: budget || '5000',
          primary_goal: 'Business growth and market analysis',
          additional_info: 'Comprehensive analysis requested'
        });
        
        analysisData = response.data;
        
        // Format the complete analysis response
        const formattedResponse = formatBusinessAnalysis(analysisData);
        
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: formattedResponse,
          timestamp: new Date(),
          reportAvailable: true,
          analysisData: analysisData,
        };

        setMessages((prev) => [...prev, aiMessage]);
        toast.success('✅ Complete business analysis ready!');
      } else {
        // Regular chat
        response = await apiClient.post('/api/ai/chat', {
          message: input,
          history: messages.slice(-5),
          budget: budget ? parseFloat(budget) : null,
          currency: currency,
        });

        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: response.data.response,
          timestamp: new Date(),
          reportAvailable: response.data.report_available,
        };

        setMessages((prev) => [...prev, aiMessage]);
        
        if (response.data.report_available) {
          toast.success('✅ Analysis complete! Detailed report available.');
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to get AI response. Please try again.');
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: "I apologize, but I'm having trouble processing your request. Please try again.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const formatBusinessAnalysis = (data) => {
    if (!data) return "Analysis data not available.";

    let formatted = `# 📊 Complete Business Analysis\n\n`;
    
    // Overview
    if (data.overview) {
      formatted += `## 🎯 Overview\n${data.overview}\n\n`;
    }

    // Market Analysis
    if (data.market_analysis) {
      const ma = data.market_analysis;
      formatted += `## 📈 Market Analysis\n\n`;
      formatted += `**Market Size:** ${ma.market_size || 'N/A'}\n`;
      formatted += `**Growth Rate:** ${ma.growth_rate || 'N/A'}\n`;
      formatted += `**Entry Barriers:** ${ma.entry_barriers || 'N/A'}\n\n`;
      
      if (ma.opportunities?.length) {
        formatted += `**Opportunities:**\n${ma.opportunities.map(o => `• ${o}`).join('\n')}\n\n`;
      }
      
      if (ma.risks?.length) {
        formatted += `**Risks:**\n${ma.risks.map(r => `• ${r}`).join('\n')}\n\n`;
      }
    }

    // User Personas
    if (data.user_personas?.length) {
      formatted += `## 👥 Target User Personas\n\n`;
      data.user_personas.forEach((persona, idx) => {
        formatted += `### ${idx + 1}. ${persona.name}\n`;
        formatted += `**Demographics:** ${persona.demographics}\n`;
        formatted += `**Pain Points:** ${persona.pain_points?.join(', ') || 'N/A'}\n`;
        formatted += `**Buying Triggers:** ${persona.buying_triggers?.join(', ') || 'N/A'}\n\n`;
      });
    }

    // Marketing Strategies
    if (data.strategies?.length) {
      formatted += `## 🎯 Marketing Strategies\n\n`;
      data.strategies.forEach((strategy, idx) => {
        formatted += `### ${idx + 1}. ${strategy.channel}\n`;
        formatted += `**Strategy:** ${strategy.strategy}\n`;
        if (strategy.content_ideas?.length) {
          formatted += `**Content Ideas:**\n${strategy.content_ideas.map(i => `• ${i}`).join('\n')}\n`;
        }
        formatted += `**Schedule:** ${strategy.posting_schedule}\n\n`;
      });
    }

    // Revenue Projection
    if (data.revenue_projection) {
      const rp = data.revenue_projection;
      formatted += `## 💰 Revenue Projection\n\n`;
      formatted += `**Minimum Monthly:** ${rp.min_monthly}\n`;
      formatted += `**Maximum Monthly:** ${rp.max_monthly}\n`;
      formatted += `**Growth Timeline:** ${rp.growth_timeline}\n\n`;
    }

    // AI Insights
    if (data.ai_insights?.length) {
      formatted += `## 🤖 AI Insights\n\n`;
      data.ai_insights.forEach((insight, idx) => {
        formatted += `**${insight.insight_type}** (${insight.confidence}% confidence)\n`;
        formatted += `${insight.description}\n\n`;
      });
    }

    // Competitor Data
    if (data.competitor_data?.competitors?.length) {
      formatted += `## 🏢 Competitor Analysis\n\n`;
      formatted += `Found ${data.competitor_data.competitors.length} competitors in the market.\n\n`;
    }

    // Final Verdict
    if (data.ai_verdict) {
      formatted += `## ✨ AI Verdict\n\n`;
      formatted += `**Growth Potential:** ${data.ai_verdict}\n`;
      formatted += `**Confidence Score:** ${data.confidence_score}%\n`;
      formatted += `**Biggest Opportunity:** ${data.biggest_opportunity}\n`;
      formatted += `**Biggest Risk:** ${data.biggest_risk}\n`;
      formatted += `**Next Action:** ${data.next_action}\n\n`;
    }

    formatted += `---\n\n`;
    formatted += `**Virality Score:** ${data.virality_score || 'N/A'}/100\n`;
    formatted += `**Retention Score:** ${data.retention_score || 'N/A'}/100\n`;
    formatted += `**AI Service:** ${data.ai_service_used || 'Unknown'}\n`;

    return formatted;
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickActions = [
    { label: 'Analyze Business', icon: Sparkles, prompt: 'I want to start a SaaS platform for small businesses' },
    { label: 'Budget Planning', icon: DollarSign, prompt: 'Help me plan a marketing budget for my e-commerce store' },
    { label: 'Market Research', icon: TrendingUp, prompt: 'Research the market for a food delivery startup' },
  ];

  const handleQuickAction = (prompt) => {
    setInput(prompt);
    setShowBudgetInput(true);
    inputRef.current?.focus();
  };

  return (
    <Card variant="glass" className="h-full flex flex-col overflow-hidden">
      <CardHeader className="border-b border-border/50 flex-shrink-0 pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <div className="p-1.5 rounded-lg bg-gradient-primary">
            <Bot className="h-4 w-4 text-white" />
          </div>
          <span className="font-semibold">AI Business Analyst</span>
          <motion.div
            className="ml-auto w-2 h-2 rounded-full bg-success"
            animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0 min-h-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-0">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-2 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-7 h-7 rounded-full bg-gradient-primary flex items-center justify-center">
                    <Bot className="h-3.5 w-3.5 text-white" />
                  </div>
                )}

                <div className={`max-w-[85%] rounded-lg p-2.5 ${message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                  <div className="text-xs leading-relaxed whitespace-pre-wrap prose prose-sm max-w-none dark:prose-invert">
                    {message.content.split('\n').map((line, idx) => {
                      // Handle headers
                      if (line.startsWith('# ')) {
                        return <h1 key={idx} className="text-base font-bold mt-2 mb-1">{line.substring(2)}</h1>;
                      }
                      if (line.startsWith('## ')) {
                        return <h2 key={idx} className="text-sm font-bold mt-2 mb-1 text-primary">{line.substring(3)}</h2>;
                      }
                      if (line.startsWith('### ')) {
                        return <h3 key={idx} className="text-xs font-semibold mt-1 mb-0.5">{line.substring(4)}</h3>;
                      }
                      // Handle bold text
                      if (line.includes('**')) {
                        const parts = line.split('**');
                        return (
                          <p key={idx} className="my-0.5">
                            {parts.map((part, i) => i % 2 === 1 ? <strong key={i}>{part}</strong> : part)}
                          </p>
                        );
                      }
                      // Handle bullet points
                      if (line.startsWith('• ') || line.startsWith('- ')) {
                        return <li key={idx} className="ml-3 my-0.5">{line.substring(2)}</li>;
                      }
                      // Handle horizontal rule
                      if (line === '---') {
                        return <hr key={idx} className="my-2 border-border" />;
                      }
                      // Regular text
                      if (line.trim()) {
                        return <p key={idx} className="my-0.5">{line}</p>;
                      }
                      return <br key={idx} />;
                    })}
                  </div>
                  
                  {message.reportAvailable && (
                    <AnimatedButton size="sm" variant="outline" className="mt-2 h-7 text-xs" onClick={() => toast.info('Report download coming soon!')}>
                      <Download className="h-3 w-3 mr-1" />
                      Download Report
                    </AnimatedButton>
                  )}
                  
                  <p className="text-[10px] opacity-50 mt-1">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center">
                    <User className="h-3.5 w-3.5 text-primary" />
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-2">
              <div className="flex-shrink-0 w-7 h-7 rounded-full bg-gradient-primary flex items-center justify-center">
                <Bot className="h-3.5 w-3.5 text-white" />
              </div>
              <div className="bg-muted rounded-lg p-2.5">
                <LoadingSpinner size="sm" />
                <p className="text-[10px] text-muted-foreground mt-1">Analyzing...</p>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Actions */}
        <div className="px-3 py-2 border-t border-border/50 flex-shrink-0">
          <div className="flex gap-1.5 flex-wrap">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <motion.button
                  key={action.label}
                  className="px-2.5 py-1 rounded-full bg-muted hover:bg-muted/80 text-[11px] flex items-center gap-1 transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleQuickAction(action.prompt)}
                >
                  <Icon className="h-3 w-3" />
                  {action.label}
                </motion.button>
              );
            })}
          </div>
        </div>

        {/* Budget Input */}
        {showBudgetInput && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }} 
            animate={{ opacity: 1, height: 'auto' }} 
            exit={{ opacity: 0, height: 0 }}
            className="px-3 py-2 border-t border-border/50 bg-muted/30 flex-shrink-0"
          >
            <Label className="text-[10px] mb-1.5 block font-medium">Budget (Optional)</Label>
            <div className="flex gap-1.5">
              <select 
                value={currency} 
                onChange={(e) => setCurrency(e.target.value)} 
                className="px-2 py-1 rounded bg-background border border-border text-xs focus:outline-none focus:ring-1 focus:ring-primary"
              >
                <option value="INR">₹ INR</option>
                <option value="USD">$ USD</option>
                <option value="EUR">€ EUR</option>
              </select>
              <Input 
                type="number" 
                value={budget} 
                onChange={(e) => setBudget(e.target.value)} 
                placeholder="Enter amount" 
                className="flex-1 text-xs h-8" 
              />
              <AnimatedButton 
                size="sm" 
                variant="ghost" 
                className="h-8 px-2 text-xs"
                onClick={() => { setShowBudgetInput(false); setBudget(''); }}
              >
                Clear
              </AnimatedButton>
            </div>
          </motion.div>
        )}

        {/* Input */}
        <div className="p-3 border-t border-border/50 flex-shrink-0">
          <div className="flex gap-2">
            <Input 
              ref={inputRef} 
              value={input} 
              onChange={(e) => setInput(e.target.value)} 
              onKeyPress={handleKeyPress} 
              placeholder="Describe your business idea..." 
              className="flex-1 text-sm h-9" 
              disabled={isLoading} 
            />
            {!showBudgetInput && (
              <AnimatedButton 
                size="icon" 
                variant="outline" 
                className="h-9 w-9"
                onClick={() => setShowBudgetInput(true)} 
                title="Add budget"
              >
                <DollarSign className="h-4 w-4" />
              </AnimatedButton>
            )}
            <AnimatedButton 
              size="icon" 
              variant="premium" 
              className="h-9 w-9"
              onClick={handleSend} 
              disabled={!input.trim() || isLoading}
            >
              {isLoading ? <LoadingSpinner size="sm" /> : <Send className="h-4 w-4" />}
            </AnimatedButton>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
