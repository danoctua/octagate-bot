'use client';

import {Page} from "@/components/Page";
import {SegmentedControl, Title} from "@telegram-apps/telegram-ui";
import {useState} from "react";
import JettonRule from "@/components/Rule/JettonRule/JettonRule";


const TABS = [
    {title: "Token", type: "jetton"},
    {title: "NFT", type: "nftCollection"},
]


const NewRulePage = ({params}: { params: { slug: string } }) => {
    const [selectedTab, setSelectedTab] = useState(TABS[0].type);

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
                        <SegmentedControl.Item
                            key={index}
                            selected={selectedTab === tab.type}
                            onClick={() => setSelectedTab(tab.type)}
                        >
                            {tab.title}
                        </SegmentedControl.Item>
                    ))
                }
            </SegmentedControl>

            {
                selectedTab === "jetton" ?
                    <JettonRule chatSlug={params.slug}/> :
                    null
            }
            {/*Not fixed bottom section as they should be owned by each tab*/}
        </Page>
    )
}

export default NewRulePage;
