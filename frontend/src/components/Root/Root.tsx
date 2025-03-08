'use client';

import {useEffect, useState, type PropsWithChildren} from 'react';
import {
    miniApp,
    useLaunchParams,
    useSignal,
} from '@telegram-apps/sdk-react';
import {TonConnectUIProvider} from '@tonconnect/ui-react';
import {AppRoot, Snackbar} from '@telegram-apps/telegram-ui';

import {ErrorBoundary} from '@/components/ErrorBoundary';
import {ErrorPage} from '@/components/ErrorPage';
import {useDidMount} from '@/hooks/useDidMount';
import {useClientOnce} from '@/hooks/useClientOnce';
import {init} from '@/core/init';

import './styles.css';
import {useTelegramMock} from "@/hooks/useTelegramMock";
import {AlertTriangle} from "lucide-react";
import {AxiosError} from "axios";
import { errorEmitter } from '@/utils/apiClient';


interface ErrorResponseData {
  detail?: {
    error?: {
      message?: string;
    };
  };
}


function RootInner({children}: PropsWithChildren) {
    const isDev = process.env.NODE_ENV === 'development';
    const [apiError, setApiError] = useState<AxiosError | undefined>(undefined);

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
        const handleError = (error: AxiosError) => {
            if (!error.response) return;
            console.error('API error', error.response.status, error.response.data);
            setApiError(error);
        };

        errorEmitter.on("apiError", handleError);

        return () => {
            errorEmitter.off("apiError", handleError);
        };
    }, []);

    return (
        <TonConnectUIProvider manifestUrl="https://gate.essentis.xyz/tonconnect-manifest.json">
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
                        description={(apiError.response?.data as ErrorResponseData)?.detail?.error?.message || 'Something went wrong'}
                        onClose={() => setApiError(undefined)}
                    >
                        An unexpected error occurred
                    </Snackbar>
                }
            </AppRoot>
        </TonConnectUIProvider>
    );
}

export function Root(props: PropsWithChildren) {
    // Unfortunately, Telegram Mini Apps does not allow us to use all features of
    // the Server Side Rendering. That's why we are showing loader on the server
    // side.
    const didMount = useDidMount();

    return didMount ? (
        <ErrorBoundary fallback={ErrorPage}>
            <RootInner {...props}/>
        </ErrorBoundary>
    ) : <div className="root__loading">Loading...</div>;
}
