import {useEffect, useRef, useState} from 'react';
import {secondaryButton} from '@telegram-apps/sdk-react';
import {IChat, IChatConfiguration, IUser} from '@/interfaces';
import {useClientOnce} from "@/hooks/useClientOnce";


const useSecondaryButton = (
    user: IUser | undefined,
    chat: IChat | undefined,
    fetchChatData: () => Promise<IChatConfiguration | void>,
) => {
    const [timeLeft, setTimeLeft] = useState<number>(0);
    const [isButtonDisabled, setIsButtonDisabled] = useState<boolean>(false);
    const isListenerAdded = useRef(false);

    useClientOnce(() => {
        secondaryButton.mount();
        secondaryButton.setParams({
            text: "Refresh",
            isEnabled: false,
            isVisible: false,
            isLoaderVisible: false,
            hasShineEffect: false,
        });
    })

    useEffect(() => {
        if (!secondaryButton.isMounted()) {
            return;
        }

        if (user?.walletAddress && !chat?.isEligible) {
            // Short timeout to make sure the main button is hidden
            let timeout = 200;

            const timerId = setTimeout(() => {
                secondaryButton.setParams({
                    isVisible: true,
                    isLoaderVisible: false,
                    isEnabled: !isButtonDisabled,
                    text: timeLeft ? `Refresh again in ${timeLeft}...` : "Refresh"
                });
                if (!isListenerAdded.current) {
                    secondaryButton.onClick(() => {
                        setIsButtonDisabled(true);
                        setTimeLeft(10);
                        fetchChatData().then();
                    });
                    isListenerAdded.current = true;
                }
            }, timeout);
            return () => clearTimeout(timerId);
        } else {
            secondaryButton.setParams({
                isVisible: false
            });
        }
    }, [chat, fetchChatData, isButtonDisabled, timeLeft, user]);

    useEffect(() => {
        if (timeLeft > 0) {
            const timerId = setTimeout(() => {
                setTimeLeft(timeLeft - 1);
            }, 1000);
            return () => clearTimeout(timerId);
        } else {
            setIsButtonDisabled(false);
        }
    }, [timeLeft]);

    return { secondaryButton }
};

export default useSecondaryButton;
