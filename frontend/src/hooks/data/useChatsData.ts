import {useState} from "react";
import {fetchChats} from "@/services";
import {IBaseChat} from "@/interfaces";
import {useClientOnce} from "@/hooks/useClientOnce";


const useChatsData = () => {
    const [ chats, setChats ] = useState<IBaseChat[] | null>(null);
    const [ isChatsLoading, setIsChatsLoading ] = useState(true);

    useClientOnce(() => {
        fetchChats().then((chatsData: IBaseChat[]) => {
            console.debug("Fetching chats", chatsData);
            setChats(chatsData);
            setIsChatsLoading(false);
        }).catch((error) => {});
    })

    return { chats, isChatsLoading };
}

export default useChatsData;