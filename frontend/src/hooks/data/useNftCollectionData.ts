import {useState} from "react";
import {INftCollection, IStatusResponse} from "@/interfaces";
import {useClientOnce} from "@/hooks/useClientOnce";
import {createNftCollection, fetchNftCollection, refreshNftCollectionMetadata, updateNftCollection} from "@/services";

const useNftCollectionData = (address?: string) => {
    const [nftCollection, setNftCollection] = useState<INftCollection | undefined>(undefined);
    const [isLoading, setIsLoading] = useState(false);
    const [isMetadataLoading, setIsMetadataLoading] = useState(false);

    useClientOnce(() => {
        if (!address) return;
        setIsLoading(true);
        fetchNftCollection(address).then(
            (data) => { setNftCollection(data) }
        ).finally(() => setIsLoading(false));
    });

    const addNftCollection = async (address: string): Promise<INftCollection> => {
        setIsLoading(true);
        return await createNftCollection(address).then(
            (data) => {
                setNftCollection(data)
                setIsLoading(false)
                return data
            }
        ).finally(() => setIsLoading(false));
    }

    const toggleNftCollection = async (address: string, isEnabled: boolean): Promise<INftCollection> => {
        setIsLoading(true);
        return await updateNftCollection(address, isEnabled).then(
            (data) => {
                setNftCollection(data)
                return data
            }
        ).finally(() => setIsLoading(false));
    }

    const refreshMetadata = async (address: string): Promise<IStatusResponse> => {
        setIsMetadataLoading(true);
        return await refreshNftCollectionMetadata(address).then(
            data => data
        ).finally(() => setIsMetadataLoading(false));
    }

    return { nftCollection, isLoading, addNftCollection, toggleNftCollection, refreshMetadata, isMetadataLoading };
}

export default useNftCollectionData;
