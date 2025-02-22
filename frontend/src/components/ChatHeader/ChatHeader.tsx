import {Avatar, AvatarStack, Skeleton, Text, Title} from "@telegram-apps/telegram-ui";
import React, {FC, PropsWithChildren} from "react";
import {IChat} from "@/interfaces";

import ImageWithFallback from "@/components/ImageWithFallback/ImageWithFallback";
import Header from "@/components/Header/Header";


const ChatHeader: FC<PropsWithChildren<{
    chat: IChat | undefined, isChatDataLoading?: boolean
}>> = ({
   chat,
   isChatDataLoading = false,
   children
}) => {
    return (
        <Header>
            <Skeleton visible={isChatDataLoading}>
                <ImageWithFallback
                    src={(chat?.logoPath && `/dynamic/chats/${chat?.logoPath}`) || ""}
                    fallbackSrc={"/welcome.gif"}
                    rounded
                    width={96}
                    height={96}
                />
            </Skeleton>
            <div style={{display: "flex", flexDirection: "column", gap: 8}}>
                <Skeleton visible={isChatDataLoading}>
                    <Title level={"2"} weight={"2"} plain>{chat?.title}</Title>
                </Skeleton>
                <Skeleton visible={isChatDataLoading}>
                    {chat?.description &&
                        <Text
                            style={{color: "var(--tg-theme-subtitle-text-color)"}}>{chat.description}
                        </Text>
                    }
                </Skeleton>
            </div>
            <Skeleton visible={isChatDataLoading}>
                <div style={{display: "flex", gap: 6}}>
                    <AvatarStack>
                        <Avatar
                            size={28}
                            src="https://t.me/i/userpic/160/takoy_sasha.jpg"
                        />
                        <Avatar
                            size={28}
                            src="https://t.me/i/userpic/160/danoctua.jpg"
                        />
                        <Avatar
                            size={28}
                            src="https://t.me/i/userpic/160/chak_zefir.jpg"
                        />
                    </AvatarStack>
                    <Text style={{color: "var(--tg-theme-subtitle-text-color)"}}>{chat?.membersCount} members</Text>
                </div>
            </Skeleton>
        </Header>
    )
}

export default ChatHeader;
