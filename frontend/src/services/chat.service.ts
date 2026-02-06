/**
 * Chat service
 * Handles chat interactions with SSE streaming support
 */

import { apiClient } from './api';
import { createSSEClient, SSEClient, SSEOptions } from './sse-client';
import { API_BASE_URL } from '@/lib/constants';
import type { ChatRequest, ChatResponse } from '@/types/chat';

export const chatService = {
    /**
     * Send a chat message with SSE streaming
     * Returns an SSEClient that streams the response in real-time
     */
    streamChat(request: ChatRequest, callbacks: SSEOptions): SSEClient {
        const params = new URLSearchParams({
            document_id: request.document_id.toString(),
            message: request.message,
        });

        if (request.conversation_id !== undefined && request.conversation_id !== null) {
            params.append('conversation_id', request.conversation_id.toString());
        }

        const url = `${API_BASE_URL}/api/chat/stream?${params.toString()}`;

        return createSSEClient(url, callbacks);
    },

    /**
     * Send a chat message (non-streaming)
     * Use this for simple request-response without streaming
     */
    async sendMessage(request: ChatRequest): Promise<ChatResponse> {
        const response = await apiClient.post<ChatResponse>('/api/chat/', request);
        return response.data;
    },
};
