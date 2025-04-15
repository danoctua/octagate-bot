import * as Sentry from '@sentry/nextjs';

export async function register() {
  Sentry.init({
    dsn: process.env.NEXT_PUBLIC_SENTRY_DNS,
    environment: process.env.NODE_ENV,
    tracesSampleRate: 1,
    debug: false,
  });
}

export const onRequestError = Sentry.captureRequestError;
