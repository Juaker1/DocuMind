/**
 * Container component for consistent page layout
 */

import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface ContainerProps extends HTMLAttributes<HTMLDivElement> {
    size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

const sizeClasses = {
    sm: 'max-w-3xl',
    md: 'max-w-5xl',
    lg: 'max-w-7xl',
    xl: 'max-w-screen-2xl',
    full: 'max-w-full',
};

export const Container = forwardRef<HTMLDivElement, ContainerProps>(
    ({ size = 'lg', className, children, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn('mx-auto w-full px-4 sm:px-6 lg:px-8', sizeClasses[size], className)}
                {...props}
            >
                {children}
            </div>
        );
    }
);

Container.displayName = 'Container';
