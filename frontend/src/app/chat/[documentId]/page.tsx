/**
 * Chat page - Dynamic route for document chat
 */

'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Container, Button, Spinner } from '@/components';
import { ChatInterface } from '@/features/chat';
import { documentsService } from '@/services';
import { ROUTES } from '@/lib/constants';
import type { DocumentDetail } from '@/types/document';

export default function ChatPage() {
    const params = useParams();
    const router = useRouter();
    const documentId = parseInt(params.documentId as string);

    const [document, setDocument] = useState<DocumentDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchDocument = async () => {
            try {
                setIsLoading(true);
                const doc = await documentsService.getById(documentId);
                setDocument(doc);
            } catch (err) {
                setError('No se pudo cargar el documento');
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };

        if (documentId) {
            fetchDocument();
        }
    }, [documentId]);

    // Loading state
    if (isLoading) {
        return (
            <Container size="lg" className="py-12">
                <div className="flex flex-col items-center justify-center min-h-[60vh]">
                    <Spinner size="lg" />
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando documento...</p>
                </div>
            </Container>
        );
    }

    // Error state
    if (error || !document) {
        return (
            <Container size="lg" className="py-12">
                <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
                    <div className="rounded-full bg-red-100 dark:bg-red-900/30 p-6 mb-4">
                        <svg className="h-16 w-16 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    </div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                        Documento no encontrado
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                        {error || 'El documento que buscas no existe o fue eliminado.'}
                    </p>
                    <Button variant="primary" onClick={() => router.push(ROUTES.HOME)}>
                        Volver al inicio
                    </Button>
                </div>
            </Container>
        );
    }

    // Not processed state
    if (!document.processed) {
        return (
            <Container size="lg" className="py-12">
                <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
                    <div className="rounded-full bg-yellow-100 dark:bg-yellow-900/30 p-6 mb-4">
                        <svg className="h-16 w-16 text-yellow-600 dark:text-yellow-400 animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                    </div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                        Documento en proceso
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                        Estamos procesando <span className="font-medium">{document.filename}</span>.
                        <br />
                        Por favor espera unos momentos y recarga la página.
                    </p>
                    <Button variant="primary" onClick={() => window.location.reload()}>
                        Recargar página
                    </Button>
                </div>
            </Container>
        );
    }

    // Chat interface
    return (
        <Container size="xl" className="py-6">
            <div className="mb-4">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push(ROUTES.HOME)}
                    className="border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                    Volver a documentos
                </Button>
            </div>

            <ChatInterface document={document} />
        </Container>
    );
}
