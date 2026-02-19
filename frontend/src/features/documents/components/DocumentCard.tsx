/**
 * DocumentCard component
 * Display individual document with actions.
 * Inline confirms for both reset-chat and delete-document actions.
 */

'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter, Badge, Button } from '@/components';
import { formatFileSize, formatRelativeTime } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';
import type { DocumentListItem } from '@/types/document';

interface DocumentCardProps {
    document: DocumentListItem;
    onDelete?: (id: number) => void;
    onReset?: (id: number) => void;
    isDeleting?: boolean;
    isResetting?: boolean;
}

export function DocumentCard({ document, onDelete, onReset, isDeleting = false, isResetting = false }: DocumentCardProps) {
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [showResetConfirm, setShowResetConfirm] = useState(false);

    return (
        <Card variant="default" padding="md" className="transition-all hover:shadow-md">
            <CardHeader>
                <div className="flex items-start justify-between gap-3">
                    <CardTitle className="text-lg truncate flex-1 min-w-0">
                        {document.filename}
                    </CardTitle>
                    <Badge
                        variant={document.processed ? 'success' : 'warning'}
                        size="sm"
                        className="flex-shrink-0"
                    >
                        {document.processed ? (
                            'Listo'
                        ) : (
                            <>
                                <svg className="h-3 w-3 animate-spin" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                </svg>
                                Procesando
                            </>
                        )}
                    </Badge>
                </div>
            </CardHeader>

            <CardContent>
                <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                    <div><span className="font-medium">Tamaño:</span> {formatFileSize(document.file_size)}</div>
                    <div><span className="font-medium">Páginas:</span> {document.total_pages}</div>
                    <div className="col-span-2"><span className="font-medium">Subido:</span> {formatRelativeTime(document.upload_date)}</div>
                </div>
            </CardContent>

            <CardFooter className="flex flex-col gap-2">

                {/* Reset confirm banner (orange) */}
                {showResetConfirm && (
                    <div className="flex items-center justify-between w-full rounded-lg bg-orange-50 border border-orange-200 px-3 py-2 text-sm">
                        <span className="text-orange-700 font-medium">¿Reiniciar chat?</span>
                        <div className="flex gap-2">
                            <button
                                onClick={() => { setShowResetConfirm(false); onReset?.(document.id); }}
                                disabled={isResetting}
                                className="rounded px-2.5 py-1 bg-orange-500 text-white hover:bg-orange-600 transition-colors font-medium text-xs disabled:opacity-50"
                            >
                                {isResetting ? 'Reiniciando...' : 'Sí, reiniciar'}
                            </button>
                            <button
                                onClick={() => setShowResetConfirm(false)}
                                className="rounded px-2.5 py-1 border border-orange-300 text-orange-600 hover:bg-orange-100 transition-colors text-xs"
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                )}

                {/* Delete confirm banner (red) */}
                {showDeleteConfirm && (
                    <div className="flex items-center justify-between w-full rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm">
                        <span className="text-red-700 font-medium">¿Eliminar documento?</span>
                        <div className="flex gap-2">
                            <button
                                onClick={() => { setShowDeleteConfirm(false); onDelete?.(document.id); }}
                                disabled={isDeleting}
                                className="rounded px-2.5 py-1 bg-red-600 text-white hover:bg-red-700 transition-colors font-medium text-xs disabled:opacity-50"
                            >
                                {isDeleting ? 'Eliminando...' : 'Sí, eliminar'}
                            </button>
                            <button
                                onClick={() => setShowDeleteConfirm(false)}
                                className="rounded px-2.5 py-1 border border-red-300 text-red-600 hover:bg-red-100 transition-colors text-xs"
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                )}

                {/* Action buttons row */}
                <div className="flex gap-2 w-full">
                    <Link href={ROUTES.CHAT(document.id)} className="flex-1">
                        <Button variant="primary" size="sm" fullWidth disabled={!document.processed}>
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                            Chat
                        </Button>
                    </Link>

                    {onReset && document.processed && !showResetConfirm && !showDeleteConfirm && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowResetConfirm(true)}
                            isLoading={isResetting}
                            disabled={!document.has_conversation}
                            title={document.has_conversation ? 'Reiniciar chat' : 'No hay chat que reiniciar'}
                            className={
                                document.has_conversation
                                    ? 'bg-orange-500 text-white hover:bg-orange-600 border-0'
                                    : 'text-gray-300 cursor-not-allowed opacity-50'
                            }
                        >
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                        </Button>
                    )}

                    {onDelete && !showDeleteConfirm && !showResetConfirm && (
                        <Button
                            variant="danger"
                            size="sm"
                            onClick={() => setShowDeleteConfirm(true)}
                            isLoading={isDeleting}
                            title="Eliminar documento"
                        >
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </Button>
                    )}
                </div>
            </CardFooter>
        </Card>
    );
}
