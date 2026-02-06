/**
 * Custom hook for handling API errors
 */

import { useState, useCallback } from 'react';
import type { ApiError } from '@/types/api';

export function useApiError() {
    const [error, setError] = useState<ApiError | null>(null);

    const handleError = useCallback((err: unknown) => {
        if (typeof err === 'object' && err !== null && 'detail' in err) {
            setError(err as ApiError);
        } else if (err instanceof Error) {
            setError({ detail: err.message });
        } else {
            setError({ detail: 'Error desconocido' });
        }
    }, []);

    const clearError = useCallback(() => {
        setError(null);
    }, []);

    return { error, handleError, clearError };
}
