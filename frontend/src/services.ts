import apiClient from "@/utils/apiClient";
import {IChatConfiguration} from "@/interfaces";


export const fetchTaskStatus = async (asyncTaskId: string) => {
    return await apiClient.get(`/system/async-tasks/${asyncTaskId}`).then(response => response.data);
}


export const updateUserWallet = async (walletAddress: string, tonProof: any, publicKey: string | undefined) => {
    return await apiClient.post("/users/wallet", {
        walletAddress: walletAddress,
        tonProof: tonProof,
        publicKey: publicKey,
    }).then(response => response.data)
}


export const disconnectUserWallet = async () => {
    return await apiClient.delete("/users/wallet").then((response) => response.data);
}


export const fetchChatData = async (slug: string): Promise<IChatConfiguration> => {
    return await apiClient.get(`/chats/${slug}`).then((response) => response.data);
}
