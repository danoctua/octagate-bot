import {Button, Divider, Multiselect, Select} from "@telegram-apps/telegram-ui";
import {X} from "lucide-react";
import React, {ChangeEvent, useCallback} from "react";
import {INftCollection, INftMetadataInput} from "@/interfaces";

const NftCollectionRuleAttribute = (
    {
        index,
        onRemove,
        nftCollection,
        attribute,
        onSelectParent,
        onSelectValue,
        onValueChange,
    }: {
        index: number,
        onRemove: (_: number) => void,
        nftCollection: INftCollection,
        attribute: INftMetadataInput,
        onSelectParent: (_: number, value: string) => void,
        onSelectValue: (_: number, value: string) => void,
        onValueChange: (_: number, value: string) => void,
    }
) => {
    const getAttributeOptionsForTraitType = useCallback(
        (currentAttribute: INftMetadataInput): string[] => {
            if (!currentAttribute.traitType) return []
            let values = nftCollection.blockchainMetadata?.attributes.find(
                attribute => attribute.traitType === currentAttribute.traitType
            )?.values || []
            if (currentAttribute.value && !values.includes(currentAttribute.value)) {
                values.push(currentAttribute.value)
            }
            return values
        }, [nftCollection.blockchainMetadata?.attributes]
    )

    return (
        <>
            <div
                        style={
                            {
                                display: "flex",
                                justifyContent: "flex-end",
                                alignItems: "center",
                                padding: "8px 22px"
                            }
                        }
                    >
                        <Button
                            mode={"outline"}
                            before={<X/>}
                            onClick={() => onRemove(index)}
                        >
                            Remove
                        </Button>
                    </div>
                    <Select
                        header={"Attribute type"}
                        value={attribute.traitType}
                        onChange={(e: ChangeEvent<HTMLSelectElement>) => onSelectParent(index, e.currentTarget.value)}
                        status={attribute.error ? "error" : "default"}
                    >
                        {
                            nftCollection.blockchainMetadata?.attributes.map((attributeOption) => (
                                <option
                                    key={attributeOption.traitType}
                                >
                                    {attributeOption.traitType}
                                </option>
                            ))
                        }
                    </Select>
                    <Multiselect
                        header={"Value"}
                        disabled={!attribute.traitType}
                        closeDropdownAfterSelect
                        onChange={(options) => {
                            if (options.length) {
                                onSelectValue(index, options[options.length - 1].value.toString())
                            } else {
                                onSelectValue(index, "")
                            }
                        }}
                        status={attribute.value ? "default" : "error"}
                        inputValue={attribute.currentValue}
                        onInputChange={(e: ChangeEvent<HTMLInputElement>) => e.target.value && onValueChange(index, e.target.value)}
                        creatable={`${attribute.currentValue} (not known)`}
                        selectedBehavior={"highlight"}
                        options={
                            getAttributeOptionsForTraitType(attribute).map((value) => (
                                {
                                    value: value,
                                    label: value
                                }
                            ))
                        }
                        value={attribute.value ? [{value: attribute.value, label: attribute.value}] : []}
                    >
                    </Multiselect>
                    <Divider/>
        </>
    )
}

export default NftCollectionRuleAttribute;
