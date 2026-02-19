/**
 * MessageList component
 * Scrollable list of messages with auto-scroll
 */

'use client';

import { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { StreamingMessage } from './StreamingMessage';
import { TypingIndicator } from './TypingIndicator';
import { Spinner } from '@/components/ui';
import type { Message } from '@/types/chat';

interface MessageListProps {
    messages: Message[];
    streamingText?: string;
    isStreaming?: boolean;
    isLoading?: boolean;
}

export function MessageList({ messages, streamingText, isStreaming = false, isLoading = false }: MessageListProps) {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, streamingText]);

    if (isLoading && messages.length === 0) {
        return (
            <div className="flex items-center justify-center h-full">
                <Spinner size="lg" />
            </div>
        );
    }

    if (messages.length === 0 && !streamingText) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-center p-8">
                <div className="rounded-full bg-blue-100 p-6 mb-4">
                    <svg className="h-16 w-16 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={1.5}
                            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                        />
                    </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Comienza una conversación
                </h3>
                <p className="text-gray-600 max-w-md">
                    Haz preguntas sobre el contenido del documento y obtén respuestas al instante con DocuMind IA.
                </p>
            </div>
        );
    }

    return (
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
            ))}

            {streamingText && <StreamingMessage text={streamingText} />}

            {/* Show typing indicator when streaming started but no text yet */}
            {isStreaming && !streamingText && <TypingIndicator />}

            <div ref={messagesEndRef} />
        </div>
    );
}
