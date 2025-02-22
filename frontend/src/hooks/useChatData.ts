import {useCallback, useState} from "react";
import {fetchChatData} from "@/services";
import {IChatConfiguration} from "@/interfaces";


const useChatData = (slug: string | undefined) => {
    const [chat, setChat] = useState<IChatConfiguration | null>(null);
    const [isChatDataLoading, setIsChatDataLoading] = useState(false);

    const refreshChatData = useCallback(async () => {
        if (!slug) {
            return;
        }
        setIsChatDataLoading(true);
        return await fetchChatData(slug).then((chatData: IChatConfiguration) => {
            console.debug("Refreshing chat data", chatData);
            setChat(chatData);
            setIsChatDataLoading(false);
            return chatData;
        });
    }, [slug])

    return { chat, setChat, fetchChatData: refreshChatData, isChatDataLoading, setIsChatDataLoading };
}

export default useChatData;