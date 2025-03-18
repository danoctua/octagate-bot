'use client';

import React, {FC, PropsWithChildren, useCallback} from "react";
import useJettonData from "@/hooks/data/useJettonData";
import {useRouter} from "next/navigation";
import ResourcePage from "@/components/layout/Resource/ResourcePage";


const JettonPage: FC<PropsWithChildren<{ address?: string }>> = ({address, children}) => {
    const {jetton, isLoading, toggleJetton} = useJettonData(address);
    const router = useRouter();


    const onSave = useCallback(
        (_: string) => {
            router.push(`/admin/jetton`)
        },
        [router]
    )

    return (
        <ResourcePage
            resource={jetton}
            isLoading={isLoading}
            toggleResource={toggleJetton}
            resourceStaticPath={"/dynamic/jettons"}
            resourceType={"jetton"}
            onSave={onSave}
        />
    )
}

export default JettonPage;
