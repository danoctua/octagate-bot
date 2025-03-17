import {useCallback, useState} from "react";
import {createChat, fetchChatData} from "@/services";
import {IChat, IChatConfiguration} from "@/interfaces";


const useChatData = (slug?: string | undefined) => {
    const [chat, setChat] = useState<IChatConfiguration | null>(null);
    const [isChatDataLoading, setIsChatDataLoading] = useState(false);

    const refreshChatData = useCallback(async () => {
        if (!slug) {
            return;
        }
        setIsChatDataLoading(true);
        return await fetchChatData(slug).then((chatData: IChatConfiguration) => {
            setChat(chatData);
            return chatData;
        }).finally(() => setIsChatDataLoading(false));
    }, [slug])

    const addChat = useCallback(async (chatIdentifier: string) => {
        if (slug || !chatIdentifier) {
            return
        }

        setIsChatDataLoading(true);
        return await createChat({chatIdentifier}).then((chatData: IChat) => {
            return chatData;
        }).finally(() => setIsChatDataLoading(false));
    }, [slug])

    return { chat, fetchChatData: refreshChatData, isChatDataLoading, setIsChatDataLoading, addChat };
}

export default useChatData;