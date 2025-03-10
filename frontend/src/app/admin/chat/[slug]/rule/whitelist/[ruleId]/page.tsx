import {Page} from "@/components/Page";
import {Title} from "@telegram-apps/telegram-ui";
import WhitelistRule from "@/components/Rule/WhitelistRule/WhitelistRule";

const EditWhitelistRulePage = ({params}: { params: { slug: string, ruleId?: number } }) => {

    return (
        <Page back={true}>
            <div style={{padding: "44px 32px"}}>
                <Title level={"1"} plain style={{textAlign: "center"}}>
                    Whitelisted users
                </Title>
            </div>
            <WhitelistRule chatSlug={params.slug} ruleId={params.ruleId}/>
        </Page>
    )
}

export default EditWhitelistRulePage;
