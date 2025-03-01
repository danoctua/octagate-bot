import apiClient from "@/utils/apiClient";
import {IBaseChat, IChatConfiguration, IJetton, IRule, IUser} from "@/interfaces";


export const fetchTaskStatus = async (asyncTaskId: string) => {
    return await apiClient.get(`/system/async-tasks/${asyncTaskId}`).then(response => response.data);
}


export const updateUserWallet = async (walletAddress: string, tonProof: any, publicKey: string | undefined): Promise<any> => {
    return await apiClient.post("/users/wallet", {
        walletAddress: walletAddress,
        tonProof: tonProof,
        publicKey: publicKey,
    }).then(response => response.data)
}


export const disconnectUserWallet = async (): Promise<IUser> => {
    return await apiClient.delete("/users/wallet").then((response) => response.data);
}


export const fetchChatData = async (slug: string): Promise<IChatConfiguration> => {
    return await apiClient.get(`/chats/${slug}`).then((response) => response.data);
}


export const fetchChats = async (): Promise<IBaseChat[]> => {
    return await apiClient.get("/chats").then(response => response.data);
}


export const createChat = async (chat: {chatIdentifier: string}): Promise<IBaseChat> => {
    return await apiClient.post("/chats", chat).then(response => response.data);
}


export const fetchJettons = async (): Promise<IJetton[]> => {
    return await apiClient.get("/resources/jettons").then(response => response.data);
}


export const fetchJettonRule = async (slug: string, jettonAddress: string): Promise<IRule> => {
    return await apiClient.get(`/chats/${slug}/rules/jettons/${jettonAddress}`).then(response => response.data);
}
