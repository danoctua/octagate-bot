import {useEffect, useCallback, useRef} from 'react';
import {mainButton, openTelegramLink} from '@telegram-apps/sdk-react';
import {IChat, IUser} from '@/interfaces';
import {useClientOnce} from "@/hooks/useClientOnce";


const useMainButton = (
    user: IUser | undefined,
    chat: IChat | undefined,
    startParam: string | undefined,
    connectWallet: () => Promise<() => void>
) => {
    const isListenerAdded = useRef(false)
    const userRef = useRef(user);
    const chatRef = useRef(chat);

    useClientOnce(() => {
        mainButton.mount();
        mainButton.setParams({
            text: "Loading...",
            isEnabled: false,
            isVisible: true,
            isLoaderVisible: true,
            hasShineEffect: false
        });
    })

    useEffect(() => {
        userRef.current = user;
        chatRef.current = chat;
    }, [chat, connectWallet, user]);

    const mainButtonOnClickListener = useCallback(() => {
        console.log("Main button on click", connectWallet)
        const currentUser = userRef.current;
        const currentChat = chatRef.current;
        if (!currentUser || !currentChat) {
            return;
        } else if (currentUser.walletAddress && !currentChat.isEligible) {
            // Secondary button is handling this case
            return;
        } else if (currentUser && !currentUser.walletAddress) {
            connectWallet().then();
        } else if (currentChat.joinUrl) {
            openTelegramLink(currentChat.joinUrl);
        } else {
            console.log("Unknown state", currentUser, currentChat);
        }
    }, [connectWallet]);

    useEffect(() => {
        if (!mainButton.isMounted()) {
            return;
        }

        if (!startParam) {
            // Don't show the button if there is no start param
            mainButton.setParams({
                isVisible: false
            })
            return
        }

        if (mainButton.onClick.isAvailable()) {
            if (!isListenerAdded.current) {
                mainButton.onClick(mainButtonOnClickListener);
                isListenerAdded.current = true;
            }
        }

        if (!user || !chat) {
            mainButton.setParams({isLoaderVisible: true, isVisible: true, isEnabled: false, text: "Loading..."});
            return;
        }

        let defaultParams = {isLoaderVisible: false, isVisible: true};

        if (user && !user.walletAddress) {
            mainButton.setParams({
                ...defaultParams,
                text: "Connect wallet to join",
                isEnabled: true,
                hasShineEffect: true
            });
            return;
        }

        if (!chat.isEligible) {
            mainButton.setParams({
                isVisible: false
            })
            return;
        }

        const chatJoinUrl = chat.joinUrl;
        if (chatJoinUrl) {
            if (chat.isMember) {
                mainButton.setParams({...defaultParams, text: "Open", isEnabled: true, hasShineEffect: true});
            } else {
                mainButton.setParams({...defaultParams, text: "Join", isEnabled: true, hasShineEffect: true});
            }
        } else {
            mainButton.setParams({...defaultParams, text: "No chat link"});
        }
    }, [chat, mainButtonOnClickListener, startParam, user]);

    return { mainButton }
};

export default useMainButton;