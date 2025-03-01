import {Cell, Input, List, Section, Selectable, Text} from "@telegram-apps/telegram-ui";
import ImageWithFallback from "@/components/ImageWithFallback/ImageWithFallback";
import {IJetton} from "@/interfaces";


const SelectableRule = (
    {
        items, category, selectedOption, onSelect, expected, onExpectedChange,
    }: {
        items: IJetton[],
        category: string,
        onSelect: (address: string) => void,
        onExpectedChange: (expected: number) => void,
        selectedOption: string | undefined,
        expected: number | undefined,
    }
) => {
    return (
        <div style={{padding: "16px 0"}}>
            <Input
                header={"Required amount"}
                type={"number"}
                value={expected}
                onChange={(event) => onExpectedChange(parseInt(event.target.value))}
            />
            <Section
                style={{padding: "16px 0"}}
                header={"Token"}
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
