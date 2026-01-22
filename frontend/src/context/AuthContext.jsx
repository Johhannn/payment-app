import React, { createContext, useState, useEffect } from 'react';
import { jwtDecode } from "jwt-decode";
import api from '../api';

const AuthContext = createContext();

export default AuthContext;

export const AuthProvider = ({ children }) => {
    let [authTokens, setAuthTokens] = useState(() => localStorage.getItem('authTokens') ? JSON.parse(localStorage.getItem('authTokens')) : null);
    let [user, setUser] = useState(() => {
        const stored = localStorage.getItem('authTokens');
        let tokens = null;
        if (stored) {
            try {
                tokens = JSON.parse(stored);
            } catch (e) {
                console.error('Failed to parse authTokens', e);
            }
        }
        return tokens && tokens.access ? jwtDecode(tokens.access) : null;
    });
    let [loading, setLoading] = useState(true);

    const loginUser = async (email, password) => {
        try {
            const response = await api.post('token/', { email, password });
            if (response.status === 200) {
                setAuthTokens(response.data);
                setUser(jwtDecode(response.data.access));
                localStorage.setItem('authTokens', JSON.stringify(response.data));
                return true;
            }
        } catch (error) {
            console.error("Login failed", error);
            return false;
        }
    };

    const registerUser = async (email, password, full_name, phone_number) => {
        try {
            const response = await api.post('register/', {
                email,
                password,
                full_name: full_name,
                phone_number: phone_number
            });
            if (response.status === 201) {
                return true;
            }
        } catch (error) {
            console.error("Registration failed", error);
            return false;
        }
    };

    const logoutUser = () => {
        setAuthTokens(null);
        setUser(null);
        localStorage.removeItem('authTokens');
    };
    let intervalId;

    // Refresh token helper
    const refreshToken = async () => {
        if (!authTokens) return null;
        try {
            const response = await api.post('token/refresh/', {
                refresh: authTokens.refresh,
            });
            if (response.status === 200) {
                setAuthTokens(response.data);
                setUser(jwtDecode(response.data.access));
                localStorage.setItem('authTokens', JSON.stringify(response.data));
                return response.data;
            } else {
                logoutUser();
                return null;
            }
        } catch (error) {
            console.error('Token Refresh Failed', error);
            logoutUser();
            return null;
        }
    };

    const updateToken = async () => {
        if (!authTokens) {
            setLoading(false);
            return;
        }
        try {
            const response = await api.post('token/refresh/', {
                refresh: authTokens.refresh
            });
            if (response.status === 200) {
                setAuthTokens(response.data);
                setUser(jwtDecode(response.data.access));
                localStorage.setItem('authTokens', JSON.stringify(response.data));
            } else {
                logoutUser();
            }
        } catch (error) {
            console.error("Token Refresh Failed", error);
            logoutUser();
        }
        if (loading) {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (loading) {
            updateToken();
        }
        // Clear any existing interval before setting a new one
        if (intervalId) {
            clearInterval(intervalId);
        }
        intervalId = setInterval(() => {
            if (authTokens) {
                updateToken();
            }
        }, 1000 * 60 * 4);
        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }, [authTokens, loading]);

    const contextData = {
        user: user,
        authTokens: authTokens,
        loginUser: loginUser,
        registerUser: registerUser,
        logoutUser: logoutUser,
        refreshToken: refreshToken,
    };

    return (
        <AuthContext.Provider value={contextData}>
            {loading ? null : children}
        </AuthContext.Provider>
    );
};
