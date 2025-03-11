import React, { PropsWithChildren, FC, useRef, useEffect, forwardRef, ChangeEvent } from 'react';
import {List, ButtonCell, Input} from '@telegram-apps/telegram-ui';
import { CirclePlus, X } from "lucide-react";
import FixedBottomSection from "@/components/ui/FixedBottomSection/FixedBottomSection";


/**
 * This is a forwarded input component that forwards the ref to the input element in order to allow focusing on it
 * as it cannot be done directly on the functional component.
 *
 * @param props - input props
 * @param ref - forwarded ref
 */
const InputWithRef = forwardRef<HTMLInputElement, any>((props, ref) => {
    const {forwardedRef, ...rest} = props;
    return <div ref={ref}><Input {...rest}/></div>
});
InputWithRef.displayName = "ForwardedInput";


const DynamicForm: FC<PropsWithChildren<{
    fields: { value: string, status?: "default" | "error" | undefined }[],
    handleInputChange: (index: number, event: ChangeEvent<HTMLInputElement>) => void,
    handleAddField: (index?: number) => void,
    handleRemoveField: (index: number) => void,
    isFormValid: boolean,
    handleSubmit: () => void,
    optionHeader?: string
}>> = (
    {
        fields,
        handleInputChange,
        handleAddField,
        handleRemoveField,
        isFormValid,
        handleSubmit,
        optionHeader
    }
) => {

    const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
    const lastAddedIndex = useRef<number | null>(null);

    useEffect(() => {
        // Focus on the last added input field
        if (lastAddedIndex.current !== null && inputRefs.current[lastAddedIndex.current]) {
            (
                inputRefs.current[lastAddedIndex.current]?.firstElementChild?.firstElementChild?.firstElementChild as HTMLInputElement
            )?.focus();
            lastAddedIndex.current = null;
        }
    }, [fields]);

    const handleAddFieldWithFocus = (index?: number) => {
        handleAddField(index);
        lastAddedIndex.current = index !== undefined ? index + 1 : fields.length;
    };

    return (
        <>
            <List>
                {fields.map((field, index) => (
                    <div key={index}>
                        <InputWithRef
                            ref={(el: HTMLInputElement) => { inputRefs.current[index] = el; }}
                            value={field.value}
                            status={field.status || "default"}
                            header={optionHeader && `${optionHeader} ${index + 1}`}
                            onKeyDown={(e: KeyboardEvent) => e.key === "Enter" && handleAddFieldWithFocus(index)}
                            onChange={(event: ChangeEvent<HTMLInputElement>) => handleInputChange(index, event)}
                            after={<X color={"var(--tgui--secondary_hint_color)"} onClick={() => handleRemoveField(index)} />}
                        />
                    </div>
                ))}
                <ButtonCell
                    key={"--new"}
                    before={<CirclePlus />}
                    onClick={() => handleAddFieldWithFocus()}
                >
                    Add option
                </ButtonCell>
            </List>
            <FixedBottomSection
                text={"Save"}
                disabled={!isFormValid}
                loading={false}
                onClick={handleSubmit}
            />
        </>
    );
};

export default DynamicForm;