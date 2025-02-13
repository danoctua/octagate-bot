import {TonConnectButton, useTonConnectUI } from "@tonconnect/ui-react";
import {useClientOnce} from "@/hooks/useClientOnce";


const useTonConnect = () => {
    const [tonConnectUI] = useTonConnectUI();

    useClientOnce(() => {
        // Generate nonce for Ton Connect
        const nonce = Math.floor(Math.random() * 10000000).toString();
        tonConnectUI.setConnectRequestParameters(
            { "state": "ready", "value": { tonProof: nonce } }
        );

    });

    return { tonConnectUI, TonConnectButton };
}

export default useTonConnect;
