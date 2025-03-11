'use client';


import React, {FC, PropsWithChildren, useCallback} from "react";
import useNftCollectionsData from "@/hooks/data/useNftCollectionsData";
import {useRouter} from "next/navigation";
import useChatNftCollectionRuleData from "@/hooks/data/useChatNftCollectionRuleData";
import BlockchainRule from "@/components/Rule/BlockchainRule/BlockchainRule";

const NftCollectionRule: FC<PropsWithChildren<{
    chatSlug: string,
    ruleId?: number
}>> = ({chatSlug, ruleId, children}) => {
    const {nftCollections} = useNftCollectionsData({whitelistedOnly: true})

    const {
        chatNftCollectionRuleData,
        updateChatNftCollectionRule,
        createChatNftCollectionRule,
        isLoading
    } = useChatNftCollectionRuleData({
        slug: chatSlug,
        ruleId: ruleId
    })

    const router = useRouter();

    const onSaveButtonClick = useCallback(
        async (expected: number, address: string, isEnabled: boolean) => {
            if (ruleId) {
                await updateChatNftCollectionRule({expected, address, isEnabled})
            } else {
                await createChatNftCollectionRule({expected, address})
            }
            // To make sure it doesn't create a bunch of history entries
            router.back()
        },
        [createChatNftCollectionRule, ruleId, router, updateChatNftCollectionRule]
    )

    return (
        <BlockchainRule
            title={"NFT Collection"}
            category={"nfts"}
            options={nftCollections?.map(nftCollection => ({...nftCollection, title: nftCollection.name, subtitle: nftCollection.description}))}
            isLoading={isLoading}
            onSave={onSaveButtonClick}
            entity={chatNftCollectionRuleData}
        />
    )
}

export default NftCollectionRule;
