'use client';

import Image from 'next/image';

import Header from '@/components/ui/Header/Header';
import {Page} from '@/components/layout/Page';
import {Cell, List, Section} from "@telegram-apps/telegram-ui";
import {ChevronRight, Coins, Images, MessageCircleMore, UserCog} from "lucide-react";
import {useRouter} from "next/navigation";


const AdminPage = () => {
    const router = useRouter();

    return (
        <Page back={false}>
            <Header>
                <Image src={"/lock-chat.png"} alt={""} width={120} height={120}/>
            </Header>

            <Section
                header={"Manage"}
            >
                <List>
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
                </List>
            </Section>

        </Page>
    )
}

export default AdminPage;
