# Go Migration Strategy and Code Organization Guidelines

## Project Structure

```
lets-go (current root)
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
│   │   └── mtproto/     # MTProto client operations
│   ├── actions/         # Business actions/use cases
│   │   ├── auth/       # Authorization actions
│   │   ├── nft/        # NFT-related actions
│   │   ├── jetton/     # Jetton-related actions
│   │   ├── wallet/     # Wallet-related actions
│   │   └── chat/       # Chat-related actions
│   ├── config/          # Configuration management
│   ├── logger/          # Logging utilities
│   ├── validator/       # Validation utilities
│   ├── errors/          # Error types and handling
│   └── middleware/      # Common middleware
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
1. **Core Exceptions & Utils**
   - Set up error types and handling
   - Implement validation utilities
   - Set up logging system
   - Foundation for all other components

2. **Core Config**
   - Implement configuration management
   - Set up environment handling
   - Configure service-specific settings

3. **Core Database & Cache**
   - Implement GORM repositories with MySQL connection pooling
   - Set up Redis for caching and session management
   - Migrate database schemas and implement migrations
   - Define database interfaces and base implementations

4. **Core Models & DTOs**
   - Migrate domain models with proper validation tags
   - Implement DTOs for data transfer
   - Set up model relationships
   - Add GORM tags for database mapping

5. **Core Base Services**
   - Implement base service structure
   - Set up TON blockchain interactions
   - Configure storage operations
   - Establish service patterns

### Phase 2: Core Business Logic
1. **Core Business Services**
   - Wallet management
   - Jetton operations
   - NFT operations
   - User management
   - Chat functionality
   - MTProto client operations

2. **Core Actions**
   - Base action structure
   - Authorization actions
   - Wallet actions
   - Jetton actions
   - NFT actions
   - Chat actions

### Phase 3: Microservices Infrastructure
1. **Shared Components**
   - Service-specific configurations
   - Common utilities
   - Shared middleware
   - Background job system (asynq)

2. **Background Job System**
   - Set up asynq for task queue management
   - Configure Redis for job storage
   - Implement worker pools
   - Set up monitoring and retry mechanisms

### Phase 4: Microservices
1. **Indexer Service**
   - Background job processing
   - Blockchain event handling
   - Data indexing
   - Event processing

2. **Scheduler Service**
   - Task scheduling
   - Cron job management
   - Background task coordination
   - Job monitoring

3. **Community Manager Service**
   - Community-wide operations
   - Background tasks
   - Event processing
   - Separate from bot_ui for better scaling

4. **Bot UI Service**
   - User interactions
   - Command handling
   - Real-time responses
   - Telegram bot integration
   - Separate from community_manager for better user experience

5. **API Service**
   - HTTP endpoints
   - Service integration
   - API documentation
   - Authentication and authorization

## Key Technical Decisions

### 1. Framework & Libraries
- **HTTP Router**: Gin (performance + middleware ecosystem)
- **ORM**: GORM
  - Rich feature set
  - Good documentation
  - Active community
  - Type safety
  - Note: Combining Python's `core/db.py` and `core/services/db.py` into a single Go package for better cohesion and idiomatic Go structure
- **Caching**: Redis
  - Fast in-memory storage
  - Pub/sub capabilities
  - Session management
  - Rate limiting
- **Validation**: go-playground/validator
- **Logging**: zap (structured logging)
- **Configuration**: viper
- **Testing**: testify + gomock
- **Documentation**: swaggo
- **Telegram Integration**:
  - Bot API: telegram-bot-api (github.com/go-telegram-bot-api/telegram-bot-api)
  - MTProto Client: gotd/td (github.com/gotd/td)
- **CLI Tools**: Cobra
- **Background Jobs**: asynq (Redis-based task queue)

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

## Service Architecture

### Core Services
- Located in `internal/` directory
- Shared business logic
- Common interfaces
- Reusable components

### Microservices
- Located in `services/` directory
- Independent deployment
- Service-specific logic
- Clear boundaries

### Service Separation Principles
1. **Single Responsibility**
   - Each service has one primary purpose
   - Clear boundaries between services
   - Minimal cross-service dependencies

2. **Independent Scaling**
   - Services can be scaled independently
   - Resource allocation per service
   - Load balancing per service

3. **Independent Deployment**
   - Services can be deployed separately
   - Version control per service
   - Rollback capability per service

4. **Independent Error Handling**
   - Service-specific error handling
   - Isolated failure domains
   - Independent monitoring

5. **Communication Patterns**
   - Well-defined interfaces
   - Clear API contracts
   - Versioned APIs

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