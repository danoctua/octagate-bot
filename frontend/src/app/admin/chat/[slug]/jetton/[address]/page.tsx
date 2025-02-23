'use client';

import {Page} from "@/components/Page";
import {SegmentedControl, Skeleton, Title} from "@telegram-apps/telegram-ui";
import {
    SegmentedControlItem
} from "@telegram-apps/telegram-ui/dist/components/Navigation/SegmentedControl/components/SegmentedControlItem/SegmentedControlItem";
import {useEffect, useState} from "react";
import useChatJettonRuleData from "@/hooks/useChatJettonRuleData";
import SelectableRule from "@/components/SelectableRule/SelectableRule";
import useJettonsData from "@/hooks/useJettonsData";
import FixedBottomSection from "@/components/FixedBottomSection/FixedBottomSection";


const TABS = [
    {title: "Token", type: "jetton"},
    {title: "NFT", type: "nftCollection"},
]


const RulePage = ({params}: { params: { slug: string, address: string } }) => {
    const [selectedTab, setSelectedTab] = useState(TABS[0].type);
    const jettons = useJettonsData()
    const chatJettonRuleData = useChatJettonRuleData({slug: params.slug, jettonAddress: params.address})
    const [selectedJettonAddress, setSelectedJettonAddress] = useState<string>("")
    const [expected, setExpected] = useState(0)

    useEffect(() => {
        if (!chatJettonRuleData) return
        setExpected(chatJettonRuleData.expected)
        setSelectedJettonAddress(chatJettonRuleData.blockchainAddress)
    }, [chatJettonRuleData]);

    return (
        <Page back={true}>
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
            {chatJettonRuleData ?
                <SelectableRule
                    items={jettons}
                    category={"jettons"}
                    selectedOption={selectedJettonAddress}
                    onSelect={setSelectedJettonAddress}
                    expected={expected}
                    onExpectedChange={setExpected}
                /> : <Skeleton/>
            }
            <FixedBottomSection text={"Save"} onClick={() => {}}/>
        </Page>
    )
}

export default RulePage;
