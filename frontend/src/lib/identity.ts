/**
 * Identity management utilities.
 * Handles both anonymous UUID sessions and registered JWT tokens.
 */

const UUID_KEY = 'documind_uuid';
const TOKEN_KEY = 'documind_token';
const REFRESH_TOKEN_KEY = 'documind_refresh_token';

/**
 * Gets or creates a persistent anonymous UUID for this browser.
 * Used as X-User-UUID header for all unauthenticated requests.
 */
export function getOrCreateUUID(): string {
    if (typeof window === 'undefined') return 'ssr-placeholder';
    let uuid = localStorage.getItem(UUID_KEY);
    if (!uuid) {
        uuid = crypto.randomUUID();
        localStorage.setItem(UUID_KEY, uuid);
    }
    return uuid;
}

/**
 * Returns the stored access JWT token, or null if not logged in.
 */
export function getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Stores an access JWT token (on login / register).
 */
export function setAuthToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Removes the access JWT token (on logout).
 */
export function clearAuthToken(): void {
    localStorage.removeItem(TOKEN_KEY);
}

/**
 * Returns the stored refresh token, or null if not present.
 */
export function getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Stores a refresh token (on login / register / token rotation).
 */
export function setRefreshToken(token: string): void {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

/**
 * Removes the refresh token (on logout or session expiry).
 */
export function clearRefreshToken(): void {
    localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * Removes both tokens — convenience function for full logout.
 */
export function clearAllTokens(): void {
    clearAuthToken();
    clearRefreshToken();
}

/**
 * Returns true when the user has a valid JWT (i.e. is registered/logged in).
 */
export function isAuthenticated(): boolean {
    return getAuthToken() !== null;
}
