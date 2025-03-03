'use client';

import React, {ChangeEvent, FC, PropsWithChildren, useCallback, useEffect, useMemo, useState} from "react";
import {Page} from "@/components/Page";
import Header from "@/components/Header/Header";
import {Cell, Info, Input, Section, Skeleton, Subheadline, Switch, Title} from "@telegram-apps/telegram-ui";
import ImageWithFallback from "@/components/ImageWithFallback/ImageWithFallback";
import useJettonData from "@/hooks/useJettonData";
import FixedBottomSection from "@/components/FixedBottomSection/FixedBottomSection";
import {useRouter} from "next/navigation";
import {Link} from "@/components/Link/Link";
import {ExternalLink} from "lucide-react";

const addressRegex = /^EQ[0-9A-Za-z\_\+\-\/]{46}$/;

const JettonPage: FC<PropsWithChildren<{ address?: string }>> = ({address, children}) => {
    const {jetton, isLoading, addJetton, toggleJetton} = useJettonData(address);
    const [jettonAddress, setJettonAddress] = useState<string>(address || "");
    const [jettonAddressError, setJettonAddressError] = useState<string | undefined>(undefined);
    const [isEnabled, setIsEnabled] = useState<boolean>(false);
    const [isFormValid, setIsFormValid] = useState<boolean>(false);
    const router = useRouter();


    useEffect(() => {
        if (!jetton) return
        console.log("Fetched Jetton data")
        setJettonAddress(jetton.address)
        setIsEnabled(jetton.isEnabled)
        setIsFormValid(true)
    }, [jetton])

    const onJettonAddressChange = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => {
            if (address) return

            const newJettonAddress = e.target.value
            setJettonAddress(newJettonAddress)
            if (addressRegex.test(newJettonAddress)) {
                setIsFormValid(true)
                setJettonAddressError(undefined)
            } else {
                setIsFormValid(false)
                setJettonAddressError("Invalid jetton address. It should be a valid bounceable address")
            }

        }, [address]
    )

    const onSaveButtonClick = useCallback(
        async () => {
            if (address) {
                await toggleJetton(jettonAddress, isEnabled)
            } else {
                await addJetton(jettonAddress)
                router.push(`/admin/jetton/${jettonAddress}`)
            }
        }, [address, toggleJetton, jettonAddress, isEnabled, addJetton, router]
    )

    const renderHeader = useMemo(
        () => {
            if (jetton) {
                return (
                    <Header>
                        <Skeleton visible={isLoading}>
                            <ImageWithFallback
                                src={`/dynamic/jettons/${jetton.logoPath}`}
                                fallbackSrc={"/welcome.gif"}
                                rounded
                                width={96}
                                height={96}
                            />
                        </Skeleton>
                        <div style={{display: "flex", flexDirection: "column", gap: 8}}>
                            <Skeleton visible={isLoading}>
                                <Title level={"2"} weight={"2"} plain>
                                    {jetton.name}
                                </Title>
                                <Subheadline>
                                    <Link
                                        href={`https://tonviewer.com/${jetton.address}`}
                                        style={{display: "flex", gap: 4, justifyContent: "center", alignItems: "center"}}
                                    >
                                        View in explorer
                                        <ExternalLink size={"16"}/>
                                    </Link>
                                </Subheadline>
                            </Skeleton>
                            <Skeleton visible={isLoading}>
                                {jetton?.description &&
                                    <Info type={"avatarStack"}>
                                        {jetton.description}
                                    </Info>
                                }
                            </Skeleton>
                        </div>
                    </Header>
                )
            } else {
                return (
                    <Header>
                        <Title level={"2"} weight={"2"} plain>Add new jetton</Title>
                    </Header>
                )
            }
        }, [address, isLoading, jetton]
    )

    const renderForm = useMemo(
        () => {
            return (
                <Section
                    footer={
                        jettonAddressError &&
                        <Section.Footer className={"error"}>
                            {jettonAddressError}
                        </Section.Footer>
                    }
                >
                    <Skeleton visible={isLoading}>
                        <Input
                            value={jettonAddress}
                            status={jettonAddressError ? "error" : "default"}
                            placeholder={"EQAvlWFDxGF2lXm67y4yzC17wYKD9A0guwPkMs1gOsM__NOT"}
                            header={"Bounceable address"}
                            readOnly={address !== undefined}
                            disabled={address !== undefined}
                            onChange={onJettonAddressChange}
                        />
                        {jetton && (
                            <>
                                <Input
                                    value={jetton.name}
                                    placeholder={"Jetton name"}
                                    header={"Name"}
                                    readOnly
                                    disabled
                                />
                                <Input
                                    value={jetton.description}
                                    placeholder={"Jetton description"}
                                    header={"Description"}
                                    readOnly
                                    disabled
                                />
                                <Cell
                                    Component={"label"}
                                    after={
                                        <Switch
                                            checked={isEnabled}
                                            onChange={e => setIsEnabled(!isEnabled)}
                                        />
                                    }
                                    description={"Whether jetton will be displayed in the list of available jettons"}
                                >
                                    Is whitelisted
                                </Cell>

                            </>
                        )}
                    </Skeleton>
                </Section>
            )
        }, [address, isEnabled, isLoading, jetton, jettonAddress, jettonAddressError, onJettonAddressChange]
    )

    return (
        <Page back>
            {renderHeader}
            {renderForm}
            <FixedBottomSection
                text={"Save"}
                disabled={!isFormValid}
                onClick={onSaveButtonClick}
            />
        </Page>
    )
}

export default JettonPage;
