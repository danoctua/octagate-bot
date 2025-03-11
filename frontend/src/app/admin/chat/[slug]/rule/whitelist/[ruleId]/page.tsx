import {Page} from "@/components/layout/Page";
import {Title} from "@telegram-apps/telegram-ui";
import WhitelistRule from "@/components/layout/Rule/WhitelistRule/WhitelistRule";

const EditWhitelistRulePage = ({params}: { params: { slug: string, ruleId?: number } }) => {

    return (
        <Page back={true}>
            <WhitelistRule chatSlug={params.slug} ruleId={params.ruleId}/>
        </Page>
    )
}

export default EditWhitelistRulePage;
