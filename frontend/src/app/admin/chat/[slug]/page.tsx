'use client';

import {Page} from '@/components/layout/Page';
import {Skeleton, Input, Section, ButtonCell, Button} from "@telegram-apps/telegram-ui";

import ChatHeader from "@/components/layout/ChatHeader/ChatHeader";
import {useClientOnce} from "@/hooks/useClientOnce";
import {notFound, useRouter} from "next/navigation";
import {useCallback, useEffect, useMemo, useState} from 'react';
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

    const {chat, isChatDataLoading, fetchChatData, updateChatData} = useAdminChatData(params.slug);
    const [description, setDescription] = useState<string>("");
    const router = useRouter();

    useClientOnce(() => {
        fetchChatData().then().catch((e) => {
            console.error(e);
            notFound();
        });
    })

    useEffect(() => {
        if (chat) {
            setDescription(chat.chat.description || "");
        }
    }, [chat])

    const onSave = useCallback(
        async () => {
            await updateChatData(description);
            router.push("/admin/chat");
        }, [description, router, updateChatData]
    )

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
            <div style={{padding: "16px 22px"}}>
                <Skeleton visible={isChatDataLoading}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: "8px" }}>
                        <Button
                            stretched
                            before={<Share/>}
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
                        <Button
                            stretched
                            before={<MessageCircle/>}
                            onClick={() => {
                                chat?.chat.joinUrl && openTelegramLink(chat?.chat.joinUrl)
                            }}
                        >
                            Open chat
                        </Button>
                    </div>
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

            <FixedBottomSection text={"Save"} onClick={onSave}/>
        </Page>
    )
}

export default ChatPage;