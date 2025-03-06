'use client';

import {Cell, Placeholder, Skeleton, Switch} from "@telegram-apps/telegram-ui";
import React, {FC, PropsWithChildren, useCallback, useEffect, useState} from "react";
import SelectableRule from "@/components/Rule/SelectableRule/SelectableRule";
import useJettonsData from "@/hooks/data/useJettonsData";
import FixedBottomSection from "@/components/FixedBottomSection/FixedBottomSection";
import useChatJettonRuleData from "@/hooks/data/useChatJettonRuleData";
import Image from "next/image";
import {useRouter} from "next/navigation";


const JettonRule: FC<PropsWithChildren<{
    chatSlug: string,
    jettonAddress?: string
}>> = ({chatSlug, jettonAddress, children}) => {
    const {jettons} = useJettonsData({whitelistedOnly: true})
    const [selectedJettonAddress, setSelectedJettonAddress] = useState<string>(jettonAddress || "")
    const [expected, setExpected] = useState(0)
    const {
        chatJettonRuleData,
        updateChatJettonRule,
        createChatJettonRule,
        toggleChatJettonRule,
        isLoading: isChatJettonRuleLoading
    } = useChatJettonRuleData({
        slug: chatSlug,
        jettonAddress
    })
    const [isEnabled, setIsEnabled] = useState<boolean>(false);
    const [isFormValid, setIsFormValid] = useState<boolean>(false);
    const router = useRouter();

    useEffect(() => {
        setIsFormValid(selectedJettonAddress !== "" && expected > 0);
    }, [selectedJettonAddress, expected]);

    const onSwitchChange = useCallback(
        async (isEnabled: boolean) => {
            await toggleChatJettonRule(isEnabled, selectedJettonAddress)
            setIsEnabled(isEnabled)
        }, [selectedJettonAddress, toggleChatJettonRule]
    )

    const onSaveButtonClick = useCallback(
        async () => {
            if (jettonAddress) {
                await updateChatJettonRule(expected, selectedJettonAddress)
            } else {
                await createChatJettonRule(expected, selectedJettonAddress)
            }
            // To make sure it doesn't create a bunch of history entries
            router.back()
        }, [createChatJettonRule, expected, jettonAddress, router, selectedJettonAddress, updateChatJettonRule]
    )

    useEffect(() => {
        if (!chatJettonRuleData) return
        setExpected(chatJettonRuleData.expected)
        setSelectedJettonAddress(chatJettonRuleData.blockchainAddress)
        setIsEnabled(chatJettonRuleData.isEnabled)
    }, [chatJettonRuleData]);

    return (
        <>
            {jettons ?
                jettons.length ?
                    <SelectableRule
                        title={"Jetton"}
                        items={jettons}
                        category={"jettons"}
                        selectedOption={selectedJettonAddress}
                        onSelect={setSelectedJettonAddress}
                        expected={expected}
                        onExpectedChange={setExpected}
                        existing={jettonAddress !== undefined}
                        isEnabled={isEnabled}
                        onToggle={onSwitchChange}
                    /> :
                    <Placeholder
                        description="Please, try again after some jettons will be whitelisted"
                        header="No jettons available"
                    >
                        <Image
                            alt="Lost bananas"
                            src="/telegram.gif"
                            width={150}
                            height={150}
                        />
                    </Placeholder>
                : <Skeleton/>
            }
            <FixedBottomSection
                text={"Save"}
                disabled={!isFormValid}
                loading={isChatJettonRuleLoading}
                onClick={onSaveButtonClick}
            />
        </>
    )
}

export default JettonRule;
