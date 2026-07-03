package config

import (
	"fmt"

	"github.com/caarlos0/env/v11"
	"github.com/joho/godotenv"
)

type Config struct {
	// General
	Environment          string `env:"ENVIRONMENT,required"`
	DBConnectionPoolSize int    `env:"DATABASE_CONNECTION_POOL_SIZE" envDefault:"10"`

	// LoadGen
	Port               string `env:"LOADGEN_PORT" envDefault:"8080"`
	TargetDB           string `env:"LOADGEN_TARGET_DB,required"`
	ConnectionPoolSize int    `env:"LOADGEN_CONNECTION_POOL_SIZE" envDefault:"10"`

	// Postgres
	PostgresHost string `env:"POSTGRES_HOST,required"`
	PostgresPort int    `env:"POSTGRES_PORT,required"`

	PostgresUser string `env:"POSTGRES_USER,required"`
	PostgresPass string `env:"POSTGRES_PASSWORD,required"`
	PostgresDB   string `env:"POSTGRES_DB,required"`

	// MongoDB
	MongoHost string `env:"MONGO_HOST,required"`
	MongoPort int    `env:"MONGO_PORT,required"`

	MongoUser         string `env:"MONGO_INITDB_ROOT_USERNAME,required"`
	MongoPass         string `env:"MONGO_INITDB_ROOT_PASSWORD,required"`
	MongoDB           string `env:"MONGO_INITDB_DATABASE,required"`
	MongoNestedDB     string `env:"MONGO_NESTED_DATABASE" envDefault:"coursework_nested"`
	MongoNormalizedDB string `env:"MONGO_NORMALIZED_DATABASE" envDefault:"coursework_normalized"`
}

func NewConfig(possibleEnvLocations []string) (*Config, error) {
	// Load .env
	loadDotenv(possibleEnvLocations)

	// Parse env vars into Config struct
	cfg, err := env.ParseAs[Config]()
	if err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}

	return &cfg, nil
}

// Iterates possibleEnvLocations and stops at the first existing .env file.
// The file is optional because Docker Compose injects the same values as process env.
func loadDotenv(possibleEnvLocations []string) {
	for _, path := range possibleEnvLocations {
		// Load .env file (not godotenv.Overload)
		// we can override env vars with actual env vars
		if err := godotenv.Load(path); err == nil {
			return
		}
	}
}
