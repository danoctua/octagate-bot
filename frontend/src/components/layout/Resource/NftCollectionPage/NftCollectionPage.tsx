'use client';

import React, {FC, PropsWithChildren, useCallback, useMemo, useState} from "react";

import {useRouter} from "next/navigation";
import useNftCollectionData from "@/hooks/data/useNftCollectionData";
import ResourcePage from "@/components/layout/Resource/ResourcePage";
import {Accordion, Cell, IconButton, Placeholder, Section, Skeleton} from "@telegram-apps/telegram-ui";
import {Dot, RefreshCw} from "lucide-react";
import Image from "next/image";
import useFlashMessages from "@/hooks/useFlashMessages";


const NftCollectionPage: FC<PropsWithChildren<{ address?: string }>> = ({address, children}) => {
    const {
        nftCollection,
        isLoading,
        toggleNftCollection,
        refreshMetadata,
        isMetadataLoading
    } = useNftCollectionData(address);
    const router = useRouter();
    const [expandedId, setExpandedId] = useState<number | undefined>(undefined);
    const { pushMessage } = useFlashMessages();
    const [isRefreshDisabled, setIsRefreshDisabled] = useState<boolean>(false);

    const onSave = useCallback(
        (_: string) => {
            router.push(`/admin/nft-collection`)
        }, [router]
    )

    const onRefreshMetadata = useCallback(async () => {
        if (!nftCollection) return
        setIsRefreshDisabled(true)
        await refreshMetadata(nftCollection.address).then(() => {
            pushMessage(
                "Metadata refresh submitted",
                "Metadata refresh has submitted successfully, but it may take some time to update.",
                "info",
            )
        })
    }, [nftCollection, pushMessage, refreshMetadata])

    const renderChildren = useMemo(() => {
        if (!nftCollection) return

        return (
            <Section
                header={
                    <Section.Header>
                        <div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
                            <span>Metadata</span>
                            <IconButton
                                mode={"plain"}
                                onClick={onRefreshMetadata}
                                disabled={isRefreshDisabled}
                            >
                                <RefreshCw/>
                            </IconButton>
                        </div>
                    </Section.Header>
                }
            >
                <Skeleton visible={isMetadataLoading || isLoading}>
                    {nftCollection.blockchainMetadata?.attributes && nftCollection.blockchainMetadata.attributes.length ?
                        nftCollection.blockchainMetadata.attributes.map(({traitType, values}, index) => (
                            <Accordion
                                key={index}
                                expanded={index === expandedId}
                                onChange={() => setExpandedId(expandedId === index ? undefined : index)}
                            >
                                <Accordion.Summary>
                                    {traitType}
                                </Accordion.Summary>
                                <Accordion.Content>
                                    {values.map(value => (
                                        <Cell
                                            key={`${traitType}-${value}`}
                                            before={<Dot/>}
                                        >
                                            {value}
                                        </Cell>
                                    ))}
                                </Accordion.Content>
                            </Accordion>
                        )) :
                        <Placeholder
                            description="Seems like this collection has no attributes"
                            header="No attributes"
                        >
                            <Image
                                alt="Lost bananas"
                                src="/telegram.gif"
                                width={150}
                                height={150}
                            />
                        </Placeholder>

                    }
                </Skeleton>
            </Section>
        )

    }, [expandedId, isLoading, isMetadataLoading, isRefreshDisabled, nftCollection, onRefreshMetadata])

    return (
        <ResourcePage
            resource={nftCollection}
            isLoading={isLoading}
            toggleResource={toggleNftCollection}
            resourceType={"NFT collection"}
            onSave={onSave}
        >
            {renderChildren}
        </ResourcePage>
    )
}

export default NftCollectionPage;
