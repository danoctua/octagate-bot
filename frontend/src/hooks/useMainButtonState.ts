import {ButtonStateProps} from "@/components/FixedBottomSection/FixedBottomSection";
import {useEffect, useMemo, useState} from "react";
import {openTelegramLink} from "@telegram-apps/sdk-react";
import {IChat, IChatConfiguration, IUser} from "@/interfaces";


const useMainButtonState = (
    isUserDataLoading: boolean,
    isChatDataLoading: boolean,
    startParam: string | undefined,
    user: IUser | undefined,
    chat: IChat | undefined,
    connectWallet: () => Promise<() => void>,
    fetchChatData: () => Promise<IChatConfiguration | void>,
): ButtonStateProps | undefined => {
    const [timeLeft, setTimeLeft] = useState<number>(0);
    const [isButtonDisabled, setIsButtonDisabled] = useState<boolean>(false);

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

    return useMemo(() => {
        if (!startParam) {
            return;
        }

        const loading = isUserDataLoading || isChatDataLoading;

        const baseAttributes = {loading}

        if (!user || !chat) {
            return {
                text: "Loading...",
                loading: loading,
                disabled: true,
                mode: "filled"
            }
        } else if (chat && chat.joinUrl) {
            return {
                ...baseAttributes,
                text: "Join",
                onClick: () => chat.joinUrl && openTelegramLink(chat.joinUrl),
            }
        } else if (chat && !user.walletAddress) {
            return {
                ...baseAttributes,
                text: "Connect wallet to join",
                mode: "filled",
                onClick: () => connectWallet().then()
            }
        } else if (chat && user.walletAddress && !chat.isEligible) {
            return {
                ...baseAttributes,
                text: timeLeft ? `Refresh again in ${timeLeft}...` : "Refresh",
                mode: "bezeled",
                disabled: isUserDataLoading || isChatDataLoading || isButtonDisabled,
                onClick: () => {
                    if (isButtonDisabled) {
                        return
                    }
                    setIsButtonDisabled(true);
                    setTimeLeft(10);
                    fetchChatData().then();
                }
            }
        } else if (chat && chat.isEligible && !chat.joinUrl) {
            return {
                ...baseAttributes,
                text: "No chat link",
                disabled: true,
                mode: "gray"
            }
        }
    }, [
        chat,
        connectWallet,
        fetchChatData,
        isButtonDisabled,
        isChatDataLoading,
        isUserDataLoading,
        startParam,
        timeLeft,
        user
    ])
}

export default useMainButtonState;
