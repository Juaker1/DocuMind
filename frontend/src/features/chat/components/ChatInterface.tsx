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
                    <div className="rounded-lg bg-red-100 p-3">
                        <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                            />
                        </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                        <h2 className="text-lg font-semibold text-gray-900 truncate">
                            {document.filename}
                        </h2>
                        <p className="text-sm text-gray-500">
                            {document.total_pages} páginas
                            {messages.length > 0 && (
                                <span className="ml-2 text-blue-600">
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
                            className="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-500 hover:bg-red-50 hover:border-red-200 hover:text-red-600 transition-colors disabled:opacity-50"
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
                            <span className="text-gray-600">¿Borrar historial?</span>
                            <button
                                onClick={handleReset}
                                className="rounded px-2.5 py-1 bg-red-600 text-white hover:bg-red-700 transition-colors font-medium"
                            >
                                Sí, borrar
                            </button>
                            <button
                                onClick={() => setShowResetConfirm(false)}
                                className="rounded px-2.5 py-1 border border-gray-300 text-gray-600 hover:bg-gray-50 transition-colors"
                            >
                                Cancelar
                            </button>
                        </div>
                    )}
                </div>
            </Card>

            {/* Error Display */}
            {error && (
                <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-600">
                    {typeof error === 'string' ? error : (error as { message?: string }).message ?? 'Error desconocido'}
                </div>
            )}

            {/* Messages Area */}
            <Card variant="default" padding="none" className="flex-1 flex flex-col overflow-hidden">
                {isHistoryLoading ? (
                    <div className="flex flex-col items-center justify-center flex-1 gap-3 text-gray-500">
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
                <div className="border-t border-gray-200 p-4 bg-white">
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
