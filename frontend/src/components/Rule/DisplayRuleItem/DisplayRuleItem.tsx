import {IRuleEligibility} from "@/interfaces";
import {Cell, Text} from "@telegram-apps/telegram-ui";
import {Check, ChevronRight, EyeOff} from "lucide-react";
import React from "react";


const DisplayRuleItem = (
    {
        rule, readOnly, onClick
    }: {
        rule: IRuleEligibility, readOnly: boolean, onClick?: () => void
    }
) => {
    let title = ''

    if (rule.category === "jetton" || rule.category === "nft_collection") {
        title = `Hold ${rule.expected} ${rule.title}`
    } else {
        title = rule.title
    }

    let before = null;
    let after;

    if (readOnly) {
        after = (
            rule.isEligible ?
                <Check style={{color: "var(--tg-theme-accent-text-color)"}}/> :
                <Text style={{color: "var(--tg-theme-subtitle-text-color)"}}>Not yet</Text>
        )
    } else {
        before = rule.isEnabled ? null : <EyeOff/>
        after = <ChevronRight/>
    }

    return (
        <Cell
            key={`blockchain-rule-${rule.title}`}
            readOnly={readOnly}
            multiline={false}
            disabled={false}
            before={before}
            after={after}
            onClick={onClick}
        >
            {title}
        </Cell>
    );
}

export default DisplayRuleItem;
