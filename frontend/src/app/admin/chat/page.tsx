'use client';

import {useState} from "react";

import {Page} from '@/components/Page';
import {Button, Cell, Chip, Divider, FixedLayout, Input, Section, Snackbar} from "@telegram-apps/telegram-ui";
import {AlertTriangle} from "lucide-react";


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

            <FixedLayout vertical={"bottom"}>
                <Divider/>
                <div style={{ padding: "16px 8px" }}>
                    <Button stretched onClick={() => {}}>
                        Save
                    </Button>
                </div>
            </FixedLayout>
        </Page>
    )
}

export default NewChatPage;
