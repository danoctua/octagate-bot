'use client';

import {backButton} from '@telegram-apps/sdk-react';
import {PropsWithChildren, ReactNode, useEffect} from 'react';
import {useRouter} from 'next/navigation';
import FixedBottomSection from "@/components/ui/FixedBottomSection/FixedBottomSection";
import {List} from "@telegram-apps/telegram-ui";

export function Page({children, back = true, fixedBottom = null, increasedBottomSpace = false}: PropsWithChildren<{
    /**
     * True if it is allowed to go back from this page.
     * @default true
     */
    back?: boolean,
    fixedBottom?: ReactNode,
    increasedBottomSpace?: boolean
}>) {
    const router = useRouter();

    if (!fixedBottom) {
        fixedBottom = <FixedBottomSection/>;
    }

    useEffect(() => {
        if (back) {
            backButton.show();
        } else {
            backButton.hide();
        }
    }, [back]);

    useEffect(() => {
        return backButton.onClick(() => {
            router.back();
        });
    }, [router]);

    let classNames = ["flex", "flex-1", "flex-col", "gap-6"]

    return <div className={"flex flex-col min-h-screen"}>
        <List className={classNames.join(' ')}>
            {children}
        </List>
        {fixedBottom}
    </div>;
}