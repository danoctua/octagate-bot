'use client';

import React, {useCallback} from "react";
import CreateResourcePage from "@/components/layout/Resource/CreateResourcePage";
import useJettonData from "@/hooks/data/useJettonData";
import {useRouter} from "next/navigation";


const CreateJettonPage = () => {
    const {addJetton, isLoading} = useJettonData();
    const router = useRouter();


    const onJettonCreated = useCallback(
        (_: string) => {
            router.push(`/admin/jetton`)
        },
        [router]
    )

    return (
        <CreateResourcePage
            title={"Add Jetton"}
            subtitle={"Add a new jetton by providing the master contract address."}
            isLoading={isLoading}
            addResource={addJetton}
            resourceType={"jetton"}
            onCreated={onJettonCreated}
        />
    )
}

export default CreateJettonPage;
