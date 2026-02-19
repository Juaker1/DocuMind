/**
 * Input component for text input
 */

'use client';

import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
    ({ label, error, fullWidth = false, className, ...props }, ref) => {
        return (
            <div className={cn('flex flex-col gap-1', fullWidth && 'w-full')}>
                {label && (
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300" htmlFor={props.id}>
                        {label}
                    </label>
                )}
                <input
                    ref={ref}
                    className={cn(
                        'rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-base transition-all',
                        'bg-white dark:bg-gray-700 text-gray-900 dark:text-white',
                        'placeholder:text-gray-400 dark:placeholder:text-gray-500',
                        'focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 dark:focus:ring-offset-gray-800',
                        'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-gray-50 dark:disabled:bg-gray-800',
                        error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
                        fullWidth && 'w-full',
                        className
                    )}
                    {...props}
                />
                {error && <span className="text-sm text-red-600 dark:text-red-400">{error}</span>}
            </div>
        );
    }
);

Input.displayName = 'Input';
