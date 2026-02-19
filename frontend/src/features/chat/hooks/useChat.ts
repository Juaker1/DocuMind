/**
 * useChat hook
 * Manages chat state, messages, and conversations with full persistence.
 * Automatically loads the last conversation for the document on mount.
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import { conversationsService } from '@/services';
import { useApiError } from '@/hooks';
import { useStreamingResponse } from './useStreamingResponse';
import type { Message, Conversation, ChatRequest } from '@/types/chat';

export function useChat(documentId: number) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isHistoryLoading, setIsHistoryLoading] = useState(true);
    const { error, handleError, clearError } = useApiError();
    const streaming = useStreamingResponse();

    /**
     * Load full message history for a given conversation
     */
    const loadConversation = useCallback(async (conversationId: number) => {
        setIsLoading(true);
        clearError();
        try {
            const conversation = await conversationsService.getById(conversationId);
            setMessages(conversation.messages ?? []);
            setCurrentConversationId(conversationId);
        } catch (err) {
            handleError(err);
        } finally {
            setIsLoading(false);
        }
    }, [handleError, clearError]);

    /**
     * On mount: fetch existing conversations for this document and auto-load the latest one.
     */
    useEffect(() => {
        let cancelled = false;

        const init = async () => {
            setIsHistoryLoading(true);
            try {
                const convos = await conversationsService.listByDocument(documentId);
                if (cancelled) return;

                setConversations(convos);

                if (convos.length > 0) {
                    // Backend ordena por fecha DESC, el más reciente es convos[0]
                    const latest = convos[0];
                    const detail = await conversationsService.getById(latest.id);
                    if (cancelled) return;
                    setMessages(detail.messages ?? []);
                    setCurrentConversationId(latest.id);
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
     * After the stream completes, captures the backend-assigned conversation_id.
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

        const request: ChatRequest = {
            document_id: documentId,
            message: messageText,
            conversation_id: currentConversationId || undefined,
        };

        try {
            streaming.startStreaming(request, (completionData) => {
                // Persist conversation_id from backend for future messages
                if (completionData.conversation_id) {
                    setCurrentConversationId(completionData.conversation_id);
                }
            });
        } catch (err) {
            handleError(err);
            setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
        }
    }, [documentId, currentConversationId, streaming, handleError, clearError]);

    /**
     * Finalize: move streaming text into the permanent messages list
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
     * Start a fresh conversation (clear history)
     */
    const startNewConversation = useCallback(() => {
        setCurrentConversationId(null);
        setMessages([]);
        streaming.resetStreaming();
    }, [streaming]);

    return {
        messages,
        conversations,
        currentConversationId,
        isLoading,
        isHistoryLoading,
        error,
        streaming,
        sendMessage,
        loadConversation,
        finalizeStreamingMessage,
        startNewConversation,
    };
}
