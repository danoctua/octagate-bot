import {IRuleEligibility} from "@/interfaces";
import {Cell, Text} from "@telegram-apps/telegram-ui";
import {Check, Coins, ExternalLink, Images, ListCheck} from "lucide-react";
import React from "react";


const DisplayRuleItem = (
    {
        rule, readOnly, onClick
    }: {
        rule: IRuleEligibility, readOnly: boolean, onClick?: () => void
    }
) => {
    let title = '';
    let subtitle = null;

    if (rule.category === "jetton" || rule.category === "nft_collection") {
        title = `Hold ${rule.expected} ${rule.title}`
        if (rule.category === "nft_collection") {
            subtitle = rule.requiredAttributes && rule.requiredAttributes.length > 0 ?
                rule.requiredAttributes.map(attribute => `${attribute.traitType}: ${attribute.value}`).join(", ") :
                null
        }
    } else {
        title = rule.title
    }

    let before = null;
    let after;

    const defaultBeforeAfterStyle = { color: "var(--tg-theme-subtitle-text-color)" }

    if (readOnly) {
        after = (
            rule.isEligible ?
                <Check style={{color: "var(--tg-theme-accent-text-color)"}}/> :
                <Text className={"whitespace-nowrap"} style={defaultBeforeAfterStyle}>Not yet</Text>
        )
    } else {
        switch (rule.category) {
            case "jetton":
                before = <Coins style={defaultBeforeAfterStyle}/>
                break;
            case "nft_collection":
                before = <Images style={defaultBeforeAfterStyle}/>
                break;
            case "whitelist":
                before = <ListCheck style={defaultBeforeAfterStyle}/>
                break;
            case "external_source":
                before = <ExternalLink style={defaultBeforeAfterStyle}/>
                break
        }
        after = null
    }

    return (
        <Cell
            key={`blockchain-rule-${rule.title}`}
            readOnly={readOnly}
            multiline={false}
            disabled={false}
            after={after}
            onClick={onClick}
            style={rule.isEnabled ? undefined: {...defaultBeforeAfterStyle, textDecoration: "line-through"}}
            subtitle={subtitle}
        >
            {title}
        </Cell>
    );
}

export default DisplayRuleItem;
