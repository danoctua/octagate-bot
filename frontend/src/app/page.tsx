'use client';

import {
    Avatar,
    AvatarStack,
    Cell,
    Headline,
    IconButton,
    List,
    Section
} from '@telegram-apps/telegram-ui';

import {Page} from '@/components/Page';

import TonConnectItem from "@/components/TonConnectItem/TonConnectItem";
import useAuthAndFetchUser from "@/hooks/useAuthAndFetchUser";
import React, {useCallback, useEffect, useMemo} from 'react';
import apiClient from "@/utils/apiClient";
import {mainButton, openLink, openTelegramLink, useLaunchParams} from '@telegram-apps/sdk-react';
import {useClientOnce} from "@/hooks/useClientOnce";
import {Binary, Check, Coins, Plus} from "lucide-react";
import useTonConnect from '@/hooks/useTonConnect';
import {Address} from "@ton/core";
import useChatData from '@/hooks/useChatData';


export default function Home() {
    const [user, setUser] = useAuthAndFetchUser();
    const launchParams = useLaunchParams();
    const { connectWallet , disconnectWallet, tonConnectUI } = useTonConnect();
    const { chat, fetchChatData } = useChatData();

    useClientOnce(() => {
        if (!launchParams.startParam) {
            return;
        }
        console.debug("Mounting main button");
        mainButton.mount()
        mainButton.setParams({text: "Loading...", isEnabled: false, isVisible: true, isLoaderVisible: true, hasShineEffect: true});
    })

    const fetchWalletData = useCallback(async () => {
        return await apiClient.post("/users/wallet", {
            walletAddress: tonConnectUI.wallet?.account.address,
            tonProof: (tonConnectUI.wallet?.connectItems?.tonProof as any)?.proof,
            publicKey: tonConnectUI.wallet?.account.publicKey,
        }).then(response => response.data)
    }, [tonConnectUI.wallet])

    const disconnectWalletAndRefresh = useCallback(async () => {
        await disconnectWallet();
        if (user?.walletAddress) {
            // Send request to backend to delete wallet
            await apiClient.delete("/users/wallet").then((response) => {
                console.debug("Setting user on wallet disconnect", response.data);
                setUser(response.data);
            });
            await fetchChatData()
        }
    }, [disconnectWallet, fetchChatData, setUser, user?.walletAddress])

    const connectWalletAndRefresh = useCallback(async () => {
        await connectWallet();
        const handleConnectionCompleted = async () => {
            console.debug("connection-completed");
            await fetchWalletData().then(
                (data) => {
                    console.debug("Setting user on wallet connect", data);
                    setUser(data);
                }
            ).catch(
                (error) => {
                    tonConnectUI.disconnect();
                    throw error;
                }
            );
            await fetchChatData();

        }
        window.addEventListener("ton-connect-connection-completed", handleConnectionCompleted, {once: true});

        return () => {
            window.removeEventListener("ton-connect-connection-completed", handleConnectionCompleted);
        };
    }, [connectWallet, fetchChatData, fetchWalletData, setUser, tonConnectUI])

    useEffect(() => {
        if (!user || chat) { return; }
        fetchChatData().then();
    }, [chat, fetchChatData, user])

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
            mainButton.setParams(
                {
                    text: "No chat link",
                    isEnabled: false,
                    isVisible: true,
                    isLoaderVisible: false,
                    hasShineEffect: false
                }
            );
            mainButton.onClick.isAvailable() && mainButton.onClick(() => {});
        }
        console.debug("Updated main button", chatJoinUrl, chat.chat.joinUrl);
    }, [chat])

    const parsedWalletAddress = useMemo(() => (
        user?.walletAddress ?
        Address.parse(user?.walletAddress).toString({bounceable: false}):
        null
    ), [user?.walletAddress])

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
                        rule.isEligible? <Check color={"green"}/>: rule.category === 'jetton' ? <Coins/>: <Binary/>
                    }
                    key={`blockchain-rule-${index}`}
                    readOnly
                    multiline={false}
                    disabled={!user.walletAddress}
                    subtitle={`${rule.actual || '?'}/${rule.expected}`}
                    after={
                        <IconButton onClick={() => {openLink(rule.promoteUrl)}}><Plus/></IconButton>
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
