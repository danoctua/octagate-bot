'use client';

import {Page} from "@/components/Page";
import {Title} from "@telegram-apps/telegram-ui";
import NftCollectionRule from "@/components/Rule/NftCollectionRule/NftCollectionRule";



const EditNftCollectionRulePage = ({params}: { params: { slug: string, address?: string } }) => {

    return (
        <Page back={true}>
            <div style={{padding: "44px 32px"}}>
                <Title level={"1"} plain style={{textAlign: "center"}}>
                    Hold to get access
                </Title>
            </div>
            <NftCollectionRule chatSlug={params.slug} nftCollectionAddress={params.address}/>
        </Page>
    )
}

export default EditNftCollectionRulePage;
