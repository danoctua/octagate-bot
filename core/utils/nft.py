from core.models.chat import TelegramChatNFTCollection
from core.models.blockchain import NftItem


def find_relevant_nft_items(
    rule: TelegramChatNFTCollection, nft_items: list[NftItem]
) -> list[NftItem]:
    """
    Find relevant NFT items for the rule
    """
    relevant_nft_items = []
    for nft_item in nft_items:
        if nft_item.collection_address == rule.address:
            if rule.required_attributes:
                # Iterate over attributes of the NFT item and check if all the required attributes are present
                if not all(
                    any(
                        attribute.trait_type == nft_item_attribute.trait_type
                        and attribute.value == nft_item_attribute.value
                        for nft_item_attribute in rule.required_attributes
                    )
                    for attribute in nft_item.blockchain_metadata.attributes
                ):
                    continue

            relevant_nft_items.append(nft_item)
    return relevant_nft_items
