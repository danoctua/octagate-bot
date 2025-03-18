'use client';

import {useCallback, useMemo, useState} from "react";
import {Input} from "@telegram-apps/telegram-ui";
import FixedBottomSection, {FixedBottomButton} from "@/components/ui/FixedBottomSection/FixedBottomSection";
import {useRouter} from "next/navigation";
import BannerPage from "@/components/layout/BannerPage/BannerPage";
import {Link} from "@/components/functional/Link/Link";
import useChatData from "@/hooks/data/useChatData";
import {IChat} from "@/interfaces";
import {AxiosError} from "axios";


const regex = /^(-?\d+(\.\d+)?)$|^(https:\/\/t\.me\/[a-zA-Z0-9_]{4,32})$/


const NewChatPage = () => {
    const [chatIdentifier, setChatIdentifier] = useState<string | null>(null);
    const [isDisabled, setIsDisabled] = useState<boolean>(true);
    const [isPermissionError, setIsPermissionError] = useState<boolean>(false);
    const [newChatSlug, setNewChatSlug] = useState<string | null>(null);
    const router = useRouter();

    const { addChat, isChatDataLoading } = useChatData();

    const validateChatIdentifier = (newChatIdentifier: string) => {
        if (!newChatIdentifier) {
            return true;
        }
        return regex.test(newChatIdentifier);
    }

    const setChatIdOnChange = useCallback(
        (input: string) => {
            if (!input) {
                setChatIdentifier(null);
                setIsDisabled(true);
                return;
            }
            setChatIdentifier(input);
            const isValid = validateChatIdentifier(input);
            setIsDisabled(!isValid);
        },
        []
    )

    const onAddChatButtonClick = useCallback(
        () => {
            if (!chatIdentifier || isDisabled || isChatDataLoading) {
                return;
            }
            addChat(chatIdentifier).then(
                (chat: IChat | undefined) => {
                    chat && setNewChatSlug(chat.slug);
                }
            ).catch(
                (e: AxiosError) => {
                    if (e.response && e.response.status === 409) {
                        setIsPermissionError(true)
                    } else {
                        throw e
                    }
                }
            );
        },
        [addChat, chatIdentifier, isChatDataLoading, isDisabled]
    )

    return useMemo(() => {
        if (isPermissionError) {
            return (
                <BannerPage
                    logoUrl={"/chain.png"}
                    title={"Add Gateway bot to the chat"}
                    subtitle={"The bot required to manage access. Add it to the chat before continuing. Bot doesn’t read messages inside the chat. "}
                    fixedBottom={
                        <FixedBottomSection
                            button={
                                <FixedBottomButton
                                    text={"Back to configuration"}
                                    onClick={() => setIsPermissionError(false)}
                                />
                            }
                        />
                    }
                />
            )
        } else if (newChatSlug) {
            return (
                <BannerPage
                    back
                    logoUrl={"/confetti.png"}
                    title={"Chat Added. Configure it"}
                    subtitle={"Great! Your chat is now connected to Gateway. Now it’s time to set access conditions."}
                    fixedBottom={
                        <FixedBottomSection
                            button={
                                <FixedBottomButton
                                    text={"Set Access Conditions"}
                                    onClick={() => router.push(`/admin/chat/${newChatSlug}`)}
                                />
                            }
                        />
                    }
                />
            )
        }
        return (
            <BannerPage
                logoUrl={"/chain.png"}
                title={"Add Telegram Chat"}
                subtitle={
                    <div className={"flex flex-col items-center"}>
                        <div>Enter your Telegram group link or chat ID (e.g. @yourgroup or -1001234567890).</div>
                        <Link href={"https://t.me/telegram"} target={"_blank"}>
                            Where to find group link or chat ID?
                        </Link>
                    </div>
                }
                fixedBottom={
                    <FixedBottomSection
                        button={
                            <FixedBottomButton
                                text={"Continue"}
                                disabled={isDisabled || isChatDataLoading}
                                loading={isChatDataLoading}
                                onClick={onAddChatButtonClick}
                            />
                        }
                    />
                }
            >
                <Input
                    placeholder={"Chat or channel ID"}
                    value={chatIdentifier || ""}
                    onChange={(event) => setChatIdOnChange(event.target.value)}
                />
            </BannerPage>
        )
    }, [chatIdentifier, isDisabled, isChatDataLoading, isPermissionError, newChatSlug, onAddChatButtonClick, router, setChatIdOnChange])
}


export default NewChatPage;
