/**
 * DocumentList component
 * Display grid of documents with loading and empty states
 */

'use client';

import { Spinner } from '@/components/ui';
import { DocumentCard } from './DocumentCard';
import type { DocumentListItem } from '@/types/document';

interface DocumentListProps {
    documents: DocumentListItem[];
    isLoading?: boolean;
    onDelete?: (id: number) => void;
    onReset?: (id: number) => void;
    deletingId?: number | null;
    resettingId?: number | null;
}

export function DocumentList({
    documents,
    isLoading = false,
    onDelete,
    onReset,
    deletingId = null,
    resettingId = null
}: DocumentListProps) {
    // Loading state
    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center py-16">
                <Spinner size="lg" />
                <p className="mt-4 text-gray-600">Cargando documentos...</p>
            </div>
        );
    }

    // Empty state
    if (documents.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 py-16">
                <div className="rounded-full bg-gray-100 p-4">
                    <svg className="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                    </svg>
                </div>
                <p className="mt-4 text-lg font-medium text-gray-900">No hay documentos</p>
                <p className="mt-1 text-sm text-gray-500">
                    Sube tu primer documento PDF para comenzar
                </p>
            </div>
        );
    }

    // Documents grid
    return (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {documents.map((document) => (
                <DocumentCard
                    key={document.id}
                    document={document}
                    onDelete={onDelete}
                    onReset={onReset}
                    isDeleting={deletingId === document.id}
                    isResetting={resettingId === document.id}
                />
            ))}
        </div>
    );
}
