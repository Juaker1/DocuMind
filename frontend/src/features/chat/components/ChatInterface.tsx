/**
 * ChatInterface component
 * Main chat interface with messages and input
 */

'use client';

import { useEffect } from 'react';
import { Card } from '@/components/ui';
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
        error,
        streaming,
        sendMessage,
        finalizeStreamingMessage,
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
                            {document.total_pages} páginas • Chatea con el documento
                        </p>
                    </div>
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
                <MessageList
                    messages={messages}
                    streamingText={streaming.streamingText}
                    isStreaming={streaming.isStreaming}
                    isLoading={isLoading}
                />

                {/* Input Area */}
                <div className="border-t border-gray-200 p-4 bg-white">
                    <MessageInput
                        onSend={sendMessage}
                        disabled={!document.processed || isLoading}
                        isStreaming={streaming.isStreaming}
                    />
                </div>
            </Card>
        </div>
    );
}
