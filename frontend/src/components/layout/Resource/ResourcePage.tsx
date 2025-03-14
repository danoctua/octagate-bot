'use client';

import React, {ChangeEvent, FC, PropsWithChildren, ReactNode, useCallback, useEffect, useMemo, useState} from "react";
import {Page} from "@/components/layout/Page";
import Header from "@/components/ui/Header/Header";
import {Cell, Info, Input, Section, Skeleton, Subheadline, Switch, Title} from "@telegram-apps/telegram-ui";
import ImageWithFallback from "@/components/ui/ImageWithFallback/ImageWithFallback";
import FixedBottomSection from "@/components/ui/FixedBottomSection/FixedBottomSection";
import {Link} from "@/components/functional/Link/Link";
import {ExternalLink} from "lucide-react";
import {IJetton, INftCollection} from "@/interfaces";

const addressRegex = /^EQ[0-9A-Za-z\_\+\-\/]{46}$/;

const ResourcePage: FC<PropsWithChildren<{
    inputAddress?: string
    resource?: INftCollection | IJetton,
    isLoading: boolean,
    addResource: (address: string) => Promise<INftCollection | IJetton>,
    toggleResource: (address: string, isEnabled: boolean) => Promise<INftCollection | IJetton>
    resourceStaticPath: string
    resourceType: "NFT collection" | "jetton",
    onNewResourceCreated: (address: string) => void,
    children?: ReactNode,
}>> = ({
           inputAddress,
           resource,
           isLoading,
           addResource,
           toggleResource,
           resourceStaticPath,
           resourceType,
           onNewResourceCreated,
           children
       }) => {
    const [address, setAddress] = useState<string>(inputAddress || "");
    const [addressError, setAddressError] = useState<string | undefined>(undefined);
    const [isEnabled, setIsEnabled] = useState<boolean>(false);
    const [isFormValid, setIsFormValid] = useState<boolean>(false);
    const [expandedId, setExpandedId] = useState<number | undefined>(undefined);

    useEffect(() => {
        if (!resource) return
        setAddress(resource.address)
        setIsEnabled(resource.isEnabled)
        setIsFormValid(true)
    }, [resource])

    const onAddressChange = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => {
            if (inputAddress) return

            const newAddress = e.target.value
            setAddress(newAddress)
            if (addressRegex.test(newAddress)) {
                setIsFormValid(true)
                setAddressError(undefined)
            } else {
                setIsFormValid(false)
                setAddressError(`Invalid ${resourceType} address. It should be a valid bounceable address`)
            }

        }, [inputAddress, resourceType]
    )

    const onSaveButtonClick = useCallback(
        async () => {
            if (inputAddress) {
                await toggleResource(address, isEnabled)
            } else {
                await addResource(address)
                onNewResourceCreated(address)
            }
        }, [addResource, address, inputAddress, isEnabled, onNewResourceCreated, toggleResource]
    )

    const renderHeader = useMemo(
        () => {
            return (
                <Header>
                    <Skeleton visible={isLoading}>
                        {resource?.logoPath &&
                            <ImageWithFallback
                                src={`${resourceStaticPath}/${resource.logoPath}`}
                                fallbackSrc={"/welcome.gif"}
                                rounded
                                width={96}
                                height={96}
                            />
                        }
                    </Skeleton>
                    <div style={{display: "flex", flexDirection: "column", gap: 8}}>
                        <Skeleton visible={isLoading}>
                            <Title level={"2"} weight={"2"} plain>
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
                        </Skeleton>
                        <Skeleton visible={isLoading}>
                            {resource?.description &&
                                <Info type={"avatarStack"}>
                                    {resource.description}
                                </Info>
                            }
                        </Skeleton>
                    </div>
                </Header>
            )
        }, [isLoading, resource, resourceStaticPath, resourceType]
    )

    const renderForm = useMemo(
        () => {
            return (
                <>
                    <Section
                        footer={
                            addressError &&
                            <Section.Footer className={"error"}>
                                {addressError}
                            </Section.Footer>
                        }
                    >
                        <Skeleton visible={isLoading}>
                            <Input
                                value={address}
                                status={addressError ? "error" : "default"}
                                placeholder={"EQAvlWFDxGF2lXm67y4yzC17wYKD9A0guwPkMs1gOsM__NOT"}
                                header={"Bounceable address"}
                                readOnly={inputAddress !== undefined}
                                disabled={inputAddress !== undefined}
                                onChange={onAddressChange}
                            />
                            {resource && (
                                <>
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
                                </>
                            )}
                        </Skeleton>
                    </Section>
                </>
            )
        }, [address, addressError, inputAddress, isEnabled, isLoading, onAddressChange, resource, resourceType]
    )

    return (
        <Page back>
            {renderHeader}
            {renderForm}
            {children}
            <FixedBottomSection
                text={"Save"}
                disabled={!isFormValid}
                onClick={onSaveButtonClick}
            />
        </Page>
    )
}

export default ResourcePage;
