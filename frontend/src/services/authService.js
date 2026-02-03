import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL !== undefined ? process.env.REACT_APP_BACKEND_URL : 'http://localhost:8001';
const API_URL = `${BACKEND_URL}/api/auth`;

const register = async (email, password, fullName) => {
    const response = await axios.post(`${API_URL}/register`, {
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

    const response = await axios.post(`${API_URL}/token`, params, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    });

    if (response.data.access_token) {
        localStorage.setItem('user_token', response.data.access_token);
    }
    return response.data;
};

const logout = () => {
    localStorage.removeItem('user_token');
};

const getCurrentUser = async () => {
    const token = localStorage.getItem('user_token');
    if (!token) return null;

    try {
        const response = await axios.get(`${API_URL}/me`, {
            headers: { Authorization: `Bearer ${token}` }
        });
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
