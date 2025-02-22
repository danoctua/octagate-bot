'use client';

import {
    Cell,
    List,
    Placeholder,
    Section,
    Spinner,
    Text,
} from '@telegram-apps/telegram-ui';

import {Page} from '@/components/Page';

import useAuthAndFetchUser from "@/hooks/useAuthAndFetchUser";
import React, {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import {useLaunchParams} from '@telegram-apps/sdk-react';
import {Check} from "lucide-react";
import useTonConnect from '@/hooks/useTonConnect';
import {Address} from "@ton/core";
import useChatData from '@/hooks/useChatData';
import Image from "next/image";
import {disconnectUserWallet, fetchTaskStatus, updateUserWallet} from "@/services";
import WalletFixedBottomItem from "@/components/WalletFixedBottomItem/WalletFixedBottomItem";
import GatewayHeader from "@/components/GatewayHeader/GatewayHeader";
import useMainButton from '@/hooks/useMainButton';
import useSecondaryButton from '@/hooks/useSecondaryButton';

export default function Home() {
    const {user, setUser, isUserDataLoading, setIsUserDataLoading} = useAuthAndFetchUser();
    const [asyncTaskId, setAsyncTaskId] = useState<string | null>(null);
    const launchParams = useLaunchParams();
    const {connectWallet, disconnectWallet, tonConnectUI} = useTonConnect();
    const {chat, fetchChatData, isChatDataLoading, setIsChatDataLoading} = useChatData();
    const onWalletConnectListenerAdded = useRef(false)


    const connectWalletAndRefresh = useCallback(async () => {
        await connectWallet();
        const handleConnectionCompleted = async () => {
            setIsChatDataLoading(true);
            setIsUserDataLoading(true);
            if (!tonConnectUI.wallet) {
                return;
            }

            await updateUserWallet(
                tonConnectUI.wallet.account.address,
                (tonConnectUI.wallet.connectItems?.tonProof as any)?.proof,
                tonConnectUI.wallet.account.publicKey
            ).then((data) => {
                setUser(data.user);
                setAsyncTaskId(data.taskId);
                setIsUserDataLoading(false);
            }).catch((error) => {
                setIsUserDataLoading(false);
                setIsChatDataLoading(false);
                tonConnectUI.disconnect();
                throw error;
            });
        };

        if (!onWalletConnectListenerAdded.current) {
            window.addEventListener("ton-connect-connection-completed", handleConnectionCompleted, {once: true});
            onWalletConnectListenerAdded.current = true;
        }

        return () => {
            window.removeEventListener("ton-connect-connection-completed", handleConnectionCompleted);
            onWalletConnectListenerAdded.current = false;
        };
    }, [connectWallet, setIsChatDataLoading, setIsUserDataLoading, setUser, tonConnectUI]);

    useMainButton(user, chat?.chat, launchParams.startParam, connectWalletAndRefresh);
    useSecondaryButton(user, chat?.chat, fetchChatData);

    const disconnectWalletAndRefresh = useCallback(async () => {
        await disconnectWallet();
        if (user?.walletAddress) {
            await disconnectUserWallet().then((data) => {
                console.debug("Setting user on wallet disconnect", data);
                setUser(data);
            });
            await fetchChatData();
        }
    }, [disconnectWallet, fetchChatData, setUser, user?.walletAddress]);

    useEffect(() => {
        if (!asyncTaskId) {
            return;
        }
        fetchTaskStatus(asyncTaskId).then(() => {
            setAsyncTaskId(null);
            fetchChatData().then();
        });
    }, [asyncTaskId, fetchChatData]);


    useEffect(() => {
        if (!user || chat) {
            return;
        }
        fetchChatData().then();
    }, [chat, fetchChatData, user]);

    const parsedWalletAddress = useMemo(() => (
        user?.walletAddress ? Address.parse(user?.walletAddress).toString({bounceable: false}) : null
    ), [user?.walletAddress]);

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
        </div>;
    }

    if (!user || !chat) {
        return <></>;
    }

    const blockchainRules = [
        <Cell
            key={"wallet"}
            readOnly
            after={
                isUserDataLoading ? <Spinner size="s"/> : parsedWalletAddress ? <Check/> :
                    <Text style={{color: "var(--tg-theme-subtitle-text-color)"}}>Not yet</Text>
            }
        >
            Connect wallet
        </Cell>,
        ...chat.rules.map((rule, index) => (
            <Cell
                key={`blockchain-rule-${index}`}
                readOnly
                multiline={false}
                disabled={!user.walletAddress}
                after={
                    isChatDataLoading ? <Spinner size="s"/> : rule.isEligible ? <Check/> :
                        <Text style={{color: "var(--tg-theme-subtitle-text-color)"}}>Not yet</Text>
                }
            >
                {["jetton", "nft-collection"].includes(rule.category) ? `Hold ${rule.expected} ${rule.title}` : rule.title}
            </Cell>
        ))
    ];

    return (
        <Page back={false}>
            <GatewayHeader chat={chat.chat}/>
            <div>
                <List>
                    <Section>
                        {blockchainRules}
                    </Section>
                </List>
            </div>
            {parsedWalletAddress && (
                <WalletFixedBottomItem
                    walletAddress={parsedWalletAddress}
                    disconnectWallet={disconnectWalletAndRefresh}
                />
            )}
        </Page>
    );
}