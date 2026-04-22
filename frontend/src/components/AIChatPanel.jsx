import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { AnimatedButton } from '@/components/ui/animated-button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Sparkles, Send, Bot, User, Zap } from 'lucide-react';
import apiClient from '@/utils/apiClient';
import { toast } from 'sonner';

/**
 * AIChatPanel - AI Chat interface integrated into the dashboard
 * Allows users to interact with the AI for business advice, content generation, etc.
 */
export const AIChatPanel = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: "👋 Hi! I'm your AI marketing assistant. I can help you with:\n\n• Generate content ideas\n• Analyze your market\n• Create ad campaigns\n• Optimize your strategy\n\nWhat would you like to work on today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
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
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call AI endpoint (you'll need to create this endpoint in the backend)
      const response = await apiClient.post('/api/ai/chat', {
        message: input,
        history: messages.slice(-5), // Send last 5 messages for context
      });

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      
      // Fallback response if endpoint doesn't exist yet
      const fallbackMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: "I'm here to help! The AI chat endpoint is being set up. In the meantime, you can:\n\n• Use the Quick Actions panel to generate content\n• Check your Growth Metrics\n• Enable Auto Mode for automated marketing\n\nWhat specific task would you like help with?",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, fallbackMessage]);
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
    { label: 'Generate Content', icon: Sparkles },
    { label: 'Analyze Market', icon: Zap },
    { label: 'Create Campaign', icon: Bot },
  ];

  const handleQuickAction = (action) => {
    setInput(action);
    inputRef.current?.focus();
  };

  return (
    <Card variant="glass" className="h-full flex flex-col">
      <CardHeader className="border-b border-border/50">
        <CardTitle className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-gradient-primary">
            <Bot className="h-5 w-5 text-white" />
          </div>
          AI Assistant
          <motion.div
            className="ml-auto w-2 h-2 rounded-full bg-success"
            animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                )}

                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <p className="text-xs opacity-60 mt-1">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
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
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-3"
            >
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div className="bg-muted rounded-lg p-3">
                <LoadingSpinner size="sm" />
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
                  className="px-3 py-1.5 rounded-full bg-muted hover:bg-muted/80 text-xs flex items-center gap-1.5 transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleQuickAction(action.label)}
                >
                  <Icon className="h-3 w-3" />
                  {action.label}
                </motion.button>
              );
            })}
          </div>
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-border/50">
          <div className="flex gap-2">
            <Input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your marketing..."
              className="flex-1"
              disabled={isLoading}
            />
            <AnimatedButton
              size="icon"
              variant="premium"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
            >
              {isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </AnimatedButton>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
