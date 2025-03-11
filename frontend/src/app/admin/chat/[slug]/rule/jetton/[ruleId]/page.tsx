'use client';

import {Page} from "@/components/layout/Page";
import {Title} from "@telegram-apps/telegram-ui";
import JettonRule from "@/components/layout/Rule/JettonRule/JettonRule";



const EditJettonRulePage = ({params}: { params: { slug: string, ruleId?: number } }) => {

    return (
        <Page back={true}>
            <JettonRule chatSlug={params.slug} ruleId={params.ruleId}/>
        </Page>
    )
}

export default EditJettonRulePage;
