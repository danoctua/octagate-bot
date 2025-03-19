# Go Migration Strategy and Code Organization Guidelines

## Project Structure

```
backend
├── internal/              # Shared core components
│   ├── models/           # Core domain models
│   │   ├── entity/      # Business entities
│   │   ├── dto/         # Data transfer objects
│   │   └── events/      # Domain events
│   ├── repository/      # Low-level database operations
│   │   ├── db/         # Database operations (MySQL)
│   │   └── cache/      # Cache operations (Redis)
│   ├── services/        # Core business logic
│   │   ├── nft/         # NFT operations and management
│   │   ├── jetton/      # Jetton operations
│   │   ├── wallet/      # Wallet management
│   │   ├── ton/         # TON blockchain interactions
│   │   ├── chat/        # Chat functionality
│   │   ├── user/        # User management
│   │   ├── storage/     # Storage operations
│   │   └── telethon/    # Telegram client operations
│   ├── actions/         # Business actions/use cases
│   │   ├── auth/       # Authorization actions
│   │   ├── nft/        # NFT-related actions
│   │   ├── jetton/     # Jetton-related actions
│   │   ├── wallet/     # Wallet-related actions
│   │   └── chat/       # Chat-related actions
│   ├── config/          # Configuration management
│   └── pkg/             # Shared utilities
│       ├── logger/      # Logging
│       ├── validator/   # Validation
│       ├── errors/      # Error types
│       └── middleware/  # Common middleware
├── services/            # Microservices
│   ├── api/            # API Service
│   │   ├── handlers/   # HTTP handlers
│   │   ├── routes/     # Route definitions
│   │   ├── middleware/ # Service-specific middleware
│   │   └── main.go     # Service entry point
│   ├── indexer/        # Indexer Service
│   │   ├── workers/    # Background workers
│   │   ├── processor/  # Event processors
│   │   └── main.go     # Service entry point
│   ├── scheduler/      # Scheduler Service
│   │   ├── jobs/       # Scheduled jobs
│   │   ├── queue/      # Task queue
│   │   └── main.go     # Service entry point
│   ├── bot_ui/         # Bot UI Service
│   │   ├── handlers/   # Bot command handlers
│   │   ├── websocket/  # WebSocket handlers
│   │   └── main.go     # Service entry point
│   └── community_manager/ # Community Manager Service
│       ├── handlers/    # Community management handlers
│       ├── notifier/    # Notification system
│       └── main.go      # Service entry point
├── tests/              # Test organization
│   ├── integration/    # Integration tests
│   ├── testutil/       # Test helpers and utilities
│   ├── mocks/          # Mock implementations
│   └── fixtures/       # Test data and fixtures
└── scripts/            # Build and deployment scripts
```

## Migration Strategy

### Phase 1: Core Infrastructure
1. **Shared Core Components**
   - Set up Go modules and project structure
   - Migrate core domain models with proper validation tags
   - Implement repository interfaces and base implementations
   - Set up shared utilities (logging, config, errors)

2. **Database Layer**
   - Implement GORM repositories with MySQL connection pooling
   - Set up Redis for caching and session management
   - Migrate database schemas and implement migrations

### Phase 2: Service Migration
Migrate services in parallel with dedicated teams:

1. **API Service**
   - Set up Fiber framework with middleware
   - Implement authentication and authorization
   - Migrate REST endpoints
   - Set up API documentation with Swagger

2. **Indexer Service**
   - Implement blockchain event listeners
   - Set up worker pools for processing
   - Migrate indexing logic
   - Implement error recovery and retry mechanisms

3. **Scheduler Service**
   - Set up cron job management
   - Implement task queue with Redis
   - Migrate scheduled tasks
   - Set up monitoring and alerts

4. **Bot UI Service**
   - Set up Telegram bot framework
   - Implement WebSocket handlers
   - Migrate bot commands and interactions
   - Set up state management

5. **Community Manager**
   - Implement community management logic
   - Set up notification system
   - Migrate moderation features
   - Implement analytics

## Key Technical Decisions

### 1. Framework & Libraries
- **HTTP Router**: Fiber (performance + middleware ecosystem)
- **ORM**: GORM with MySQL driver
- **Caching**: Redis (distributed caching + pub/sub)
- **Validation**: go-playground/validator
- **Logging**: zap (structured logging)
- **Configuration**: viper
- **Testing**: testify + gomock
- **Documentation**: swaggo

### 2. Communication Patterns
- **Inter-service**: gRPC for synchronous, NATS for async
- **Event Sourcing**: Event store for blockchain events
- **Message Queue**: Redis streams for task queue
- **WebSocket**: gorilla/websocket for real-time

### 3. Development Practices
- **Code Style**: golangci-lint configuration
- **Error Handling**: Custom error types with stack traces
- **Dependency Injection**: wire for compile-time DI
- **Testing**: Table-driven tests + integration tests
- **Documentation**: godoc + OpenAPI/Swagger

## Interface Design Patterns

```go
// Repository pattern with generics
type Repository[T any] interface {
    Create(ctx context.Context, entity *T) error
    FindByID(ctx context.Context, id string) (*T, error)
    Update(ctx context.Context, entity *T) error
    Delete(ctx context.Context, id string) error
}

// Service layer with dependency injection
type Service struct {
    repo    Repository[Entity]
    cache   Cache
    logger  Logger
    config  Config
}

// Event handling
type EventHandler interface {
    HandleEvent(ctx context.Context, event Event) error
}

// Worker pool pattern
type Worker interface {
    Start(ctx context.Context)
    Stop()
    AddTask(task Task) error
}
```

## Migration Guidelines

1. **Service Migration Process**
   - Create new service directory
   - Set up basic infrastructure (config, logging)
   - Implement core functionality
   - Add minimal tests using Go's standard testing package and testify
     - Unit tests for critical business logic
     - Integration tests for database operations
     - Mock external dependencies using testify/mock
     - Test organization:
       - Unit tests in same package as code (e.g., `service_test.go`)
       - Integration tests in `tests/integration` directory
       - Test helpers in `tests/testutil` package
       - Mock implementations in `tests/mocks` directory
       - Test fixtures in `tests/fixtures` directory
   - Create Dockerfile and update docker-compose.yml
   - Build and test Docker image
   - Deploy alongside existing service
   - Gradually shift traffic
   - Monitor and validate
   - Decommission old service

2. **Documentation**
   - API documentation (OpenAPI/Swagger)
   - Architecture decision records (ADRs)
   - Service runbooks (last step)