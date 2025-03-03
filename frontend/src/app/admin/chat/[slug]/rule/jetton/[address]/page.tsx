'use client';

import {Page} from "@/components/Page";
import {Title} from "@telegram-apps/telegram-ui";
import JettonRule from "@/components/Rule/JettonRule/JettonRule";



const EditJettonRulePage = ({params}: { params: { slug: string, address?: string } }) => {

    return (
        <Page back={true}>
            <div style={{padding: "44px 32px"}}>
                <Title level={"1"} plain style={{textAlign: "center"}}>
                    Hold to get access
                </Title>
            </div>
            <JettonRule chatSlug={params.slug} jettonAddress={params.address}/>
        </Page>
    )
}

export default EditJettonRulePage;
