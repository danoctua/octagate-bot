import {useCallback, useState} from "react";
import {useLaunchParams} from "@telegram-apps/sdk-react";
import {fetchChatData} from "@/services";
import {IChatConfiguration} from "@/interfaces";


const useChatData = () => {
    const [chat, setChat] = useState<IChatConfiguration | null>(null);
    const [isChatDataLoading, setIsChatDataLoading] = useState(false);
    const launchParams = useLaunchParams();

    const refreshChatData = useCallback(async () => {
        if (!launchParams.startParam) {
            return;
        }
        setIsChatDataLoading(true);
        return await fetchChatData(launchParams.startParam).then((chatData: IChatConfiguration) => {
            console.debug("Refreshing chat data", chatData);
            setChat(chatData);
            setIsChatDataLoading(false);
            return chatData;
        }).catch((error) => {});
    }, [launchParams.startParam])

    return { chat, setChat, fetchChatData: refreshChatData, isChatDataLoading, setIsChatDataLoading };
}

export default useChatData;