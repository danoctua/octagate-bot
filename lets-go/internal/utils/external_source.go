package utils

import (
	"context"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"time"
)

// Constants for timeouts
const (
	RequestTimeout = 10 * time.Second
	ReadTimeout    = 5 * time.Second
	ConnectTimeout = 5 * time.Second
)

// WhitelistRule represents the expected response structure
type WhitelistRule struct {
	Users []string `json:"users"`
}

// fetchWhitelistMembers fetches and validates whitelist members from a given URL
func FetchWhitelistMembers(url string) (*WhitelistRule, error) {
	// Create an HTTP client with timeout settings
	client := &http.Client{
		Timeout: RequestTimeout,
	}

	// Create a context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), RequestTimeout)
	defer cancel()

	// Make the HTTP GET request
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}

	response, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()

	// Check for HTTP status errors
	if response.StatusCode != http.StatusOK {
		return nil, errors.New("failed to fetch data, status: " + response.Status)
	}

	// Decode the JSON response
	var whitelist WhitelistRule
	if err := json.NewDecoder(response.Body).Decode(&whitelist); err != nil {
		return nil, errors.New("failed to decode response JSON: " + err.Error())
	}

	// Log the result and return
	log.Printf("Fetched %d users from %s.\n", len(whitelist.Users), url)
	return &whitelist, nil
}