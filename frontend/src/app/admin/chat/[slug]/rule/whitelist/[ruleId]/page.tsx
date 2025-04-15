import {Page} from "@/components/layout/Page";
import WhitelistRule from "@/components/layout/Rule/WhitelistRule/WhitelistRule";

const EditWhitelistRulePage = ({params}: { params: { slug: string, ruleId?: number } }) => {

    return (
        <Page back={true}>
            <WhitelistRule chatSlug={params.slug} ruleId={params.ruleId}/>
        </Page>
    )
}

export default EditWhitelistRulePage;
