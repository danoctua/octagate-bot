'use client';

import React, {FC, PropsWithChildren, useCallback} from 'react';

import {Address} from '@ton/core';
import useTonConnect from "@/hooks/userTonConnect";
import {IUser} from "@/hooks/useAuthAndFetchUser";
import apiClient from "@/utils/apiClient";
import {Button, Cell} from "@telegram-apps/telegram-ui";
import {Check, Wallet} from "lucide-react";


export const  TonConnectItem: FC<PropsWithChildren<{ user: IUser, setUser: (user: IUser) => void }>> = ({ user, setUser, children }) => {

    const {tonConnectUI} = useTonConnect();

    const disconnectWallet = useCallback(async () => {
        if (tonConnectUI.wallet) {
            await tonConnectUI.disconnect();
        }

        if (user?.walletAddress) {
            // Send request to backend to delete wallet
            apiClient.delete("/users/wallet").then((response) => {
                console.log("Setting user on wallet disconnect", response.data);
                setUser(response.data);
            });
        }
    }, [setUser, tonConnectUI, user])

    const connectWallet = useCallback(async () => {
        await tonConnectUI.openModal();

        const handleConnectionCompleted = () => {
            console.log("connection-completed");
            console.log(tonConnectUI.wallet?.connectItems);
            apiClient.post("/users/wallet", {
                walletAddress: tonConnectUI.wallet?.account.address,
                tonProof: (tonConnectUI.wallet?.connectItems?.tonProof as any)?.proof,
                publicKey: tonConnectUI.wallet?.account.publicKey,
            }).then(
                (response) => {
                    console.log("Setting user on wallet connect", response.data);
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
    }, [setUser, tonConnectUI])

    const parsedWalletAddress = user?.walletAddress ?
        Address.parse(user?.walletAddress).toString({bounceable: false}):
        null

    const shortenWalletAddress = parsedWalletAddress ? `${parsedWalletAddress.slice(0, 4)}...${parsedWalletAddress.slice(-4)}` : null

    return (

        <Cell
            key={"wallet-connect"}
            before={
                user.walletAddress ? <Check color={"green"}/> : <Wallet/>
            }
            after={
                <Button
                    size={"s"}
                    onClick={() => {user.walletAddress ? disconnectWallet() : connectWallet()}}
                >
                    {user.walletAddress? 'Disconnect' : 'Connect'}
                </Button>
            }
            readOnly
            multiline={false}
            subtitle={shortenWalletAddress ?? "No wallet connected"}
        >
            {user.walletAddress ? "Wallet connected" : "Connect wallet"}
        </Cell>
    );
};
