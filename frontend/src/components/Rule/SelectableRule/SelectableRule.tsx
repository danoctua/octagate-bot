import {Cell, Input, List, Section, Selectable, Switch, Text} from "@telegram-apps/telegram-ui";
import ImageWithFallback from "@/components/ImageWithFallback/ImageWithFallback";
import {IJetton, INftCollection} from "@/interfaces";
import React from "react";


const SelectableRule = (
    {
        title, items, category, selectedOption, onSelect, expected, onExpectedChange, existing, isEnabled = true, onToggle = undefined
    }: {
        title: string,
        items: IJetton[] | INftCollection[],
        category: string,
        onSelect: (address: string) => void,
        onExpectedChange: (expected: number) => void,
        selectedOption: string | undefined,
        expected: number | undefined,
        existing: boolean,
        isEnabled?: boolean,
        onToggle?: (isEnabled: boolean) => void
    }
) => {
    return (
        <div style={{padding: "16px 0"}}>
            {existing && <Section>
                <Cell
                    Component={"label"}
                    after={
                        <Switch
                            checked={isEnabled}
                            onChange={_ => onToggle && onToggle(!isEnabled)}
                        />
                    }
                    description={"Whether the rule is active or not"}
                >
                    Is active
                </Cell>
            </Section>}
            <Input
                header={"Required amount"}
                type={"number"}
                value={expected}
                onChange={(event) => onExpectedChange(parseInt(event.target.value))}
            />
            <Section
                style={{padding: "16px 0"}}
                header={title}
            >
                <List>
                    {items.map((item, index) => (
                        <Cell
                            key={item.address}
                            Component={"label"}
                            before={
                                <ImageWithFallback
                                    src={`/dynamic/${category}/${item.logoPath}`}
                                    fallbackSrc={"/welcome.gif"}
                                    rounded
                                    width={40}
                                    height={40}
                                />
                            }
                            after={
                                <Selectable
                                    defaultChecked={index === 0}
                                    checked={selectedOption === item.address}
                                    onClick={() => onSelect(item.address)}
                                />
                            }
                        >
                            {item.name}
                        </Cell>
                    ))}
                </List>
            </Section>
        </div>
    )
}

export default SelectableRule;
