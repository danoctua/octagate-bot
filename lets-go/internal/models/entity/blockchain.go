package entity

import (
	"time"
)

// Jetton represents a Jetton entity in the database.
type Jetton struct {
	Address    string    `gorm:"primaryKey;column:address"`             // Blockchain Address
	Name       string    `gorm:"column:name;not null"`                 // Name of the Jetton
	Description *string   `gorm:"column:description;type:text"`         // Jetton description
	Symbol     string    `gorm:"column:symbol;not null"`               // Symbol for the Jetton
	TotalSupply int64     `gorm:"column:total_supply;not null"`         // Total supply of the Jetton
	LogoPath   string    `gorm:"column:logo_path;not null"`            // Path to the logo
	IsEnabled  bool      `gorm:"column:is_enabled;not null;default:true"` // Whether the Jetton is enabled
	CreatedAt  time.Time `gorm:"column:created_at;type:timestamp;default:current_timestamp"` // Creation time

	// One-to-Many Relationship
	TelegramChatJettons []TelegramChatJetton `gorm:"foreignKey:JettonAddress;references:Address"`
}

// TableName sets the correct table name for the Jetton entity.
func (Jetton) TableName() string {
	return "jetton"
}


// NFTCollection represents a collection of NFTs in the database.
type NFTCollection struct {
	Address          string  `gorm:"primaryKey;column:address"`            // Blockchain Address
	Name             string  `gorm:"column:name;not null"`                // Name of the Collection
	Description      *string `gorm:"column:description;type:text"`        // Description of the Collection
	LogoPath         string  `gorm:"column:logo_path;not null"`           // Logo image path
	IsEnabled        bool    `gorm:"column:is_enabled;not null;default:true"` // Whether the collection is enabled
	BlockchainMetadata []byte  `gorm:"column:blockchain_metadata;type:json"` // Serialized metadata in JSON format
	CreatedAt        time.Time `gorm:"column:created_at;type:timestamp;default:current_timestamp"` // Creation time

	// One-to-Many Relationship
	TelegramChatNftCollections []TelegramChatNFTCollection `gorm:"foreignKey:CollectionAddress;references:Address"`
}

// TableName sets the correct table name for the NFTCollection entity.
func (NFTCollection) TableName() string {
	return "nft_collection"
}


// NftItem represents an individual NFT in the database.
type NftItem struct {
	Address           string  `gorm:"primaryKey;column:address"`            // Blockchain Address
	OwnerAddress      string  `gorm:"column:owner_address;not null;index"` // Owner's blockchain address (foreign key)
	CollectionAddress string  `gorm:"column:collection_address;not null;index"` // Collection blockchain address (foreign key)
	BlockchainMetadata []byte  `gorm:"column:blockchain_metadata;type:json"` // Serialized metadata in JSON format
	CreatedAt         time.Time `gorm:"column:created_at;type:timestamp;default:current_timestamp"` // Creation time
	UpdatedAt         time.Time `gorm:"column:updated_at;type:timestamp;default:current_timestamp;onupdate:current_timestamp"`

	// Relationships
	UserWallet      UserWallet     `gorm:"foreignKey:OwnerAddress;references:Address;constraint:OnDelete:CASCADE"`
	NFTCollection   NFTCollection  `gorm:"foreignKey:CollectionAddress;references:Address;constraint:OnDelete:CASCADE"`
}

// TableName sets the correct table name for the NftItem entity.
func (NftItem) TableName() string {
	return "nft_item"
}