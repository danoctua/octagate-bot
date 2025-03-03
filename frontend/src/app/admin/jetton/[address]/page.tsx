'use client';

import React from "react";
import JettonPage from "@/components/Resource/JettonPage/JettonPage";


const EditJettonPage = ({params}: {params: {address: string}}) => {
    return (
        <JettonPage address={params.address}/>
    )
}

export default EditJettonPage;
