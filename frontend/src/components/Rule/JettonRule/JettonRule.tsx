'use client';

import React, {FC, PropsWithChildren, useCallback, useState} from "react";
import useJettonsData from "@/hooks/data/useJettonsData";
import useChatJettonRuleData from "@/hooks/data/useChatJettonRuleData";
import {useRouter} from "next/navigation";
import BlockchainRule from "@/components/Rule/BlockchainRule/BlockchainRule";


const JettonRule: FC<PropsWithChildren<{
    chatSlug: string,
    ruleId?: number
}>> = ({chatSlug, ruleId, children}) => {
    const {jettons} = useJettonsData({whitelistedOnly: true})
    const {
        chatJettonRuleData,
        updateChatJettonRule,
        createChatJettonRule,
        isLoading: isChatJettonRuleLoading
    } = useChatJettonRuleData({
        slug: chatSlug,
        ruleId: ruleId
    })
    const [isEnabled, setIsEnabled] = useState<boolean>(false);
    const router = useRouter();


    const onSaveButtonClick = useCallback(
        async (expected: number, address: string, isEnabled: boolean) => {
            if (ruleId) {
                await updateChatJettonRule({expected, address, isEnabled})
            } else {
                await createChatJettonRule({expected, address})
            }
            // To make sure it doesn't create a bunch of history entries
            router.back()
        }, [createChatJettonRule, ruleId, router, updateChatJettonRule]
    )

    return (
        <BlockchainRule
            title={"Token"}
            category={"jettons"}
            options={jettons?.map(jetton => ({...jetton, title: jetton.symbol, subtitle: jetton.name}))}
            isLoading={isChatJettonRuleLoading}
            onSave={onSaveButtonClick}
            entity={chatJettonRuleData}
        />
    )
}

export default JettonRule;
