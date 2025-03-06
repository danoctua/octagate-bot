'use client';


import React, {FC, PropsWithChildren, useCallback, useEffect, useState} from "react";
import SelectableRule from "@/components/Rule/SelectableRule/SelectableRule";
import {Placeholder, Skeleton} from "@telegram-apps/telegram-ui";
import Image from "next/image";
import FixedBottomSection from "@/components/FixedBottomSection/FixedBottomSection";
import {IJetton, INftCollection, IRule} from "@/interfaces";

const BlockchainRule: FC<PropsWithChildren<{
    title: string,
    category: "nfts" | "jettons",
    options: IJetton[] | INftCollection[] | undefined,
    isLoading: boolean,
    entity?: IRule | null,
    onSave: (expected: number, address: string, isEnabled: boolean) => void
}>> = ({title, category, options, entity, isLoading, onSave, children}) => {
    const [selectedAddress, setSelectedAddress] = useState<string>(entity?.blockchainAddress || "")
    const [expected, setExpected] = useState(0)

    const [isEnabled, setIsEnabled] = useState<boolean>(false);
    const [isFormValid, setIsFormValid] = useState<boolean>(false);

    useEffect(() => {
        if (!entity) return
        setSelectedAddress(entity.blockchainAddress)
        setExpected(entity.expected)
        setIsEnabled(entity.isEnabled)
        setIsFormValid(true)
    }, [entity])

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
                        />:
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
            <FixedBottomSection
                text={"Save"}
                disabled={!isFormValid}
                loading={isLoading}
                onClick={onSaveButtonClick}
            />
        </>
    )
}

export default BlockchainRule;
