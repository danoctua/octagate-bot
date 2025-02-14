'use client';

import {
    Avatar,
    AvatarStack, Banner,
    Cell, FixedLayout,
    IconButton,
    List,
    Section
} from '@telegram-apps/telegram-ui';
import {useTranslations} from 'next-intl';

import {Page} from '@/components/Page';

import {TonConnectItem} from "@/components/TonConnectItem/TonConnectItem";
import {IUser, useAuthAndFetchUser} from "@/hooks/useAuthAndFetchUser";
import {useCallback, useEffect, useState} from 'react';
import apiClient from "@/utils/apiClient";
import {mainButton, openLink, openTelegramLink, useLaunchParams} from '@telegram-apps/sdk-react';
import {useClientOnce} from "@/hooks/useClientOnce";
import {Binary, Check, Coins, Plus} from "lucide-react";


interface IChat {
    id: number,
    username: string,
    title: string,
    slug: string,
    isForum: boolean,
    logoPath: string,
    joinUrl?: string,
    isMember: boolean,
}

interface IRule {
    category: string,
    title: string,
    promoteUrl: string,
    expected: number,
    actual?: number,
    photoUrl: string,
    isEligible: boolean,
}

interface IChatConfiguration {
    chat: IChat,
    rules: IRule[],
}

export default function Home() {
    const t = useTranslations('i18n');
    const [user, setUser] = useAuthAndFetchUser();
    const launchParams = useLaunchParams();
    const [chat, setChat] = useState<IChatConfiguration | null>(null);

    useClientOnce(() => {
        if (!launchParams.startParam) {
            return;
        }
        console.log("Mounting main button");
        mainButton.mount()
        mainButton.setParams({text: "Loading...", isEnabled: false, isVisible: true, isLoaderVisible: true, hasShineEffect: true});
        console.log(mainButton.state())
    })

    const fetchChatData = useCallback(async () => {
        return await apiClient.get(`/chats/${launchParams.startParam}`).then((response) => {
            return response.data;
        });
    }, [launchParams.startParam])

    useEffect(() => {
        if (!user || chat) { return; }
        fetchChatData().then((data) => {setChat(data)});
        console.log("Fetched chat data", launchParams.startParam);
    }, [chat, fetchChatData, launchParams.startParam, user])

    useEffect(() => {
        if (!chat) { return; }
        const chatJoinUrl = chat.chat.joinUrl;
        if (chatJoinUrl) {
            mainButton.setParams({isEnabled: true, isVisible: true, isLoaderVisible: false});
            if (chat.chat.isMember){
                mainButton.setParams({text: "Open chat", hasShineEffect: true});
            } else {
                mainButton.setParams({text: "Join chat", hasShineEffect: true});
            }
            mainButton.onClick(() => {
                openTelegramLink(chatJoinUrl);
            });
        } else {
            // Disable the button if no URL is provided
            mainButton.setParams({text: "No chat link", isEnabled: false, isVisible: true, isLoaderVisible: false});
            mainButton.onClick.isAvailable() && mainButton.onClick(() => {
            });
        }
        console.log("Updated main button", chat.chat.joinUrl);
    }, [chat])

    const setUserAndRefreshChatData = useCallback(async (user: IUser | undefined) => {
        setUser(user);
        setChat(null);
        await fetchChatData().then((data) => {setChat(data)});
    }, [fetchChatData, setUser])

    if (!user || !chat) {
        return <></>
    }

    const blockchainRules = [
        <TonConnectItem key={"connect-wallet"} user={user} setUser={setUserAndRefreshChatData}/>,
        ...chat.rules.map(
            (rule, index) => (
                <Cell
                    before={
                        rule.isEligible? <Check color={"green"}/>: rule.category === 'jetton' ? <Coins/>: <Binary/>
                    }
                    key={`blockchain-rule-${index}`}
                    readOnly
                    multiline={false}
                    disabled={!user.walletAddress}
                    subtitle={`${rule.actual || '?'}/${rule.expected}`}
                    after={
                        <IconButton
                            onClick={() => {
                                openLink(rule.promoteUrl);
                            }}
                        >
                            <Plus/>
                        </IconButton>
                    }
                >
                    {rule.title}
                </Cell>
            )
        )
    ]

    return (
        <Page back={false}>
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                padding: 42
            }}>
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
                <Section>
                    {blockchainRules}
                </Section>
            </List>
        </Page>
    );
}
