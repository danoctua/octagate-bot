'use client';

import {useCallback, useState} from "react";

import {Page} from '@/components/Page';
import {Caption, Input, Section, Info, Text, Subheadline} from "@telegram-apps/telegram-ui";
import FixedBottomSection from "@/components/FixedBottomSection/FixedBottomSection";
import {createChat} from "@/services";
import {useRouter} from "next/navigation";
import {AlertTriangle} from "lucide-react";
import Callout from "@/components/Callout/Callout";


const regex = /^(-?\d+(\.\d+)?)$|^(https:\/\/t\.me\/[a-zA-Z0-9_]{4,32})$/


const NewChatPage = () => {
    const [chatIdentifier, setChatIdentifier] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [isDisabled, setIsDisabled] = useState<boolean>(true);
    const [formError, setFormError] = useState<string | null>(null);
    const router = useRouter();

    const validateChatIdentifier = (newChatIdentifier: string) => {
        if (!newChatIdentifier) {
            return true;
        }
        return regex.test(newChatIdentifier);
    }

    const setChatIdOnChange = useCallback(
        (input: string) => {
            if (!input) {
                setChatIdentifier(null);
                setIsDisabled(true);
                return;
            }
            setChatIdentifier(input);
            const isValid = validateChatIdentifier(input);
            setIsDisabled(!isValid);
            if (!isValid) {
                setFormError("Invalid chat identifier. It should be chat ID or a proper link to chat, e.g. https://t.me/telegram");
            } else {
                setFormError(null);
            }
        },
        []
    )

    const onAddChatButtonClick = useCallback(
        () => {
            if (!chatIdentifier) {
                return;
            }
            setIsDisabled(true);
            setIsLoading(true);
            createChat({chatIdentifier: chatIdentifier}).then(
                (chatData) => {
                    router.push(`/admin/chat/${chatData.slug}`)
                }
            ).catch(
                e => {
                    let errorMessage = `Failed to add chat ${chatIdentifier}`;

                    if (
                        e.response && e.response.data && e.response.data.detail
                        && e.response.data.detail.error
                        && e.response.data.detail.error.message
                    ) {
                        errorMessage = e.response.data.detail.error.message;
                    }
                    setFormError(errorMessage);
                }
            );
            setIsLoading(false);
        },
        [chatIdentifier, router]
    )

    let footerDefaultText = "Сhat or channel should include Gateway bot with admin privileges";
    let footer = null;
    if (formError) {
        footer = (
            <Section.Footer style={{color: "var(--tgui--destructive_text_color)"}}>
                {formError}<br/><br/>
                {footerDefaultText}
            </Section.Footer>
        )
    } else {
        footer = (
            <Section.Footer>
                {footerDefaultText}
            </Section.Footer>
        )
    }

    return (
        <Page back={true}>
            <Section
                header={<Section.Header large>Add chat or channel</Section.Header>}
                footer={
                    <div>
                        {formError &&
                            <Section.Footer className={"error"}>
                                {formError}
                            </Section.Footer>
                        }
                        <Section.Footer>
                            {footerDefaultText}
                        </Section.Footer>
                    </div>
                }
            >
                <Input
                    placeholder={"Chat or channel ID"}
                    status={formError ? "error" : "default"}
                    value={chatIdentifier || ""}
                    onChange={(event) => setChatIdOnChange(event.target.value)}
                />
            </Section>

            <FixedBottomSection
                text={"Save"}
                disabled={isDisabled}
                loading={isLoading}
                onClick={onAddChatButtonClick}
            />
        </Page>
    )
}


export default NewChatPage;
