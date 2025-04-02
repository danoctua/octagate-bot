package core

type NFTItem struct {
	CollectionAddress    string      `json:"collection_address"`
	BlockchainMetadata   Metadata    `json:"blockchain_metadata"`
}

type Metadata struct {
	Attributes []Attribute `json:"attributes"`
}

type Attribute struct {
	TraitType string `json:"trait_type"`
	Value     string `json:"value"`
}

type TelegramChatNFTCollection struct {
	Address            string      `json:"address"`
	RequiredAttributes []Attribute `json:"required_attributes"` // Optional attributes to match
}

// FindRelevantNFTItems filters and returns the relevant NFT items based on the given rule
func FindRelevantNFTItems(rule TelegramChatNFTCollection, nftItems []NFTItem) []NFTItem {
	var relevantNFTItems []NFTItem

	// Iterate over the list of NFT items
	for _, nftItem := range nftItems {
		if nftItem.CollectionAddress == rule.Address {
			// If attributes are required, validate them
			if len(rule.RequiredAttributes) > 0 {
				// Check if all required attributes are present in the NFT item's attributes
				matchesAll := true
				for _, reqAttr := range rule.RequiredAttributes {
					matches := false
					for _, nftAttr := range nftItem.BlockchainMetadata.Attributes {
						if reqAttr.TraitType == nftAttr.TraitType &&
							reqAttr.Value == nftAttr.Value {
							matches = true
							break
						}
					}
					if !matches {
						matchesAll = false
						break
					}
				}
				if !matchesAll {
					continue
				}
			}
			// Add the NFT item to the relevant list if it matches the rule
			relevantNFTItems = append(relevantNFTItems, nftItem)
		}
	}
	return relevantNFTItems
}