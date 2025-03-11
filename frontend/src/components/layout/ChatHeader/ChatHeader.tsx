import {Info, Skeleton, Title} from "@telegram-apps/telegram-ui";
import React, {FC, PropsWithChildren} from "react";
import {IChat} from "@/interfaces";

import ImageWithFallback from "@/components/ui/ImageWithFallback/ImageWithFallback";
import Header from "@/components/ui/Header/Header";


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
                {chat &&
                    <ImageWithFallback
                        src={`/dynamic/chats/${chat?.logoPath}`}
                        fallbackSrc={"/welcome.gif"}
                        rounded
                        width={96}
                        height={96}
                    />
                }
            </Skeleton>
            <div style={{display: "flex", flexDirection: "column", gap: 8}}>
                <Skeleton visible={isChatDataLoading}>
                    <Title level={"2"} weight={"2"} plain>{chat?.title}</Title>
                </Skeleton>
                <Skeleton visible={isChatDataLoading}>
                    {chat?.description &&
                        <Info type={"avatarStack"}>
                            {chat.description}
                        </Info>
                    }
                </Skeleton>
            </div>
            {/*<Skeleton visible={isChatDataLoading}>*/}
            {/*    <div style={{display: "flex", gap: 6}}>*/}
            {/*        <Info type={"avatarStack"}>{chat?.membersCount} members</Info>*/}
            {/*    </div>*/}
            {/*</Skeleton>*/}
        </Header>
    )
}

export default ChatHeader;
