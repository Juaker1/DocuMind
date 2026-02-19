/**
 * Home page - Document upload and management
 */

'use client';

import { useEffect, useState } from 'react';
import { Container, Button, Modal } from '@/components';
import { DocumentUpload, DocumentList, useDocuments, useDocumentPolling } from '@/features/documents';
import { conversationsService } from '@/services';

export default function HomePage() {
  const {
    documents,
    isLoading,
    isUploading,
    error,
    fetchDocuments,
    uploadDocument,
    deleteDocument,
    setDocuments,
  } = useDocuments();

  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [resettingId, setResettingId] = useState<number | null>(null);

  // Fetch documents on mount
  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Handle file upload
  const handleUpload = async (file: File) => {
    const result = await uploadDocument(file);
    if (result) {
      setIsUploadModalOpen(false);
    }
  };

  // Handle delete — called after inline confirm in DocumentCard
  const handleDelete = async (id: number) => {
    setDeletingId(id);
    await deleteDocument(id);
    setDeletingId(null);
  };

  // Handle reset chat
  const handleReset = async (id: number) => {
    setResettingId(id);
    try {
      await conversationsService.resetByDocument(id);
    } catch {
      // silently ignore — no conversation to reset is fine
    } finally {
      setResettingId(null);
    }
  };

  // Auto-update document status when processing completes
  useDocumentPolling({
    documents,
    onUpdate: (updatedDocs) => {
      // Silently update documents without triggering loading state
      setDocuments(updatedDocs);
    },
    enabled: !isLoading, // Only poll when not loading
  });

  return (
    <Container size="xl" className="py-8">
      {/* Hero Section */}
      <div className="mb-12 text-center">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl">
          Chatea con tus{' '}
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Documentos PDF
          </span>
        </h1>
        <p className="mt-4 text-lg text-gray-600">
          Sube tus PDFs y chatea con ellos usando inteligencia artificial
        </p>
      </div>

      {/* Upload Button */}
      <div className="mb-8 flex justify-end">
        <Button
          variant="primary"
          size="lg"
          onClick={() => setIsUploadModalOpen(true)}
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Subir Documento
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 rounded-lg bg-red-50 p-4 text-red-800">
          <div className="flex items-start gap-3">
            <svg className="h-5 w-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <h3 className="font-medium">Error</h3>
              <p className="text-sm">{error.detail}</p>
            </div>
          </div>
        </div>
      )}

      {/* Documents List */}
      <DocumentList
        documents={documents}
        isLoading={isLoading}
        onDelete={handleDelete}
        onReset={handleReset}
        deletingId={deletingId}
        resettingId={resettingId}
      />

      {/* Upload Modal */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Subir Documento PDF"
        size="md"
      >
        <DocumentUpload onUpload={handleUpload} isUploading={isUploading} />
      </Modal>


      {/* Stats Section (if there are documents) */}
      {documents.length > 0 && (
        <div className="mt-12 grid gap-6 sm:grid-cols-3">
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <div className="text-sm font-medium text-gray-500">Total Documentos</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">{documents.length}</div>
          </div>
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <div className="text-sm font-medium text-gray-500">Procesados</div>
            <div className="mt-2 text-3xl font-bold text-green-600">
              {documents.filter((d) => d.processed).length}
            </div>
          </div>
          <div className="rounded-lg bg-white p-6 shadow-sm">
            <div className="text-sm font-medium text-gray-500">Pendientes</div>
            <div className="mt-2 text-3xl font-bold text-yellow-600">
              {documents.filter((d) => !d.processed).length}
            </div>
          </div>
        </div>
      )}
    </Container>
  );
}
