import apiClient from "@/utils/apiClient";
import {
    IBaseChat, IChat,
    IChatConfiguration,
    IExternalWhitelistRule,
    IJetton,
    INftCollection, INftCollectionRule, INftMetadata,
    IRule, IStatusResponse,
    IUser,
    IWhitelistRule
} from "@/interfaces";


export const fetchTaskStatus = async (asyncTaskId: string): Promise<IStatusResponse> => {
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

export const createChat = async (chat: { chatIdentifier: string }): Promise<IChat> => {
    return await apiClient.post("/admin/chats", chat).then(response => response.data);
}

export const updateChat = async (slug: string, description: string): Promise<IChat> => {
    return await apiClient.put(`/admin/chats/${slug}`, {description}).then(response => response.data);
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
    return await apiClient.post(`/admin/chats/${slug}/rules/jettons`, {
        address,
        expected
    }).then(response => response.data);
}

export const updateJettonRule = async (slug: string, ruleId: number, {address, expected, isEnabled}: {
    address: string,
    expected: number,
    isEnabled: boolean
}): Promise<IRule> => {
    return await apiClient.put(`/admin/chats/${slug}/rules/jettons/${ruleId}`, {
        address,
        expected,
        isEnabled
    }).then(response => response.data);
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

export const refreshNftCollectionMetadata = async (address: string): Promise<IStatusResponse> => {
    return await apiClient.post(`/admin/resources/nft-collections/${address}/metadata`).then(response => response.data);
}

export const fetchNftCollectionRule = async (slug: string, ruleId: number): Promise<INftCollectionRule> => {
    return await apiClient.get(`/admin/chats/${slug}/rules/nft-collections/${ruleId}`).then(response => response.data);
}

export const createNftCollectionRule = async (
    slug: string, address: string, expected: number, requiredAttributes: INftMetadata[]
): Promise<INftCollectionRule> => {
    return await apiClient.post(`/admin/chats/${slug}/rules/nft-collections`, {
        address,
        expected,
        requiredAttributes
    }).then(response => response.data);
}

export const updateNftCollectionRule = async (
    slug: string,
    ruleId: number,
    {
        address, expected, isEnabled, requiredAttributes
    }: {
        address: string, expected: number, isEnabled: boolean, requiredAttributes: INftMetadata[]
    }
): Promise<INftCollectionRule> => {
    return await apiClient.put(`/admin/chats/${slug}/rules/nft-collections/${ruleId}`, {
        address,
        expected,
        isEnabled,
        requiredAttributes
    }).then(response => response.data);
}

export const fetchWhitelistRule = async (slug: string, ruleId: number): Promise<IWhitelistRule> => {
    return await apiClient.get(`/admin/chats/${slug}/rules/whitelist/${ruleId}`).then(response => response.data);
}

export const createWhitelistRule = async (slug: string, name: string, description: string | undefined | null, users: number[]): Promise<IWhitelistRule> => {
    return await apiClient.post(`/admin/chats/${slug}/rules/whitelist`, {
        name,
        description,
        users
    }).then(response => response.data);
}

export const updateWhitelistRule = async (slug: string, ruleId: number, {name, description, users, isEnabled}: {
    name: string,
    description: string | undefined | null,
    users: number[],
    isEnabled: boolean
}): Promise<IWhitelistRule> => {
    return await apiClient.put(`/admin/chats/${slug}/rules/whitelist/${ruleId}`, {
        name,
        description,
        users,
        isEnabled
    }).then(response => response.data);
}

export const fetchExternalWhitelistRule = async (slug: string, ruleId: number): Promise<IExternalWhitelistRule> => {
    return await apiClient.get(`/admin/chats/${slug}/rules/whitelist-external/${ruleId}`).then(response => response.data);
}

export const createExternalWhitelistRule = async (slug: string, name: string, description: string | undefined | null, url: string): Promise<IExternalWhitelistRule> => {
    return await apiClient.post(`/admin/chats/${slug}/rules/whitelist-external`, {
        name,
        description,
        url
    }).then(response => response.data);
}

export const updateExternalWhitelistRule = async (slug: string, ruleId: number, {name, description, isEnabled, url}: {
    name: string,
    description: string | undefined | null,
    isEnabled: boolean,
    url: string
}): Promise<IExternalWhitelistRule> => {
    return await apiClient.put(`/admin/chats/${slug}/rules/whitelist-external/${ruleId}`, {
        name,
        description,
        isEnabled,
        url
    }).then(response => response.data);
}
