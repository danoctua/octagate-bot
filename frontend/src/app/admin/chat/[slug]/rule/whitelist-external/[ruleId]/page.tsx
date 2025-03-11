import {Page} from "@/components/layout/Page";
import {Title} from "@telegram-apps/telegram-ui";
import WhitelistExternalRule from "@/components/layout/Rule/WhitelistExternalRule/WhitelistExternalRule";

const EditWhitelistExternalRulePage = ({params}: { params: { slug: string, ruleId?: number } }) => {

    return (
        <Page back={true}>
            <WhitelistExternalRule chatSlug={params.slug} ruleId={params.ruleId}/>
        </Page>
    )
}

export default EditWhitelistExternalRulePage;
