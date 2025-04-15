import {useClientOnce} from "@/hooks/useClientOnce";
import {createJettonRule, fetchJettonRule, updateJettonRule} from "@/services";
import {useCallback, useState} from "react";
import {IRule} from "@/interfaces";


const useChatJettonRuleData = ({slug, ruleId}: { slug: string, ruleId?: number }) => {
    const [chatJettonRuleData, setChatJettonRuleData] = useState<IRule | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    useClientOnce(() => {
        if (!ruleId) return;
        setIsLoading(true);
        fetchJettonRule(slug, ruleId).then(
            (data) => {
                setChatJettonRuleData(data)
            }
        ).finally(() => {
            setIsLoading(false)
        });
    });

    const createChatJettonRule = useCallback(async ({expected, address}: { expected: number, address: string }) => {
        if (!slug || ruleId) return;
        setIsLoading(true);
        createJettonRule(slug, address, expected).then(
            (data) => {
                setChatJettonRuleData(data)
            }
        ).catch((e) => {
            setIsLoading(false)
            throw e;
        });
    }, [ruleId, slug])

    const updateChatJettonRule = useCallback(
        async ({expected, address, isEnabled}: { expected: number, address: string, isEnabled: boolean }) => {
            if (!ruleId) return;
            setIsLoading(true);
            updateJettonRule(slug, ruleId, {address, expected, isEnabled}).then(
                (data) => {
                    setChatJettonRuleData(data)
                }
            ).catch((e) => {
                setIsLoading(false)
                throw e;
            });
        },
        [ruleId, slug]
    )

    return {chatJettonRuleData, createChatJettonRule, updateChatJettonRule, isLoading};
};

export default useChatJettonRuleData;
