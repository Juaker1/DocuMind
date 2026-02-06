/**
 * DocumentCard component
 * Display individual document with actions
 */

'use client';

import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent, CardFooter, Badge, Button } from '@/components';
import { formatFileSize, formatRelativeTime } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';
import type { DocumentListItem } from '@/types/document';

interface DocumentCardProps {
    document: DocumentListItem;
    onDelete?: (id: number) => void;
    isDeleting?: boolean;
}

export function DocumentCard({ document, onDelete, isDeleting = false }: DocumentCardProps) {
    return (
        <Card variant="default" padding="md" className="transition-all hover:shadow-md">
            <CardHeader>
                <div className="flex items-start justify-between gap-3">
                    <CardTitle className="text-lg">{document.filename}</CardTitle>
                    <Badge variant={document.processed ? 'success' : 'warning'} size="sm">
                        {document.processed ? 'Procesado' : 'Pendiente'}
                    </Badge>
                </div>
            </CardHeader>

            <CardContent>
                <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                    <div>
                        <span className="font-medium">Tamaño:</span> {formatFileSize(document.file_size)}
                    </div>
                    <div>
                        <span className="font-medium">Páginas:</span> {document.total_pages}
                    </div>
                    <div className="col-span-2">
                        <span className="font-medium">Subido:</span> {formatRelativeTime(document.upload_date)}
                    </div>
                </div>
            </CardContent>

            <CardFooter className="flex gap-2">
                <Link href={ROUTES.CHAT(document.id)} className="flex-1">
                    <Button
                        variant="primary"
                        size="sm"
                        fullWidth
                        disabled={!document.processed}
                    >
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                            />
                        </svg>
                        Chat
                    </Button>
                </Link>

                {onDelete && (
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onDelete(document.id)}
                        isLoading={isDeleting}
                    >
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                            />
                        </svg>
                    </Button>
                )}
            </CardFooter>
        </Card>
    );
}
