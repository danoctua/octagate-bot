'use client';

import {Page} from '@/components/layout/Page';
import {Skeleton, Input, Section, ButtonCell, Button, Banner} from "@telegram-apps/telegram-ui";

import ChatHeader from "@/components/layout/ChatHeader/ChatHeader";
import {useClientOnce} from "@/hooks/useClientOnce";
import {notFound, useRouter} from "next/navigation";
import {useCallback, useEffect, useMemo, useState} from 'react';
import DisplayRuleItem from "@/components/layout/Rule/DisplayRuleItem/DisplayRuleItem";
import {AlertTriangle, CirclePlus, Copy, MessageCircle, RefreshCw, Share, Trash2} from "lucide-react";
import {generateBotJoinLink} from "@/utils/bot";
import {shareURL, init, openTelegramLink, popup, themeParams} from "@telegram-apps/sdk-react";
import {copyTextToClipboard} from "@telegram-apps/sdk"
import useAdminChatData from "@/hooks/data/useAdminChatData";
import useFlashMessages from "@/hooks/useFlashMessages";
import {IChat} from "@/interfaces";
import useConfig from "@/hooks/useConfig";


const removeChatPopupButtons: {
    id: string,
    type?: "default" | "destructive" | undefined;
    text: string;
}[] = [
    {id: "remove", type: "destructive", text: "Remove"},
    {id: "cancel", type: "default", text: "Cancel"}
]


const RULE_CATEGORY_MAPPING: { [key: string]: string } = {
    jetton: "jetton",
    nft_collection: "nft-collection",
    whitelist: "whitelist",
    external_source: "whitelist-external"
}


const ChatPage = ({params}: { params: { slug: string } }) => {

    const {
        chat,
        isChatDataLoading,
        fetchChatData,
        updateChatData,
        removeChat,
        refreshChatData
    } = useAdminChatData(params.slug);
    const {pushMessage} = useFlashMessages();
    const [description, setDescription] = useState<string>("");
    const router = useRouter();
    const config = useConfig();

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
        }, [description, updateChatData]
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
                            key={`rule-${rule.category}-${rule.id}`}
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

    const onDeleteButtonClick = useCallback(
        async () => {
            if (popup.open.isAvailable()) {
                const buttonId = await popup.open({
                    title: 'Remove chat!',
                    message: 'Removing this chat will delete all created access conditions. Your chat will not be deleted.',
                    buttons: removeChatPopupButtons,
                });
                switch (buttonId) {
                    case "remove":
                        await removeChat();
                        router.push("/admin/chat");
                        break;
                    default:
                        break;
                }

            }
        }, [removeChat, router]
    )

    const chatJoinLink = useMemo(() => {
        if (!chat || !config) {
            return "";
        }
        return generateBotJoinLink(config.botUrl, chat.chat.slug);
    }, [config, chat]);

    return (
        <Page
            back={true}
        >
            <ChatHeader chat={chat?.chat} isChatDataLoading={isChatDataLoading}/>

            <Skeleton visible={isChatDataLoading} className={"flex flex-col gap-6"}>
                {chat &&
                    <>
                        {
                            chat.chat.insufficientPrivileges && (
                                <Banner
                                    before={<AlertTriangle size={32} color={themeParams.destructiveTextColor()}/>}
                                    header={"Insufficient privileges"}
                                    subheader={"Bot does not have enough privileges to manage this chat. Please, check chat admin rights."}
                                />
                            )
                        }
                        <Section
                            header={"Invite link"}
                            footer={"Share this link with your users to join the chat through the gateway."}
                        >
                            <div>
                                <div className={"w-full py-2 px-4 flex flex-col gap-2"}>
                                    <Button
                                        readOnly
                                        mode={"gray"}
                                        after={<Copy/>}
                                        onClick={
                                            () => {
                                                copyTextToClipboard(chatJoinLink).then(
                                                    () => pushMessage("Copied", "Link copied to clipboard", "info")
                                                )
                                            }
                                        }
                                    >
                                        {chatJoinLink}
                                    </Button>
                                    <div className={"flex flex-1 justify-between gap-2"}>
                                        <Button
                                            stretched
                                            before={<Share/>}
                                            onClick={() => {
                                                // Without an explicit call to init, the SDK will not be able to share the URL
                                                init();
                                                if (shareURL.isAvailable()) {
                                                    shareURL(chatJoinLink, `Join ${chat?.chat.title}`);
                                                }
                                            }}
                                        >
                                            Share
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
                                </div>
                            </div>
                        </Section>
                        <div className={"w-full"}>
                            <Input
                                placeholder={"Short description"}
                                header={"Description"}
                                value={description}
                                onBlur={onSave}
                                onChange={(event) => setDescription(event.target.value)}
                            />
                        </div>
                        <Section
                            header={"To join"}
                            footer={"Any of the rules above must be met to join the chat."}
                        >
                            {chatJoinRules}
                        </Section>
                        <Section>
                            <ButtonCell
                                before={<RefreshCw/>}
                                onClick={() => {
                                    refreshChatData().then((chatData: IChat | undefined) => {
                                        if (!chatData || !chat) {
                                            return
                                        }
                                        chatData.slug !== chat.chat.slug && router.push(`/admin/chat/${chatData.slug}`);
                                    })
                                }}
                            >
                                Refresh chat data
                            </ButtonCell>
                            <ButtonCell
                                // style={{color: "var(--tg-theme-destructive-text-color)"}}
                                mode={"destructive"}
                                onClick={onDeleteButtonClick}
                                before={<Trash2/>}
                            >
                                Remove chat
                            </ButtonCell>
                        </Section>
                    </>
                }
            </Skeleton>


        </Page>
    )
}

export default ChatPage;