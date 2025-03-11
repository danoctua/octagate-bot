import {Page} from "@/components/Page";
import {Title} from "@telegram-apps/telegram-ui";
import WhitelistExternalRule from "@/components/Rule/WhitelistExternalRule/WhitelistExternalRule";

const EditWhitelistExternalRulePage = ({params}: { params: { slug: string, ruleId?: number } }) => {

    return (
        <Page back={true}>
            <div style={{padding: "44px 32px"}}>
                <Title level={"1"} plain style={{textAlign: "center"}}>
                    External source whitelist
                </Title>
            </div>
            <WhitelistExternalRule chatSlug={params.slug} ruleId={params.ruleId}/>
        </Page>
    )
}

export default EditWhitelistExternalRulePage;
