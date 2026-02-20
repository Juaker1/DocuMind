/**
 * Base API client configuration using Axios
 * Handles all HTTP communication with the FastAPI backend
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL } from '@/lib/constants';
import type { ApiError } from '@/types/api';

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

/**
 * Request interceptor
 * Add authentication tokens, logging, etc.
 */
apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // Add timestamp for request tracking
        if (process.env.NODE_ENV === 'development') {
            console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        }

        // Inject identity headers on every request
        if (typeof window !== 'undefined') {
            const { getAuthToken, getOrCreateUUID } = require('@/lib/identity');
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

/**
 * Response interceptor
 * Handle errors globally, transform responses, etc.
 */
apiClient.interceptors.response.use(
    (response) => {
        if (process.env.NODE_ENV === 'development') {
            console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`);
        }
        return response;
    },
    (error: AxiosError<ApiError>) => {
        // Handle different error types
        if (error.response) {
            // Server responded with error status
            const apiError: ApiError = {
                detail: error.response.data?.detail || 'Error en el servidor',
                status: error.response.status,
            };

            console.error('❌ API Error:', apiError);

            // Handle specific status codes
            switch (error.response.status) {
                case 401:
                    // Unauthorized - redirect to login if needed
                    break;
                case 404:
                    // Not found
                    break;
                case 500:
                    // Server error
                    break;
            }

            return Promise.reject(apiError);
        } else if (error.request) {
            // Request made but no response
            const apiError: ApiError = {
                detail: 'No se pudo conectar con el servidor',
                status: 0,
            };
            console.error('❌ Network Error:', apiError);
            return Promise.reject(apiError);
        } else {
            // Something else happened
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
