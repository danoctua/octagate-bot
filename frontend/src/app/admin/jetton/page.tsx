'use client';

import useJettonsData from "@/hooks/data/useJettonsData";
import {useMemo} from "react";
import {ButtonCell, Cell, Section, Skeleton, Title} from "@telegram-apps/telegram-ui";
import ImageWithFallback from "@/components/ui/ImageWithFallback/ImageWithFallback";
import {CirclePlus} from "lucide-react";
import {useRouter} from "next/navigation";
import {Page} from "@/components/layout/Page";
import Image from "next/image";
import Header from "@/components/ui/Header/Header";


const JettonsPage = () => {
    const {jettons, isLoading: isJettonsLoading} = useJettonsData({whitelistedOnly: false});
    const router = useRouter();

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
                                subtitle={jetton.name}
                                onClick={() => router.push(`/admin/jetton/${jetton.address}`)}
                                key={jetton.address}
                            >
                                {jetton.symbol}
                            </Cell>
                        )) || []
                    ),
                    <ButtonCell
                        key={"--new"}
                        before={<CirclePlus/>}
                        onClick={() => router.push(`/admin/jetton/new`)}>
                        Add jetton
                    </ButtonCell>
                ]
            )
        }, [jettons, router]
    )

    return (
        <Page back={true}>
            <Header>
                <Image src={"/lock-chat.png"} alt={""} width={120} height={120}/>
                <Title level={"1"} weight={"1"}>Manage Whitelisted Tokens</Title>
            </Header>
            <Section header={"Jettons"}>
                <Skeleton visible={isJettonsLoading}>
                    {renderJettons}
                </Skeleton>
            </Section>
        </Page>
    )
}

export default JettonsPage;
