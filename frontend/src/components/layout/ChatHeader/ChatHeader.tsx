import {Avatar, Skeleton, Title} from "@telegram-apps/telegram-ui";
import React, {FC, PropsWithChildren, ReactNode} from "react";
import {IChat} from "@/interfaces";

import Header from "@/components/ui/Header/Header";
import {getAcronymFromName} from "@/utils/text";
import {getImageUrl} from "@/utils/image";


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
                        <Avatar
                            src={getImageUrl(chat.logoPath)}
                            acronym={getAcronymFromName(chat.title)}
                            size={96}
                        />
                        <Title level={"2"} weight={"2"} plain className={"flex items-center gap-2"}>
                            {chat.title}
                        </Title>
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
