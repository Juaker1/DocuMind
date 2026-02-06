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
            `/api/conversations/document/${documentId}`
        );
        return response.data;
    },

    /**
     * Get all conversations (across all documents)
     */
    async list(): Promise<Conversation[]> {
        const response = await apiClient.get<Conversation[]>('/api/conversations/');
        return response.data;
    },

    /**
     * Get full conversation details with all messages
     */
    async getById(conversationId: number): Promise<ConversationDetail> {
        const response = await apiClient.get<ConversationDetail>(
            `/api/conversations/${conversationId}`
        );
        return response.data;
    },

    /**
     * Delete a conversation
     */
    async delete(conversationId: number): Promise<{ message: string }> {
        const response = await apiClient.delete(
            `/api/conversations/${conversationId}`
        );
        return response.data;
    },
};
