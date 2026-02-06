/**
 * Chat and conversation related TypeScript types
 */

export interface Message {
    id: number;
    role: 'user' | 'assistant';
    content: string;
    created_at: string;
    cited_pages?: number[];
}

export interface ChatRequest {
    document_id: number;
    message: string;
    conversation_id?: number;
}

export interface ChatResponse {
    conversation_id: number;
    message_id: number;
    response: string;
    cited_pages: number[];
}

export interface Conversation {
    id: number;
    document_id: number;
    created_at: string;
    title?: string;
    message_count: number;
}

export interface ConversationDetail extends Conversation {
    document_filename: string;
    messages: Message[];
}

export interface StreamingState {
    text: string;
    isStreaming: boolean;
    error: string | null;
}
