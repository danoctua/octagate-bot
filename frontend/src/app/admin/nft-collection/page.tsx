'use client';

import useNftCollectionsData from "@/hooks/data/useNftCollectionsData";
import {useRouter} from "next/navigation";
import {useMemo} from "react";
import {Avatar, ButtonCell, Cell, Section, Skeleton, Title} from "@telegram-apps/telegram-ui";
import ImageWithFallback from "@/components/ui/ImageWithFallback/ImageWithFallback";
import {CirclePlus} from "lucide-react";
import {Page} from "@/components/layout/Page";
import Header from "@/components/ui/Header/Header";
import Image from "next/image";
import {getImageUrl} from "@/utils/image";
import {getAcronymFromName} from "@/utils/text";

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
                                    <Avatar
                                        src={getImageUrl(nftCollection.logoPath)}
                                        acronym={getAcronymFromName(nftCollection.name)}
                                        size={40}
                                    />
                                }
                                subtitle={nftCollection.description}
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
                        onClick={() => router.push(`/admin/nft-collection/new`)}>
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
                <Title level={"1"} weight={"1"}>Manage Whitelisted NFT Collections</Title>
            </Header>
            <Section header={"NFT Collections"}>
                <Skeleton visible={isNftCollectionsLoading}>
                    {renderNftCollections}
                </Skeleton>
            </Section>
        </Page>
    )
}

export default NftCollectionsPage;