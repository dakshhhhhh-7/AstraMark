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
      content: "👋 Hi! I'm your AI business analyst. I can help you with:\n\n• **Market Research** - Analyze any business idea\n• **Budget Planning** - Get detailed budget breakdowns\n• **Profit/Loss Projections** - Revenue forecasts & ROI\n• **Competitor Analysis** - Understand your competition\n• **Growth Strategy** - Actionable recommendations\n\nDescribe your business idea and budget to get started!",
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
      const response = await apiClient.post('/api/ai/chat', {
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

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickActions = [
    { label: 'Analyze Business', icon: Sparkles, prompt: 'I want to analyze a business idea' },
    { label: 'Budget Planning', icon: DollarSign, prompt: 'Help me plan my business budget' },
    { label: 'Market Research', icon: TrendingUp, prompt: 'Research the market for my business' },
  ];

  const handleQuickAction = (prompt) => {
    setInput(prompt);
    setShowBudgetInput(true);
    inputRef.current?.focus();
  };

  return (
    <Card variant="glass" className="h-full flex flex-col">
      <CardHeader className="border-b border-border/50">
        <CardTitle className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-gradient-primary">
            <Bot className="h-5 w-5 text-white" />
          </div>
          AI Business Analyst
          <motion.div
            className="ml-auto w-2 h-2 rounded-full bg-success"
            animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                )}

                <div className={`max-w-[80%] rounded-lg p-3 ${message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  
                  {message.reportAvailable && (
                    <AnimatedButton size="sm" variant="outline" className="mt-2" onClick={() => toast.info('Report download coming soon!')}>
                      <Download className="h-3 w-3 mr-1" />
                      Download Report
                    </AnimatedButton>
                  )}
                  
                  <p className="text-xs opacity-60 mt-1">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                    <User className="h-4 w-4 text-primary" />
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div className="bg-muted rounded-lg p-3">
                <LoadingSpinner size="sm" />
                <p className="text-xs text-muted-foreground mt-1">Analyzing...</p>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Actions */}
        <div className="px-4 py-2 border-t border-border/50">
          <div className="flex gap-2 flex-wrap">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <motion.button
                  key={action.label}
                  className="px-3 py-1.5 rounded-full bg-muted hover:bg-muted/80 text-xs flex items-center gap-1.5"
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
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="px-4 py-2 border-t border-border/50 bg-muted/30">
            <Label className="text-xs mb-2 block">Budget (Optional)</Label>
            <div className="flex gap-2">
              <select value={currency} onChange={(e) => setCurrency(e.target.value)} className="px-2 py-1 rounded bg-background border border-border text-sm">
                <option value="INR">₹ INR</option>
                <option value="USD">$ USD</option>
                <option value="EUR">€ EUR</option>
              </select>
              <Input type="number" value={budget} onChange={(e) => setBudget(e.target.value)} placeholder="Enter amount" className="flex-1 text-sm" />
              <AnimatedButton size="sm" variant="ghost" onClick={() => { setShowBudgetInput(false); setBudget(''); }}>Clear</AnimatedButton>
            </div>
          </motion.div>
        )}

        {/* Input */}
        <div className="p-4 border-t border-border/50">
          <div className="flex gap-2">
            <Input ref={inputRef} value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={handleKeyPress} placeholder="Describe your business idea..." className="flex-1" disabled={isLoading} />
            {!showBudgetInput && (
              <AnimatedButton size="icon" variant="outline" onClick={() => setShowBudgetInput(true)} title="Add budget">
                <DollarSign className="h-4 w-4" />
              </AnimatedButton>
            )}
            <AnimatedButton size="icon" variant="premium" onClick={handleSend} disabled={!input.trim() || isLoading}>
              {isLoading ? <LoadingSpinner size="sm" /> : <Send className="h-4 w-4" />}
            </AnimatedButton>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
