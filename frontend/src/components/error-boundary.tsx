"use client";

import { AlertTriangle, RefreshCw } from "lucide-react";
import { Component, type ReactNode } from "react";

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, info: React.ErrorInfo) {
        console.error("ErrorBoundary caught:", error, info);
    }

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) return this.props.fallback;

            return (
                <div className="flex min-h-[400px] items-center justify-center">
                    <div className="card max-w-md p-8 text-center">
                        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-danger-light">
                            <AlertTriangle className="h-6 w-6 text-danger" />
                        </div>
                        <h2 className="text-lg font-semibold text-text">Something went wrong</h2>
                        <p className="mt-2 text-sm text-muted">
                            {this.state.error?.message || "An unexpected error occurred."}
                        </p>
                        <button
                            onClick={() => this.setState({ hasError: false, error: undefined })}
                            className="btn btn-primary btn-sm mt-4"
                        >
                            <RefreshCw className="h-4 w-4" /> Try Again
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
