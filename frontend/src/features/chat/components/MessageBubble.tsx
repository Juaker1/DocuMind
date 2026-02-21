/**
 * MessageBubble component
 * Individual message display for user and assistant
 */

'use client';

import { useState } from 'react';
import { Card, Badge } from '@/components/ui';
import { formatRelativeTime } from '@/lib/utils';
import type { Message } from '@/types/chat';

interface MessageBubbleProps {
    message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
    const isUser = message.role === 'user';
    const [sourcesOpen, setSourcesOpen] = useState(false);

    const hasCitations = message.cited_pages && message.cited_pages.length > 0;
    const hasSnippets = message.cited_snippets && message.cited_snippets.length > 0;

    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
            <Card
                variant="default"
                padding="md"
                className={`max-w-[80%] ${isUser
                    ? 'bg-blue-600 dark:bg-blue-700 text-white border-blue-600 dark:border-blue-700'
                    : 'bg-gray-100 dark:bg-gray-700 border-gray-200 dark:border-gray-600'
                    }`}
            >
                <div className="flex items-start gap-3">
                    {/* AI Avatar */}
                    {!isUser && (
                        <div className="flex-shrink-0 rounded-full bg-blue-600 p-2">
                            <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                                />
                            </svg>
                        </div>
                    )}

                    {/* Message Content */}
                    <div className="flex-1 min-w-0">
                        {!isUser && (
                            <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">DocuMind IA</p>
                        )}
                        <div className={`prose prose-sm max-w-none ${isUser ? 'text-white' : 'text-gray-800 dark:text-gray-100'}`}>
                            {message.content}
                        </div>

                        {/* Page citation badges */}
                        {hasCitations && (
                            <div className="mt-2 flex flex-wrap items-center gap-1.5">
                                <span className="text-xs text-gray-500 dark:text-gray-400">Fuentes:</span>
                                {message.cited_pages!.map((page) => (
                                    <Badge key={page} variant="info" size="sm">
                                        Pág. {page}
                                    </Badge>
                                ))}

                                {/* Toggle snippets button */}
                                {hasSnippets && (
                                    <button
                                        onClick={() => setSourcesOpen(!sourcesOpen)}
                                        className="inline-flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 transition-colors ml-1"
                                    >
                                        <svg
                                            className={`h-3 w-3 transition-transform ${sourcesOpen ? 'rotate-180' : ''}`}
                                            fill="none" viewBox="0 0 24 24" stroke="currentColor"
                                        >
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                        </svg>
                                        {sourcesOpen ? 'Ocultar' : 'Ver'} fragmentos
                                    </button>
                                )}
                            </div>
                        )}

                        {/* Snippet accordion */}
                        {hasSnippets && sourcesOpen && (
                            <div className="mt-2 space-y-2">
                                {message.cited_snippets!.map((snippet, i) => (
                                    <div
                                        key={i}
                                        className="rounded-lg border border-blue-100 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20 px-3 py-2"
                                    >
                                        <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-blue-600 dark:text-blue-400">
                                            Página {snippet.page}
                                        </p>
                                        <p className="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">
                                            {snippet.text}
                                            {snippet.text.length >= 250 ? '…' : ''}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Timestamp */}
                        <p className={`mt-1 text-xs ${isUser ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'}`}>
                            {formatRelativeTime(message.created_at)}
                        </p>
                    </div>

                    {/* User Avatar */}
                    {isUser && (
                        <div className="flex-shrink-0 rounded-full bg-white p-2">
                            <svg className="h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                                />
                            </svg>
                        </div>
                    )}
                </div>
            </Card>
        </div>
    );
}
