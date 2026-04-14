import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '@/services/authService';
import { getAccessToken, initializeTokens } from '@/utils/apiClient';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const logout = () => {
        authService.logout();
        setUser(null);
    };

    useEffect(() => {
        // Check for logged-in user on mount
        const initAuth = async () => {
            try {
                // Initialize tokens from localStorage
                initializeTokens();
                
                // Check if we have a token
                const token = getAccessToken();
                
                if (!token) {
                    console.log('⚠️ No token found, user not logged in');
                    setUser(null);
                    setLoading(false);
                    return;
                }
                
                console.log('🔐 Token found, fetching user profile...');
                
                // Try to get current user (will auto-refresh if token expired)
                const currentUser = await authService.getCurrentUser();
                
                if (currentUser) {
                    console.log('✅ User authenticated:', currentUser.email);
                    setUser(currentUser);
                } else {
                    console.log('⚠️ Failed to get user, clearing auth state');
                    setUser(null);
                }
            } catch (error) {
                console.error('❌ Auth initialization failed:', error);
                setUser(null);
            } finally {
                setLoading(false);
            }
        };
        
        initAuth();
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

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
