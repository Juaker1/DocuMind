/**
 * StreamingMessage component
 * Displays AI message with typing animation
 */

'use client';

import { Card } from '@/components/ui';

interface StreamingMessageProps {
    text: string;
}

export function StreamingMessage({ text }: StreamingMessageProps) {
    // Ocultar el marcador @@FUENTES:[]@@ si el LLM ya lo está escribiendo al final del stream
    const displayText = text.replace(/@@FUENTES:\[[^\]]*\]?@@?/g, '').trimEnd();

    return (
        <div className="flex justify-start">
            <Card variant="default" padding="md" className="max-w-[80%] bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
                <div className="flex items-start gap-3">
                    {/* AI Avatar */}
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

                    {/* Message Content */}
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-1">DocuMind IA</p>
                        <div className="prose prose-sm max-w-none text-gray-800 dark:text-gray-100">
                            {displayText}
                            <span className="inline-block w-2 h-4 ml-1 bg-blue-600 dark:bg-blue-400 animate-pulse" />
                        </div>
                    </div>
                </div>
            </Card>
        </div>
    );
}
