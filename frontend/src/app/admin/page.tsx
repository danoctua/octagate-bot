'use client';

import Image from 'next/image';

import Header from '@/components/Header/Header';
import {Page} from '@/components/Page';
import {ButtonCell, Cell, List, Section, Skeleton} from "@telegram-apps/telegram-ui";
import useChatsData from '@/hooks/useChatsData';
import ImageWithFallback from "@/components/ImageWithFallback/ImageWithFallback";
import {ChevronRight, CirclePlus} from "lucide-react";
import {useRouter} from "next/navigation";
import FixedBottomSection from "@/components/FixedBottomSection/FixedBottomSection";
import useJettonsData from "@/hooks/useJettonsData";
import {useMemo} from "react";


const AdminPage = () => {
    const {chats, isChatsLoading} = useChatsData();
    const {jettons, isLoading: isJettonsLoading} = useJettonsData({whitelistedOnly: false});
    const router = useRouter();

    const renderChats = useMemo(
        () => {
            return (
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
                        after={<ChevronRight/>}
                        key={chat.id}
                    >
                        {chat.title}
                    </Cell>
                ))
            )
        }, [chats, router]
    )

    const renderJettons = useMemo(
        () => {
            return (
                [
                ...(
                        jettons?.map((jetton) => (
                            <Cell
                                before={
                                    <ImageWithFallback
                                        src={`/dynamic/jettons/${jetton.logoPath}`}
                                        fallbackSrc={"/welcome.gif"}
                                        width={40}
                                        height={40}
                                        rounded
                                    />
                                }
                                after={<ChevronRight/>}
                                onClick={() => router.push(`/admin/jetton/${jetton.address}`)}
                                key={jetton.address}
                            >
                                {jetton.name}
                            </Cell>
                        )) || []
                    ),
                    <ButtonCell
                        key={"--new"}
                        before={<CirclePlus/>}
                        onClick={() => router.push(`/admin/jetton`)}>
                        Add jetton
                    </ButtonCell>
                ]
            )
        }, [jettons, router]
    )

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
                        {renderChats}
                    </List>
                </Skeleton>
            </Section>
            <Section
                header={"Jettons"}
            >
                <Skeleton visible={isJettonsLoading}>
                    <List>
                        {renderJettons}
                    </List>
                </Skeleton>
            </Section>
            <FixedBottomSection text={"Add chat"} onClick={() => {
                router.push('/admin/chat')
            }}/>
        </Page>
    )
}

export default AdminPage;
