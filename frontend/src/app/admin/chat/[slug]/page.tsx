'use client';

import {Page} from '@/components/layout/Page';
import {Skeleton, Input, Section, ButtonCell, InlineButtons} from "@telegram-apps/telegram-ui";

import ChatHeader from "@/components/layout/ChatHeader/ChatHeader";
import {useClientOnce} from "@/hooks/useClientOnce";
import {notFound, useRouter} from "next/navigation";
import {useEffect, useMemo, useState} from 'react';
import DisplayRuleItem from "@/components/layout/Rule/DisplayRuleItem/DisplayRuleItem";
import {CirclePlus, MessageCircle, Share} from "lucide-react";
import FixedBottomSection from "@/components/ui/FixedBottomSection/FixedBottomSection";
import {generateBotJoinLink} from "@/utils/bot";
import {shareURL, init, openTelegramLink} from "@telegram-apps/sdk-react";
import useAdminChatData from "@/hooks/data/useAdminChatData";


const RULE_CATEGORY_MAPPING: { [key: string]: string } = {
    jetton: "jetton",
    nft_collection: "nft-collection",
    whitelist: "whitelist",
    external_source: "whitelist-external"
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
                    <InlineButtons>
                        <InlineButtons.Item
                            text={"Share join link"}
                            mode={"bezeled"}
                            onClick={() => {
                                // Without an explicit call to init, the SDK will not be able to share the URL
                                init();
                                if (shareURL.isAvailable()) {
                                    shareURL(generateBotJoinLink(chat?.chat.slug || ""), `Join ${chat?.chat.title}`);
                                }
                            }}
                        >
                            <Share/>
                        </InlineButtons.Item>
                        <InlineButtons.Item
                            text={"Open chat"}
                            mode={"bezeled"}
                            onClick={() => {
                                chat?.chat.joinUrl && openTelegramLink(chat?.chat.joinUrl)
                            }}
                        >
                            <MessageCircle/>
                        </InlineButtons.Item>
                    </InlineButtons>
                </Skeleton>
            </div>

            <Skeleton visible={isChatDataLoading}>
                <Input
                    placeholder={"Short description"}
                    value={description}
                    onChange={(event) => setDescription(event.target.value)}
                />
                <Section
                    header={"To join"}
                    footer={"Any of the rules above must be met to join the chat."}
                >
                    {chatJoinRules}
                </Section>
            </Skeleton>

            <FixedBottomSection text={"Save"} onClick={() => {
            }}/>
        </Page>
    )
}

export default ChatPage;