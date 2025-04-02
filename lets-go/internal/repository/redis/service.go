package redis

import (
	"context"
	"errors"
	"time"

	"github.com/redis/go-redis/v9"
)

type RedisService struct {
	client *redis.Client
	ctx    context.Context
}

// NewRedisService initializes a new Redis service with the provided config
func NewRedisService(host string, port int, db int, password string) *RedisService {
	opts := &redis.Options{
		Addr:     fmt.Sprintf("%s:%d", host, port),
		DB:       db,
		Password: password,
	}
	client := redis.NewClient(opts)

	// Test connection on initialization
	ctx := context.Background()
	err := client.Ping(ctx).Err()
	if err != nil {
		panic("Failed to connect to Redis: " + err.Error())
	}

	return &RedisService{
		client: client,
		ctx:    ctx, // Use a shared context for convenience
	}
}

// Get gets a value from Redis
func (r *RedisService) Get(key string) (string, error) {
	val, err := r.client.Get(r.ctx, key).Result()
	if err == redis.Nil {
		return "", errors.New("key does not exist")
	}
	return val, err
}

// Set sets a value in Redis
func (r *RedisService) Set(key string, value string, expiration time.Duration) error {
	return r.client.Set(r.ctx, key, value, expiration).Err()
}

// Delete deletes a key from Redis
func (r *RedisService) Delete(key string) error {
	return r.client.Del(r.ctx, key).Err()
}

// AddToSet adds values to a Redis set
func (r *RedisService) AddToSet(name string, values ...string) error {
	return r.client.SAdd(r.ctx, name, values).Err()
}

// RemoveFromSet removes values from a Redis set
func (r *RedisService) RemoveFromSet(name string, values ...string) error {
	return r.client.SRem(r.ctx, name, values).Err()
}

// GetStreamItems reads all items from a stream
func (r *RedisService) GetStreamItems(streamName string) (map[string]map[string]string, error) {
	// Read the stream from the beginning
	streams, err := r.client.XRead(r.ctx, &redis.XReadArgs{
		Streams: []string{streamName, "0-0"}, // Start from the beginning of the stream
		Count:   100,                        // Return up to 100 items at a time
		Block:   0,                          // Wait indefinitely if no items are available
	}).Result()

	if err != nil {
		if err == redis.Nil {
			return nil, nil // No items in the stream
		}
		return nil, err
	}

	// Collect results
	result := make(map[string]map[string]string)
	for _, stream := range streams {
		for _, message := range stream.Messages {
			result[message.ID] = message.Values
		}
	}

	return result, nil
}

// RemoveStreamItems removes consumed items from a stream
func (r *RedisService) RemoveStreamItems(streamName string, keys ...string) error {
	return r.client.XDel(r.ctx, streamName, keys...).Err()
}
