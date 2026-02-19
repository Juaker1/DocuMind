/**
 * useChat hook
 * Manages chat state for a single document.
 * One conversation per document — backend handles find-or-create.
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import { conversationsService } from '@/services';
import { useApiError } from '@/hooks';
import { useStreamingResponse } from './useStreamingResponse';
import type { Message } from '@/types/chat';

export function useChat(documentId: number) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
    const [isHistoryLoading, setIsHistoryLoading] = useState(true);
    const [isResetting, setIsResetting] = useState(false);
    const { error, handleError, clearError } = useApiError();
    const streaming = useStreamingResponse();

    /**
     * On mount: fetch the single existing conversation for this document (if any)
     * and load its messages.
     */
    useEffect(() => {
        let cancelled = false;

        const init = async () => {
            setIsHistoryLoading(true);
            try {
                const convos = await conversationsService.listByDocument(documentId);
                if (cancelled) return;

                if (convos.length > 0) {
                    // There is at most one conversation per document
                    const conv = convos[0];
                    const detail = await conversationsService.getById(conv.id);
                    if (cancelled) return;
                    setMessages(detail.messages ?? []);
                    setCurrentConversationId(conv.id);
                }
            } catch (err) {
                if (!cancelled) handleError(err);
            } finally {
                if (!cancelled) setIsHistoryLoading(false);
            }
        };

        init();

        return () => { cancelled = true; };
    }, [documentId, handleError]);

    /**
     * Send a message with SSE streaming.
     * Does not pass conversation_id — backend always resolves by document_id.
     */
    const sendMessage = useCallback(async (messageText: string) => {
        if (!messageText.trim()) return;

        clearError();

        // Optimistically add user message to UI
        const userMessage: Message = {
            id: Date.now(),
            role: 'user',
            content: messageText,
            created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, userMessage]);

        try {
            streaming.startStreaming(
                { document_id: documentId, message: messageText },
                (completionData) => {
                    if (completionData.conversation_id) {
                        setCurrentConversationId(completionData.conversation_id);
                    }
                }
            );
        } catch (err) {
            handleError(err);
            setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
        }
    }, [documentId, streaming, handleError, clearError]);

    /**
     * Move streaming text into the permanent messages list once stream completes.
     */
    const finalizeStreamingMessage = useCallback(() => {
        if (streaming.streamingText) {
            const assistantMessage: Message = {
                id: Date.now(),
                role: 'assistant',
                content: streaming.streamingText,
                created_at: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMessage]);
            streaming.resetStreaming();
        }
    }, [streaming]);

    /**
     * Reset: delete the conversation from the backend and clear all local state.
     * The next message will create a fresh conversation automatically.
     */
    const resetConversation = useCallback(async () => {
        setIsResetting(true);
        clearError();
        try {
            await conversationsService.resetByDocument(documentId);
            setMessages([]);
            setCurrentConversationId(null);
            streaming.resetStreaming();
        } catch (err) {
            handleError(err);
        } finally {
            setIsResetting(false);
        }
    }, [documentId, streaming, handleError, clearError]);

    return {
        messages,
        currentConversationId,
        isHistoryLoading,
        isResetting,
        error,
        streaming,
        sendMessage,
        finalizeStreamingMessage,
        resetConversation,
    };
}
