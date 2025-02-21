'use client';

import React, {FC, PropsWithChildren, useMemo} from 'react';

import {Button, Cell, FixedLayout, Modal, Title, Text} from "@telegram-apps/telegram-ui";
import {ChevronRight, Wallet} from "lucide-react";


const WalletFixedBottomItem: FC<PropsWithChildren<{
    walletAddress: string,
    disconnectWallet: () => void
}>> = ({walletAddress, disconnectWallet, children}) => {
    const shortenWalletAddress = `${walletAddress.slice(0, 4)}...${walletAddress.slice(-4)}`

    const walletCell = useMemo(
        () => (
            <Cell
                multiline={false}
                readOnly
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
                            <Wallet strokeWidth={2}/>
                        </span>
                }
                after={<ChevronRight color={"var(--tg-theme-section-header-text-color)"}/>}
                subtitle={"Wallet connected"}
            >
                {shortenWalletAddress}
            </Cell>
        ), [shortenWalletAddress]
    )

    const disconnectWalletModal = useMemo(
        () => (
            <Modal
                trigger={walletCell}
            >
                <div style={{padding: 16, display: "flex", flexDirection: "column", gap: 16}}>
                    <Title plain>
                        Disconnect wallet?
                    </Title>
                    <Text>
                        After disconnecting the wallet you&apos;ll be kicked out of all the chats you joined through the
                        Gateway.
                    </Text>
                    <div style={{display: "flex", flexDirection: "column", gap: 8}}>
                        <Button stretched width={"100%"} onClick={disconnectWallet}>Disconnect</Button>
                        <Modal.Close>
                            <Button stretched mode={"bezeled"}>
                                Cancel
                            </Button>
                        </Modal.Close>
                    </div>
                </div>
            </Modal>
        ), [disconnectWallet, walletCell]
    )


    return (
        <FixedLayout vertical={"bottom"}>
            {disconnectWalletModal}
        </FixedLayout>
    )

};

export default WalletFixedBottomItem;
