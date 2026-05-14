/*
Business Startup Analysis - AI-Powered Conversational Analysis
Complete AI-powered analysis for new businesses with real-time chat interface
*/

import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import LinearLayout from '../components/LinearLayout';
import { 
  Sparkles, TrendingUp, Users, Target, DollarSign, 
  BarChart3, Zap, ArrowRight, CheckCircle2, AlertCircle,
  Send, Loader2, Download, FileText
} from 'lucide-react';
import { toast } from 'sonner';
import growthOSClient from '../lib/growthOSClient';

export default function BusinessAnalysisPage() {
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  
  // Session state
  const [sessionId, setSessionId] = useState(null);
  const [conversationState, setConversationState] = useState('GREETING');
  const [messages, setMessages] = useState([]);
  
  // UI state
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  
  // Analysis result state
  const [analysisResult, setAnalysisResult] = useState(null);
  const [reportId, setReportId] = useState(null);
  const [reportFormat, setReportFormat] = useState('pdf');

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Start session on mount
  useEffect(() => {
    startNewSession();
  }, []);

  const startNewSession = async () => {
    try {
      setIsLoading(true);
      const response = await growthOSClient.startBusinessAnalysis();
      
      setSessionId(response.session_id);
      setConversationState(response.state);
      setMessages([{
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString()
      }]);
      
      toast.success('Session started!');
    } catch (error) {
      console.error('Error starting session:', error);
      toast.error(error.message || 'Failed to start session. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!userInput.trim() || isSending || !sessionId) return;

    const userMessage = userInput.trim();
    setUserInput('');
    setIsSending(true);

    // Add user message to chat
    const newUserMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, newUserMessage]);

    try {
      const response = await growthOSClient.sendBusinessAnalysisMessage(sessionId, userMessage);
      
      // Add assistant response to chat
      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      // Update conversation state
      setConversationState(response.state);
      
      // Check if analysis is complete and we have results
      if (response.state === 'ANALYSIS_COMPLETE' && response.metadata?.analysis_result) {
        setAnalysisResult(response.metadata.analysis_result);
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Determine error type and provide specific guidance
      let errorMessage = 'Sorry, I encountered an error processing your message.';
      let userGuidance = 'Please try again.';
      
      if (error.message?.includes('network') || error.message?.includes('fetch')) {
        errorMessage = 'Network connection issue detected.';
        userGuidance = 'Please check your internet connection and try again.';
      } else if (error.message?.includes('timeout')) {
        errorMessage = 'The request took too long to process.';
        userGuidance = 'Our servers might be busy. Please try again in a moment.';
      } else if (error.message?.includes('unauthorized') || error.message?.includes('401')) {
        errorMessage = 'Your session has expired.';
        userGuidance = 'Please refresh the page and log in again.';
      } else if (error.message?.includes('service unavailable') || error.message?.includes('503')) {
        errorMessage = 'External data service temporarily unavailable.';
        userGuidance = 'We\'re working with limited data. You can continue, but some insights may be incomplete.';
      }
      
      toast.error(`${errorMessage} ${userGuidance}`);
      
      // Add error message to chat with guidance
      const errorChatMessage = {
        role: 'assistant',
        content: `${errorMessage}\n\n${userGuidance}\n\nIf this problem persists, you can report the issue using the "Report Issue" button below.`,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorChatMessage]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const generateReport = async (format = 'pdf') => {
    if (!sessionId) {
      toast.error('No active session');
      return;
    }

    setIsGeneratingReport(true);
    const loadingToast = toast.loading(`Generating your ${format.toUpperCase()} report...`);

    try {
      const response = await growthOSClient.generateAnalysisReport(sessionId, format);
      
      setReportId(response.report_id);
      setReportFormat(format);
      toast.success(`${format.toUpperCase()} report generated successfully!`, { id: loadingToast });
      
      // Add success message to chat
      const successMessage = {
        role: 'assistant',
        content: `Great! Your comprehensive business analysis report has been generated in ${format.toUpperCase()} format. You can download it now or access it later from your analysis history.`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, successMessage]);
      
    } catch (error) {
      console.error('Error generating report:', error);
      
      // Provide specific error guidance
      let errorMessage = 'Failed to generate report.';
      let guidance = 'Please try again.';
      
      if (error.message?.includes('incomplete')) {
        errorMessage = 'Session data is incomplete.';
        guidance = 'Please complete the conversation before generating a report.';
      } else if (error.message?.includes('market data')) {
        errorMessage = 'Some market data is temporarily unavailable.';
        guidance = 'The report will be generated with available data. Some sections may have limited insights.';
      } else if (error.message?.includes('timeout')) {
        errorMessage = 'Report generation is taking longer than expected.';
        guidance = 'Please wait a moment and try again.';
      }
      
      toast.error(`${errorMessage} ${guidance}`, { id: loadingToast });
      
      // Add error message to chat
      const errorChatMessage = {
        role: 'assistant',
        content: `${errorMessage}\n\n${guidance}\n\nIf you continue to experience issues, please use the "Report Issue" button.`,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorChatMessage]);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const reportIssue = () => {
    const issueData = {
      sessionId,
      conversationState,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      lastMessages: messages.slice(-5) // Last 5 messages for context
    };
    
    // In production, this would send to a support system
    console.log('Issue reported:', issueData);
    
    toast.success('Issue reported! Our team will investigate. You can continue using the analysis.');
    
    // Add confirmation message
    const confirmMessage = {
      role: 'assistant',
      content: 'Thank you for reporting the issue. Our team has been notified and will investigate. You can continue with your analysis, and we\'ll work to resolve any problems.',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, confirmMessage]);
  };

  const downloadReport = async () => {
    if (!reportId) {
      toast.error('No report available');
      return;
    }

    try {
      toast.loading('Downloading report...');
      const blob = await growthOSClient.downloadReport(reportId);
      
      // Determine file extension based on format
      const extensions = {
        'pdf': 'pdf',
        'docx': 'docx',
        'json': 'json'
      };
      const extension = extensions[reportFormat] || 'pdf';
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `business_analysis_report_${reportId.substring(0, 8)}.${extension}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Report downloaded successfully!');
    } catch (error) {
      console.error('Error downloading report:', error);
      toast.error(error.message || 'Failed to download report. Please try again.');
    }
  };

  const resetAnalysis = () => {
    setSessionId(null);
    setConversationState('GREETING');
    setMessages([]);
    setAnalysisResult(null);
    setReportId(null);
    setUserInput('');
    startNewSession();
  };

  const getStateProgress = () => {
    const stateMap = {
      'GREETING': 10,
      'BUSINESS_IDEA_COLLECTION': 25,
      'BUSINESS_IDEA_CONFIRMATION': 40,
      'BUDGET_COLLECTION': 55,
      'BUDGET_CONFIRMATION': 70,
      'ANALYSIS_IN_PROGRESS': 85,
      'ANALYSIS_COMPLETE': 95,
      'REPORT_GENERATION': 98,
      'COMPLETE': 100
    };
    return stateMap[conversationState] || 0;
  };

  const getStateLabel = () => {
    const labelMap = {
      'GREETING': 'Getting Started',
      'BUSINESS_IDEA_COLLECTION': 'Describing Business',
      'BUSINESS_IDEA_CONFIRMATION': 'Confirming Details',
      'BUDGET_COLLECTION': 'Budget Planning',
      'BUDGET_CONFIRMATION': 'Finalizing Budget',
      'ANALYSIS_IN_PROGRESS': 'Analyzing Data',
      'ANALYSIS_COMPLETE': 'Analysis Complete',
      'REPORT_GENERATION': 'Generating Report',
      'COMPLETE': 'Complete'
    };
    return labelMap[conversationState] || 'In Progress';
  };

  const canGenerateReport = () => {
    return conversationState === 'ANALYSIS_COMPLETE' || conversationState === 'COMPLETE';
  };

  const actions = (
    <button
      onClick={() => navigate('/dashboard')}
      className="px-4 py-2 rounded-lg text-sm font-medium text-white/80 hover:text-white hover:bg-white/5 transition-all"
    >
      Back to Dashboard
    </button>
  );

  if (isLoading) {
    return (
      <LinearLayout 
        title="Business Analysis" 
        subtitle="AI-powered business feasibility analysis"
        actions={actions}
      >
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-violet-500" />
            <p className="text-white/60">Starting your analysis session...</p>
          </div>
        </div>
      </LinearLayout>
    );
  }

  return (
    <LinearLayout 
      title="Business Analysis" 
      subtitle="AI-powered business feasibility analysis"
      actions={actions}
    >
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Progress Bar */}
        <div className="p-6 rounded-xl border border-white/5 bg-white/[0.02]">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-violet-400" />
              <span className="font-medium">{getStateLabel()}</span>
            </div>
            <span className="text-sm text-white/60">{getStateProgress()}%</span>
          </div>
          <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-violet-500 to-purple-600 transition-all duration-500 ease-out"
              style={{ width: `${getStateProgress()}%` }}
            />
          </div>
        </div>

        {/* Chat Interface */}
        <div className="rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden flex flex-col h-[600px] sm:h-[600px] max-h-[70vh]">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 overscroll-contain">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] sm:max-w-[80%] rounded-2xl px-3 py-2 sm:px-4 sm:py-3 ${
                    message.role === 'user'
                      ? 'bg-violet-500 text-white'
                      : message.isError
                      ? 'bg-red-500/10 border border-red-500/20 text-red-400'
                      : 'bg-white/5 border border-white/10 text-white/90'
                  }`}
                >
                  <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{message.content}</p>
                  <p className={`text-xs mt-2 ${
                    message.role === 'user' ? 'text-white/60' : 'text-white/40'
                  }`}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            
            {isSending && (
              <div className="flex justify-start">
                <div className="bg-white/5 border border-white/10 rounded-2xl px-3 py-2 sm:px-4 sm:py-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-violet-400" />
                    <span className="text-sm text-white/60">Analyzing...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-white/5 p-3 sm:p-4">
            <div className="flex gap-2 sm:gap-3">
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                disabled={isSending || conversationState === 'COMPLETE'}
                className="flex-1 px-3 py-2 sm:px-4 sm:py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base touch-manipulation"
              />
              <button
                onClick={sendMessage}
                disabled={!userInput.trim() || isSending || conversationState === 'COMPLETE'}
                className="px-4 py-2 sm:px-6 sm:py-3 rounded-lg bg-violet-500 hover:bg-violet-600 active:bg-violet-700 text-white font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 touch-manipulation min-w-[44px] min-h-[44px] justify-center"
              >
                {isSending ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        {canGenerateReport() && (
          <div className="space-y-3">
            {!reportId ? (
              <>
                {/* Format Selection */}
                <div className="flex flex-col sm:flex-row gap-3 items-center">
                  <span className="text-sm text-white/60">Select format:</span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => generateReport('pdf')}
                      disabled={isGeneratingReport}
                      className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all disabled:opacity-50 text-sm touch-manipulation"
                    >
                      PDF
                    </button>
                    <button
                      onClick={() => generateReport('docx')}
                      disabled={isGeneratingReport}
                      className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all disabled:opacity-50 text-sm touch-manipulation"
                    >
                      DOCX
                    </button>
                    <button
                      onClick={() => generateReport('json')}
                      disabled={isGeneratingReport}
                      className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all disabled:opacity-50 text-sm touch-manipulation"
                    >
                      JSON
                    </button>
                  </div>
                </div>
                
                {/* Generate Button */}
                <button
                  onClick={() => generateReport('pdf')}
                  disabled={isGeneratingReport}
                  className="w-full px-6 py-4 rounded-lg bg-white text-black font-medium hover:bg-white/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 touch-manipulation"
                >
                  {isGeneratingReport ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Generating Report...
                    </>
                  ) : (
                    <>
                      <FileText className="w-5 h-5" />
                      Generate Full Report
                    </>
                  )}
                </button>
              </>
            ) : (
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={downloadReport}
                  className="flex-1 px-6 py-4 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white font-medium transition-all flex items-center justify-center gap-2 touch-manipulation"
                >
                  <Download className="w-5 h-5" />
                  Download {reportFormat.toUpperCase()} Report
                </button>
                <button
                  onClick={resetAnalysis}
                  className="flex-1 px-6 py-4 rounded-lg bg-white/5 hover:bg-white/10 font-medium transition-all touch-manipulation"
                >
                  Start New Analysis
                </button>
              </div>
            )}
          </div>
        )}

        {/* Report Issue Button */}
        <div className="flex justify-center">
          <button
            onClick={reportIssue}
            className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-sm font-medium transition-all flex items-center gap-2 touch-manipulation"
          >
            <AlertCircle className="w-4 h-4" />
            Report Issue
          </button>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl border border-white/5 bg-white/[0.02]">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
                <Target className="w-5 h-5 text-violet-400" />
              </div>
              <h3 className="font-semibold">Market Research</h3>
            </div>
            <p className="text-sm text-white/60">
              Comprehensive competitor analysis and market insights
            </p>
          </div>

          <div className="p-4 rounded-xl border border-white/5 bg-white/[0.02]">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-emerald-400" />
              </div>
              <h3 className="font-semibold">Financial Projections</h3>
            </div>
            <p className="text-sm text-white/60">
              Detailed revenue forecasts and ROI calculations
            </p>
          </div>

          <div className="p-4 rounded-xl border border-white/5 bg-white/[0.02]">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-blue-400" />
              </div>
              <h3 className="font-semibold">Growth Strategy</h3>
            </div>
            <p className="text-sm text-white/60">
              Actionable roadmap with milestones and KPIs
            </p>
          </div>
        </div>
      </div>
    </LinearLayout>
  );
}
