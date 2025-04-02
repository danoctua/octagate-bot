package db

import (
	"fmt"
	"log"
	"time"

	"internal/config" // Import the package from settings.go

	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
	"gorm.io/gorm/schema"
)

// DatabaseRepository represents the database connection and operations
type DatabaseRepository struct {
	DB *gorm.DB
}

// NewDatabaseRepository initializes the database connection
func NewDatabaseRepository(settings *config.CoreSettings) (*DatabaseRepository, error) {
	// Fetch the database connection string from settings
	dsn := settings.DBConnectionString()

	// Initialize GORM with the MySQL driver
	db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{
		NamingStrategy: schema.NamingStrategy{
			SingularTable: true, // Use singular table names
		},
		Logger: logger.Default.LogMode(logger.Info), // Log SQL queries for debugging
	})

	if err != nil {
		return nil, fmt.Errorf("failed to connect to the database: %w", err)
	}

	// Configure the database connection pool
	sqlDB, err := db.DB()
	if err != nil {
		return nil, fmt.Errorf("failed to get database object: %w", err)
	}
	sqlDB.SetMaxOpenConns(300)              // Max open connections (pool size)
	sqlDB.SetConnMaxLifetime(time.Hour)     // Reuse connections for up to 1 hour
	sqlDB.SetMaxIdleConns(30)               // Max idle connections
	sqlDB.SetConnMaxIdleTime(10 * time.Minute) // Max idle connection time

	log.Println("Database connection established successfully.")
	return &DatabaseRepository{DB: db}, nil
}

// GetDB returns the GORM DB object
func (repo *DatabaseRepository) GetDB() *gorm.DB {
	return repo.DB
}
