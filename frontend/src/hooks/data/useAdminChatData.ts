import {useCallback, useState} from "react";
import {fetchAdminChatData, fetchChatData, updateChat} from "@/services";
import {IChat, IChatConfiguration} from "@/interfaces";


const useAdminChatData = (slug: string | undefined,) => {
    const [chat, setChat] = useState<IChatConfiguration | null>(null);
    const [isChatDataLoading, setIsChatDataLoading] = useState(false);

    const fetchChatData = useCallback(async () => {
        if (!slug) {
            return;
        }
        setIsChatDataLoading(true);
        return await fetchAdminChatData(slug).then((chatData: IChatConfiguration) => {
            console.debug("Refreshing chat data", chatData);
            setChat(chatData);
            setIsChatDataLoading(false);
            return chatData;
        });
    }, [slug])

    const updateChatData = useCallback(async (description: string) => {
        if (!slug || !chat) {
            return;
        }
        setIsChatDataLoading(true);
        return await updateChat(slug, description).then((chatData: IChat) => {
            console.debug("Updating chat data", chatData);
            setChat({...chat, chat: chatData});
            return chatData;
        }).finally(() => {setIsChatDataLoading(false)});
    }, [slug, chat])

    return {
        chat,
        fetchChatData,
        updateChatData,
        isChatDataLoading,
        setIsChatDataLoading
    };
}

export default useAdminChatData;