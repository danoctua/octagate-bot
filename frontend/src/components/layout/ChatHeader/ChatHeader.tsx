import {Info, Skeleton, Title} from "@telegram-apps/telegram-ui";
import React, {FC, PropsWithChildren, ReactNode} from "react";
import {IChat} from "@/interfaces";

import ImageWithFallback from "@/components/ui/ImageWithFallback/ImageWithFallback";
import Header from "@/components/ui/Header/Header";


const ChatHeader: FC<PropsWithChildren<{
    chat: IChat | undefined, isChatDataLoading?: boolean, children?: ReactNode
}>> = ({
           chat,
           isChatDataLoading = false,
           children
       }) => {
    return (
        <Header>
            <Skeleton visible={isChatDataLoading}>
                {chat &&
                    <div className={"w-full flex items-center justify-center flex-col gap-2"}>
                        <ImageWithFallback
                            src={`/dynamic/chats/${chat?.logoPath}`}
                            fallbackSrc={"/welcome.gif"}
                            rounded
                            width={96}
                            height={96}
                        />
                        <Title level={"2"} weight={"2"} plain>{chat?.title}</Title>
                    </div>
                }
            </Skeleton>
            {children}
            {/*<Skeleton visible={isChatDataLoading}>*/}
            {/*    <div style={{display: "flex", gap: 6}}>*/}
            {/*        <Info type={"avatarStack"}>{chat?.membersCount} members</Info>*/}
            {/*    </div>*/}
            {/*</Skeleton>*/}
        </Header>
    )
}

export default ChatHeader;
