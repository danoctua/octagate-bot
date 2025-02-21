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
import React, {useCallback, useEffect, useMemo, useState} from 'react';
import {mainButton, openTelegramLink, secondaryButton, useLaunchParams} from '@telegram-apps/sdk-react';
import {useClientOnce} from "@/hooks/useClientOnce";
import {Check} from "lucide-react";
import useTonConnect from '@/hooks/useTonConnect';
import {Address} from "@ton/core";
import useChatData from '@/hooks/useChatData';
import Image from "next/image";
import {disconnectUserWallet, fetchTaskStatus, updateUserWallet} from "@/services";
import WalletFixedBottomItem from "@/components/WalletFixedBottomItem/WalletFixedBottomItem";
import GatewayHeader from "@/components/GatewayHeader/GatewayHeader";


export default function Home() {
    const {user, setUser, isUserDataLoading, setIsUserDataLoading} = useAuthAndFetchUser();
    const [asyncTaskId, setAsyncTaskId] = useState<string | null>(null);
    const launchParams = useLaunchParams();
    const {connectWallet, disconnectWallet, tonConnectUI} = useTonConnect();
    const {chat, fetchChatData, isChatDataLoading, setIsChatDataLoading} = useChatData();
    const [timeLeft, setTimeLeft] = useState<number>(0);
    const [isButtonDisabled, setIsButtonDisabled] = useState<boolean>(true);

    useEffect(() => {
        if (timeLeft > 0) {
            setIsButtonDisabled(true);
            const timerId = setTimeout(() => {
                setTimeLeft(timeLeft - 1);
            }, 1000);
            return () => clearTimeout(timerId);
        } else {
            setIsButtonDisabled(false);
        }
    }, [timeLeft]);

    useClientOnce(() => {
        if (!launchParams.startParam) {
            return;
        }
        console.debug("Mounting main button");
        mainButton.mount()
        secondaryButton.mount()
        mainButton.setParams({
            text: "Loading...",
            isEnabled: false,
            isVisible: true,
            isLoaderVisible: true,
            hasShineEffect: false
        });
        secondaryButton.setParams({
            text: "Refresh",
            isEnabled: false,
            isVisible: false,
            isLoaderVisible: false,
            hasShineEffect: false,
        })
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
        if (!asyncTaskId) {
            return;
        }
        fetchTaskStatus(asyncTaskId).then(
            () => {
                fetchChatData().then()
            }
        );
    }, [asyncTaskId, fetchChatData])

    const connectWalletAndRefresh = useCallback(async () => {

        await connectWallet();
        const handleConnectionCompleted = async () => {
            setIsChatDataLoading(true);
            setIsUserDataLoading(true);
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
                    setIsUserDataLoading(false);
                }
            ).catch(
                (error) => {
                    setIsUserDataLoading(false);
                    setIsChatDataLoading(false);
                    tonConnectUI.disconnect();
                    throw error;
                }
            );
        }
        window.addEventListener("ton-connect-connection-completed", handleConnectionCompleted, {once: true});

        return () => {
            window.removeEventListener("ton-connect-connection-completed", handleConnectionCompleted);
        };
    }, [connectWallet, setIsChatDataLoading, setIsUserDataLoading, setUser, tonConnectUI])

    useEffect(() => {
        if (!user || chat) {
            return;
        }
        console.log("Fetching chat data", user, chat);
        fetchChatData().then();
    }, [chat, fetchChatData, user])

    useEffect(() => {
        if (!mainButton.isMounted() || !secondaryButton.isMounted()) {
            return
        }

        if (!chat || !user) {
            // Main button handles this case
            return;
        }

        if (user.walletAddress && !chat.chat.isEligible) {
            let timeout = 0

            if (mainButton.isVisible()) {
                // If main button is visible, hide it and only then show secondary button
                mainButton.setParams({isVisible: false})
                timeout = 500;
            }

            const timerId = setTimeout(() => {
                console.log("Setting button to not eligible", mainButton.state());
                mainButton.setParams({isEnabled: false, isVisible: false})
                if (!secondaryButton.isMounted()) {
                    secondaryButton.mount()
                }
                secondaryButton.setParams(
                    {
                        isVisible: true,
                        isLoaderVisible: false,
                        isEnabled: !isButtonDisabled,
                        text: timeLeft ? `Refresh again in ${timeLeft}...` : "Refresh"
                    }
                )
                secondaryButton.onClick(() => {
                    console.log("Secondary button hit");
                    setTimeLeft(10)
                    fetchChatData().then();
                })
            }, timeout)
            return () => clearTimeout(timerId);
        }
    }, [chat, fetchChatData, isButtonDisabled, timeLeft, user]);

    useEffect(() => {
        if (!mainButton.isMounted() || !secondaryButton.isMounted()) {
            return;
        }

        secondaryButton.setParams({isVisible: false})

        if (!user || !chat) {
            console.log("Setting button to disabled");
            mainButton.setParams({isLoaderVisible: true, isVisible: true, isEnabled: false, text: "Loading..."});
            if (mainButton.offClick.isAvailable()) {
                mainButton.offClick(() => {
                });
            }
            return
        }

        if (user.walletAddress && !chat.chat.isEligible) {
            // Secondary button is handling this case
            return
        }

        let defaultParams = {isLoaderVisible: false, isVisible: true};

        if (user && !user.walletAddress) {
            console.log("Setting button to connect wallet");
            mainButton.setParams({
                ...defaultParams,
                text: "Connect wallet to join",
                isEnabled: true,
                hasShineEffect: true
            });
            if (mainButton.onClick.isAvailable()) {
                mainButton.offClick(() => {
                })
                mainButton.onClick(() => {
                    connectWalletAndRefresh().then();
                });
            }
            return
        }

        const chatJoinUrl = chat.chat.joinUrl;
        if (chatJoinUrl) {
            if (chat.chat.isMember) {
                console.log("Setting button to open chat");
                mainButton.setParams({...defaultParams, text: "Open", isEnabled: true, hasShineEffect: true});
            } else {
                console.log("Setting button to join chat");
                mainButton.setParams({...defaultParams, text: "Join", isEnabled: true, hasShineEffect: true});
            }
            if (mainButton.onClick.isAvailable()) {
                mainButton.offClick(() => {
                })
                mainButton.onClick(() => {
                    openTelegramLink(chatJoinUrl);
                });
            }
        } else {
            console.log("Setting button to no chat link");
            // Disable the button if no URL is provided
            if (mainButton.offClick.isAvailable()) {
                mainButton.offClick(() => {
                });
            }
            mainButton.setParams({...defaultParams, text: "No chat link"});
        }
    }, [chat, connectWalletAndRefresh, fetchChatData, isButtonDisabled, timeLeft, user])

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
        ...chat.rules.map(
            (rule, index) => (
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
                    {
                        ["jetton", "nft-collection"].includes(rule.category) ? `Hold ${rule.expected} ${rule.title}` : rule.title
                    }
                </Cell>
            )
        )
    ]

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
            {
                parsedWalletAddress &&
                <WalletFixedBottomItem
                    walletAddress={parsedWalletAddress}
                    disconnectWallet={disconnectWalletAndRefresh}
                />
            }
        </Page>
    );
}
