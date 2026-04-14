/**
 * Production-Grade Auth Interceptor with Silent Token Refresh
 * Ensures users NEVER get logged out during critical flows
 */

import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    
    failedQueue = [];
};

export const setupAuthInterceptor = (onLogout) => {
    // Request interceptor - Add token to all requests
    const requestInterceptor = axios.interceptors.request.use(
        (config) => {
            const token = localStorage.getItem('user_token');
            if (token && !config.headers.Authorization) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        },
        (error) => Promise.reject(error)
    );

    // Response interceptor - Handle 401 with token refresh
    const responseInterceptor = axios.interceptors.response.use(
        (response) => response,
        async (error) => {
            const originalRequest = error.config;

            // If error is not 401 or request already retried, reject
            if (error.response?.status !== 401 || originalRequest._retry) {
                return Promise.reject(error);
            }

            // Don't retry login/register endpoints
            if (originalRequest.url?.includes('/auth/token') || 
                originalRequest.url?.includes('/auth/register')) {
                return Promise.reject(error);
            }

            // If already refreshing, queue this request
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                })
                    .then(token => {
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        return axios(originalRequest);
                    })
                    .catch(err => Promise.reject(err));
            }

            originalRequest._retry = true;
            isRefreshing = true;

            // Try to refresh token
            const refreshToken = localStorage.getItem('refresh_token');
            
            if (!refreshToken) {
                console.error('❌ No refresh token found - logging out');
                isRefreshing = false;
                processQueue(new Error('No refresh token'), null);
                if (onLogout) onLogout();
                return Promise.reject(error);
            }

            try {
                console.log('🔄 Refreshing token...');
                
                // Call refresh endpoint
                const response = await axios.post(`${BACKEND_URL}/api/auth/refresh`, {
                    refresh_token: refreshToken
                }, {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                const { access_token } = response.data;
                
                console.log('✅ Token refreshed successfully');
                
                // Store new token
                localStorage.setItem('user_token', access_token);
                
                // Update axios default header
                axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
                
                // Update original request with new token
                originalRequest.headers.Authorization = `Bearer ${access_token}`;
                
                // Process queued requests
                processQueue(null, access_token);
                
                isRefreshing = false;
                
                console.log('🔄 Retrying original request...');
                
                // Retry original request
                return axios(originalRequest);
                
            } catch (refreshError) {
                console.error('❌ Token refresh failed:', refreshError);
                
                // Refresh failed - logout user
                processQueue(refreshError, null);
                isRefreshing = false;
                
                localStorage.removeItem('user_token');
                localStorage.removeItem('refresh_token');
                
                if (onLogout) onLogout();
                
                return Promise.reject(refreshError);
            }
        }
    );
    
    return () => {
        axios.interceptors.request.eject(requestInterceptor);
        axios.interceptors.response.eject(responseInterceptor);
    };
};
