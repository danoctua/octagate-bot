'use client';

import useChatsData from "@/hooks/data/useChatsData";
import {useMemo} from "react";
import {ButtonCell, Cell, List, Section, Skeleton} from "@telegram-apps/telegram-ui";
import ImageWithFallback from "@/components/ImageWithFallback/ImageWithFallback";
import {ChevronRight, CirclePlus} from "lucide-react";
import {useRouter} from "next/navigation";
import Header from "@/components/Header/Header";
import Image from "next/image";
import {Page} from "@/components/Page";


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
                                    <ImageWithFallback
                                        src={`/dynamic/chats/${chat.logoPath}`}
                                        fallbackSrc={"/welcome.gif"}
                                        width={40}
                                        height={40}
                                        rounded
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
            </Header>


            <Skeleton visible={isChatsLoading}>
                <Section
                    header={"Groups and settings"}
                >
                    <List>
                        {renderChats}
                    </List>
                </Section>
            </Skeleton>
        </Page>
    )
}

export default ChatsPage;
