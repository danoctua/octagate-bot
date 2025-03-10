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
import {mainButton, secondaryButton, useLaunchParams} from '@telegram-apps/sdk-react';
import {Check} from "lucide-react";
import useTonConnect from '@/hooks/useTonConnect';
import {Address} from "@ton/core";
import useChatData from '@/hooks/data/useChatData';
import Image from "next/image";
import {disconnectUserWallet, fetchTaskStatus, updateUserWallet} from "@/services";
import ConnectedWalletCell from "@/components/ConnectedWalletCell/ConnectedWalletCell";
import ChatHeader from "@/components/ChatHeader/ChatHeader";
import FixedBottomSection, {ButtonStateProps} from "@/components/FixedBottomSection/FixedBottomSection";
import useMainButtonState from "@/hooks/useMainButtonState";
import {useClientOnce} from "@/hooks/useClientOnce";
import DisplayRuleItem from "@/components/Rule/DisplayRuleItem/DisplayRuleItem";

export default function Home() {
    const {user, setUser, isUserDataLoading, setIsUserDataLoading} = useAuthAndFetchUser();
    const [asyncTaskId, setAsyncTaskId] = useState<string | null>(null);
    const launchParams = useLaunchParams();
    const {connectWallet, disconnectWallet, tonConnectUI} = useTonConnect();
    const {chat, fetchChatData, isChatDataLoading, setIsChatDataLoading} = useChatData(launchParams.startParam);
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

    useClientOnce(() => {
        mainButton.mount();
        mainButton.setParams({isVisible: false});
        mainButton.unmount()
        secondaryButton.mount();
        secondaryButton.setParams({isVisible: false});
        secondaryButton.unmount()
    })

    const mainButtonState: ButtonStateProps | undefined = useMainButtonState(
        isUserDataLoading,
        isChatDataLoading,
        launchParams.startParam,
        user,
        chat?.chat,
        connectWalletAndRefresh,
        fetchChatData
    )

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
                isUserDataLoading ?
                    <Spinner size="s"/> :
                    parsedWalletAddress ?
                        <Check style={{color: "var(--tg-theme-accent-text-color)"}}/> :
                        <Text style={{color: "var(--tg-theme-subtitle-text-color)"}}>
                            Not yet
                        </Text>
            }
        >
            Connect wallet
        </Cell>,
        ...chat.rules.map((rule, index) => (
            <DisplayRuleItem
                key={`blockchain-rule-${index}`}
                rule={rule}
                readOnly
            />
        ))
    ];

    return (
        <Page back={false}>
            <ChatHeader chat={chat.chat}/>
            <div>
                <List>
                    <Section>
                        {blockchainRules}
                    </Section>
                </List>
            </div>
            {mainButtonState &&
                <FixedBottomSection {...mainButtonState}>
                    {parsedWalletAddress &&
                        <ConnectedWalletCell
                            walletAddress={parsedWalletAddress}
                            disconnectWallet={disconnectWalletAndRefresh}
                        />
                    }
                </FixedBottomSection>
            }
        </Page>
    );
}
