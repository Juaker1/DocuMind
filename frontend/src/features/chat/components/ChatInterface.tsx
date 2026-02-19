/**
 * ChatInterface component
 * Main chat interface with message history, streaming, and persistence.
 */

'use client';

import { useEffect } from 'react';
import { Card, Spinner } from '@/components/ui';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { useChat } from '../hooks';
import type { DocumentDetail } from '@/types/document';

interface ChatInterfaceProps {
    document: DocumentDetail;
}

export function ChatInterface({ document }: ChatInterfaceProps) {
    const {
        messages,
        isLoading,
        isHistoryLoading,
        error,
        streaming,
        sendMessage,
        finalizeStreamingMessage,
        startNewConversation,
        currentConversationId,
    } = useChat(document.id);

    // Finalize streaming message when complete
    useEffect(() => {
        if (!streaming.isStreaming && streaming.streamingText) {
            finalizeStreamingMessage();
        }
    }, [streaming.isStreaming, streaming.streamingText, finalizeStreamingMessage]);

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
                        <p className="text-sm text-gray-600">
                            {document.total_pages} páginas
                            {currentConversationId
                                ? <span className="ml-2 text-blue-600">• Conversación #{currentConversationId}</span>
                                : <span className="ml-2 text-gray-400">• Nueva conversación</span>
                            }
                        </p>
                    </div>

                    {/* New conversation button */}
                    {currentConversationId && (
                        <button
                            onClick={startNewConversation}
                            className="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
                            title="Iniciar nueva conversación"
                        >
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                            Nueva sesión
                        </button>
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
                        isLoading={isLoading}
                    />
                )}

                {/* Input Area */}
                <div className="border-t border-gray-200 p-4 bg-white">
                    <MessageInput
                        onSend={sendMessage}
                        disabled={!document.processed || isLoading || isHistoryLoading}
                        isStreaming={streaming.isStreaming}
                    />
                </div>
            </Card>
        </div>
    );
}
