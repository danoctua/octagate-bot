package config

import (
	"errors"
	"os"
	"strconv"
	"strings"

	"github.com/kelseyhightower/envconfig"
)

// CoreSettings defines the structure for environment variables and application settings
type CoreSettings struct {
	RedisHost                      string   `envconfig:"REDIS_HOST" required:"true"`
	RedisPort                      int      `envconfig:"REDIS_PORT" required:"true"`
	RedisDB                        int      `envconfig:"REDIS_DB" required:"true"`
	RedisTransactionDB             int      `envconfig:"REDIS_TRANSACTION_DB" required:"true"`
	RedisUsername                  string   `envconfig:"REDIS_USERNAME"`
	RedisPassword                  string   `envconfig:"REDIS_PASSWORD"`
	RedisTransactionStreamName     string   `envconfig:"REDIS_TRANSACTION_STREAM_NAME" required:"true"`

	MySQLHost                      string   `envconfig:"MYSQL_HOST" required:"true"`
	MySQLPort                      int      `envconfig:"MYSQL_PORT" required:"true"`
	MySQLDatabase                  string   `envconfig:"MYSQL_DATABASE" required:"true"`
	MySQLUser                      string   `envconfig:"MYSQL_USER" required:"true"`
	MySQLPassword                  string   `envconfig:"MYSQL_PASSWORD" required:"true"`
	MySQLRootPassword              string   `envconfig:"MYSQL_ROOT_PASSWORD" required:"true"`

	TelegramBotToken               string   `envconfig:"TELEGRAM_BOT_TOKEN" required:"true"`
	TelegramAppID                  int      `envconfig:"TELEGRAM_APP_ID" required:"true"`
	TelegramAppHash                string   `envconfig:"TELEGRAM_APP_HASH" required:"true"`

	DefaultLanguage                string   `envconfig:"DEFAULT_LANGUAGE" default:"en"`
	RedisTaskStatusExpiration      int      `envconfig:"REDIS_TASK_STATUS_EXPIRATION" default:"300"`
	BlacklistedWalletsFilePath     string   `envconfig:"BLACKLISTED_WALLETS_FILE_PATH" required:"true"`

	BeatScheduleFilename           string   `envconfig:"BEAT_SCHEDULE_FILENAME" default:"/tmp/celerybeat-schedule"`

	Env                            string   `envconfig:"ENV" default:"development"`

	CDNAccessKey                   string   `envconfig:"CDN_ACCESS_KEY" required:"true"`
	CDNSecretKey                   string   `envconfig:"CDN_SECRET_KEY" required:"true"`
	CDNEndpoint                    string   `envconfig:"CDN_ENDPOINT" required:"true"`
	CDNRegion                      string   `envconfig:"CDN_REGION" default:"auto"`
	CDNBucketName                  string   `envconfig:"CDN_BUCKET_NAME" required:"true"`
}

// BrokerURL generates the Redis URL for usage as a message broker
func (c *CoreSettings) BrokerURL() string {
	credentials := ""
	if c.RedisUsername != "" && c.RedisPassword != "" {
		credentials = c.RedisUsername + ":" + c.RedisPassword + "@"
	}
	return "redis://" + credentials + c.RedisHost + ":" + strconv.Itoa(c.RedisPort) + "/" + strconv.Itoa(c.RedisDB)
}

// DBConnectionString generates the MySQL connection string
func (c *CoreSettings) DBConnectionString() string {
	return "mysql://" + c.MySQLUser + ":" + c.MySQLPassword + "@" + c.MySQLHost + ":" + strconv.Itoa(c.MySQLPort) + "/" + c.MySQLDatabase
}

// BlacklistedWallets loads and caches the blacklisted wallets from a file
func (c *CoreSettings) BlacklistedWallets() ([]string, error) {
	filePath := c.BlacklistedWalletsFilePath
	if filePath == "" {
		return nil, errors.New("blacklisted wallets file path is not set")
	}

	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	wallets := strings.Split(string(data), "\n")
	for i, wallet := range wallets {
		wallets[i] = strings.TrimSpace(wallet) // Trim whitespace for robust parsing
	}
	return wallets, nil
}

// LoadConfig loads and validates the environment variables into the CoreSettings struct
func LoadConfig() (*CoreSettings, error) {
	var config CoreSettings
	err := envconfig.Process("", &config) // Load environment variables
	if err != nil {
		return nil, err
	}
	return &config, nil
}
