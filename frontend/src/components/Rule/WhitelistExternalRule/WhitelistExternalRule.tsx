'use client';

import React, {useState, useEffect, useCallback, ChangeEvent, useMemo} from "react";
import {ButtonCell, Cell, Input, List, Section, Skeleton, Switch} from "@telegram-apps/telegram-ui";
import {useRouter} from "next/navigation";
import useChatExternalWhitelistRuleData from "@/hooks/data/useChatExternalWhitelistRuleData";
import FixedBottomSection from "@/components/FixedBottomSection/FixedBottomSection";
import {ChevronDown, ChevronUp} from "lucide-react";


const DEFAULT_DISPLAY_ITEMS = 5;


const HttpUrlRegex = new RegExp(
    "^(http|https):\\/\\/[a-zA-Z0-9-\.\:]{2,}(.[a-zA-Z]{2,})?.*"
);

type FieldType = {
    header: string,
    value: string,
    onChange: (e: ChangeEvent<HTMLInputElement>) => void,
    error?: string | null,
    placeholder?: string,
}


const WhitelistExternalRule = ({chatSlug, ruleId}: { chatSlug: string, ruleId?: number }) => {
    const [name, setName] = useState<string>("");
    const [description, setDescription] = useState<string>("");
    const [isEnabled, setIsEnabled] = useState<boolean>(true);
    const [isFormValid, setIsFormValid] = useState<boolean>(false);
    const [url, setUrl] = useState<string>("");
    const {rule, createRule, updateRule, isLoading} = useChatExternalWhitelistRuleData(chatSlug, ruleId);
    const router = useRouter();
    const [showAll, setShowAll] = useState<boolean>(false);

    const [errors, setErrors] = useState<Record<string, string | null>>({});

    const handleUpdateName = async (e: ChangeEvent<HTMLInputElement>) => {
        const newName = e.target.value;
        setName(newName)
        if (newName.length < 2 || newName.length > 255) {
            setErrors(prev => ({...prev, name: "Name should be between 2 and 255 characters"}))
        } else {
            setErrors(prev => ({...prev, name: null}))
        }
    }

    const handleUpdateDescription = async (e: ChangeEvent<HTMLInputElement>) => {
        const newDescription = e.target.value;
        setDescription(newDescription)
        if (newDescription.length > 255) {
            setErrors(prev => ({...prev, description: "Description should be less than 255 characters"}))
        } else {
            setErrors(prev => ({...prev, description: null}))
        }
    }

    const handleUpdateUrl = async (e: ChangeEvent<HTMLInputElement>) => {
        const newUrl = e.target.value;
        setUrl(newUrl)
        if (!HttpUrlRegex.test(newUrl)) {
            setErrors(prev => ({...prev, url: "Invalid URL"}))
        } else {
            setErrors(prev => ({...prev, url: null}))
        }
    }

    const fields: Record<string, FieldType> = useMemo(() => ({
        name: {
            header: "Name",
            value: name,
            onChange: handleUpdateName,
            error: errors.name,
            placeholder: "Diamond NOT holders"
        },
        description: {
            header: "Description",
            value: description,
            onChange: handleUpdateDescription,
            error: errors.description,
            placeholder: "Whitelist for Diamond NOT holders"
        },
        url: {
            header: "URL",
            value: url,
            onChange: handleUpdateUrl,
            error: errors.url,
            placeholder: "https://notco.in"
        }
    }), [description, errors.description, errors.name, errors.url, name, url])

    useEffect(() => {
        if (rule) {
            setName(rule.name);
            setDescription(rule.description || "");
            setIsEnabled(rule.isEnabled);
            setUrl(rule.url);
        }
    }, [rule]);

    const handleSubmit = useCallback(async () => {
        if (!ruleId) {
            await createRule(name, description, url)
        } else {
            await updateRule(name, description, isEnabled, url)
        }
        router.push(`/admin/chat/${chatSlug}`)
    }, [chatSlug, createRule, description, isEnabled, name, router, ruleId, updateRule, url])

    useEffect(() => {
        if (Object.values(errors).every(error => !error) && name && url) {
            setIsFormValid(true)
        } else {
            setIsFormValid(false)
        }
    }, [errors, name, url])

    const displayUsers = useMemo(() => {
        if (!rule) {
            return [];
        }

        if (rule.users.length <= DEFAULT_DISPLAY_ITEMS || showAll) {
            return rule.users;
        }

        return rule.users.slice(0, DEFAULT_DISPLAY_ITEMS);
    }, [rule, showAll])

    const renderUsers = useMemo(() => {
        let items = displayUsers.map((user, index) => (
            <Cell key={index} multiline>
                {user}
            </Cell>
        ));
        items.push(
            <ButtonCell
                key={"--show-all"}
                before={showAll ? <ChevronUp/> : <ChevronDown/>}
                onClick={() => setShowAll(!showAll)}
            >
                {showAll ? "Show less" : "Show all"}
            </ButtonCell>
        )
        return <List>{items}</List>;
    }, [displayUsers, showAll])

    const renderErrors = useMemo(() => {
        return (
            <Section.Footer className={"error"}>
                {
                    Object.entries(errors).filter(
                        ([_, error]) => error !== null
                    ).map(
                        ([name, error], index) => (
                            <div key={index}>{fields[name].header}: {error}</div>
                        )
                    )
                }
            </Section.Footer>
        )
    }, [errors, fields])

    return (
        <>
            <Skeleton visible={isLoading}>
                <Section footer={
                    !isFormValid && renderErrors
                }>
                    {
                        Object.entries(fields).map(([name, field], index) => (
                            <Input
                                key={index}
                                header={field.header}
                                placeholder={field.placeholder}
                                value={field.value}
                                onChange={field.onChange}
                                status={errors[name] ? "error" : "default"}
                            />
                        ))
                    }
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
            </Skeleton>
            {ruleId &&
                <Skeleton visible={isLoading}>
                    <Section
                        header={"Whitelist Telegram IDs"}
                        footer={`Last updated: ${rule?.updatedAt && new Date(rule?.updatedAt).toLocaleString()}`}
                    >
                        {renderUsers}
                    </Section>
                </Skeleton>
            }
            <FixedBottomSection
                text={"Save"}
                onClick={handleSubmit}
                disabled={!isFormValid || isLoading}
                loading={isLoading}
            />
        </>
    )
}

export default WhitelistExternalRule;
