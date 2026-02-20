'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { apiClient } from '@/services/api';
import {
    getOrCreateUUID,
    getAuthToken,
    setAuthToken,
    clearAuthToken,
} from '@/lib/identity';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface AuthUser {
    id: number;
    uuid: string;
    email: string | null;
    is_anonymous: boolean;
}

interface AuthContextValue {
    user: AuthUser | null;
    isAnonymous: boolean;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string) => Promise<void>;
    logout: () => void;
    deleteAccount: () => Promise<void>;
    refreshUser: () => Promise<void>;
}

// ─── Context ──────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
    return ctx;
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Ensure the anonymous UUID exists and fetch current user on mount
    const refreshUser = useCallback(async () => {
        getOrCreateUUID(); // Ensure UUID exists
        const token = getAuthToken();
        if (token) {
            try {
                const res = await apiClient.get<AuthUser>('/api/auth/me');
                setUser(res.data);
            } catch {
                // Token expired or invalid — clear it, go anonymous
                clearAuthToken();
                setUser(null);
            }
        } else {
            setUser(null);
        }
    }, []);

    useEffect(() => {
        refreshUser().finally(() => setIsLoading(false));
    }, [refreshUser]);

    // ── Login ────────────────────────────────────────────────────────────────
    const login = useCallback(async (email: string, password: string) => {
        const res = await apiClient.post<{ token: string; user: AuthUser }>('/api/auth/login', {
            email,
            password,
        });
        setAuthToken(res.data.token);
        setUser(res.data.user);
    }, []);

    // ── Register (anonymous → registered, docs preserved) ────────────────────
    const register = useCallback(async (email: string, password: string) => {
        const uuid = getOrCreateUUID();
        const res = await apiClient.post<{ token: string; user: AuthUser }>('/api/auth/register', {
            email,
            password,
            uuid,
        });
        setAuthToken(res.data.token);
        setUser(res.data.user);
    }, []);

    // ── Logout ───────────────────────────────────────────────────────────────
    const logout = useCallback(() => {
        clearAuthToken();
        setUser(null);
        // Keep UUID so the browser retains anonymous session state
    }, []);

    // ── Delete account ───────────────────────────────────────────────────────
    const deleteAccount = useCallback(async () => {
        await apiClient.delete('/api/auth/account');
        clearAuthToken();
        setUser(null);
    }, []);

    const isAnonymous = user === null || user.is_anonymous;

    return (
        <AuthContext.Provider
            value={{ user, isAnonymous, isLoading, login, register, logout, deleteAccount, refreshUser }}
        >
            {children}
        </AuthContext.Provider>
    );
}
