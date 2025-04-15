import {useEffect, useState} from "react";
import {fetchChats} from "@/services";
import {IBaseChat} from "@/interfaces";
import {useClientOnce} from "@/hooks/useClientOnce";


const useChatsData = () => {
    const [chats, setChats] = useState<IBaseChat[] | null>(null);
    const [isChatsLoading, setIsChatsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useClientOnce(() => {
        fetchChats().then((chatsData: IBaseChat[]) => {
            setChats(chatsData);
        }).catch((error) => setError(error)).finally(() => {
            setIsChatsLoading(false);
        });
    })

    useEffect(() => {
        if (error) {
            console.error("Error fetching chats:", error);
            throw error;
        }
    }, [error]);

    return {chats, isChatsLoading};
}

export default useChatsData;