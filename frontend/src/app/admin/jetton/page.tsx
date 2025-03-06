'use client';

import useJettonsData from "@/hooks/data/useJettonsData";
import {useMemo} from "react";
import {ButtonCell, Cell, List, Section, Skeleton} from "@telegram-apps/telegram-ui";
import ImageWithFallback from "@/components/ImageWithFallback/ImageWithFallback";
import {ChevronRight, CirclePlus} from "lucide-react";
import {useRouter} from "next/navigation";
import {Page} from "@/components/Page";
import Image from "next/image";
import Header from "@/components/Header/Header";


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
            </Header>
            <Section header={"Jettons"}>
                <Skeleton visible={isJettonsLoading}>
                    <List>
                        {renderJettons}
                    </List>
                </Skeleton>
            </Section>
        </Page>
    )
}

export default JettonsPage;
