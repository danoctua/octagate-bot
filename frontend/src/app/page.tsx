'use client';

import {List} from '@telegram-apps/telegram-ui';
import {useTranslations} from 'next-intl';

import {Page} from '@/components/Page';

import {TonConnectHeader} from "@/components/TonConnectHeader/TonConnectHeader";
import {useAuthAndFetchUser} from "@/hooks/useAuthAndFetchUser";

export default function Home() {
    const t = useTranslations('i18n');
    const user = useAuthAndFetchUser();

    return (
        <Page back={false}>
            <TonConnectHeader/>
            <List>
                <h1>{user?.firstName}</h1>
                <div>{user?.walletAddress}</div>
            </List>
        </Page>
    );
}
