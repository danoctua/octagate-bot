'use client';

import {Avatar, AvatarStack, List} from '@telegram-apps/telegram-ui';
import {useTranslations} from 'next-intl';

import {Page} from '@/components/Page';

import {TonConnectHeader} from "@/components/TonConnectHeader/TonConnectHeader";
import {useAuthAndFetchUser} from "@/hooks/useAuthAndFetchUser";
import { useState } from 'react';
import apiClient from "@/utils/apiClient";
import { useLaunchParams } from '@telegram-apps/sdk-react';
import {useClientOnce} from "@/hooks/useClientOnce";
import {DisplayData} from "@/components/DisplayData/DisplayData";


interface IChat {
    id: number,
    username: string,
    title: string,
    slug: string,
    isForum: boolean,
    logoPath: string,
}

interface IRule {
    category: string,
    title: string,
    promoteUrl: string,
    expected: number,
    photoUrl: string,
}

interface IChatConfiguration {
    chat: IChat,
    rules: IRule[],
}

export default function Home() {
    const t = useTranslations('i18n');
    const [ user ] = useAuthAndFetchUser();
    const launchParams = useLaunchParams();
    const [ chat, setChat ] = useState<IChatConfiguration | null>(null);

    useClientOnce(() => {
        if (!launchParams.startParam) {
            return;
        }
        apiClient.get(`/chats/${launchParams.startParam}`).then((response) => {
            setChat(response.data);
        });
    })

    if (!chat) {
        return <></>
    }

    return (
        <Page back={false}>
            <TonConnectHeader/>
            <div style={{ display: 'flex', justifyContent: 'center', padding: '30px', flexDirection: 'column', alignItems: 'center' }}>
                <AvatarStack>
                    <Avatar
                      size={48}
                      src="https://avatars.githubusercontent.com/u/84640980?v=4"
                    />
                    <Avatar
                      size={48}
                      src="https://avatars.githubusercontent.com/u/84640980?v=4"
                    />
                    <Avatar
                      size={48}
                      src="https://avatars.githubusercontent.com/u/84640980?v=4"
                    />
                    <Avatar
                      size={48}
                      src="https://avatars.githubusercontent.com/u/84640980?v=4"
                    />
                </AvatarStack>
                <h2>Join {chat.chat.title}</h2>
            </div>
            <List>
                <DisplayData header={"Rules"} rows={
                    chat.rules.map((rule) => ({title: rule.title, value: `0/${rule.expected}`})) || []
                }>
                </DisplayData>
            </List>
        </Page>
    );
}
