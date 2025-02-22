'use client';

import {Page} from '@/components/Page';
import {Skeleton, Input, Section, Cell, Button, Divider, FixedLayout} from "@telegram-apps/telegram-ui";

import useChatData from "@/hooks/useChatData";
import ChatHeader from "@/components/ChatHeader/ChatHeader";
import {useClientOnce} from "@/hooks/useClientOnce";
import {notFound} from "next/navigation";
import {useEffect, useState} from 'react';
import RuleItem from "@/components/RuleItem/RuleItem";
import {Share} from "lucide-react";


const ChatPage = ({params}: { params: { slug: string } }) => {

    const {chat, isChatDataLoading, fetchChatData} = useChatData(params.slug);
    const [description, setDescription] = useState<string>("");

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
                    {
                        chat?.rules.map((rule) => (
                            <RuleItem key={rule.title} rule={rule} readOnly={false}/>
                        ))
                    }
                </Section>
            </Skeleton>

            <FixedLayout vertical={"bottom"}>
                <Divider/>
                <div style={{ padding: "16px 8px" }}>
                    <Button stretched onClick={() => {}}>
                        Save
                    </Button>
                </div>
            </FixedLayout>
        </Page>
    )
}

export default ChatPage;