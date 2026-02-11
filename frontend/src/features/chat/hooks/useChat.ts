/**
 * useChat hook
 * Manages chat state, messages, and conversations
 */

'use client';

import { useState, useCallback } from 'react';
import { chatService, conversationsService } from '@/services';
import { useApiError } from '@/hooks';
import { useStreamingResponse } from './useStreamingResponse';
import type { Message, Conversation, ConversationDetail, ChatRequest } from '@/types/chat';

export function useChat(documentId: number) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const { error, handleError, clearError } = useApiError();
    const streaming = useStreamingResponse();

    /**
     * Load conversation history
     */
    const loadConversation = useCallback(async (conversationId: number) => {
        setIsLoading(true);
        clearError();

        try {
            const conversation = await conversationsService.getById(conversationId);
            setMessages(conversation.messages);
            setCurrentConversationId(conversationId);
        } catch (err) {
            handleError(err);
        } finally {
            setIsLoading(false);
        }
    }, [handleError, clearError]);

    /**
     * Load all conversations for this document
     */
    const loadConversations = useCallback(async () => {
        try {
            const convos = await conversationsService.listByDocument(documentId);
            setConversations(convos);
        } catch (err) {
            handleError(err);
        }
    }, [documentId, handleError]);

    /**
     * Send a message with streaming
     */
    const sendMessage = useCallback(async (messageText: string) => {
        if (!messageText.trim()) return;

        clearError();

        // Add user message to UI immediately
        const userMessage: Message = {
            id: Date.now(), // Temporary ID
            role: 'user',
            content: messageText,
            created_at: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);

        // Prepare request
        const request: ChatRequest = {
            document_id: documentId,
            message: messageText,
            conversation_id: currentConversationId || undefined,
        };

        try {
            // Start streaming
            streaming.startStreaming(request);

            // Note: The actual message saving happens on backend
            // We'll need to refresh after streaming completes

        } catch (err) {
            handleError(err);
            // Remove user message on error
            setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
        }
    }, [documentId, currentConversationId, streaming, handleError, clearError]);

    /**
     * Add streaming message to chat when complete
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
     * Start new conversation
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
        error,
        streaming,
        sendMessage,
        loadConversation,
        loadConversations,
        finalizeStreamingMessage,
        startNewConversation,
    };
}
