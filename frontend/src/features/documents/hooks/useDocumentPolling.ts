/**
 * Hook for polling document status
 * Automatically checks processing status and updates when complete
 */

'use client';

import { useEffect, useRef } from 'react';
import { documentsService } from '@/services';
import type { DocumentListItem } from '@/types/document';

interface UseDocumentPollingOptions {
    documents: DocumentListItem[];
    onUpdate: (documents: DocumentListItem[]) => void;
    enabled?: boolean;
    interval?: number;
}

export function useDocumentPolling({
    documents,
    onUpdate,
    enabled = true,
    interval = 3000, // Check every 3 seconds
}: UseDocumentPollingOptions) {
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        if (!enabled) {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
            return;
        }

        // Find documents that are currently processing
        const processingDocs = documents.filter((doc) => !doc.processed);

        // If no documents are processing, don't poll
        if (processingDocs.length === 0) {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
            return;
        }

        // Start polling
        const checkStatus = async () => {
            try {
                // Fetch all documents to get updated status
                const updatedDocs = await documentsService.list();

                // Check if any processing document changed status
                const hasChanges = processingDocs.some((procDoc) => {
                    const updated = updatedDocs.find((d) => d.id === procDoc.id);
                    return updated && updated.processed !== procDoc.processed;
                });

                if (hasChanges) {
                    console.log('📄 Document processing status updated');
                    onUpdate(updatedDocs);
                }
            } catch (error) {
                console.error('Error polling document status:', error);
            }
        };

        // Set up interval
        intervalRef.current = setInterval(checkStatus, interval);

        // Cleanup
        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
        };
    }, [documents, onUpdate, enabled, interval]);
}
