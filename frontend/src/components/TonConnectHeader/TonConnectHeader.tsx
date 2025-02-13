'use client';

import {FC, useCallback} from 'react';

import {Address} from '@ton/core';
import useTonConnect from "@/hooks/userTonConnect";
import {useAuthAndFetchUser} from "@/hooks/useAuthAndFetchUser";
import apiClient from "@/utils/apiClient";

export const TonConnectHeader: FC = () => {

    const {tonConnectUI} = useTonConnect();
    const [user, setUser] = useAuthAndFetchUser();

    const disconnectWallet = useCallback(() => {
        if (tonConnectUI.wallet) {
            tonConnectUI.disconnect();
        }

        if (user?.walletAddress) {
            // Send request to backend to delete wallet
            apiClient.delete("/users/wallet").then((response) => {
                setUser(response.data);
            });
        }
    }, [setUser, tonConnectUI, user])

    const connectWallet = useCallback(() => {
        tonConnectUI.openModal();

        const handleConnectionCompleted = () => {
            console.log("connection-completed");
            console.log(tonConnectUI.wallet?.connectItems);
            apiClient.post("/users/wallet", {
                walletAddress: tonConnectUI.wallet?.account.address,
                tonProof: (tonConnectUI.wallet?.connectItems?.tonProof as any)?.proof,
                publicKey: tonConnectUI.wallet?.account.publicKey,
            }).then(
                (response) => {
                    setUser(response.data);
                }
            ).catch(
                (error) => {
                    alert(error);
                    tonConnectUI.disconnect();
                }
            );
        }
        window.addEventListener("ton-connect-connection-completed", handleConnectionCompleted);

        return () => {
            window.removeEventListener("ton-connect-connection-completed", handleConnectionCompleted);
        };
    }, [tonConnectUI])

    return (
        <div style={{display: 'flex', justifyContent: 'flex-end', padding: '20px'}}>
            {
                user?.walletAddress ?
                    <div style={{display: 'flex', alignItems: 'center'}}>
                        <div style={{marginRight: '10px'}}>{Address.parse(user.walletAddress).toString({bounceable: false})}</div>
                        <button onClick={disconnectWallet}>Disconnect wallet</button>
                    </div>
                    : <div style={{display: 'flex', alignItems: 'center'}}>
                        <div style={{marginRight: '10px'}}>Connect wallet</div>
                        <button onClick={connectWallet}>Connect wallet</button>
                    </div>
            }
        </div>
    );
};
