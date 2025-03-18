'use client';

import {Page} from "@/components/layout/Page";
import {SegmentedControl, Title} from "@telegram-apps/telegram-ui";
import {useMemo, useState} from "react";
import JettonRule from "@/components/layout/Rule/JettonRule/JettonRule";
import NftCollectionRule from "@/components/layout/Rule/NftCollectionRule/NftCollectionRule";
import WhitelistRule from "@/components/layout/Rule/WhitelistRule/WhitelistRule";
import WhitelistExternalRule from "@/components/layout/Rule/WhitelistExternalRule/WhitelistExternalRule";
import {miniApp, useSignal} from "@telegram-apps/sdk-react";


const TABS = [
    {title: "Token", type: "jetton"},
    {title: "NFT", type: "nftCollection"},
    {title: "ID Match", type: "whitelist"},
    {title: "API check", type: "externalApi"},
]


const NewRulePage = ({params}: { params: { slug: string } }) => {
    const [selectedTab, setSelectedTab] = useState(TABS[0].type);
    const isDark = useSignal(miniApp.isDark);

    const renderTab = useMemo(
        () => {
            switch (selectedTab) {
                case "jetton":
                    return <JettonRule chatSlug={params.slug}/>;
                case "nftCollection":
                    return <NftCollectionRule chatSlug={params.slug}/>;
                case "whitelist":
                    return <WhitelistRule chatSlug={params.slug}/>
                case "externalApi":
                    return <WhitelistExternalRule chatSlug={params.slug}/>
                default:
                    return null;
            }
        }, [params.slug, selectedTab]
    );

    return (
        <Page back={true}>
            <>
                <div>
                    <div style={{padding: "44px 32px"}}>
                        <Title level={"1"} weight={"1"} style={{textAlign: "center"}}>
                            Add condition
                        </Title>
                    </div>

                    <SegmentedControl
                        style={{background: isDark ? "#2F2F2F" : "#F6F6FA"}}
                    >
                        {
                            TABS.map((tab, index) => (
                                <SegmentedControl.Item
                                    style={{background: selectedTab === tab.type ? "var(--tgui--bg_color)" : "transparent"}}
                                    key={index}
                                    selected={selectedTab === tab.type}
                                    onClick={() => setSelectedTab(tab.type)}
                                >
                                    {tab.title}
                                </SegmentedControl.Item>
                            ))
                        }
                    </SegmentedControl>
                </div>
            </>

            {renderTab}
            {/*Not fixed bottom section as they should be owned by each tab*/}
        </Page>
    )
}

export default NewRulePage;
