/**
 * Base API client configuration using Axios
 * Handles all HTTP communication with the FastAPI backend
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL } from '@/lib/constants';
import type { ApiError } from '@/types/api';
import {
    getAuthToken, setAuthToken,
    getRefreshToken, setRefreshToken,
    clearAllTokens,
    getOrCreateUUID,
} from '@/lib/identity';

/**
 * Create Axios instance with default configuration
 */
export const apiClient: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 seconds
});

// ---------------------------------------------------------------------------
// Refresh token rotation state
// Prevents multiple concurrent requests from all trying to refresh at once.
// ---------------------------------------------------------------------------
let _isRefreshing = false;
type QueueEntry = { resolve: (token: string) => void; reject: (err: unknown) => void };
let _failedQueue: QueueEntry[] = [];

function _processQueue(error: unknown, token: string | null = null) {
    _failedQueue.forEach(({ resolve, reject }) => {
        if (error) reject(error);
        else resolve(token!);
    });
    _failedQueue = [];
}

// ---------------------------------------------------------------------------
// Request interceptor — inject auth headers
// ---------------------------------------------------------------------------
apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        if (process.env.NODE_ENV === 'development') {
            console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        }

        if (typeof window !== 'undefined') {
            const token = getAuthToken();
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            } else {
                const uuid = getOrCreateUUID();
                config.headers['X-User-UUID'] = uuid;
            }
        }

        return config;
    },
    (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
    }
);

// ---------------------------------------------------------------------------
// Response interceptor — handle 401 with auto-refresh, then normalize errors
// ---------------------------------------------------------------------------
apiClient.interceptors.response.use(
    (response) => {
        if (process.env.NODE_ENV === 'development') {
            console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`);
        }
        return response;
    },
    async (error: AxiosError<ApiError>) => {
        const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

        // ── Auto-refresh on 401 ──────────────────────────────────────────────
        // Skip refresh for auth endpoints themselves (avoid infinite loops)
        const isAuthEndpoint = originalRequest?.url?.includes('/api/auth/');
        if (
            error.response?.status === 401 &&
            originalRequest &&
            !originalRequest._retry &&
            !isAuthEndpoint
        ) {
            if (_isRefreshing) {
                // Another request is already refreshing — queue this one
                return new Promise<string>((resolve, reject) => {
                    _failedQueue.push({ resolve, reject });
                })
                    .then((newToken) => {
                        originalRequest.headers.Authorization = `Bearer ${newToken}`;
                        return apiClient(originalRequest);
                    })
                    .catch((err) => Promise.reject(err));
            }

            originalRequest._retry = true;
            _isRefreshing = true;

            const refreshToken = getRefreshToken();
            if (!refreshToken) {
                // No refresh token — user must log in again
                clearAllTokens();
                _isRefreshing = false;
            } else {
                try {
                    const res = await apiClient.post<{
                        access_token: string;
                        refresh_token: string;
                    }>('/api/auth/refresh', { refresh_token: refreshToken });

                    const { access_token, refresh_token: newRefreshToken } = res.data;
                    setAuthToken(access_token);
                    setRefreshToken(newRefreshToken);

                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    _processQueue(null, access_token);
                    return apiClient(originalRequest);
                } catch (refreshError) {
                    _processQueue(refreshError, null);
                    clearAllTokens();
                    return Promise.reject(refreshError);
                } finally {
                    _isRefreshing = false;
                }
            }
        }

        // ── Normalize to ApiError ────────────────────────────────────────────
        if (error.response) {
            const apiError: ApiError = {
                detail: error.response.data?.detail || 'Error en el servidor',
                status: error.response.status,
            };
            console.error('❌ API Error:', apiError);
            return Promise.reject(apiError);
        } else if (error.request) {
            const apiError: ApiError = {
                detail: 'No se pudo conectar con el servidor',
                status: 0,
            };
            console.error('❌ Network Error:', apiError);
            return Promise.reject(apiError);
        } else {
            const apiError: ApiError = {
                detail: error.message || 'Error desconocido',
            };
            console.error('❌ Unknown Error:', apiError);
            return Promise.reject(apiError);
        }
    }
);

/**
 * Health check endpoint
 */
export async function checkHealth() {
    const response = await apiClient.get('/health');
    return response.data;
}

