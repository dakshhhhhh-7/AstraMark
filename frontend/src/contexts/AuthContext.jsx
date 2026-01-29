import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '@/services/authService';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for logged-in user on mount
        const initAuth = async () => {
            const user = await authService.getCurrentUser();
            setUser(user);
            setLoading(false);
        };
        initAuth();
    }, []);

    // Axios interceptor for adding token
    useEffect(() => {
        const requestInterceptor = axios.interceptors.request.use(
            (config) => {
                const token = authService.getToken();
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        const responseInterceptor = axios.interceptors.response.use(
            (response) => response,
            (error) => {
                // If 401 Unauthorized, logout user
                if (error.response && error.response.status === 401) {
                    if (!error.config.url.includes('/auth/token')) { // Don't logout on failed login
                        logout();
                    }
                }
                return Promise.reject(error);
            }
        );

        return () => {
            axios.interceptors.request.eject(requestInterceptor);
            axios.interceptors.response.eject(responseInterceptor);
        };
    }, []);

    const login = async (email, password) => {
        const data = await authService.login(email, password);
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
        return data;
    };

    const register = async (email, password, fullName) => {
        return await authService.register(email, password, fullName);
    };

    const logout = () => {
        authService.logout();
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
