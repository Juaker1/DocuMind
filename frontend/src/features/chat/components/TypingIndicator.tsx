/**
 * TypingIndicator component
 * Shows animated dots when AI is thinking before first token arrives
 */

'use client';

import { Card } from '@/components/ui';

export function TypingIndicator() {
    return (
        <div className="flex justify-start">
            <Card variant="default" padding="md" className="bg-blue-50 border-blue-200">
                <div className="flex items-center gap-3">
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

                    {/* Dots */}
                    <div className="flex items-center gap-1 py-1">
                        <span
                            className="block h-2 w-2 rounded-full bg-blue-400 animate-bounce"
                            style={{ animationDelay: '0ms' }}
                        />
                        <span
                            className="block h-2 w-2 rounded-full bg-blue-400 animate-bounce"
                            style={{ animationDelay: '150ms' }}
                        />
                        <span
                            className="block h-2 w-2 rounded-full bg-blue-400 animate-bounce"
                            style={{ animationDelay: '300ms' }}
                        />
                    </div>
                </div>
            </Card>
        </div>
    );
}
