/**
 * Application-wide constants
 */

export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || 'DocuMind';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export const ALLOWED_FILE_TYPES = ['application/pdf'];

/** Debe mantenerse en sincón con MAX_MESSAGE_LENGTH en conversation_dto.py */
export const MAX_MESSAGE_LENGTH = 4000;

export const MESSAGES_PER_PAGE = 50;

export const DEBOUNCE_DELAY = 300; // ms

export const ROUTES = {
    HOME: '/',
    DOCUMENTS: '/documents',
    CHAT: (documentId: number | string) => `/chat/${documentId}`,
} as const;
