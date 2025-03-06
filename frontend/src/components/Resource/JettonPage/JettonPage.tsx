'use client';

import React, {FC, PropsWithChildren, useCallback} from "react";
import useJettonData from "@/hooks/data/useJettonData";
import {useRouter} from "next/navigation";
import ResourcePage from "@/components/Resource/ResourcePage";


const JettonPage: FC<PropsWithChildren<{ address?: string }>> = ({address, children}) => {
    const {jetton, isLoading, addJetton, toggleJetton} = useJettonData(address);
    const router = useRouter();


    const onJettonCreated = useCallback(
        (address: string) => {
            router.push(`/admin/jetton/${address}`)
        },
        [router]
    )

    return (
        <ResourcePage
            inputAddress={address}
            resource={jetton}
            isLoading={isLoading}
            addResource={addJetton}
            toggleResource={toggleJetton}
            resourceStaticPath={"/dynamic/jettons"}
            resourceType={"jetton"}
            onNewResourceCreated={onJettonCreated}
        />
    )
}

export default JettonPage;
