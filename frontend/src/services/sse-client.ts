/**
 * Server-Sent Events (SSE) client for real-time streaming
 * Used for chat message streaming from the backend
 */

export interface SSECompletionData {
    conversation_id: number;
    message_id: number;
    cited_pages: number[];
    cited_snippets: { page: number; text: string }[];
}

export interface SSEOptions {
    /**
     * Callback when a message chunk is received
     */
    onMessage: (data: string) => void;

    /**
     * Callback when an error occurs
     */
    onError?: (error: Event) => void;

    /**
     * Callback when streaming is complete — receives conversation metadata
     */
    onComplete?: (data: SSECompletionData) => void;

    /**
     * Callback when connection is opened
     */
    onOpen?: () => void;
}


/**
 * SSE Client for handling streaming connections
 */
export class SSEClient {
    private eventSource: EventSource | null = null;
    private url: string = '';

    /**
     * Connect to SSE endpoint and start listening for messages
     */
    connect(url: string, options: SSEOptions): void {
        this.url = url;

        try {
            this.eventSource = new EventSource(url);

            // Connection opened
            this.eventSource.onopen = () => {
                console.log('🔗 SSE Connection opened:', url);
                options.onOpen?.();
            };

            // Message received
            this.eventSource.onmessage = (event: MessageEvent) => {
                // Parse data
                try {
                    const data = JSON.parse(event.data);

                    // Check for completion signal
                    if (data.done === true) {
                        console.log('✅ SSE Stream complete', data);
                        options.onComplete?.({
                            conversation_id: data.conversation_id,
                            message_id: data.message_id,
                            cited_pages: data.cited_pages ?? [],
                            cited_snippets: data.cited_snippets ?? [],
                        });
                        this.close();
                        return;
                    }

                    // Check for error
                    if (data.error) {
                        console.error('❌ SSE Error from server:', data.error);
                        options.onError?.(new Event('error'));
                        this.close();
                        return;
                    }

                    // Pass chunk to callback
                    if (data.chunk) {
                        options.onMessage(data.chunk);
                    }
                } catch (e) {
                    // Fallback: check for [DONE] string
                    if (event.data === '[DONE]') {
                        console.log('✅ SSE Stream complete (fallback)');
                        options.onComplete?.({
                            conversation_id: 0,
                            message_id: 0,
                            cited_pages: [],
                            cited_snippets: [],
                        });
                        this.close();
                        return;
                    }

                    // Pass raw data if not JSON
                    options.onMessage(event.data);
                }
            };

            // Error occurred
            this.eventSource.onerror = (error: Event) => {
                console.error('❌ SSE Error:', error);
                options.onError?.(error);
                this.close();
            };

        } catch (error) {
            console.error('❌ Failed to create EventSource:', error);
            options.onError?.(error as Event);
        }
    }

    /**
     * Close the SSE connection
     */
    close(): void {
        if (this.eventSource) {
            console.log('🔌 Closing SSE connection');
            this.eventSource.close();
            this.eventSource = null;
        }
    }

    /**
     * Check if connection is active
     */
    isConnected(): boolean {
        return this.eventSource !== null && this.eventSource.readyState === EventSource.OPEN;
    }

    /**
     * Get current connection state
     */
    getReadyState(): number {
        return this.eventSource?.readyState ?? EventSource.CLOSED;
    }
}

/**
 * Create and connect a new SSE client
 */
export function createSSEClient(url: string, options: SSEOptions): SSEClient {
    const client = new SSEClient();
    client.connect(url, options);
    return client;
}
