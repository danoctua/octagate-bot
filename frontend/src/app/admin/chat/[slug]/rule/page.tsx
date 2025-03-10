'use client';

import {Page} from "@/components/Page";
import {Select, Title} from "@telegram-apps/telegram-ui";
import {useMemo, useState} from "react";
import JettonRule from "@/components/Rule/JettonRule/JettonRule";
import NftCollectionRule from "@/components/Rule/NftCollectionRule/NftCollectionRule";
import WhitelistRule from "@/components/Rule/WhitelistRule/WhitelistRule";


const TABS = [
    {title: "Token", type: "jetton"},
    {title: "NFT", type: "nftCollection"},
    {title: "Whitelist", type: "whitelist"},
    {title: "External API", type: "externalApi"},
]


const NewRulePage = ({params}: { params: { slug: string } }) => {
    const [selectedTab, setSelectedTab] = useState(TABS[0].type);

    const renderTab = useMemo(
        () => {
            switch (selectedTab) {
                case "jetton":
                    return <JettonRule chatSlug={params.slug}/>;
                case "nftCollection":
                    return <NftCollectionRule chatSlug={params.slug}/>;
                case "whitelist":
                    return <WhitelistRule chatSlug={params.slug}/>
                default:
                    return null;
            }
        }, [params.slug, selectedTab]
    );

    return (
        <Page back={true}>
            <div style={{padding: "44px 32px"}}>
                <Title level={"1"} style={{textAlign: "center"}}>
                    New condition
                </Title>
            </div>

            <Select header={"Type"} onChange={e => setSelectedTab(e.target.value)}>
                {
                    TABS.map((tab, index) => (
                        <option
                            key={index}
                            value={tab.type}
                            selected={selectedTab === tab.type}
                            onSelect={() => setSelectedTab(tab.type)}
                        >
                            {tab.title}
                        </option>
                    ))
                }
            </Select>

            {renderTab}
            {/*Not fixed bottom section as they should be owned by each tab*/}
        </Page>
    )
}

export default NewRulePage;
