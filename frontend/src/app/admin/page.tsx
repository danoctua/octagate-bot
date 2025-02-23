'use client';

import Image from 'next/image';

import Header from '@/components/Header/Header';
import {Page} from '@/components/Page';
import {Cell, List, Section, Skeleton} from "@telegram-apps/telegram-ui";
import useChats from '@/hooks/useChats';
import ImageWithFallback from "@/components/ImageWithFallback/ImageWithFallback";
import {ChevronRight} from "lucide-react";
import {useRouter} from "next/navigation";
import FixedBottomSection from "@/components/FixedBottomSection/FixedBottomSection";


const AdminPage = () => {
    const {chats, isChatsLoading} = useChats();
    const router = useRouter();

    return (
        <Page back={false}>
            <Header>
                <Image src={"/lock-chat.png"} alt={""} width={120} height={120}/>
            </Header>
            <Section
                header={"Groups and settings"}
            >
                <Skeleton visible={isChatsLoading}>
                    <List>
                        {chats?.map((chat) => (
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
                                after={<ChevronRight/>}
                                key={chat.id}
                            >
                                {chat.title}
                            </Cell>
                        ))}
                    </List>
                </Skeleton>
            </Section>
            <FixedBottomSection text={"Add chat"} onClick={() => {router.push('/admin/chat')}}/>
        </Page>
    )
}

export default AdminPage;
