/**
 * MessageInput component
 * Input field for sending chat messages
 */

'use client';

import { useState, FormEvent } from 'react';
import { Button, Input } from '@/components/ui';

interface MessageInputProps {
    onSend: (message: string) => void;
    disabled?: boolean;
    isStreaming?: boolean;
}

export function MessageInput({ onSend, disabled = false, isStreaming = false }: MessageInputProps) {
    const [message, setMessage] = useState('');

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();

        if (!message.trim() || disabled || isStreaming) return;

        onSend(message);
        setMessage('');
    };

    return (
        <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Escribe tu pregunta sobre el documento..."
                disabled={disabled || isStreaming}
                fullWidth
                className="text-base"
            />
            <Button
                type="submit"
                variant="primary"
                size="md"
                disabled={!message.trim() || disabled || isStreaming}
                isLoading={isStreaming}
            >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                    />
                </svg>
                Enviar
            </Button>
        </form>
    );
}
