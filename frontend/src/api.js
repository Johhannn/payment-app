import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/',
    headers: {
        'Content-Type': 'application/json',
    }
});

api.interceptors.request.use(async (config) => {
    const stored = localStorage.getItem('authTokens');
    let authTokens = null;
    if (stored) {
        try {
            authTokens = JSON.parse(stored);
        } catch (e) {
            console.error('Failed to parse authTokens', e);
        }
    }
    if (authTokens && authTokens.access) {
        config.headers.Authorization = `Bearer ${authTokens.access}`;
    }
    return config;
});

export default api;
