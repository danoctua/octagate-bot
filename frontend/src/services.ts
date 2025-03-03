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


export const fetchChatData = async (slug: string, full: boolean = false): Promise<IChatConfiguration> => {
    return await apiClient.get(`/chats/${slug}?full=${full}`).then((response) => response.data);
}

export const fetchChats = async (): Promise<IBaseChat[]> => {
    return await apiClient.get("/chats").then(response => response.data);
}

export const createChat = async (chat: {chatIdentifier: string}): Promise<IBaseChat> => {
    return await apiClient.post("/chats", chat).then(response => response.data);
}

export const fetchAllJettons = async (): Promise<IJetton[]> => {
    return await apiClient.get("/resources/jettons?whitelistedOnly=false").then(response => response.data);
}

export const fetchJetton = async (address: string): Promise<IJetton> => {
    return await apiClient.get(`/resources/jettons/${address}`).then(response => response.data);
}

export const fetchWhitelistedJettons = async (): Promise<IJetton[]> => {
    return await apiClient.get("/resources/jettons").then(response => response.data);
}

export const createJetton = async (address: string): Promise<IJetton> => {
    return await apiClient.post(`/resources/jettons`, {address: address}).then(response => response.data);
}

export const updateJetton = async (address: string, isEnabled: boolean): Promise<IJetton> => {
    return await apiClient.put(`/resources/jettons/${address}`, {isEnabled: isEnabled}).then(response => response.data);
}

export const fetchJettonRule = async (slug: string, jettonAddress: string): Promise<IRule> => {
    return await apiClient.get(`/chats/${slug}/rules/jettons/${jettonAddress}`).then(response => response.data);
}

export const createJettonRule = async (slug: string, jettonAddress: string, expected: number): Promise<IRule> => {
    return await apiClient.post(`/chats/${slug}/rules/jettons/${jettonAddress}`, {expected: expected}).then(response => response.data);
}

export const updateJettonRule = async (slug: string, jettonAddress: string, expected: number): Promise<IRule> => {
    return await apiClient.put(`/chats/${slug}/rules/jettons/${jettonAddress}`, {expected: expected}).then(response => response.data);
}

export const toggleJettonRule = async (slug: string, jettonAddress: string, isEnabled: boolean): Promise<IRule> => {
    return await apiClient.put(`/chats/${slug}/rules/jettons/${jettonAddress}/toggle`, {isEnabled: isEnabled}).then(response => response.data);
}
