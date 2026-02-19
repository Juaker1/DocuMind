/**
 * useStreamingResponse hook
 * Manages SSE streaming for real-time AI chat responses
 */

'use client';

import { useState, useCallback, useRef } from 'react';
import { chatService } from '@/services';
import type { ChatRequest } from '@/types/chat';
import { SSEClient } from '@/services/sse-client';
import type { SSECompletionData } from '@/services/sse-client';

export function useStreamingResponse() {
    const [streamingText, setStreamingText] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const sseClientRef = useRef<SSEClient | null>(null);

    /**
     * Start streaming chat response.
     * onComplete receives the backend metadata (conversation_id, etc.)
     */
    const startStreaming = useCallback((
        request: ChatRequest,
        onComplete?: (data: SSECompletionData) => void,
    ) => {
        setStreamingText('');
        setIsStreaming(true);
        setError(null);

        const client = chatService.streamChat(request, {
            onOpen: () => {
                console.log('🔗 SSE Connection opened');
            },
            onMessage: (chunk) => {
                setStreamingText((prev) => prev + chunk);
            },
            onComplete: (data) => {
                console.log('✅ SSE Stream complete', data);
                setIsStreaming(false);
                onComplete?.(data);
            },
            onError: (err) => {
                console.error('❌ SSE Error:', err);
                setError('Error en el streaming');
                setIsStreaming(false);
            },
        });

        sseClientRef.current = client;
    }, []);

    /**
     * Stop streaming
     */
    const stopStreaming = useCallback(() => {
        if (sseClientRef.current) {
            sseClientRef.current.close();
            sseClientRef.current = null;
            setIsStreaming(false);
        }
    }, []);

    /**
     * Reset streaming state
     */
    const resetStreaming = useCallback(() => {
        setStreamingText('');
        setError(null);
        setIsStreaming(false);
    }, []);

    return {
        streamingText,
        isStreaming,
        error,
        startStreaming,
        stopStreaming,
        resetStreaming,
    };
}
