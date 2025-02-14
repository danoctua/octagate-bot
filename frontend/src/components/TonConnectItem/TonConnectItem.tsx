'use client';

import React, {FC, PropsWithChildren} from 'react';

import {Button, Cell} from "@telegram-apps/telegram-ui";
import {Check, Wallet} from "lucide-react";


const TonConnectItem: FC<PropsWithChildren<{ walletAddress: string | null, disconnectWallet: () => void, connectWallet: () => void }>> = ({ walletAddress, disconnectWallet, connectWallet, children }) => {

    const shortenWalletAddress = walletAddress ? `${walletAddress.slice(0, 4)}...${walletAddress.slice(-4)}` : null

    return (
        <Cell
            key={"wallet-connect"}
            before={
                walletAddress ? <Check color={"green"}/> : <Wallet/>
            }
            after={
                <Button
                    size={"s"}
                    onClick={() => {walletAddress ? disconnectWallet() : connectWallet()}}
                >
                    {walletAddress? 'Disconnect' : 'Connect'}
                </Button>
            }
            readOnly
            multiline={false}
            subtitle={shortenWalletAddress ?? "No wallet connected"}
        >
            {walletAddress ? "Wallet connected" : "Connect wallet"}
        </Cell>
    );
};

export default TonConnectItem;
