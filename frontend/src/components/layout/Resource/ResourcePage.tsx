'use client';

import React, {FC, PropsWithChildren, ReactNode, useCallback, useEffect, useMemo, useState} from "react";
import {Page} from "@/components/layout/Page";
import Header from "@/components/ui/Header/Header";
import {Cell, Info, Section, Skeleton, Subheadline, Switch, Title} from "@telegram-apps/telegram-ui";
import ImageWithFallback from "@/components/ui/ImageWithFallback/ImageWithFallback";
import FixedBottomSection, {FixedBottomButton} from "@/components/ui/FixedBottomSection/FixedBottomSection";
import {Link} from "@/components/functional/Link/Link";
import {ExternalLink} from "lucide-react";
import {IJetton, INftCollection} from "@/interfaces";


const ResourcePage: FC<PropsWithChildren<{
    resource?: INftCollection | IJetton,
    isLoading: boolean,
    toggleResource: (address: string, isEnabled: boolean) => Promise<INftCollection | IJetton>
    resourceStaticPath: string
    resourceType: "NFT collection" | "jetton",
    onSave: (address: string) => void,
    children?: ReactNode,
}>> = ({
           resource,
           isLoading,
           toggleResource,
           resourceStaticPath,
           resourceType,
           onSave,
           children
       }) => {
    const [isEnabled, setIsEnabled] = useState<boolean>(false);

    useEffect(() => {
        if (!resource) return
        setIsEnabled(resource.isEnabled)
    }, [resource])

    const onSaveButtonClick = useCallback(
        async () => {
            if (!resource) return
            await toggleResource(resource.address, isEnabled).then(() => onSave(resource.address))
        }, [resource, toggleResource, isEnabled, onSave]
    )

    const renderHeader = useMemo(
        () => {
            return (
                <Header>
                    {resource &&
                        <>
                            <ImageWithFallback
                                src={`${resourceStaticPath}/${resource?.logoPath}`}
                                fallbackSrc={"/welcome.gif"}
                                rounded
                                width={96}
                                height={96}
                            />
                            <div className={"flex flex-col items-center justify-center text-center gap-1"}>
                                <Title level={"1"} weight={"1"} plain>
                                    {resource?.name || `Add new ${resourceType}`}
                                </Title>
                                {resource?.address &&
                                    <Subheadline>
                                        <Link
                                            href={`https://tonviewer.com/${resource?.address}`}
                                            style={{
                                                display: "flex",
                                                gap: 4,
                                                justifyContent: "center",
                                                alignItems: "center"
                                            }}
                                        >
                                            View in explorer
                                            <ExternalLink size={"16"}/>
                                        </Link>
                                    </Subheadline>
                                }
                                {resource?.description &&
                                    <Info type={"avatarStack"}>
                                        {resource.description}
                                    </Info>
                                }
                            </div>
                        </>
                    }
                </Header>
            )
        }, [resource, resourceStaticPath, resourceType]
    )

    const renderForm = useMemo(
        () => {
            return (
                <>
                    <Section>
                        <Skeleton visible={isLoading}>
                            <Cell
                                Component={"label"}
                                after={
                                    <Switch
                                        checked={isEnabled}
                                        onChange={e => setIsEnabled(!isEnabled)}
                                    />
                                }
                                description={`Whether ${resourceType} will be displayed in the list of available ${resourceType}s`}
                            >
                                Is whitelisted
                            </Cell>
                        </Skeleton>
                    </Section>
                </>
            )
        }, [isEnabled, isLoading, resourceType]
    )

    return (
        <Page
            back
            fixedBottom={
                <FixedBottomSection
                    button={
                        <FixedBottomButton
                            text={"Save"}
                            onClick={onSaveButtonClick}
                        />
                    }
                />
            }
        >
            {renderHeader}
            {renderForm}
            {children}
        </Page>
    )
}

export default ResourcePage;
