/*
Analysis History Page - View past business analyses
Displays list of user's analysis sessions with search, filter, and download capabilities
*/

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import LinearLayout from '../components/LinearLayout';
import { 
  FileText, Download, Trash2, Clock, DollarSign, 
  Search, Filter, ChevronRight, Loader2, AlertCircle,
  Calendar, TrendingUp, RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import growthOSClient from '../lib/growthOSClient';

export default function AnalysisHistoryPage() {
  const navigate = useNavigate();
  
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all'); // 'all', 'completed', 'in_progress'
  const [isDeleting, setIsDeleting] = useState(null);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setIsLoading(true);
      const response = await growthOSClient.getBusinessAnalysisSessions(50);
      setSessions(response.sessions || []);
    } catch (error) {
      console.error('Error loading sessions:', error);
      toast.error('Failed to load analysis history');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadReport = async (reportId, sessionId) => {
    try {
      toast.loading('Downloading report...');
      const blob = await growthOSClient.downloadReport(reportId);
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `business_analysis_${sessionId.substring(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Report downloaded successfully!');
    } catch (error) {
      console.error('Error downloading report:', error);
      toast.error('Failed to download report');
    }
  };

  const handleResumeSession = async (sessionId) => {
    try {
      await growthOSClient.resumeBusinessAnalysisSession(sessionId);
      navigate('/business-analysis', { state: { sessionId } });
      toast.success('Session resumed');
    } catch (error) {
      console.error('Error resuming session:', error);
      toast.error('Failed to resume session');
    }
  };

  const handleDeleteSession = async (sessionId) => {
    if (!window.confirm('Are you sure you want to delete this analysis? This action cannot be undone.')) {
      return;
    }

    try {
      setIsDeleting(sessionId);
      await growthOSClient.deleteBusinessAnalysisSession(sessionId);
      setSessions(sessions.filter(s => s.session_id !== sessionId));
      toast.success('Analysis deleted');
    } catch (error) {
      console.error('Error deleting session:', error);
      toast.error('Failed to delete analysis');
    } finally {
      setIsDeleting(null);
    }
  };

  const filteredSessions = sessions.filter(session => {
    // Filter by status
    if (filterStatus !== 'all') {
      const isCompleted = session.state === 'COMPLETE' || session.state === 'ANALYSIS_COMPLETE';
      if (filterStatus === 'completed' && !isCompleted) return false;
      if (filterStatus === 'in_progress' && isCompleted) return false;
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const businessIdea = session.business_idea_summary?.toLowerCase() || '';
      const budget = session.budget_summary?.toLowerCase() || '';
      return businessIdea.includes(query) || budget.includes(query);
    }

    return true;
  });

  const getStateLabel = (state) => {
    const labels = {
      'GREETING': 'Started',
      'BUSINESS_IDEA_COLLECTION': 'Collecting Info',
      'BUSINESS_IDEA_CONFIRMATION': 'Confirming Details',
      'BUDGET_COLLECTION': 'Budget Planning',
      'BUDGET_CONFIRMATION': 'Finalizing Budget',
      'ANALYSIS_IN_PROGRESS': 'Analyzing',
      'ANALYSIS_COMPLETE': 'Complete',
      'REPORT_GENERATION': 'Generating Report',
      'COMPLETE': 'Complete'
    };
    return labels[state] || state;
  };

  const getStateColor = (state) => {
    const isComplete = state === 'COMPLETE' || state === 'ANALYSIS_COMPLETE';
    return isComplete ? 'text-emerald-400' : 'text-yellow-400';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const actions = (
    <div className="flex items-center gap-3">
      <button
        onClick={loadSessions}
        className="px-4 py-2 rounded-lg text-sm font-medium text-white/80 hover:text-white hover:bg-white/5 transition-all flex items-center gap-2"
      >
        <RefreshCw className="w-4 h-4" />
        Refresh
      </button>
      <button
        onClick={() => navigate('/business-analysis')}
        className="px-4 py-2 rounded-lg text-sm font-medium bg-violet-500 hover:bg-violet-600 transition-all"
      >
        New Analysis
      </button>
    </div>
  );

  return (
    <LinearLayout 
      title="Analysis History" 
      subtitle="View and manage your past business analyses"
      actions={actions}
    >
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Search and Filter */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search analyses..."
              className="w-full pl-10 pr-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-white/60" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all"
            >
              <option value="all">All Analyses</option>
              <option value="completed">Completed</option>
              <option value="in_progress">In Progress</option>
            </select>
          </div>
        </div>

        {/* Sessions List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-violet-500" />
              <p className="text-white/60">Loading your analyses...</p>
            </div>
          </div>
        ) : filteredSessions.length === 0 ? (
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 mx-auto mb-4 text-white/40" />
            <h3 className="text-lg font-semibold mb-2">No analyses found</h3>
            <p className="text-white/60 mb-6">
              {searchQuery || filterStatus !== 'all' 
                ? 'Try adjusting your search or filter'
                : 'Start your first business analysis to see it here'}
            </p>
            <button
              onClick={() => navigate('/business-analysis')}
              className="px-6 py-3 rounded-lg bg-violet-500 hover:bg-violet-600 font-medium transition-all"
            >
              Start New Analysis
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredSessions.map((session) => (
              <div
                key={session.session_id}
                className="p-6 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <FileText className="w-5 h-5 text-violet-400 flex-shrink-0" />
                      <h3 className="font-semibold truncate">
                        {session.business_idea_summary || 'Business Analysis'}
                      </h3>
                      <span className={`text-sm ${getStateColor(session.state)}`}>
                        {getStateLabel(session.state)}
                      </span>
                    </div>
                    
                    <div className="flex flex-wrap items-center gap-4 text-sm text-white/60">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        {formatDate(session.created_at)}
                      </div>
                      {session.budget_summary && (
                        <div className="flex items-center gap-2">
                          <DollarSign className="w-4 h-4" />
                          {session.budget_summary}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {(session.state === 'COMPLETE' || session.state === 'ANALYSIS_COMPLETE') && (
                      <button
                        onClick={() => handleDownloadReport(session.report_id || session.session_id, session.session_id)}
                        className="p-2 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition-all"
                        title="Download Report"
                      >
                        <Download className="w-5 h-5" />
                      </button>
                    )}
                    
                    {session.state !== 'COMPLETE' && (
                      <button
                        onClick={() => handleResumeSession(session.session_id)}
                        className="p-2 rounded-lg bg-violet-500/10 hover:bg-violet-500/20 text-violet-400 transition-all"
                        title="Resume Analysis"
                      >
                        <ChevronRight className="w-5 h-5" />
                      </button>
                    )}
                    
                    <button
                      onClick={() => handleDeleteSession(session.session_id)}
                      disabled={isDeleting === session.session_id}
                      className="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-all disabled:opacity-50"
                      title="Delete Analysis"
                    >
                      {isDeleting === session.session_id ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <Trash2 className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Stats */}
        {!isLoading && sessions.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl border border-white/5 bg-white/[0.02]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-violet-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{sessions.length}</p>
                  <p className="text-sm text-white/60">Total Analyses</p>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-xl border border-white/5 bg-white/[0.02]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {sessions.filter(s => s.state === 'COMPLETE' || s.state === 'ANALYSIS_COMPLETE').length}
                  </p>
                  <p className="text-sm text-white/60">Completed</p>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-xl border border-white/5 bg-white/[0.02]">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-yellow-500/10 flex items-center justify-center">
                  <Clock className="w-5 h-5 text-yellow-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {sessions.filter(s => s.state !== 'COMPLETE' && s.state !== 'ANALYSIS_COMPLETE').length}
                  </p>
                  <p className="text-sm text-white/60">In Progress</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </LinearLayout>
  );
}
