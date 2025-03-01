'use client';

import {Page} from '@/components/Page';
import {Skeleton, Input, Section, Button, ButtonCell} from "@telegram-apps/telegram-ui";

import useChatData from "@/hooks/useChatData";
import ChatHeader from "@/components/ChatHeader/ChatHeader";
import {useClientOnce} from "@/hooks/useClientOnce";
import {notFound, useRouter} from "next/navigation";
import {useEffect, useMemo, useState} from 'react';
import RuleItem from "@/components/RuleItem/RuleItem";
import {CirclePlus, Share} from "lucide-react";
import FixedBottomSection from "@/components/FixedBottomSection/FixedBottomSection";
import {generateBotJoinLink} from "@/utils/bot";
import {shareURL, init} from "@telegram-apps/sdk";


const ChatPage = ({params}: { params: { slug: string } }) => {

    const {chat, isChatDataLoading, fetchChatData} = useChatData(params.slug);
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
        return ([
                ...(chat?.rules.map((rule) => (
                    <RuleItem key={rule.title} rule={rule} readOnly={false}
                              onClick={() => router.push(`/admin/chat/${chat?.chat.slug}/${rule.category}/${rule.blockchainAddress}`)}/>
                )) || []),
                <ButtonCell key={"--new"} before={<CirclePlus/>}>
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