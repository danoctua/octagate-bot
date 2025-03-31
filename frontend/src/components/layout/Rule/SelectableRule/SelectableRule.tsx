import {Avatar, ButtonCell, Cell, Info, Input, Section, Selectable, Switch} from "@telegram-apps/telegram-ui";
import ImageWithFallback from "@/components/ui/ImageWithFallback/ImageWithFallback";
import {IJettonWithTitle, INftCollectionWithTitle} from "@/interfaces";
import React, {useMemo, useState} from "react";
import {ChevronDown, ChevronUp} from "lucide-react";
import {getImageUrl} from "@/utils/image";
import {getAcronymFromName} from "@/utils/text";


const DEFAULT_MAX_ITEMS = 3;


const SelectableRule = (
    {
        title,
        items,
        category,
        selectedOption,
        onSelect,
        expected,
        onExpectedChange,
        existing,
        isEnabled = true,
        onToggle = undefined
    }: {
        title: string,
        items: IJettonWithTitle[] | INftCollectionWithTitle[],
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

    const [showAll, setShowAll] = useState<boolean>(false);

    const displayedOptions = useMemo(
        () => {
            if (items.length <= DEFAULT_MAX_ITEMS || showAll) {
                return items;
            }
            // Sort items by whether it's selected or not and then by name
            return items.sort((a, b) => {
                if (a.address === selectedOption) {
                    return -1;
                }
                if (b.address === selectedOption) {
                    return 1;
                }
                return a.name.localeCompare(b.name);
            }).slice(0, DEFAULT_MAX_ITEMS);
        },
        [items, selectedOption, showAll]
    )

    const renderOptions = useMemo(() => {
        if (!displayedOptions || !displayedOptions.length) {
            return null;
        }

        let options = displayedOptions.map((item, index) => (
            <Cell
                key={item.address}
                Component={"label"}
                before={
                    <Avatar
                        src={getImageUrl(item.logoPath)}
                        acronym={getAcronymFromName(item.name)}
                        size={40}
                    />
                }
                after={
                    <Selectable
                        checked={selectedOption === item.address}
                        onChange={() => onSelect(item.address)}
                    />
                }
                subtitle={item.subtitle}
            >
                {item.title}
            </Cell>
        ));
        if (items.length > DEFAULT_MAX_ITEMS) {
            options.push(
                <ButtonCell
                    before={showAll ? <ChevronUp/> : <ChevronDown/>}
                    key={"--show-all"}
                    Component={"label"}
                    onClick={() => setShowAll(!showAll)}
                >
                    {showAll ? "Show less" : "Show more"}
                </ButtonCell>
            )
        }
        return options
    }, [category, displayedOptions, items, onSelect, selectedOption, showAll])

    return (
        <>
            <Section header={<Section.Header large>Hold to get access</Section.Header>}>
                <Input
                    className={"text-end"}
                    before={<Info type={"text"} className={"whitespace-nowrap"}>Required amount</Info>}
                    after={<Info type={"text"} className={"whitespace-nowrap"}>{category}</Info>}
                    type={"number"}
                    value={expected}
                    onChange={(event) => onExpectedChange(parseInt(event.target.value))}
                />
            </Section>
            <Section
                header={title}
            >
                {renderOptions}
            </Section>
            <Section
                header={"Access matrix"}
            >
                {existing &&
                    <Cell
                        Component={"label"}
                        multiline
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
                }
                <Cell
                    Component={"label"}
                    after={<Switch checked onChange={() => {
                    }}/>}
                    disabled
                    multiline
                    description={"Whether that rule grants write access to the chat"}
                >
                    Grants write access
                </Cell>

            </Section>
        </>
    )
}

export default SelectableRule;
