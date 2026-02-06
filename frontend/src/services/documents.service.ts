/**
 * Documents service
 * Handles all document-related API calls
 */

import { apiClient } from './api';
import type {
    Document,
    DocumentUploadResponse,
    DocumentListItem,
    DocumentDetail,
} from '@/types/document';

export const documentsService = {
    /**
     * Upload a new PDF document
     */
    async upload(file: File): Promise<DocumentUploadResponse> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await apiClient.post<DocumentUploadResponse>(
            '/api/documents/upload',
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                // Track upload progress if needed
                onUploadProgress: (progressEvent) => {
                    if (progressEvent.total) {
                        const percentCompleted = Math.round(
                            (progressEvent.loaded * 100) / progressEvent.total
                        );
                        console.log(`Upload progress: ${percentCompleted}%`);
                    }
                },
            }
        );

        return response.data;
    },

    /**
     * Get list of all documents
     */
    async list(): Promise<DocumentListItem[]> {
        const response = await apiClient.get<DocumentListItem[]>('/api/documents/');
        return response.data;
    },

    /**
     * Get details of a specific document
     */
    async getById(documentId: number): Promise<DocumentDetail> {
        const response = await apiClient.get<DocumentDetail>(
            `/api/documents/${documentId}`
        );
        return response.data;
    },

    /**
     * Manually trigger document processing
     */
    async process(documentId: number): Promise<{ message: string; chunks_created: number }> {
        const response = await apiClient.post(
            `/api/documents/${documentId}/process`
        );
        return response.data;
    },

    /**
     * Delete a document
     */
    async delete(documentId: number): Promise<{ message: string }> {
        const response = await apiClient.delete(`/api/documents/${documentId}`);
        return response.data;
    },
};
