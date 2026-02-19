/**
 * DocumentUpload component
 * Drag-and-drop file upload for PDFs
 */

'use client';

import { useState, useCallback, useRef } from 'react';
import { Button } from '@/components/ui';
import { MAX_FILE_SIZE, ALLOWED_FILE_TYPES } from '@/lib/constants';
import { formatFileSize } from '@/lib/utils';

interface DocumentUploadProps {
    onUpload: (file: File) => Promise<void>;
    isUploading?: boolean;
}

export function DocumentUpload({ onUpload, isUploading = false }: DocumentUploadProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const validateFile = useCallback((file: File): string | null => {
        // Check if it's a PDF
        if (!ALLOWED_FILE_TYPES.includes(file.type)) {
            return 'Solo se permiten archivos PDF';
        }

        // Check file size
        if (file.size > MAX_FILE_SIZE) {
            return `El archivo es demasiado grande (máx: ${formatFileSize(MAX_FILE_SIZE)})`;
        }

        return null;
    }, []);

    const handleFile = useCallback(async (file: File) => {
        const validationError = validateFile(file);
        if (validationError) {
            setError(validationError);
            return;
        }

        setError(null);
        await onUpload(file);
    }, [validateFile, onUpload]);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const file = e.dataTransfer.files[0];
        if (file) {
            handleFile(file);
        }
    }, [handleFile]);

    const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            handleFile(file);
        }
    }, [handleFile]);

    const handleClick = useCallback(() => {
        fileInputRef.current?.click();
    }, []);

    return (
        <div className="w-full">
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={handleClick}
                className={`
          relative cursor-pointer rounded-lg border-2 border-dashed p-12 text-center transition-all
          ${isDragging
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800/50 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50/50 dark:hover:bg-blue-900/10'}
          ${isUploading ? 'pointer-events-none opacity-50' : ''}
        `}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf"
                    onChange={handleFileInputChange}
                    className="hidden"
                    disabled={isUploading}
                />

                <div className="flex flex-col items-center gap-4">
                    {/* Icon */}
                    <div className="rounded-full bg-blue-100 dark:bg-blue-900/30 p-4">
                        <svg className="h-12 w-12 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                        </svg>
                    </div>

                    {/* Text */}
                    <div>
                        <p className="text-lg font-medium text-gray-900 dark:text-white">
                            {isUploading ? 'Subiendo documento...' : 'Arrastra tu PDF aquí'}
                        </p>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            o haz clic para seleccionar un archivo
                        </p>
                        <p className="mt-2 text-xs text-gray-400 dark:text-gray-500">
                            Máximo {formatFileSize(MAX_FILE_SIZE)}
                        </p>
                    </div>

                    {/* Button */}
                    {!isUploading && (
                        <Button
                            variant="primary"
                            size="md"
                            onClick={handleClick}
                            type="button"
                        >
                            Seleccionar archivo
                        </Button>
                    )}
                </div>
            </div>

            {/* Error message */}
            {error && (
                <div className="mt-2 rounded-lg bg-red-50 dark:bg-red-900/20 p-3 text-sm text-red-600 dark:text-red-400">
                    {error}
                </div>
            )}
        </div>
    );
}
