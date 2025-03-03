'use client';

import React, {FC, PropsWithChildren, useCallback, useMemo} from 'react';

import {Cell} from "@telegram-apps/telegram-ui";
import {ChevronRight, Wallet} from "lucide-react";
import { popup } from '@telegram-apps/sdk-react';


const ConnectedWalletCell: FC<PropsWithChildren<{
    walletAddress: string,
    disconnectWallet: () => void
}>> = ({walletAddress, disconnectWallet, children}) => {
    const shortenWalletAddress = `${walletAddress.slice(0, 4)}...${walletAddress.slice(-4)}`

    const popupCallback = useCallback(async () => {
        if (popup.isSupported()){
            const buttonId = await popup.open(
                {
                    title: "Disconnect wallet",
                    message: (
                        `Are you sure you want to disconnect the wallet ${shortenWalletAddress} from your account? \n\nAfter disconnecting the wallet you'll be kicked out of all the chats you joined through the Gateway`
                    ),
                    buttons: [
                        {id: "confirm", type: "destructive", text: "Disconnect"},
                        {id: "cancel", type: "default", text: "Cancel"}
                    ]
                }
            )
            if (buttonId === "confirm") {
                disconnectWallet()
            }
        }
    }, [disconnectWallet, shortenWalletAddress])

    return useMemo(
        () => (
            <Cell
                multiline={false}
                readOnly
                onClick={popupCallback}
                before={
                    <span
                        style={{
                            backgroundColor: "var(--tg-theme-button-color)",
                            width: 40,
                            height: 40,
                            borderRadius: 100,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center"
                        }}>
                            <Wallet strokeWidth={2} color={"white"}/>
                        </span>
                }
                after={<ChevronRight color={"var(--tg-theme-section-header-text-color)"}/>}
                subtitle={"Wallet connected"}
            >
                {shortenWalletAddress}
            </Cell>
        ), [popupCallback, shortenWalletAddress]
    )
};

export default ConnectedWalletCell;
