/**
 * Growth OS API Client
 * Handles all API calls to the Growth Operating System backend
 */

const API_BASE_URL = 'http://localhost:8001/api';

class GrowthOSClient {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || error.message || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API Request Error:', error);
      throw error;
    }
  }

  // Growth Strategist APIs
  async getDailyActions(businessId) {
    return this.request(`/growth/daily-actions/${businessId}`);
  }

  async predictRevenue(data) {
    return this.request('/growth/predict-revenue', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Campaign Launcher APIs
  async launchCampaign(campaignData) {
    return this.request('/campaigns/launch', {
      method: 'POST',
      body: JSON.stringify(campaignData),
    });
  }

  async getCampaign(campaignId) {
    return this.request(`/campaigns/${campaignId}`);
  }

  async pauseCampaign(campaignId) {
    return this.request(`/campaigns/${campaignId}/pause`, {
      method: 'POST',
    });
  }

  async resumeCampaign(campaignId) {
    return this.request(`/campaigns/${campaignId}/resume`, {
      method: 'POST',
    });
  }

  // Autonomous Mode APIs
  async enableAutonomous(config) {
    return this.request('/autonomous/enable', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  async disableAutonomous(businessId) {
    return this.request('/autonomous/disable', {
      method: 'POST',
      body: JSON.stringify({ business_id: businessId }),
    });
  }

  async getAutonomousStatus(businessId) {
    return this.request(`/autonomous/status/${businessId}`);
  }

  // Competitor Intelligence APIs
  async addCompetitor(competitorData) {
    return this.request('/competitors/add', {
      method: 'POST',
      body: JSON.stringify(competitorData),
    });
  }

  async getCompetitors(businessId) {
    return this.request(`/competitors/${businessId}`);
  }

  async getCompetitorStrategies(competitorId) {
    return this.request(`/competitors/${competitorId}/strategies`);
  }

  // Content Generation APIs
  async generateViralContent(data) {
    return this.request('/content/viral', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async generateCampaignAssets(data) {
    return this.request('/content/campaign-assets', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Conversion Optimization APIs
  async analyzePage(data) {
    return this.request('/conversion/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async createABTest(data) {
    return this.request('/conversion/ab-test', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Funnel APIs
  async createFunnel(data) {
    return this.request('/funnels/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async addLeadToFunnel(funnelId, leadData) {
    return this.request(`/funnels/${funnelId}/leads`, {
      method: 'POST',
      body: JSON.stringify(leadData),
    });
  }

  async getFunnelAnalytics(funnelId) {
    return this.request(`/funnels/${funnelId}/analytics`);
  }

  // Business Analysis APIs
  async analyzeWebsite(data) {
    return this.request('/analyze/website', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async analyzeCompetitor(data) {
    return this.request('/analyze/competitor', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getAnalysisHistory(userId) {
    return this.request(`/analyze/history/${userId}`);
  }

  // Payment APIs
  async createRazorpayOrder(data) {
    return this.request('/payments/razorpay/create-order', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async verifyRazorpayPayment(data) {
    return this.request('/payments/razorpay/verify', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // User APIs
  async getCurrentUser() {
    return this.request('/auth/me');
  }

  async updateUserProfile(data) {
    return this.request('/users/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Business Analysis APIs
  async startBusinessAnalysis() {
    return this.request('/ai/business-analysis/start', {
      method: 'POST',
    });
  }

  async sendBusinessAnalysisMessage(sessionId, message) {
    return this.request('/ai/business-analysis/chat', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
      }),
    });
  }

  async generateAnalysisReport(sessionId, format = 'pdf') {
    return this.request('/ai/business-analysis/generate-report', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        format: format,
      }),
    });
  }

  async getBusinessAnalysisSessions(limit = 10) {
    return this.request(`/ai/business-analysis/sessions?limit=${limit}`);
  }

  async downloadReport(reportId) {
    const headers = {
      ...this.token && { 'Authorization': `Bearer ${this.token}` },
    };

    const response = await fetch(`${API_BASE_URL}/ai/business-analysis/download/${reportId}`, {
      headers,
    });

    if (!response.ok) {
      throw new Error('Failed to download report');
    }

    return response.blob();
  }

  async resumeBusinessAnalysisSession(sessionId) {
    return this.request(`/ai/business-analysis/sessions/${sessionId}/resume`, {
      method: 'PUT',
    });
  }

  async deleteBusinessAnalysisSession(sessionId) {
    return this.request(`/ai/business-analysis/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async getAnalysisStatus(sessionId) {
    return this.request(`/ai/business-analysis/sessions/${sessionId}/status`);
  }
}

export default new GrowthOSClient();
