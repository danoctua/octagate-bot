import {IWhitelistRule} from "@/interfaces";
import {useCallback, useState} from "react";
import {useClientOnce} from "@/hooks/useClientOnce";
import {createWhitelistRule, fetchWhitelistRule, updateWhitelistRule} from "@/services";

export const useChatWhitelistRuleData = (slug: string, ruleId?: number) => {
    const [rule, setRule] = useState<IWhitelistRule | null>(null);

    useClientOnce(() => {
        if (ruleId) {
            fetchWhitelistRule(slug, ruleId).then(setRule);
        }
    })

    const createRule = useCallback(
        async (name: string, description: string | undefined | null, users: number[]) => {
            return await createWhitelistRule(slug, name, description, users).then(
                newRule => {
                    setRule(newRule);
                    return newRule;
                }
            );
        },
        [slug]
    )

    const updateRule = useCallback(
        async (name: string, description: string | undefined | null, isEnabled: boolean, users: number[]) => {
            if (!ruleId) { return;}
            return await updateWhitelistRule(slug, ruleId, {name, description, isEnabled, users}).then(
                updatedRule => {
                    setRule(updatedRule);
                    return updatedRule;
                }
            );
        },
        [ruleId, slug]
    )

    return {rule, createRule, updateRule};
}

export default useChatWhitelistRuleData;
