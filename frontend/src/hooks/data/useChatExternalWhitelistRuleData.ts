import {IExternalWhitelistRule} from "@/interfaces";
import {useCallback, useState} from "react";
import {useClientOnce} from "@/hooks/useClientOnce";
import {
    createExternalWhitelistRule,
    fetchExternalWhitelistRule,
    updateExternalWhitelistRule,
} from "@/services";

export const useChatExternalWhitelistRuleData = (slug: string, ruleId?: number) => {
    const [rule, setRule] = useState<IExternalWhitelistRule | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);

    useClientOnce(() => {
        if (ruleId) {
            setIsLoading(true);
            fetchExternalWhitelistRule(slug, ruleId).then(setRule).finally(() => setIsLoading(false));
        }
    })

    const createRule = useCallback(
        async (name: string, description: string | undefined | null, url: string) => {
            setIsLoading(true);
            return await createExternalWhitelistRule(slug, name, description, url).then(
                newRule => {
                    setRule(newRule);
                    return newRule;
                }
            ).finally(() => setIsLoading(false));
        },
        [slug]
    )

    const updateRule = useCallback(
        async (name: string, description: string | undefined | null, isEnabled: boolean, url: string) => {
            if (!ruleId) { return;}
            setIsLoading(true);
            return await updateExternalWhitelistRule(slug, ruleId, {name, description, isEnabled, url}).then(
                updatedRule => {
                    setRule(updatedRule);
                    return updatedRule;
                }
            ).finally(() => setIsLoading(false));
        },
        [ruleId, slug]
    )

    return {rule, createRule, updateRule, isLoading};
}

export default useChatExternalWhitelistRuleData;
