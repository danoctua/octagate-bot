import {useState} from "react";
import {INftCollection} from "@/interfaces";
import {useClientOnce} from "@/hooks/useClientOnce";
import {fetchAllNftCollections, fetchWhiteListedNftCollections} from "@/services";

const useNftCollectionsData = (
    {whitelistedOnly = true}: {whitelistedOnly: boolean}
) => {
    const [ nftCollections, setNftCollections ] = useState<INftCollection[] | undefined>(undefined);
    const [ isLoading, setIsLoading ] = useState(false);

    useClientOnce(() => {
        setIsLoading(true);
        (
            whitelistedOnly ? fetchWhiteListedNftCollections(): fetchAllNftCollections()
        ).then((data) => {
            setNftCollections(data);
            setIsLoading(false);
        });
    })

    return { nftCollections, isLoading };
}

export default useNftCollectionsData;
