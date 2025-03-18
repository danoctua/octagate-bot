'use client';

import React, {ChangeEvent, FC, PropsWithChildren, ReactNode, useCallback, useState} from "react";
import {Input} from "@telegram-apps/telegram-ui";
import FixedBottomSection, {FixedBottomButton} from "@/components/ui/FixedBottomSection/FixedBottomSection";
import {IJetton, INftCollection} from "@/interfaces";
import BannerPage from "@/components/layout/BannerPage/BannerPage";

const addressRegex = /^EQ[0-9A-Za-z\_\+\-\/]{46}$/;

const CreateResourcePage: FC<PropsWithChildren<{
    title: string,
    subtitle: string,
    isLoading: boolean,
    addResource: (address: string) => Promise<INftCollection | IJetton>,
    resourceType: "NFT collection" | "jetton",
    onCreated: (address: string) => void,
    children?: ReactNode,
}>> = ({
           title,
           subtitle,
           isLoading,
           addResource,
           resourceType,
           onCreated,
           children
       }) => {
    const [address, setAddress] = useState<string>("");
    const [addressError, setAddressError] = useState<string | undefined>(undefined);
    const [isFormValid, setIsFormValid] = useState<boolean>(false);

    const onAddressChange = useCallback(
        (e: ChangeEvent<HTMLInputElement>) => {
            const newAddress = e.target.value
            setAddress(newAddress)
            if (addressRegex.test(newAddress)) {
                setIsFormValid(true)
                setAddressError(undefined)
            } else {
                setIsFormValid(false)
                setAddressError(`Invalid ${resourceType} address. It should be a valid bounceable address`)
            }

        }, [resourceType]
    )

    const onSaveButtonClick = useCallback(
        async () => {
            await addResource(address).then(() => onCreated(address))
        }, [addResource, address, onCreated]
    )

    return (
        <BannerPage
            back
            logoUrl={"/chain.png"}
            title={title}
            subtitle={subtitle}
            fixedBottom={
                <FixedBottomSection
                    button={
                        <FixedBottomButton
                            text={"Save"}
                            disabled={!isFormValid || isLoading}
                            loading={isLoading}
                            onClick={onSaveButtonClick}
                        />
                    }

                />
            }
        >
            <Input
                value={address}
                status={addressError ? "error" : "default"}
                placeholder={"EQAvlWFDxGF2lXm67y4yzC17wYKD9A0guwPkMs1gOsM__NOT"}
                header={"Bounceable address"}
                onChange={onAddressChange}
            />
        </BannerPage>
    )
}

export default CreateResourcePage;
