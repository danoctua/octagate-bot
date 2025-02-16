'use client';

import {
    Avatar,
    AvatarStack,
    Cell,
    IconButton,
    List,
    Placeholder,
    Section
} from '@telegram-apps/telegram-ui';

import {Page} from '@/components/Page';

import TonConnectItem from "@/components/TonConnectItem/TonConnectItem";
import useAuthAndFetchUser from "@/hooks/useAuthAndFetchUser";
import React, {useCallback, useEffect, useMemo, useState} from 'react';
import {mainButton, openLink, openTelegramLink, useLaunchParams} from '@telegram-apps/sdk-react';
import {useClientOnce} from "@/hooks/useClientOnce";
import {Binary, Check, Coins, Plus} from "lucide-react";
import useTonConnect from '@/hooks/useTonConnect';
import {Address} from "@ton/core";
import useChatData from '@/hooks/useChatData';
import Image from "next/image";
import {disconnectUserWallet, fetchTaskStatus, updateUserWallet} from "@/services";


export default function Home() {
    const [user, setUser] = useAuthAndFetchUser();
    const [ asyncTaskId, setAsyncTaskId ] = useState<string | null>(null);
    const launchParams = useLaunchParams();
    const {connectWallet, disconnectWallet, tonConnectUI} = useTonConnect();
    const {chat, fetchChatData} = useChatData();

    useClientOnce(() => {
        if (!launchParams.startParam) {
            return;
        }
        console.debug("Mounting main button");
        mainButton.mount()
        mainButton.setParams({
            text: "Loading...",
            isEnabled: false,
            isVisible: true,
            isLoaderVisible: true,
            hasShineEffect: false
        });
    })

    const disconnectWalletAndRefresh = useCallback(async () => {
        await disconnectWallet();
        if (user?.walletAddress) {
            // Send request to backend to delete wallet
            await disconnectUserWallet().then((data) => {
                console.debug("Setting user on wallet disconnect", data);
                setUser(data);
            });
            await fetchChatData()
        }
    }, [disconnectWallet, fetchChatData, setUser, user?.walletAddress])

    useEffect(() => {
        if (!asyncTaskId) { return; }
        fetchTaskStatus(asyncTaskId).then(
            () => {
                fetchChatData().then()
            }
        );
    }, [asyncTaskId, fetchChatData])

    const connectWalletAndRefresh = useCallback(async () => {
        await connectWallet();
        const handleConnectionCompleted = async () => {
            console.debug("connection-completed");
            if (!tonConnectUI.wallet) {
                console.error("No wallet connected");
                return;
            }

            await updateUserWallet(
                tonConnectUI.wallet.account.address,
                (tonConnectUI.wallet.connectItems?.tonProof as any)?.proof,
                tonConnectUI.wallet.account.publicKey
            ).then(
                (data) => {
                    console.debug("Setting user on wallet connect", data);
                    setUser(data.user);
                    setAsyncTaskId(data.taskId);
                }
            ).catch(
                (error) => {
                    tonConnectUI.disconnect();
                    throw error;
                }
            );
        }
        window.addEventListener("ton-connect-connection-completed", handleConnectionCompleted, {once: true});

        return () => {
            window.removeEventListener("ton-connect-connection-completed", handleConnectionCompleted);
        };
    }, [connectWallet, setUser, tonConnectUI])

    useEffect(() => {
        if (!user || chat) {
            return;
        }
        fetchChatData().then();
    }, [chat, fetchChatData, user])

    useEffect(() => {
        if (!mainButton.isMounted()) {
            return;
        }
        console.log("Is eligible", chat?.chat.isEligible, chat);
        if (!chat) {
            console.log("Setting button to disabled");
            mainButton.setParams({isLoaderVisible: false, isVisible: true, isEnabled: false, text: "Loading..."});
            if (mainButton.offClick.isAvailable()) {
                mainButton.offClick(() => {});
            }
            return;
        }

        let defaultParams = {isLoaderVisible: false, isVisible: true};

        if (!chat.chat.isEligible) {
            console.log("Setting button to not eligible");
            mainButton.setParams({...defaultParams, isEnabled: false, text: "Not eligible",});
            if (mainButton.offClick.isAvailable()) {
                mainButton.offClick(() => {});
            }
            return;
        }

        const chatJoinUrl = chat.chat.joinUrl;
        if (chatJoinUrl) {
            if (chat.chat.isMember) {
                console.log("Setting button to open chat");
                mainButton.setParams({...defaultParams, text: "Open chat", isEnabled: true, hasShineEffect: true});
            } else {
                console.log("Setting button to join chat");
                mainButton.setParams({...defaultParams, text: "Join chat", isEnabled: true, hasShineEffect: true});
            }
            console.log("Setting button click handler");
            if (mainButton.onClick.isAvailable()) {
                mainButton.onClick(() => {
                    openTelegramLink(chatJoinUrl);
                });
            }
        } else {
            // Disable the button if no URL is provided
            if (mainButton.offClick.isAvailable()) {
                mainButton.offClick(() => {});
            }
            mainButton.setParams({...defaultParams, text: "No chat link"});
        }
    }, [chat])

    const parsedWalletAddress = useMemo(() => (
        user?.walletAddress ?
            Address.parse(user?.walletAddress).toString({bounceable: false}) :
            null
    ), [user?.walletAddress])

    if (!launchParams.startParam) {
        return <div>
            <Placeholder
                description="Please, try again, we don't have chats gallery yet"
                header="You got lost"
            >
                <Image
                    alt="Lost bananas"
                    src="/telegram.gif"
                    width={150}
                    height={150}
                />
            </Placeholder>
        </div>
    }

    if (!user || !chat) {
        return <></>
    }

    const blockchainRules = [
        <TonConnectItem
            key={"connect-wallet"}
            walletAddress={parsedWalletAddress}
            disconnectWallet={disconnectWalletAndRefresh}
            connectWallet={connectWalletAndRefresh}
        />,
        ...chat.rules.map(
            (rule, index) => (
                <Cell
                    before={
                        rule.isEligible ? <Check color={"green"}/> : rule.category === 'jetton' ? <Coins/> : <Binary/>
                    }
                    key={`blockchain-rule-${index}`}
                    readOnly
                    multiline={false}
                    disabled={!user.walletAddress}
                    subtitle={`${rule.actual ?? '?'}/${rule.expected}`}
                    after={
                        <IconButton onClick={() => {
                            openLink(rule.promoteUrl)
                        }}><Plus/></IconButton>
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
                padding: 32,
                paddingTop: 48,
            }}>
                <AvatarStack>
                    <Avatar
                        size={48}
                        src="https://t.me/i/userpic/160/takoy_sasha.jpg"
                    />
                    <Avatar
                        size={48}
                        src="https://t.me/i/userpic/160/danoctua.jpg"
                    />
                    <Avatar
                        size={48}
                        src="https://t.me/i/userpic/160/chak_zefir.jpg"
                    />
                    <Avatar
                        size={48}
                        src="https://t.me/i/userpic/160/durov.jpg"
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
