'use client';

import {useRouter} from "next/navigation";
import React, {useCallback} from "react";
import CreateResourcePage from "@/components/layout/Resource/CreateResourcePage";
import useNftCollectionData from "@/hooks/data/useNftCollectionData";

const CreateNftCollectionPage = () => {
    const {addNftCollection, isLoading} = useNftCollectionData()
    const router = useRouter();


    const onNftCollectionCreated = useCallback(
        (_: string) => {
            router.push(`/admin/nft-collection`)
        },
        [router]
    )

    return (
        <CreateResourcePage
            title={"Add NFT Collection"}
            subtitle={"Add a new NFT collection by providing the master contract address."}
            isLoading={isLoading}
            addResource={addNftCollection}
            resourceType={"NFT collection"}
            onCreated={onNftCollectionCreated}
        />
    )
}

export default CreateNftCollectionPage;
