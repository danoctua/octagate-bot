package entity

import (
	"time"

	"internal/config"
)

// User represents a user of the application.
type User struct {
	ID              uint      `gorm:"primaryKey;autoIncrement;column:id"`
	TelegramID      int64     `gorm:"uniqueIndex;not null;index;column:telegram_id"`
	IsPremium       bool      `gorm:"not null;default:false;column:is_premium"`
	Username        *string   `gorm:"type:varchar(255);index;column:username"`
	FirstName       string    `gorm:"type:varchar(255);not null;column:first_name"`
	LastName        *string   `gorm:"type:varchar(255);column:last_name"`
	Language        string    `gorm:"type:varchar(10);not null;default:'en';column:language"`
	IsBlocked       bool      `gorm:"not null;default:false;column:is_blocked"`
	IsAdmin         bool      `gorm:"not null;default:false;column:is_admin"`
	CreatedAt       time.Time `gorm:"type:timestamp;not null;default:current_timestamp;column:created_at"`
	AllowsWriteToPM bool      `gorm:"not null;default:true;column:allows_write_to_pm"`

	// Relationship with UserWallet
	Wallet *UserWallet `gorm:"foreignKey:UserID;constraint:OnUpdate:CASCADE,OnDelete:SET NULL;column:wallet"`
}

// FullName is a convenience method to get the full name of the user.
func (u *User) FullName() string {
	if u.LastName != nil {
		return u.FirstName + " " + *u.LastName
	}
	return u.FirstName
}

// BeforeCreate hook to set default values
func (u *User) BeforeCreate(tx *gorm.DB) (err error) {
	// Set default language if not provided
	if u.Language == "" {
		u.Language = config.DefaultLanguage
	}
	return nil
}
