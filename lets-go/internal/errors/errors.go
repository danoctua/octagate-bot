package errors

import "errors"

// UserWalletExistError is used when an attempt is made to create a wallet that already exists.
var ErrUserWalletExist = errors.New("user wallet already exists")

// UserWalletConnectedError is used when an attempt is made to connect a wallet that is already connected.
var ErrUserWalletConnected = errors.New("user wallet already connected")

// TelegramChatNotExistsError is used when a Telegram chat does not exist.
var ErrTelegramChatNotExists = errors.New("telegram chat does not exist")

// ProofValidationError is used when a proof validation fails.
var ErrProofValidation = errors.New("proof validation error")

// TelegramChatNotSufficientPrivilegesError is used when a user does not have sufficient privileges for the Telegram chat.
var ErrTelegramChatNotSufficientPrivileges = errors.New("insufficient privileges for the Telegram chat")

// TelegramChatAlreadyExistsError is used when trying to create a Telegram chat that already exists.
var ErrTelegramChatAlreadyExists = errors.New("telegram chat already exists")

// TelegramChatInvalidExternalSourceError is used when an invalid external source is associated with a Telegram chat.
var ErrTelegramChatInvalidExternalSource = errors.New("invalid external source for the Telegram chat")
