import NftCollectionPage from "@/components/layout/Resource/NftCollectionPage/NftCollectionPage";

const EditNftCollectionPage = ({params}: {params: {address: string}}) => {
    return (
        <div>
            <NftCollectionPage address={params.address} />
        </div>
    );
}

export default EditNftCollectionPage;
