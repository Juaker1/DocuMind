/**
 * ChatInterface component
 * Main chat interface with one persistent conversation per document.
 */

'use client';

import { useEffect, useState } from 'react';
import { Card, Spinner } from '@/components/ui';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { useChat } from '../hooks';
import type { DocumentDetail } from '@/types/document';

interface ChatInterfaceProps {
    document: DocumentDetail;
}

export function ChatInterface({ document }: ChatInterfaceProps) {
    const [showResetConfirm, setShowResetConfirm] = useState(false);
    const {
        messages,
        isHistoryLoading,
        isResetting,
        error,
        streaming,
        sendMessage,
        finalizeStreamingMessage,
        resetConversation,
    } = useChat(document.id);

    // Finalize streaming message when stream ends
    useEffect(() => {
        if (!streaming.isStreaming && streaming.streamingText) {
            finalizeStreamingMessage();
        }
    }, [streaming.isStreaming, streaming.streamingText, finalizeStreamingMessage]);

    const handleReset = async () => {
        setShowResetConfirm(false);
        await resetConversation();
    };

    return (
        <div className="flex flex-col h-[calc(100vh-12rem)]">
            {/* Document Header */}
            <Card variant="default" padding="md" className="mb-4">
                <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-blue-100 dark:bg-blue-900/30 p-3">
                        <svg className="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                            />
                        </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                            {document.filename}
                        </h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            {document.total_pages} páginas
                            {messages.length > 0 && (
                                <span className="ml-2 text-blue-600 dark:text-blue-400">
                                    • {messages.length} mensaje{messages.length !== 1 ? 's' : ''}
                                </span>
                            )}
                        </p>
                    </div>

                    {/* Reset chat button */}
                    {messages.length > 0 && !showResetConfirm && (
                        <button
                            onClick={() => setShowResetConfirm(true)}
                            disabled={isResetting}
                            className="flex items-center gap-1.5 rounded-lg border border-gray-200 dark:border-gray-600 px-3 py-1.5 text-sm text-gray-500 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:border-red-200 dark:hover:border-red-700 hover:text-red-600 dark:hover:text-red-400 transition-colors disabled:opacity-50"
                            title="Borrar historial del chat"
                        >
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                            {isResetting ? 'Borrando...' : 'Borrar chat'}
                        </button>
                    )}

                    {/* Confirm reset */}
                    {showResetConfirm && (
                        <div className="flex items-center gap-2 text-sm">
                            <span className="text-gray-600 dark:text-gray-300">¿Borrar historial?</span>
                            <button
                                onClick={handleReset}
                                className="rounded px-2.5 py-1 bg-red-600 text-white hover:bg-red-700 transition-colors font-medium"
                            >
                                Sí, borrar
                            </button>
                            <button
                                onClick={() => setShowResetConfirm(false)}
                                className="rounded px-2.5 py-1 border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                            >
                                Cancelar
                            </button>
                        </div>
                    )}
                </div>
            </Card>

            {/* Error Display */}
            {error && (
                <div className="mb-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 text-sm text-red-600 dark:text-red-400">
                    {typeof error === 'string' ? error : (error as { message?: string }).message ?? 'Error desconocido'}
                </div>
            )}

            {/* Messages Area */}
            <Card variant="default" padding="none" className="flex-1 flex flex-col overflow-hidden">
                {isHistoryLoading ? (
                    <div className="flex flex-col items-center justify-center flex-1 gap-3 text-gray-500 dark:text-gray-400">
                        <Spinner size="md" />
                        <p className="text-sm">Cargando historial de chat...</p>
                    </div>
                ) : (
                    <MessageList
                        messages={messages}
                        streamingText={streaming.streamingText}
                        isStreaming={streaming.isStreaming}
                    />
                )}

                {/* Input Area */}
                <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">
                    <MessageInput
                        onSend={sendMessage}
                        disabled={!document.processed || isHistoryLoading || isResetting}
                        isStreaming={streaming.isStreaming}
                    />
                </div>
            </Card>
        </div>
    );
}
