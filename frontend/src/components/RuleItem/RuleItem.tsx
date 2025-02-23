import { IRule } from "@/interfaces";
import { Cell, Text } from "@telegram-apps/telegram-ui";
import {Check, ChevronRight} from "lucide-react";
import React from "react";


const RuleItem = ({ rule, readOnly }: { rule: IRule, readOnly: boolean}) => {
    let title = ''

    if (rule.category === "jetton" || rule.category === "nft-collection") {
        title = `Hold ${rule.expected} ${rule.title}`
    } else {
        title = rule.title
    }

    let after;

    if (readOnly) {
        after = (
            rule.isEligible ?
                <Check style={{ color: "var(--tg-theme-accent-text-color)" }}/> :
                <Text style={{color: "var(--tg-theme-subtitle-text-color)"}}>Not yet</Text>
        )
    } else {
        after = <ChevronRight/>
    }

    return (
        <Cell
            key={`blockchain-rule-${rule.title}`}
            readOnly={readOnly}
            multiline={false}
            disabled={false}
            after={after}
        >
            {title}
        </Cell>
    );
}

export default RuleItem;
