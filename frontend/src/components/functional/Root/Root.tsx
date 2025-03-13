'use client';

import {useEffect, useState, type PropsWithChildren} from 'react';
import {
    miniApp,
    useLaunchParams,
    useSignal,
} from '@telegram-apps/sdk-react';
import {AppRoot, Snackbar} from '@telegram-apps/telegram-ui';

import {ErrorBoundary} from '@/components/layout/ErrorBoundary';
import {ErrorPage} from '@/components/layout/ErrorPage';
import {useDidMount} from '@/hooks/useDidMount';
import {useClientOnce} from '@/hooks/useClientOnce';
import {init} from '@/core/init';

import './styles.css';
import {useTelegramMock} from "@/hooks/useTelegramMock";
import {AlertTriangle} from "lucide-react";
import {AxiosError} from "axios";
import {errorEmitter} from '@/utils/apiClient';
import {TonConnectUIProvider} from "@tonconnect/ui-react";
import {usePathname} from "next/navigation";


interface ErrorResponseData {
    detail?: {
        error?: {
            message?: string;
        };
    } | string;
}


function RootInner({children}: PropsWithChildren) {
    const isDev = process.env.NODE_ENV === 'development';
    const [apiError, setApiError] = useState<string | undefined>(undefined);

    // Mock Telegram environment in development mode if needed.
    if (isDev) {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        useTelegramMock();
    }

    const lp = useLaunchParams();
    const debug = isDev || lp.startParam === 'debug';

    // Initialize the library.
    useClientOnce(() => {
        init(debug);
    });

    const isDark = useSignal(miniApp.isDark);

    useEffect(() => {
        const extractErrorMessage = (error: AxiosError): string => {
            if (!error.response || !error.response.data) {
                return 'Something went wrong';
            }

            const _error = error.response.data as ErrorResponseData;

            if (typeof _error.detail === "object" && _error.detail?.error?.message) {
                return _error.detail.error.message;
            } else if (
                typeof _error.detail === 'string'
            ) {
                return _error.detail;
            }
            return "Something went wrong"
        }

        const handleError = (error: AxiosError) => {
            if (!error.response) return;
            console.error('API error', error.response.status, error.response.data);
            setApiError(extractErrorMessage(error));
        };

        errorEmitter.on("apiError", handleError);

        return () => {
            errorEmitter.off("apiError", handleError);
        };
    }, []);

    return (
        <AppRoot
            appearance={isDark ? 'dark' : 'light'}
            platform={['macos', 'ios'].includes(lp.platform) ? 'ios' : 'base'}
        >
            {children}
            {
                apiError &&
                <Snackbar
                    before={<AlertTriangle/>}
                    duration={5000}
                    description={apiError}
                    onClose={() => setApiError(undefined)}
                >
                    An unexpected error occurred
                </Snackbar>
            }
        </AppRoot>
    );
}

export function Root(props: PropsWithChildren) {
    // Unfortunately, Telegram Mini Apps does not allow us to use all features of
    // the Server Side Rendering. That's why we are showing loader on the server
    // side.
    const didMount = useDidMount();
    const pathname = usePathname();

    return didMount ? (
        <ErrorBoundary fallback={ErrorPage}>
            {
                pathname === '/' ?
                    // Include the TonConnectUIProvider component to enable the TonConnect UI,
                    //  but only for the root page which is the gateway page
                    <TonConnectUIProvider manifestUrl="https://gate.essentis.xyz/tonconnect-manifest.json">
                        <RootInner {...props}/>
                    </TonConnectUIProvider> :
                    <RootInner {...props}/>
            }
        </ErrorBoundary>
    ) : <div className="root__loading">Loading...</div>;
}
