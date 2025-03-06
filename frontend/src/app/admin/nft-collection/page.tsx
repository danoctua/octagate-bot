'use client';

import useNftCollectionsData from "@/hooks/data/useNftCollectionsData";
import {useRouter} from "next/navigation";
import {useMemo} from "react";
import {ButtonCell, Cell, List, Section, Skeleton} from "@telegram-apps/telegram-ui";
import ImageWithFallback from "@/components/ImageWithFallback/ImageWithFallback";
import {ChevronRight, CirclePlus} from "lucide-react";
import {Page} from "@/components/Page";
import Header from "@/components/Header/Header";
import Image from "next/image";

const NftCollectionsPage = () => {
    const {nftCollections, isLoading: isNftCollectionsLoading} = useNftCollectionsData({whitelistedOnly: false});
    const router = useRouter();

    const renderNftCollections = useMemo(
        () => {
            return (
                [
                    ...(
                        nftCollections?.map((nftCollection) => (
                            <Cell
                                before={
                                    <ImageWithFallback
                                        src={`/dynamic/nfts/${nftCollection.logoPath}`}
                                        fallbackSrc={"/welcome.gif"}
                                        width={40}
                                        height={40}
                                        rounded
                                    />
                                }
                                after={<ChevronRight/>}
                                onClick={() => router.push(`/admin/nft-collection/${nftCollection.address}`)}
                                key={nftCollection.address}
                            >
                                {nftCollection.name}
                            </Cell>
                        )) || []
                    ),
                    <ButtonCell
                        key={"--new"}
                        before={<CirclePlus/>}
                        onClick={() => router.push(`/admin/nft-collection`)}>
                        Add NFT collection
                    </ButtonCell>
                ]
            )
        }, [nftCollections, router]
    )

    return (
        <Page back={true}>
            <Header>
                <Image src={"/lock-chat.png"} alt={""} width={120} height={120}/>
            </Header>
            <Section header={"NFT Collections"}>
                <Skeleton visible={isNftCollectionsLoading}>
                    <List>
                        {renderNftCollections}
                    </List>
                </Skeleton>
            </Section>
        </Page>
    )
}

export default NftCollectionsPage;