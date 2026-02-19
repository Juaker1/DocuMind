/**
 * Conversations service
 * Handles conversation history and management
 */

import { apiClient } from './api';
import type { Conversation, ConversationDetail } from '@/types/chat';

export const conversationsService = {
    /**
     * Get all conversations for a document
     */
    async listByDocument(documentId: number): Promise<Conversation[]> {
        const response = await apiClient.get<Conversation[]>(
            `/api/chat/documents/${documentId}/conversations`
        );
        return response.data;
    },

    /**
     * Get full conversation details with all messages
     */
    async getById(conversationId: number): Promise<ConversationDetail> {
        const response = await apiClient.get<ConversationDetail>(
            `/api/chat/conversations/${conversationId}`
        );
        return response.data;
    },

    /**
     * Delete a conversation
     */
    async delete(conversationId: number): Promise<{ message: string }> {
        const response = await apiClient.delete(
            `/api/chat/conversations/${conversationId}`
        );
        return response.data;
    },

    /**
     * Reset (delete) the single conversation for a document.
     * The next chat message will create a fresh conversation automatically.
     */
    async resetByDocument(documentId: number): Promise<{ message: string }> {
        const response = await apiClient.delete(
            `/api/chat/documents/${documentId}/conversation`
        );
        return response.data;
    },
};
