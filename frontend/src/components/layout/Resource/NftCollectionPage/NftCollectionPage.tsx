'use client';

import React, {FC, PropsWithChildren, useCallback} from "react";

import {useRouter} from "next/navigation";
import useNftCollectionData from "@/hooks/data/useNftCollectionData";
import ResourcePage from "@/components/layout/Resource/ResourcePage";


const NftCollectionPage: FC<PropsWithChildren<{ address?: string }>> = ({address, children}) => {
    const {nftCollection, isLoading, addNftCollection, toggleNftCollection} = useNftCollectionData(address);
    const router = useRouter();

    const onNftCollectionCreated = useCallback(
        (_: string) => {
            router.push(`/admin/nft-collection`)
        }, [router]
    )

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
        />
    )
}

export default NftCollectionPage;
