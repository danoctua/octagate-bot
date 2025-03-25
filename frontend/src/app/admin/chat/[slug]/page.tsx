'use client';

import {Page} from '@/components/layout/Page';
import {Skeleton, Input, Section, ButtonCell, Button} from "@telegram-apps/telegram-ui";

import ChatHeader from "@/components/layout/ChatHeader/ChatHeader";
import {useClientOnce} from "@/hooks/useClientOnce";
import {notFound, useRouter} from "next/navigation";
import {useCallback, useEffect, useMemo, useState} from 'react';
import DisplayRuleItem from "@/components/layout/Rule/DisplayRuleItem/DisplayRuleItem";
import {CirclePlus, Copy, MessageCircle, RefreshCw, Share, Trash2} from "lucide-react";
import FixedBottomSection, {FixedBottomButton} from "@/components/ui/FixedBottomSection/FixedBottomSection";
import {generateBotJoinLink} from "@/utils/bot";
import {shareURL, init, openTelegramLink, popup} from "@telegram-apps/sdk-react";
import {copyTextToClipboard} from "@telegram-apps/sdk"
import useAdminChatData from "@/hooks/data/useAdminChatData";
import useFlashMessages from "@/hooks/useFlashMessages";
import {IChat} from "@/interfaces";


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

    const {chat, isChatDataLoading, fetchChatData, updateChatData, removeChat, refreshChatData} = useAdminChatData(params.slug);
    const {pushMessage} = useFlashMessages();
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

    return (
        <Page
            back={true}
            fixedBottom={
                <FixedBottomSection button={<FixedBottomButton text={"Save"} onClick={onSave} loading={isChatDataLoading}/>}/>
            }
        >
            <ChatHeader chat={chat?.chat} isChatDataLoading={isChatDataLoading}/>

            <Skeleton visible={isChatDataLoading} className={"flex flex-col gap-6"}>
                {chat &&
                    <>
                        <Section
                    header={"Invite link"}
                >
                    <div>
                        <div className={"w-full py-2 px-4 flex flex-col gap-2"}>
                            <Button
                                // disabled
                                readOnly
                                mode={"gray"}
                                after={<Copy/>}
                                onClick={
                                    () => {
                                        copyTextToClipboard(generateBotJoinLink(chat?.chat.slug || "")).then(
                                            () => pushMessage("Copied", "Link copied to clipboard", "info")
                                        )
                                    }
                                }
                            >
                                {generateBotJoinLink(chat?.chat.slug || "")}
                            </Button>
                            <div className={"flex flex-1 justify-between gap-2"}>
                                <Button
                                    stretched
                                    mode={"bezeled"}
                                    before={<Share/>}
                                    onClick={() => {
                                        // Without an explicit call to init, the SDK will not be able to share the URL
                                        init();
                                        if (shareURL.isAvailable()) {
                                            shareURL(generateBotJoinLink(chat?.chat.slug || ""), `Join ${chat?.chat.title}`);
                                        }
                                    }}
                                >
                                    Share
                                </Button>
                                <Button
                                    stretched
                                    mode={"bezeled"}
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