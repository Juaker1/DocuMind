/**
 * API related TypeScript types
 */

export interface ApiError {
    detail: string;
    status?: number;
}

export interface HealthCheckResponse {
    status: string;
    message: string;
    timestamp: string;
    database_connected?: boolean;
    ollama_available?: boolean;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    page_size: number;
}
