'use client';

import { useState } from 'react';
import { useAuth } from '@/features/auth/AuthProvider';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

type Tab = 'login' | 'register';

interface AuthModalProps {
    isOpen: boolean;
    onClose: () => void;
    defaultTab?: Tab;
}

export function AuthModal({ isOpen, onClose, defaultTab = 'register' }: AuthModalProps) {
    const { login, register } = useAuth();
    const [tab, setTab] = useState<Tab>(defaultTab);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState<string | null>(null);

    const reset = () => {
        setEmail(''); setPassword(''); setConfirm('');
        setError(null); setSuccess(null); setLoading(false);
    };

    const switchTab = (t: Tab) => { setTab(t); reset(); };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        if (tab === 'register' && password !== confirm) {
            setError('Las contraseñas no coinciden');
            return;
        }
        if (password.length < 8) {
            setError('La contraseña debe tener al menos 8 caracteres');
            return;
        }

        setLoading(true);
        try {
            if (tab === 'login') {
                await login(email, password);
                setSuccess('¡Sesión iniciada!');
            } else {
                await register(email, password);
                setSuccess('¡Cuenta creada! Tus documentos fueron preservados. ✅');
            }
            setTimeout(() => { reset(); onClose(); }, 1200);
        } catch (err: unknown) {
            const msg = (err as { detail?: string })?.detail
                || (err as { message?: string })?.message
                || 'Ocurrió un error. Intenta de nuevo.';
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={tab === 'login' ? 'Iniciar sesión' : 'Crear cuenta'} size="sm">
            {/* Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
                {(['register', 'login'] as Tab[]).map((t) => (
                    <button
                        key={t}
                        onClick={() => switchTab(t)}
                        className={`flex-1 py-2 text-sm font-medium transition-colors ${tab === t
                                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                            }`}
                    >
                        {t === 'register' ? 'Crear cuenta' : 'Iniciar sesión'}
                    </button>
                ))}
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                    label="Email"
                    type="email"
                    id="auth-email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="tu@email.com"
                    required
                    autoComplete="email"
                />
                <Input
                    label="Contraseña"
                    type="password"
                    id="auth-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Mínimo 8 caracteres"
                    required
                    autoComplete={tab === 'login' ? 'current-password' : 'new-password'}
                />
                {tab === 'register' && (
                    <Input
                        label="Confirmar contraseña"
                        type="password"
                        id="auth-confirm"
                        value={confirm}
                        onChange={(e) => setConfirm(e.target.value)}
                        placeholder="Repite la contraseña"
                        required
                        autoComplete="new-password"
                    />
                )}

                {error && (
                    <p className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg px-3 py-2">
                        {error}
                    </p>
                )}
                {success && (
                    <p className="text-sm text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg px-3 py-2">
                        {success}
                    </p>
                )}

                <Button type="submit" variant="primary" className="w-full" isLoading={loading} disabled={loading}>
                    {tab === 'login' ? 'Iniciar sesión' : 'Crear cuenta'}
                </Button>
            </form>

            {tab === 'register' && (
                <p className="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center">
                    💡 Al registrarte, tus documentos subidos como invitado se preservan automáticamente.
                </p>
            )}
        </Modal>
    );
}
