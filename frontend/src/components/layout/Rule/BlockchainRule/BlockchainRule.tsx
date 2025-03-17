'use client';


import React, {FC, PropsWithChildren, ReactNode, useCallback, useEffect, useState} from "react";
import SelectableRule from "@/components/layout/Rule/SelectableRule/SelectableRule";
import {Placeholder, Section, Skeleton} from "@telegram-apps/telegram-ui";
import Image from "next/image";
import FixedBottomSection, {FixedBottomButton} from "@/components/ui/FixedBottomSection/FixedBottomSection";
import {IJettonWithTitle, INftCollectionWithTitle, IRule} from "@/interfaces";

const BlockchainRule: FC<PropsWithChildren<{
    title: string,
    category: "nfts" | "jettons",
    options: IJettonWithTitle[] | INftCollectionWithTitle[] | undefined,
    selectedAddress: string,
    setSelectedAddress: (address: string) => void,
    isLoading: boolean,
    entity?: IRule | null,
    onSave: (expected: number, address: string, isEnabled: boolean) => void
    children?: ReactNode
    isChildValid?: boolean,
}>> = (
    {
        title,
        category,
        options,
        selectedAddress,
        setSelectedAddress,
        entity,
        isLoading,
        onSave,
        children,
        isChildValid = true
    }) => {
    const [expected, setExpected] = useState(0)

    const [isEnabled, setIsEnabled] = useState<boolean>(false);
    const [isFormValid, setIsFormValid] = useState<boolean>(false);

    useEffect(() => {
        if (!entity) return
        setSelectedAddress(entity.blockchainAddress)
        setExpected(entity.expected)
        setIsEnabled(entity.isEnabled)
        setIsFormValid(true)
    }, [entity, setSelectedAddress])

    useEffect(() => {
        setIsFormValid(selectedAddress !== "" && expected > 0);
    }, [selectedAddress, expected]);

    const onSaveButtonClick = useCallback(
        async () => {
            onSave(expected, selectedAddress, isEnabled)
        },
        [expected, isEnabled, onSave, selectedAddress]
    )

    return (
        <>
            {
                options ?
                    options.length ?
                        <SelectableRule
                            title={title}
                            items={options}
                            category={category}
                            onSelect={setSelectedAddress}
                            onExpectedChange={setExpected}
                            selectedOption={selectedAddress}
                            expected={expected}
                            existing={!!entity}
                            isEnabled={isEnabled}
                            onToggle={() => setIsEnabled(!isEnabled)}
                        /> :
                        <Placeholder
                            description={`Please, try again after some ${title}s will be whitelisted`}
                            header={`No ${title}s available`}
                        >
                            <Image
                                alt="Lost bananas"
                                src="/telegram.gif"
                                width={150}
                                height={150}
                            />
                        </Placeholder>
                    : <Skeleton/>
            }
            {children}
            <FixedBottomSection
                button={
                    <FixedBottomButton
                        text={"Save"}
                        disabled={!isFormValid || !isChildValid}
                        loading={isLoading}
                        onClick={onSaveButtonClick}
                    />
                }
            />
        </>
    )
}

export default BlockchainRule;
