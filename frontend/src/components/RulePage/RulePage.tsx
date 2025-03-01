'use client';

import {SegmentedControl, Title} from "@telegram-apps/telegram-ui";
import {
    SegmentedControlItem
} from "@telegram-apps/telegram-ui/dist/components/Navigation/SegmentedControl/components/SegmentedControlItem/SegmentedControlItem";
import {FC, PropsWithChildren, useState} from "react";
import {IRule} from "@/interfaces";


const TABS = [
    {title: "Token", type: "jetton"},
    {title: "NFT", type: "nftCollection"},
]


const RulePage: FC<PropsWithChildren<{ruleData: IRule, type: string}>> = ({ruleData, type, children}) => {
    const [selectedTab, setSelectedTab] = useState(type);

    return (
        <>
            <div style={{padding: "44px 32px"}}>
                <Title level={"1"} plain style={{textAlign: "center"}}>
                    Hold to get access
                </Title>
            </div>
            <SegmentedControl>
                {
                    TABS.map((tab, index) => (
                        <SegmentedControlItem
                            key={index}
                            selected={selectedTab === tab.type}
                            onClick={() => setSelectedTab(tab.type)}
                        >
                            {tab.title}
                        </SegmentedControlItem>
                    ))
                }
            </SegmentedControl>
            {children}
        </>
    )
}

export default RulePage
