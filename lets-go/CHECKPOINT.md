# Migration Checkpoint

This document tracks the progress of migrating Python codebase to Go. The migration follows the strategy defined in GUIDELINES-AI.md.

## Migration Progress

### Phase 1: Core Infrastructure

#### Core Exceptions & Utils
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| core/exceptions/* | Custom exceptions | internal/errors/* | Custom error types | |
| core/utils/* | Utility functions | internal/validator/* | Validation utilities | |
| core/constants.py | Constants | internal/constants/constants.go | Constants | |

#### Core Config
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| core/config/* | Configuration | internal/config/* | Configuration structs | |
| core/settings.py | Settings | internal/config/settings.go | Settings | |

#### Core Database & Cache
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| core/db.py | Database setup | internal/repository/db/database.go | DatabaseRepository | |
| core/services/db.py | DatabaseService | internal/repository/db/service.go | DatabaseService | |
| core/services/superredis.py | RedisService | internal/repository/cache/redis.go | RedisRepository | |

#### Core Models & DTOs
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| core/models/* | Various models | internal/models/entity/* | Corresponding Go structs | |
| core/dtos/* | Various DTOs | internal/models/dto/* | Corresponding Go structs | |

#### Core Base Services
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| core/services/base.py | BaseService | internal/services/base.go | BaseService | |
| core/services/ton.py | TonService | internal/services/ton/ton.go | TonService | |
| core/services/storage.py | StorageService | internal/services/storage/storage.go | StorageService | |

### Phase 2: Core Business Logic

#### Business Services
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| core/services/wallet.py | WalletService | internal/services/wallet/wallet.go | WalletService | |
| core/services/jetton.py | JettonService | internal/services/jetton/jetton.go | JettonService | |
| core/services/nft.py | NFTService | internal/services/nft/nft.go | NFTService | |
| core/services/user.py | UserService | internal/services/user/user.go | UserService | |
| core/services/chat/* | ChatService | internal/services/chat/chat.go | ChatService | |
| core/services/supertelethon.py | TelethonService | internal/services/mtproto/mtproto.go | MTProtoService | |

#### Business Actions
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| core/actions/base.py | BaseAction | internal/actions/base.go | BaseAction | |
| core/actions/authorization.py | AuthorizationAction | internal/actions/auth/authorization.go | AuthorizationAction | |
| core/actions/wallet.py | WalletAction | internal/actions/wallet/wallet.go | WalletAction | |
| core/actions/jetton.py | JettonAction | internal/actions/jetton/jetton.go | JettonAction | |
| core/actions/nft_collection.py | NFTCollectionAction | internal/actions/nft/collection.go | NFTCollectionAction | |
| core/actions/chat/* | ChatAction | internal/actions/chat/chat.go | ChatAction | |

### Phase 3: Microservices Infrastructure

#### Shared Components
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| */config/* | Service configs | services/shared/config/* | Shared configs | |
| */utils/* | Service utils | services/shared/utils/* | Shared utils | |
| */middleware/* | Service middleware | services/shared/middleware/* | Shared middleware | |

### Phase 4: Microservices

#### Indexer Service
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| indexer/celery_app.py | Celery app | services/indexer/main.go | Worker setup | |
| indexer/indexers/* | Indexer implementations | services/indexer/workers/* | Indexer workers | |
| indexer/tasks/* | Background tasks | services/indexer/workers/* | Background workers | |
| indexer/utils/* | Utilities | services/indexer/utils/* | Utility functions | |
| indexer/data/* | Data structures | services/indexer/models/* | Data models | |
| indexer/cli/* | CLI commands | services/indexer/cli/* | CLI handlers | |
| indexer/config/* | Configuration | services/indexer/config/* | Config structs | |

#### Scheduler Service
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| scheduler/celery_app.py | Celery app | services/scheduler/main.go | Scheduler setup | |
| scheduler/tasks/* | Scheduled tasks | services/scheduler/jobs/* | Scheduled jobs | |
| scheduler/config/* | Configuration | services/scheduler/config/* | Config structs | |

#### Community Manager Service
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| community_manager/celery_app.py | Celery app | services/community_manager/main.go | Worker setup | |
| community_manager/tasks/* | Background tasks | services/community_manager/workers/* | Background workers | |
| community_manager/config/* | Configuration | services/community_manager/config/* | Config structs | |

#### Bot UI Service
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| bot_ui/__init__.py | Bot initialization | services/bot_ui/main.go | Bot setup | |
| bot_ui/handlers/* | Command handlers | services/bot_ui/handlers/* | Command handlers | |
| bot_ui/cache.py | Cache management | services/bot_ui/cache/cache.go | Cache manager | |
| bot_ui/utils.py | Utilities | services/bot_ui/utils/* | Utility functions | |
| bot_ui/not_telegram_ext/* | Extensions | services/bot_ui/extensions/* | Bot extensions | |
| bot_ui/config/* | Configuration | services/bot_ui/config/* | Config structs | |

#### API Service
| Python Module | Python Class/Function | Go Module | Go Class/Function | Status |
|--------------|----------------------|-----------|-------------------|---------|
| api/app.py | FastAPI app | services/api/main.go | Gin app | |
| api/deps.py | Dependencies | services/api/deps/deps.go | Dependencies | |
| api/routes/* | Route handlers | services/api/handlers/* | HTTP handlers | |
| api/pos/* | POS endpoints | services/api/handlers/pos/* | POS handlers | |
| api/services/* | Service integrations | services/api/services/* | Service clients | |
| api/config/* | Configuration | services/api/config/* | Config structs | |

## Migration Status Legend

- Empty cell: Not started
- ✓: Completed
- ⚠️: In progress
- ❌: Blocked/Issues

## Notes
1. Maintain exact feature parity with Python codebase
2. Keep existing business logic intact
3. Preserve all current functionality
4. Ensure proper error handling and logging
5. Test each component thoroughly
