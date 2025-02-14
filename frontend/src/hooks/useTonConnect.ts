import {TonConnectButton, useTonConnectUI } from "@tonconnect/ui-react";
import {useClientOnce} from "@/hooks/useClientOnce";
import {useCallback} from "react";


const useTonConnect = () => {
    const [tonConnectUI] = useTonConnectUI();

    useClientOnce(() => {
        // Generate nonce for Ton Connect
        const nonce = Math.floor(Math.random() * 10000000).toString();
        tonConnectUI.setConnectRequestParameters(
            { "state": "ready", "value": { tonProof: nonce } }
        );

    });

    const disconnectWallet = useCallback(async () => {
        if (tonConnectUI.wallet) {
            await tonConnectUI.disconnect();
        }
    }, [tonConnectUI])

    const connectWallet = useCallback(async () => {
        await tonConnectUI.openModal();
    }, [tonConnectUI])

    return { tonConnectUI, TonConnectButton, disconnectWallet, connectWallet };
}

export default useTonConnect;
