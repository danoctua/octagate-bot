import type { PropsWithChildren } from 'react';
import type { Metadata } from 'next';

import { Root } from '@/components/Root/Root';

import '@telegram-apps/telegram-ui/dist/styles.css';
import 'normalize.css/normalize.css';
import './_assets/globals.css';

export const metadata: Metadata = {
  title: 'Octagate',
  description: 'Your gate to the web3 world',
};

export default async function RootLayout({ children }: PropsWithChildren) {
  const locale = 'en';
  return (
    <html lang={locale}>
    <body style={{ paddingBottom: '120px' }}>
      <Root>
        {children}
      </Root>
    </body>
    </html>
  );
}
