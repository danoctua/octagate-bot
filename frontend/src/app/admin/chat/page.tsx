'use client';

import {useState} from "react";

import {Page} from '@/components/Page';
import {Input, Section} from "@telegram-apps/telegram-ui";
import FixedBottomSection from "@/components/FixedBottomSection/FixedBottomSection";


const NewChatPage = () => {
    const [chatId, setChatId] = useState<string>('');

    return (
        <Page back={true}>
            <Section
                header={"Add chat"}
                footer={"Сhat or channel should include Gateway bot with admin privileges"}
            >
                <Input
                    placeholder={"Link or chat ID"}
                    value={chatId}
                    onChange={(event) => setChatId(event.target.value)}
                />
            </Section>

            <FixedBottomSection text={"Save"} onClick={() => {}}/>
        </Page>
    )
}

export default NewChatPage;
