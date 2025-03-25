'use client';

import {
    Cell,
    Info,
    Placeholder,
    Section,
    Spinner,
    Text,
} from '@telegram-apps/telegram-ui';

import {Page} from '@/components/layout/Page';

import useAuthAndFetchUser from "@/hooks/data/useAuthAndFetchUser";
import React, {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import {mainButton, secondaryButton, useLaunchParams} from '@telegram-apps/sdk-react';
import {Check} from "lucide-react";
import useTonConnect from '@/hooks/useTonConnect';
import {Address} from "@ton/core";
import useChatData from '@/hooks/data/useChatData';
import Image from "next/image";
import {disconnectUserWallet, fetchTaskStatus, updateUserWallet} from "@/services";
import ConnectedWalletCell from "@/components/layout/ConnectedWalletCell/ConnectedWalletCell";
import ChatHeader from "@/components/layout/ChatHeader/ChatHeader";
import FixedBottomSection, {
    ButtonStateProps,
    FixedBottomButton
} from "@/components/ui/FixedBottomSection/FixedBottomSection";
import useMainButtonState from "@/hooks/useMainButtonState";
import {useClientOnce} from "@/hooks/useClientOnce";
import DisplayRuleItem from "@/components/layout/Rule/DisplayRuleItem/DisplayRuleItem";

export default function Home() {
    const {user, setUser, isUserDataLoading} = useAuthAndFetchUser();
    const [asyncTaskId, setAsyncTaskId] = useState<string | null>(null);
    const launchParams = useLaunchParams();
    const {connectWallet, disconnectWallet, tonConnectUI} = useTonConnect();
    const {chat, fetchChatData, isChatDataLoading} = useChatData(launchParams.startParam);
    const onWalletConnectListenerAdded = useRef(false)

    const connectWalletAndRefresh = useCallback(async () => {
        await connectWallet();
        const handleConnectionCompleted = async () => {
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
            }).catch((error) => {
                tonConnectUI.disconnect();
                throw error;
            })
        };

        if (!onWalletConnectListenerAdded.current) {
            window.addEventListener("ton-connect-connection-completed", handleConnectionCompleted, {once: true});
            onWalletConnectListenerAdded.current = true;
        }

        return () => {
            window.removeEventListener("ton-connect-connection-completed", handleConnectionCompleted);
            onWalletConnectListenerAdded.current = false;
        };
    }, [connectWallet, setUser, tonConnectUI]);

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
        <Page
            increasedBottomSpace
            back={false}
            fixedBottom={mainButtonState &&
                <FixedBottomSection
                    button={<FixedBottomButton {...mainButtonState}/>}
                >
                    {parsedWalletAddress &&
                        <ConnectedWalletCell
                            walletAddress={parsedWalletAddress}
                            disconnectWallet={disconnectWalletAndRefresh}
                        />
                    }
                </FixedBottomSection>
            }
        >
            <ChatHeader chat={chat.chat}>
                {chat.chat.description &&
                    <Info type={"avatarStack"}>{chat.chat.description}</Info>
                }
            </ChatHeader>
            <Section>
                {blockchainRules}
            </Section>
        </Page>
    );
}
