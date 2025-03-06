'use client';

import Image from 'next/image';

import Header from '@/components/Header/Header';
import {Page} from '@/components/Page';
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
                            <MessageCircleMore/>
                        }
                        after={<ChevronRight/>}
                        onClick={() => router.push(`/admin/chat`)}
                        subtitle={"Add and configure chats"}
                    >
                        Groups and settings
                    </Cell>
                    <Cell
                        before={<Coins/>}
                        after={<ChevronRight/>}
                        onClick={() => router.push(`/admin/jetton`)}
                        subtitle={"Add and configure jettons"}
                    >
                        Jettons
                    </Cell>
                    <Cell
                        before={<Images/>}
                        after={<ChevronRight/>}
                        onClick={() => router.push(`/admin/nft-collection`)}
                        subtitle={"Add and configure NFT collections"}
                    >
                        NFT Collections
                    </Cell>
                    <Cell
                        before={<UserCog/>}
                        after={<ChevronRight/>}
                        subtitle={"Promote and manage users"}
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
