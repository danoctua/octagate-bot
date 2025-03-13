'use client';

import React, {FC, PropsWithChildren, useCallback, useMemo, useState} from "react";

import {useRouter} from "next/navigation";
import useNftCollectionData from "@/hooks/data/useNftCollectionData";
import ResourcePage from "@/components/layout/Resource/ResourcePage";
import {Accordion, Cell, IconButton, Placeholder, Section, Skeleton} from "@telegram-apps/telegram-ui";
import {Dot, RefreshCw} from "lucide-react";
import Image from "next/image";


const NftCollectionPage: FC<PropsWithChildren<{ address?: string }>> = ({address, children}) => {
    const {
        nftCollection,
        isLoading,
        addNftCollection,
        toggleNftCollection,
        refreshMetadata,
        isMetadataLoading
    } = useNftCollectionData(address);
    const router = useRouter();
    const [expandedId, setExpandedId] = useState<number | undefined>(undefined);
    const [isRefreshDisabled, setIsRefreshDisabled] = useState<boolean>(false);

    const onNftCollectionCreated = useCallback(
        (_: string) => {
            router.push(`/admin/nft-collection`)
        }, [router]
    )

    const onRefreshMetadata = useCallback(async () => {
        if (!nftCollection) return
        setIsRefreshDisabled(true)
        await refreshMetadata(nftCollection.address)
    }, [nftCollection, refreshMetadata])

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
            inputAddress={address}
            resource={nftCollection}
            isLoading={isLoading}
            addResource={addNftCollection}
            toggleResource={toggleNftCollection}
            resourceStaticPath={"/dynamic/nfts"}
            resourceType={"NFT collection"}
            onNewResourceCreated={onNftCollectionCreated}
        >
            {renderChildren}
        </ResourcePage>
    )
}

export default NftCollectionPage;
