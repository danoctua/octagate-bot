import {useCallback, useState} from "react";
import apiClient from "@/utils/apiClient";
import {useLaunchParams} from "@telegram-apps/sdk-react";


export interface IChat {
    id: number,
    username: string,
    title: string,
    slug: string,
    isForum: boolean,
    logoPath: string,
    joinUrl?: string,
    isMember: boolean,
}

export interface IRule {
    category: string,
    title: string,
    promoteUrl: string,
    expected: number,
    actual?: number,
    photoUrl: string,
    isEligible: boolean,
}

export interface IChatConfiguration {
    chat: IChat,
    rules: IRule[],
}


const useChatData = () => {
    const [chat, setChat] = useState<IChatConfiguration | null>(null);
    const launchParams = useLaunchParams();

    const fetchChatData = useCallback(async () => {
        return await apiClient.get(`/chats/${launchParams.startParam}`).then((response) => {
            const chatData = response.data;
            console.debug("Refreshing chat data", chatData);
            setChat(chatData);
            return chatData;
        }).catch((error) => {});
    }, [launchParams.startParam])

    return { chat, setChat, fetchChatData}
}

export default useChatData;