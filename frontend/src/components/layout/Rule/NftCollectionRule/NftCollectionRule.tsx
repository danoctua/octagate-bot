'use client';


import React, {
    FC,
    PropsWithChildren,
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState
} from "react";
import useNftCollectionsData from "@/hooks/data/useNftCollectionsData";
import {useRouter} from "next/navigation";
import useChatNftCollectionRuleData from "@/hooks/data/useChatNftCollectionRuleData";
import BlockchainRule from "@/components/layout/Rule/BlockchainRule/BlockchainRule";
import {INftCollection, INftMetadataInput} from "@/interfaces";
import {ButtonCell, Caption, List, Section} from "@telegram-apps/telegram-ui";
import {CirclePlus} from "lucide-react";
import NftCollectionRuleAttribute from "@/components/layout/Rule/NftCollectionRule/NftCollectionRuleAttribute";

const NftCollectionRule: FC<PropsWithChildren<{
    chatSlug: string,
    ruleId?: number
}>> = ({chatSlug, ruleId, children}) => {
    const {nftCollections} = useNftCollectionsData({whitelistedOnly: true})
    const [requiredAttributes, setRequiredAttributes] = useState<INftMetadataInput[]>([])
    const [isFormValid, setIsFormValid] = useState<boolean>(true)
    const [selectedNftCollection, setSelectedNftCollection] = useState<INftCollection | null>(null)

    const {
        chatNftCollectionRuleData,
        updateChatNftCollectionRule,
        createChatNftCollectionRule,
        isLoading
    } = useChatNftCollectionRuleData({
        slug: chatSlug,
        ruleId: ruleId
    })

    const router = useRouter();

    const setSelectedAddress = useCallback(
        (address: string) => {
            const nftCollection = nftCollections?.find(nftCollection => nftCollection.address === address)
            if (!nftCollection) return

            setSelectedNftCollection(nftCollection)
            setRequiredAttributes(
                address === chatNftCollectionRuleData?.blockchainAddress ?
                    chatNftCollectionRuleData.requiredAttributes ?
                        chatNftCollectionRuleData.requiredAttributes.map(
                            attribute => ({...attribute, currentValue: "", error: null})
                        ) : [] : []
            )
        }, [chatNftCollectionRuleData, nftCollections]
    )

    useEffect(() => {
        if (!chatNftCollectionRuleData?.blockchainAddress || !nftCollections) return
        setSelectedAddress(chatNftCollectionRuleData.blockchainAddress)
    }, [chatNftCollectionRuleData, nftCollections, setSelectedAddress]);

    const onSaveButtonClick = useCallback(
        async (expected: number, address: string, isEnabled: boolean) => {
            const preprocessedAttributes = requiredAttributes ? requiredAttributes.map(attribute => ({
                traitType: attribute.traitType,
                value: attribute.value
            })): []
            if (ruleId) {
                await updateChatNftCollectionRule({expected, address, isEnabled, requiredAttributes: preprocessedAttributes})
            } else {
                await createChatNftCollectionRule({expected, address, requiredAttributes: preprocessedAttributes})
            }
            router.push(`/admin/chat/${chatSlug}`)
        },
        [requiredAttributes, ruleId, router, chatSlug, updateChatNftCollectionRule, createChatNftCollectionRule]
    )

    const onSelectTraitType = useCallback(
        (index: number, traitType: string) => {
            setRequiredAttributes(
                requiredAttributes.map((attribute, i) => {
                    if (i === index) {
                        return {...attribute, traitType: traitType}
                    }
                    return attribute
                })
            )
        }, [requiredAttributes]
    )

    const onValueChange = useCallback(
        (index: number, value: string) => {
            setRequiredAttributes(
                requiredAttributes.map((attribute, i) => {
                    if (i === index) {
                        return {...attribute, currentValue: value}
                    }
                    return attribute
                })
            )
        }, [requiredAttributes]
    )

    const onSelectValue = useCallback(
        (index: number, value: string) => {
            setRequiredAttributes(
                requiredAttributes.map((attribute, i) => {
                    if (i === index) {
                        return {...attribute, value: value, currentValue: ""}
                    }
                    return attribute
                })
            )
        }, [requiredAttributes]
    )

    const onAddRequiredAttribute = useCallback(
        () => {
            if (!selectedNftCollection?.blockchainMetadata?.attributes?.length) return
            setRequiredAttributes(
                [
                    ...requiredAttributes,
                    {
                        traitType: selectedNftCollection.blockchainMetadata.attributes[0].traitType || "",
                        value: "",
                        currentValue: "",
                        error: null
                    }
                ]
            )
        }, [requiredAttributes, selectedNftCollection]
    )

    const onRemoveRequiredAttribute = useCallback(
        (index: number) => {
            setRequiredAttributes(
                requiredAttributes.filter((_, i) => i !== index)
            )
        }, [requiredAttributes]
    )

    const prevRequiredAttributesRef = useRef<INftMetadataInput[]>([]);

    // Form validation
    // 1. Ensure there are no duplicate attributes on the traitType level
    // 2. Ensure all attributes have a value
    useEffect(() => {
        if (!selectedNftCollection || !requiredAttributes) {
            setIsFormValid(true)
            return
        }
        let errors = false;
        let traitTypes = new Set<string>()
        const updatedAttributes = requiredAttributes.map(attribute => {
            if (traitTypes.has(attribute.traitType)) {
                attribute.error = "Duplicate attribute";
                errors = true;
            } else {
                attribute.error = null;
                traitTypes.add(attribute.traitType);
                if (!attribute.value) {
                    // Fail form validation in case of empty value
                    errors = true;
                }
            }
            return attribute;
        });

        if (JSON.stringify(prevRequiredAttributesRef.current) !== JSON.stringify(updatedAttributes)) {
            prevRequiredAttributesRef.current = updatedAttributes;
            setRequiredAttributes(updatedAttributes);
        }

        setIsFormValid(!errors)
    }, [requiredAttributes, selectedNftCollection]);

    const renderRequiredAttributesForm = useMemo(() => {
        if (!selectedNftCollection || !requiredAttributes) return null

        let fields = requiredAttributes.map((attribute, index) => {
            return (
                <NftCollectionRuleAttribute
                    key={index}
                    index={index}
                    onRemove={onRemoveRequiredAttribute}
                    nftCollection={selectedNftCollection}
                    attribute={attribute}
                    onSelectParent={onSelectTraitType}
                    onSelectValue={onSelectValue}
                    onValueChange={onValueChange}
                />
            )
        })
        fields.push(
            <ButtonCell
                key={"add-attribute"}
                before={<CirclePlus/>}
                onClick={onAddRequiredAttribute}
                // disabled={selectedNftCollection?.blockchainMetadata?.attributes?.length === requiredAttributes.length}
            >
                Add attribute rule
            </ButtonCell>
        )
        return <List>
            {fields}
        </List>;
    }, [onAddRequiredAttribute, onRemoveRequiredAttribute, onSelectTraitType, onSelectValue, onValueChange, requiredAttributes, selectedNftCollection])

    return (
        <BlockchainRule
            title={"NFT Collection"}
            category={"nfts"}
            options={nftCollections?.map(nftCollection => ({
                ...nftCollection,
                title: nftCollection.name,
                subtitle: nftCollection.description
            }))}
            isLoading={isLoading}
            onSave={onSaveButtonClick}
            entity={chatNftCollectionRuleData}
            selectedAddress={selectedNftCollection?.address || ""}
            setSelectedAddress={setSelectedAddress}
            isChildValid={isFormValid}
        >
            <Section
                header={"Required attributes"}
            >
                <Caption
                    Component={"div"}
                    style={{color: "var(--tg-theme-subtitle-text-color)", padding: "8px 22px"}}
                >
                    It will add <b>AND</b> constraint for that condition, meaning that all of the attributes selected
                    below should present in the NFT item to pass the rule.
                    <br/>If you need more of <b>OR</b> between conditions, please create a new rule instead.
                </Caption>
                {renderRequiredAttributesForm}
            </Section>
        </BlockchainRule>
    )
}

export default NftCollectionRule;
