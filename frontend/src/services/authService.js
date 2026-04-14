import apiClient, { setTokens, clearTokens } from '@/utils/apiClient';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API_URL = `${BACKEND_URL}/api/auth`;

const register = async (email, password, fullName) => {
    const response = await apiClient.post('/api/auth/register', {
        email,
        password,
        full_name: fullName,
    });
    return response.data;
};

const login = async (email, password) => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);

    const response = await apiClient.post('/api/auth/token', params, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    });

    if (response.data.access_token) {
        // Update tokens in centralized API client (CRITICAL)
        setTokens(response.data.access_token, response.data.refresh_token);
    }
    
    return response.data;
};

const logout = () => {
    // Clear tokens from centralized API client
    clearTokens();
};

const getCurrentUser = async () => {
    try {
        const response = await apiClient.get('/api/auth/me');
        return response.data;
    } catch (error) {
        return null;
    }
};

const getToken = () => {
    return localStorage.getItem('user_token');
};

export const authService = {
    register,
    login,
    logout,
    getCurrentUser,
    getToken
};
