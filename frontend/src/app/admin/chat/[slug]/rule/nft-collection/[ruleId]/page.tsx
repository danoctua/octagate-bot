'use client';

import {Page} from "@/components/layout/Page";
import {Title} from "@telegram-apps/telegram-ui";
import NftCollectionRule from "@/components/layout/Rule/NftCollectionRule/NftCollectionRule";



const EditNftCollectionRulePage = ({params}: { params: { slug: string, ruleId?: number } }) => {

    return (
        <Page back={true}>
            <NftCollectionRule chatSlug={params.slug} ruleId={params.ruleId}/>
        </Page>
    )
}

export default EditNftCollectionRulePage;
