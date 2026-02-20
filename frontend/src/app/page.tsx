/**
 * Home page - Document upload and management
 */

'use client';

import { useEffect, useState } from 'react';
import { Container, Button, Modal } from '@/components';
import { DocumentUpload, DocumentList, useDocuments, useDocumentPolling } from '@/features/documents';
import { conversationsService } from '@/services';
import { useAuth } from '@/features/auth/AuthProvider';
import { AuthModal } from '@/features/auth/components/AuthModal';

export default function HomePage() {
  const { isAnonymous } = useAuth();
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
  const [authOpen, setAuthOpen] = useState(false);

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
      {/* Anonymous user banner */}
      {isAnonymous && (
        <div className="mb-8 flex items-center justify-between gap-4 rounded-xl border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20 px-5 py-4 text-sm">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🔒</span>
            <div>
              <p className="font-semibold text-blue-900 dark:text-blue-200">Estás navegando como invitado</p>
              <p className="text-blue-700 dark:text-blue-400">Crea una cuenta para acceder a tus documentos desde cualquier dispositivo.</p>
            </div>
          </div>
          <button
            onClick={() => setAuthOpen(true)}
            className="shrink-0 rounded-lg bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 text-sm font-medium transition-colors"
          >
            Crear cuenta gratis
          </button>
        </div>
      )}

      {/* Hero Section */}
      <div className="mb-12 text-center">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white sm:text-5xl">
          Chatea con tus{' '}
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Documentos PDF
          </span>
        </h1>
        <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
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
        <div className="mb-6 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 text-red-800 dark:text-red-300">
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

      {/* Auth Modal (triggered from anonymous banner) */}
      <AuthModal isOpen={authOpen} onClose={() => setAuthOpen(false)} defaultTab="register" />

      {/* Stats Section (if there are documents) */}
      {documents.length > 0 && (
        <div className="mt-12 grid gap-6 sm:grid-cols-3">
          <div className="rounded-lg bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 p-6 shadow-sm">
            <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Documentos</div>
            <div className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{documents.length}</div>
          </div>
          <div className="rounded-lg bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 p-6 shadow-sm">
            <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Procesados</div>
            <div className="mt-2 text-3xl font-bold text-green-600 dark:text-green-400">
              {documents.filter((d) => d.processed).length}
            </div>
          </div>
          <div className="rounded-lg bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 p-6 shadow-sm">
            <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Pendientes</div>
            <div className="mt-2 text-3xl font-bold text-yellow-600 dark:text-yellow-400">
              {documents.filter((d) => !d.processed).length}
            </div>
          </div>
        </div>
      )}
    </Container>
  );
}
