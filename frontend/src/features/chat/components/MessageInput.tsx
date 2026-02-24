/**
 * MessageInput component
 * Input field for sending chat messages with character limit enforcement.
 */

'use client';

import { useState, FormEvent } from 'react';
import { Button, Input } from '@/components/ui';
import { MAX_MESSAGE_LENGTH } from '@/lib/constants';

interface MessageInputProps {
    onSend: (message: string) => void;
    disabled?: boolean;
    isStreaming?: boolean;
}

export function MessageInput({ onSend, disabled = false, isStreaming = false }: MessageInputProps) {
    const [message, setMessage] = useState('');

    const charsLeft = MAX_MESSAGE_LENGTH - message.length;
    const isOverLimit = charsLeft < 0;
    // Mostrar contador solo cuando el usuario está cerca del límite (últimos 20%)
    const showCounter = message.length > MAX_MESSAGE_LENGTH * 0.8;

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();

        if (!message.trim() || disabled || isStreaming || isOverLimit) return;

        onSend(message.trim());
        setMessage('');
    };

    return (
        <div className="flex flex-col gap-1">
            <form onSubmit={handleSubmit} className="flex gap-2">
                <Input
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Escribe tu pregunta sobre el documento..."
                    disabled={disabled || isStreaming}
                    maxLength={MAX_MESSAGE_LENGTH + 50} // deja escribir un poco más para notificar
                    fullWidth
                    className="text-base"
                    error={isOverLimit ? `Límite de ${MAX_MESSAGE_LENGTH} caracteres superado` : undefined}
                />
                <Button
                    type="submit"
                    variant="primary"
                    size="md"
                    disabled={!message.trim() || disabled || isStreaming || isOverLimit}
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

            {/* Contador visible solo cuando se acerca al límite */}
            {showCounter && (
                <span className={`text-xs text-right pr-1 ${isOverLimit ? 'text-red-500' : 'text-gray-400'}`}>
                    {isOverLimit
                        ? `${Math.abs(charsLeft)} caracteres de más`
                        : `${charsLeft} caracteres restantes`}
                </span>
            )}
        </div>
    );
}
