/**
 * PRODUCTION-GRADE API CLIENT (STRIPE-LEVEL)
 * Centralized axios instance with automatic token refresh
 * Ensures retry requests ALWAYS use the NEW token
 */

import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// In-memory token storage (CRITICAL - not just localStorage)
let accessToken = null;
let refreshToken = null;

// Token refresh state
let isRefreshing = false;
let refreshSubscribers = [];
let hasLoggedOut = false; // Prevent infinite logout loops

/**
 * Initialize tokens from localStorage
 */
export const initializeTokens = () => {
    accessToken = localStorage.getItem('user_token');
    refreshToken = localStorage.getItem('refresh_token');
    
    // Reset logout flag if we have tokens
    if (accessToken || refreshToken) {
        hasLoggedOut = false;
    }
    
    console.log('🔐 Tokens initialized:', { 
        hasAccessToken: !!accessToken, 
        hasRefreshToken: !!refreshToken 
    });
};

/**
 * Update tokens (called after login/refresh)
 */
export const setTokens = (newAccessToken, newRefreshToken) => {
    accessToken = newAccessToken;
    if (newRefreshToken) {
        refreshToken = newRefreshToken;
    }
    
    // Also update localStorage
    if (newAccessToken) {
        localStorage.setItem('user_token', newAccessToken);
    }
    if (newRefreshToken) {
        localStorage.setItem('refresh_token', newRefreshToken);
    }
    
    hasLoggedOut = false; // Reset logout flag when tokens are set
    isRefreshing = false; // Reset refreshing state
    console.log('✅ Tokens updated in memory and localStorage');
};

/**
 * Clear tokens (called on logout)
 */
export const clearTokens = () => {
    accessToken = null;
    refreshToken = null;
    localStorage.removeItem('user_token');
    localStorage.removeItem('refresh_token');
    hasLoggedOut = true; // Set logout flag
    console.log('🗑️ Tokens cleared');
};

/**
 * Get current access token
 */
export const getAccessToken = () => accessToken;

/**
 * Subscribe to token refresh
 */
const subscribeTokenRefresh = (callback) => {
    refreshSubscribers.push(callback);
};

/**
 * Notify all subscribers with new token
 */
const onTokenRefreshed = (newToken) => {
    refreshSubscribers.forEach(callback => callback(newToken));
    refreshSubscribers = [];
};

/**
 * Refresh access token
 */
const refreshAccessToken = async () => {
    try {
        console.log('🔄 Refreshing access token...');
        
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await axios.post(
            `${BACKEND_URL}/api/auth/refresh`,
            { refresh_token: refreshToken },
            {
                headers: { 'Content-Type': 'application/json' }
            }
        );

        const { access_token } = response.data;
        
        if (!access_token) {
            throw new Error('No access token in refresh response');
        }

        // Update in-memory token (CRITICAL)
        setTokens(access_token, null);
        
        console.log('✅ Token refreshed successfully');
        
        return access_token;
        
    } catch (error) {
        console.error('❌ Token refresh failed:', error);
        clearTokens();
        throw error;
    }
};

/**
 * Create axios instance with interceptors
 */
const apiClient = axios.create({
    baseURL: BACKEND_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

/**
 * REQUEST INTERCEPTOR - Attach latest token
 */
apiClient.interceptors.request.use(
    (config) => {
        // ALWAYS use in-memory token (not localStorage)
        const token = getAccessToken();
        
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

/**
 * RESPONSE INTERCEPTOR - Handle 401 with token refresh
 */
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        // If not 401 or already retried, reject
        if (error.response?.status !== 401 || originalRequest._retry) {
            return Promise.reject(error);
        }

        // Don't retry auth endpoints (including /auth/me which is just a check)
        if (originalRequest.url?.includes('/auth/token') || 
            originalRequest.url?.includes('/auth/register') ||
            originalRequest.url?.includes('/auth/refresh') ||
            originalRequest.url?.includes('/auth/me')) {
            return Promise.reject(error);
        }

        // If already logged out, don't try to refresh
        if (hasLoggedOut) {
            console.log('⚠️ Already logged out, skipping refresh');
            return Promise.reject(error);
        }

        // Mark as retried
        originalRequest._retry = true;

        // If already refreshing, wait for it
        if (isRefreshing) {
            console.log('⏳ Token refresh in progress, queuing request...');
            return new Promise((resolve, reject) => {
                subscribeTokenRefresh((newToken) => {
                    if (newToken) {
                        originalRequest.headers.Authorization = `Bearer ${newToken}`;
                        resolve(apiClient(originalRequest));
                    } else {
                        reject(error);
                    }
                });
            });
        }

        isRefreshing = true;

        try {
            // Refresh token
            const newToken = await refreshAccessToken();
            
            // Update original request with NEW token (CRITICAL)
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            
            console.log('🔄 Retrying original request with new token');
            
            // Notify subscribers
            onTokenRefreshed(newToken);
            
            isRefreshing = false;
            
            // Retry original request
            return apiClient(originalRequest);
            
        } catch (refreshError) {
            console.error('❌ Token refresh failed, logging out');
            isRefreshing = false;
            onTokenRefreshed(null); // Notify subscribers of failure
            clearTokens();
            
            // Only redirect if not already on login page
            if (!window.location.pathname.includes('/login')) {
                console.log('🔄 Redirecting to login...');
                window.location.href = '/login';
            }
            
            return Promise.reject(refreshError);
        }
    }
);

// Initialize tokens on module load
initializeTokens();

export default apiClient;
