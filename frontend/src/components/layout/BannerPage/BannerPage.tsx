'use client';


import {FC, PropsWithChildren, ReactNode} from "react";
import Image from "next/image";
import {Title, Text} from "@telegram-apps/telegram-ui";
import {Page} from "@/components/layout/Page";

const BannerPage: FC<PropsWithChildren<{
    logoUrl: string,
    title: ReactNode,
    subtitle: ReactNode,
    back?: boolean,
    fixedBottom?: ReactNode,
    children?: ReactNode,
}>> = ({logoUrl, title, subtitle, back = false, fixedBottom, children}) => {
    return (
        <Page
            back={back}
            fixedBottom={fixedBottom}
        >
            <div className={"flex items-center justify-center flex-col py-8"}>
                <div id={"title"} className={"flex items-center justify-center flex-col px-6 gap-4 text-center"}>
                    <Image src={logoUrl} alt={"logo"} width={112} height={112}/>
                    <div className={"flex items-center justify-center flex-col gap-3"}>
                        <Title weight={"1"} level={"1"}>{title}</Title>
                        <Text className={"flex items-center justify-center"}>{subtitle}</Text>
                    </div>
                </div>
                <div className={"mt-7 w-full"}>
                    {children}
                </div>
            </div>
        </Page>
    )
}

export default BannerPage;
