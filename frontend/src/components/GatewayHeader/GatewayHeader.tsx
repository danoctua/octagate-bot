import {Avatar, AvatarStack, Text, Title} from "@telegram-apps/telegram-ui";
import React, {FC, PropsWithChildren} from "react";
import {IChat} from "@/interfaces";

import ImageWithFallback from "@/components/ImageWithFallback/ImageWithFallback";


const GatewayHeader: FC<PropsWithChildren<{chat: IChat}>> = ({chat, children}) => {
    return (
        <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            padding: "40px 16px",
            paddingTop: 48,
            gap: 12,
            textAlign: "center"
        }}>
            <ImageWithFallback
                src={`/dynamic/chats/${chat.logoPath}`}
                fallbackSrc={"/welcome.gif"}
                rounded
                width={96}
                height={96}
            />
            <div style={{display: "flex", flexDirection: "column", gap: 8}}>
                <Title level={"2"} weight={"2"} plain>{chat.title}</Title>
                {chat.description &&
                    <Text
                        style={{color: "var(--tg-theme-subtitle-text-color)"}}>{chat.description}
                    </Text>
                }
            </div>
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
                <Text style={{color: "var(--tg-theme-subtitle-text-color)"}}>{chat.membersCount} members</Text>
            </div>
        </div>
    )
}

export default GatewayHeader;
