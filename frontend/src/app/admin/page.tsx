'use client';

import Image from 'next/image';

import Header from '@/components/ui/Header/Header';
import {Page} from '@/components/layout/Page';
import {Cell, Section, Title} from "@telegram-apps/telegram-ui";
import {Coins, Images, MessageCircleMore, UserCog} from "lucide-react";
import {useRouter} from "next/navigation";
import useAuthAdmin from "@/hooks/data/useAuthAndFetchAdminUser";


const AdminPage = () => {
    const {isAdminUserAuthenticated} = useAuthAdmin()
    const router = useRouter();

    return (
        <Page back={false}>
            {isAdminUserAuthenticated ?
                <>
                    <Header>
                        <Image src={"/lock-chat.png"} alt={""} width={120} height={120}/>
                        <Title level={"1"} weight={"1"}>Manage Your Private Telegram Chats</Title>
                    </Header>

                    <Section
                        header={"Manage"}
                    >
                        <Cell
                            before={
                                <MessageCircleMore color={"var(--tg-theme-hint-color)"}/>
                            }
                            onClick={() => router.push(`/admin/chat`)}
                        >
                            Groups and settings
                        </Cell>
                        <Cell
                            before={<Coins color={"var(--tg-theme-hint-color)"}/>}
                            onClick={() => router.push(`/admin/jetton`)}
                        >
                            Jettons
                        </Cell>
                        <Cell
                            before={<Images color={"var(--tg-theme-hint-color)"}/>}
                            onClick={() => router.push(`/admin/nft-collection`)}
                        >
                            NFT Collections
                        </Cell>
                        <Cell
                            before={<UserCog color={"var(--tg-theme-hint-color)"}/>}
                            disabled
                        >
                            Users
                        </Cell>
                    </Section>
                </>: <div className={"flex flex-1 justify-center items-center"}>Loading...</div>
            }

        </Page>
    )
}

export default AdminPage;
