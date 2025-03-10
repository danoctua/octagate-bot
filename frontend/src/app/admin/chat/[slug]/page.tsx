'use client';

import {Page} from '@/components/Page';
import {Skeleton, Input, Section, Button, ButtonCell} from "@telegram-apps/telegram-ui";

import ChatHeader from "@/components/ChatHeader/ChatHeader";
import {useClientOnce} from "@/hooks/useClientOnce";
import {notFound, useRouter} from "next/navigation";
import {useEffect, useMemo, useState} from 'react';
import DisplayRuleItem from "@/components/Rule/DisplayRuleItem/DisplayRuleItem";
import {CirclePlus, Share} from "lucide-react";
import FixedBottomSection from "@/components/FixedBottomSection/FixedBottomSection";
import {generateBotJoinLink} from "@/utils/bot";
import {shareURL, init} from "@telegram-apps/sdk-react";
import useAdminChatData from "@/hooks/data/useAdminChatData";


const RULE_CATEGORY_MAPPING: { [key: string]: string } = {
    jetton: "jetton",
    nft_collection: "nft-collection",
    whitelist: "whitelist",
    external_source: "external-api"
}


const ChatPage = ({params}: { params: { slug: string } }) => {

    const {chat, isChatDataLoading, fetchChatData} = useAdminChatData(params.slug);
    const [description, setDescription] = useState<string>("");
    const router = useRouter();

    useClientOnce(() => {
        fetchChatData().then().catch((e) => {
            console.error(e);
            notFound();
        });
    })

    useEffect(() => {
        if (chat && chat.chat.description && !description) {
            setDescription(chat.chat.description);
        }
    }, [chat, description])

    if (!params.slug) {
        notFound();
    }

    const chatJoinRules = useMemo(() => {
        return (
            [
                ...(
                    chat?.rules.map((rule) => (
                        <DisplayRuleItem
                            key={rule.title}
                            rule={rule}
                            readOnly={false}
                            onClick={() => router.push(`/admin/chat/${chat?.chat.slug}/rule/${RULE_CATEGORY_MAPPING[rule.category]}/${rule.id}`)}
                        />
                    )) || []
                ),
                <ButtonCell
                    key={"--new"}
                    before={<CirclePlus/>}
                    onClick={() => router.push(`/admin/chat/${chat?.chat.slug}/rule`)}
                >
                    Add condition
                </ButtonCell>
            ]
        )
    }, [chat?.chat.slug, chat?.rules, router])

    return (
        <Page back={true}>
            <ChatHeader chat={chat?.chat} isChatDataLoading={isChatDataLoading}/>
            <div style={{padding: "16px 8px"}}>
                <Skeleton visible={isChatDataLoading}>
                    <Button
                        before={<Share/>}
                        mode={"bezeled"}
                        stretched
                        onClick={() => {
                            // Without an explicit call to init, the SDK will not be able to share the URL
                            init();
                            if (shareURL.isAvailable()) {
                                shareURL(generateBotJoinLink(chat?.chat.slug || ""), `Join ${chat?.chat.title}`);
                            }
                        }}
                    >
                        Share join link
                    </Button>
                </Skeleton>
            </div>

            <Skeleton visible={isChatDataLoading}>
                <Input placeholder={"Short description"} value={description}
                       onChange={(event) => setDescription(event.target.value)}/>
                <Section header={"To join"}>
                    {chatJoinRules}
                </Section>
            </Skeleton>

            <FixedBottomSection text={"Save"} onClick={() => {
            }}/>
        </Page>
    )
}

export default ChatPage;