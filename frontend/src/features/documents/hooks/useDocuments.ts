/**
 * useDocuments hook
 * Manages document state and operations
 */

'use client';

import { useState, useCallback } from 'react';
import { documentsService } from '@/services';
import { useApiError } from '@/hooks';
import type { Document, DocumentListItem, DocumentDetail } from '@/types/document';

export function useDocuments() {
    const [documents, setDocuments] = useState<DocumentListItem[]>([]);
    const [selectedDocument, setSelectedDocument] = useState<DocumentDetail | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const { error, handleError, clearError } = useApiError();

    /**
     * Fetch all documents
     */
    const fetchDocuments = useCallback(async () => {
        setIsLoading(true);
        clearError();

        try {
            const data = await documentsService.list();
            setDocuments(data);
        } catch (err) {
            handleError(err);
        } finally {
            setIsLoading(false);
        }
    }, [handleError, clearError]);

    /**
     * Fetch single document details
     */
    const fetchDocument = useCallback(async (documentId: number) => {
        setIsLoading(true);
        clearError();

        try {
            const data = await documentsService.getById(documentId);
            setSelectedDocument(data);
            return data;
        } catch (err) {
            handleError(err);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [handleError, clearError]);

    /**
     * Upload a new document
     */
    const uploadDocument = useCallback(async (file: File) => {
        setIsUploading(true);
        clearError();

        try {
            const newDoc = await documentsService.upload(file);

            // Add to list
            setDocuments((prev) => [newDoc, ...prev]);

            return newDoc;
        } catch (err) {
            handleError(err);
            return null;
        } finally {
            setIsUploading(false);
        }
    }, [handleError, clearError]);

    /**
     * Delete a document
     */
    const deleteDocument = useCallback(async (documentId: number) => {
        setIsLoading(true);
        clearError();

        try {
            await documentsService.delete(documentId);

            // Remove from list
            setDocuments((prev) => prev.filter((doc) => doc.id !== documentId));

            // Clear selected if it's the deleted one
            if (selectedDocument?.id === documentId) {
                setSelectedDocument(null);
            }

            return true;
        } catch (err) {
            handleError(err);
            return false;
        } finally {
            setIsLoading(false);
        }
    }, [handleError, clearError, selectedDocument]);

    /**
     * Process a document
     */
    const processDocument = useCallback(async (documentId: number) => {
        setIsLoading(true);
        clearError();

        try {
            const result = await documentsService.process(documentId);

            // Update document in list
            setDocuments((prev) =>
                prev.map((doc) =>
                    doc.id === documentId ? { ...doc, processed: true } : doc
                )
            );

            return result;
        } catch (err) {
            handleError(err);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [handleError, clearError]);

    return {
        documents,
        selectedDocument,
        isLoading,
        isUploading,
        error,
        fetchDocuments,
        fetchDocument,
        uploadDocument,
        deleteDocument,
        processDocument,
        clearError,
        setDocuments, // Expose for polling hook
    };
}
