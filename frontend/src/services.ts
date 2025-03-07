import apiClient from "@/utils/apiClient";
import {IBaseChat, IChatConfiguration, IJetton, INftCollection, IRule, IUser} from "@/interfaces";


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

export const fetchAdminChatData = async (slug: string): Promise<IChatConfiguration> => {
    return await apiClient.get(`/admin/chats/${slug}`).then((response) => response.data);
}

export const fetchChats = async (): Promise<IBaseChat[]> => {
    return await apiClient.get("/admin/chats").then(response => response.data);
}

export const createChat = async (chat: {chatIdentifier: string}): Promise<IBaseChat> => {
    return await apiClient.post("/admin/chats", chat).then(response => response.data);
}

export const fetchAllJettons = async (): Promise<IJetton[]> => {
    return await apiClient.get("/admin/resources/jettons?whitelistedOnly=false").then(response => response.data);
}

export const fetchJetton = async (address: string): Promise<IJetton> => {
    return await apiClient.get(`/admin/resources/jettons/${address}`).then(response => response.data);
}

export const fetchWhitelistedJettons = async (): Promise<IJetton[]> => {
    return await apiClient.get("/admin/resources/jettons").then(response => response.data);
}

export const createJetton = async (address: string): Promise<IJetton> => {
    return await apiClient.post(`/admin/resources/jettons`, {address}).then(response => response.data);
}

export const updateJetton = async (address: string, isEnabled: boolean): Promise<IJetton> => {
    return await apiClient.put(`/admin/resources/jettons/${address}`, {isEnabled}).then(response => response.data);
}

export const fetchJettonRule = async (slug: string, ruleId: number): Promise<IRule> => {
    return await apiClient.get(`/admin/chats/${slug}/rules/jettons/${ruleId}`).then(response => response.data);
}

export const createJettonRule = async (slug: string, address: string, expected: number): Promise<IRule> => {
    return await apiClient.post(`/admin/chats/${slug}/rules/jettons`, {address, expected}).then(response => response.data);
}

export const updateJettonRule = async (slug: string, ruleId: number, {address, expected, isEnabled}: {address: string, expected: number, isEnabled: boolean}): Promise<IRule> => {
    return await apiClient.put(`/admin/chats/${slug}/rules/jettons/${ruleId}`, {address, expected, isEnabled}).then(response => response.data);
}

export const fetchAllNftCollections = async (): Promise<INftCollection[]> => {
    return await apiClient.get("/admin/resources/nft-collections?whitelistedOnly=false").then(response => response.data);
}

export const fetchWhiteListedNftCollections = async (): Promise<INftCollection[]> => {
    return await apiClient.get("/admin/resources/nft-collections?whitelistedOnly=true").then(response => response.data);
}

export const fetchNftCollection = async (address: string): Promise<INftCollection> => {
    return await apiClient.get(`/admin/resources/nft-collections/${address}`).then(response => response.data);
}

export const createNftCollection = async (address: string): Promise<INftCollection> => {
    return await apiClient.post(`/admin/resources/nft-collections`, {address}).then(response => response.data);
}

export const updateNftCollection = async (address: string, isEnabled: boolean): Promise<INftCollection> => {
    return await apiClient.put(`/admin/resources/nft-collections/${address}`, {isEnabled}).then(response => response.data);
}

export const fetchNftCollectionRule = async (slug: string, ruleId: number): Promise<IRule> => {
    return await apiClient.get(`/admin/chats/${slug}/rules/nft-collections/${ruleId}`).then(response => response.data);
}

export const createNftCollectionRule = async (slug: string, address: string, expected: number): Promise<IRule> => {
    return await apiClient.post(`/admin/chats/${slug}/rules/nft-collections`, {address, expected}).then(response => response.data);
}

export const updateNftCollectionRule = async (slug: string, ruleId: number, {address, expected, isEnabled}: {address: string, expected: number, isEnabled: boolean}): Promise<IRule> => {
    return await apiClient.put(`/admin/chats/${slug}/rules/nft-collections/${ruleId}`, {address, expected, isEnabled}).then(response => response.data);
}
