/**
 * Header component — logo + dark mode toggle + auth button/user menu.
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { APP_NAME, ROUTES } from '@/lib/constants';
import { useTheme } from './ThemeProvider';
import { useAuth } from '@/features/auth/AuthProvider';
import { AuthModal } from '@/features/auth/components/AuthModal';

export function Header() {
    const { theme, toggleTheme } = useTheme();
    const { user, isAnonymous, logout, deleteAccount } = useAuth();
    const [authOpen, setAuthOpen] = useState(false);
    const [userMenuOpen, setUserMenuOpen] = useState(false);
    const [defaultTab, setDefaultTab] = useState<'login' | 'register'>('register');

    const openRegister = () => { setDefaultTab('register'); setAuthOpen(true); };
    const openLogin = () => { setDefaultTab('login'); setAuthOpen(true); };

    const handleDeleteAccount = async () => {
        if (!confirm('¿Eliminar tu cuenta y todos tus documentos? Esta acción no se puede deshacer.')) return;
        await deleteAccount();
        setUserMenuOpen(false);
    };

    return (
        <>
            <header className="sticky top-0 z-40 w-full border-b border-gray-200 bg-white/80 dark:border-gray-700 dark:bg-gray-900/80 backdrop-blur-sm">
                <div className="container mx-auto flex h-16 items-center justify-between px-4">
                    {/* Logo */}
                    <Link href={ROUTES.HOME} className="flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
                            <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                />
                            </svg>
                        </div>
                        <span className="text-xl font-bold text-gray-900 dark:text-white">{APP_NAME}</span>
                    </Link>

                    {/* Right side controls */}
                    <div className="flex items-center gap-2">
                        {/* Dark mode toggle */}
                        <button
                            onClick={toggleTheme}
                            aria-label={theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
                            className="flex items-center gap-2 rounded-lg border border-gray-200 dark:border-gray-700 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                        >
                            {theme === 'dark' ? (
                                <>
                                    <svg className="h-4 w-4 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
                                    </svg>
                                    Modo claro
                                </>
                            ) : (
                                <>
                                    <svg className="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                                    </svg>
                                    Modo oscuro
                                </>
                            )}
                        </button>

                        {/* Auth section */}
                        {isAnonymous ? (
                            <div className="flex items-center gap-1.5">
                                <button
                                    onClick={openLogin}
                                    className="text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                                >
                                    Iniciar sesión
                                </button>
                                <button
                                    onClick={openRegister}
                                    className="text-sm bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg transition-colors font-medium"
                                >
                                    Crear cuenta
                                </button>
                            </div>
                        ) : (
                            <div className="relative">
                                <button
                                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                                    className="flex items-center gap-2 rounded-lg border border-gray-200 dark:border-gray-700 px-3 py-1.5 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                                >
                                    {/* Avatar initial */}
                                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-white text-xs font-bold">
                                        {user?.email?.[0]?.toUpperCase() ?? '?'}
                                    </span>
                                    <span className="max-w-[120px] truncate">{user?.email}</span>
                                    <svg className="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                </button>

                                {/* Dropdown */}
                                {userMenuOpen && (
                                    <>
                                        {/* Backdrop */}
                                        <div className="fixed inset-0 z-10" onClick={() => setUserMenuOpen(false)} />
                                        <div className="absolute right-0 top-full mt-1 z-20 w-48 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg py-1">
                                            <div className="px-3 py-2 border-b border-gray-100 dark:border-gray-700">
                                                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.email}</p>
                                            </div>
                                            <button
                                                onClick={() => { setUserMenuOpen(false); logout(); }}
                                                className="w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                                            >
                                                Cerrar sesión
                                            </button>
                                            <button
                                                onClick={handleDeleteAccount}
                                                className="w-full text-left px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                                            >
                                                Eliminar cuenta
                                            </button>
                                        </div>
                                    </>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </header>

            <AuthModal isOpen={authOpen} onClose={() => setAuthOpen(false)} defaultTab={defaultTab} />
        </>
    );
}
