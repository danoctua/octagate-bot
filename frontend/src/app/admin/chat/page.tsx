'use client';

import useChatsData from "@/hooks/data/useChatsData";
import {useMemo} from "react";
import {Avatar, ButtonCell, Cell, Section, Skeleton, Title} from "@telegram-apps/telegram-ui";
import {CirclePlus} from "lucide-react";
import {useRouter} from "next/navigation";
import Header from "@/components/ui/Header/Header";
import Image from "next/image";
import {Page} from "@/components/layout/Page";
import {getAcronymFromName} from "@/utils/text";


const ChatsPage = () => {
    const {chats, isChatsLoading} = useChatsData();
    const router = useRouter();

    const renderChats = useMemo(
        () => {
            return (
                [
                    ...(
                        chats?.map((chat) => (
                            <Cell
                                before={
                                    <Avatar
                                        src={`/dynamic/chats/${chat.logoPath}`}
                                        acronym={getAcronymFromName(chat.title)}
                                        size={40}
                                    />
                                }
                                onClick={() => router.push(`/admin/chat/${chat.slug}`)}
                                subtitle={chat.description}
                                key={chat.id}
                            >
                                {chat.title}
                            </Cell>
                        )) || []
                    ),
                    <ButtonCell
                        key={"--new-chat"}
                        before={<CirclePlus/>}
                        onClick={() => router.push('/admin/chat/new')}>
                        Add chat
                    </ButtonCell>
                ]
            )
        }, [chats, router]
    )

    return (
        <Page back={true}>
            <Header>
                <Image src={"/lock-chat.png"} alt={""} width={120} height={120}/>
                <Title level={"1"} weight={"1"}>Manage Your Private Telegram Chats</Title>
            </Header>


            <Skeleton visible={isChatsLoading}>
                <Section
                    header={"Groups and settings"}
                >
                    {renderChats}
                </Section>
            </Skeleton>
        </Page>
    )
}

export default ChatsPage;
