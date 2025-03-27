'use client';

import React, {useState, ChangeEvent, useEffect, useCallback} from "react";
import DynamicForm from "@/components/ui/DynamicForm/DynamicForm";
import {Cell, Input, Section, Switch} from "@telegram-apps/telegram-ui";
import useChatWhitelistRuleData from "@/hooks/data/useChatWhitelistRuleData";
import {useRouter} from "next/navigation";

const WhitelistRule = ({chatSlug, ruleId}: { chatSlug: string, ruleId?: number }) => {
    const [ name, setName ] = useState<string>("");
    const [ description, setDescription ] = useState<string>("");
    const [ isEnabled, setIsEnabled ] = useState<boolean>(true);
    const [ fields, setFields ] = useState<{
        value: string, status?: "default" | "error" | undefined
    }[]>([{ value: "", status: "default" }]);
    const [ isFormValid, setIsFormValid ] = useState<boolean>(false);
    const { rule, createRule, updateRule } = useChatWhitelistRuleData(chatSlug, ruleId);
    const router = useRouter();

    const handleWhitelistInputChange = (index: number, event: ChangeEvent<HTMLInputElement>) => {
        const newFields = fields.map((field, i) => {
            if (i === index) {
                return {...field, value: event.target.value};
            }
            return field;
        });
        setFields(newFields);
    };

    useEffect(() => {
        if (rule) {
            setName(rule.name);
            setDescription(rule.description || "");
            setIsEnabled(rule.isEnabled);
            setFields(rule.users.map(user => ({value: user.toString(), status: "default"})));
        }
    }, [rule]);

    const handleAddWhitelistOption = (index?: number) => {
        if (index !== undefined) {
            const newFields = [...fields];
            newFields.splice(index + 1, 0, {value: '', status: "default"});
            setFields(newFields);
            return;
        }
        setFields([...fields, {value: '', status: "default"}]);
    };

    const handleRemoveWhitelistOption = (index: number) => {
        const newFields = fields.filter((_, i) => i !== index);
        setFields(newFields);
    };

    const handleSubmit = useCallback(async () => {
        const userIds = fields.map(
            field => parseInt(field.value)
        ).filter(
            id => !isNaN(id) && id !== null
        )
        if (!ruleId) {
            await createRule(name, description, userIds)
        } else {
            await updateRule(name, description, isEnabled, userIds)
        }
        router.push(`/admin/chat/${chatSlug}`)
    }, [chatSlug, createRule, description, fields, isEnabled, name, router, ruleId, updateRule])

    useEffect(
        () => {
            // Validate each field and set status: "error" if it's not a valid integer
            let isValid = true;
            fields.forEach((field, index) => {
                if (field.value && isNaN(parseInt(field.value))) {
                    fields[index].status = "error";
                    isValid = false;
                } else {
                    fields[index].status = "default";
                }
            })

            setIsFormValid(isValid && !!name);
        },
        [fields, name]
    )

    return (
        <>
            <Section
                header={
                    <Section.Header large>
                        Whitelist users
                    </Section.Header>
                }
            >
                <Input
                    header={"Title"}
                    value={name}
                    placeholder={"Title"}
                    onChange={e => setName(e.target.value)}
                />
                <Input
                    header={"Description"}
                    value={description}
                    placeholder={"Description"}
                    onChange={e => setDescription(e.target.value)}
                />
                {ruleId && (
                    <Cell
                        Component={"label"}
                        multiline
                        after={
                            <Switch
                                checked={isEnabled}
                                onChange={_ => setIsEnabled(!isEnabled)}
                            />
                        }
                        description={"Whether the rule is active or not"}
                    >
                        Is active
                    </Cell>
                )
                }
            </Section>

            <DynamicForm
                fields={fields}
                handleInputChange={handleWhitelistInputChange}
                handleAddField={handleAddWhitelistOption}
                handleRemoveField={handleRemoveWhitelistOption}
                isFormValid={isFormValid}
                handleSubmit={handleSubmit}
                optionHeader={"Telegram ID"}
            />
        </>
    )
}

export default WhitelistRule;
