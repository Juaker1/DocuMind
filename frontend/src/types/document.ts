/**
 * Document related TypeScript types
 */

export interface Document {
    id: number;
    filename: string;
    file_size: number;
    total_pages: number;
    upload_date: string;
    processed: boolean;
    conversation_count?: number;
}

export interface DocumentUploadResponse {
    id: number;
    filename: string;
    file_size: number;
    total_pages: number;
    upload_date: string;
    processed: boolean;
}

export interface DocumentListItem {
    id: number;
    filename: string;
    file_size: number;
    total_pages: number;
    upload_date: string;
    processed: boolean;
}

export interface DocumentDetail extends Document {
    conversation_count: number;
}
