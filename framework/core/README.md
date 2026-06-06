# Framework Core Module

## Overview

The `framework/core` module contains **core infrastructure components** that are shared across all layers of the framework (API, Web, Mobile, Database). These are foundational utilities that provide common functionality needed by all test types.

**Why "core" instead of "base"?**
- "Core" better describes that these are essential, foundational components
- "Base" was confusing as it could imply base test classes (which are now in layer-specific folders)
- "Core" clearly indicates these are the central infrastructure pieces

## Components

### 1. `config_manager.py` - Unified Configuration Manager

**Purpose**: Centralized configuration management with layer-specific configs.

**Architecture**:
- **Base Config** (`base_config.py`): Shared settings (env, logging, reporting, test data)
- **Layer-Specific Configs**: 
  - `framework/api/config.py` - API settings
  - `framework/web/config.py` - Web UI settings
  - `framework/mobile/config.py` - Mobile UI settings
  - `framework/db/config.py` - Database settings

**Benefits of Separate Configs**:
1. **Separation of Concerns**: Each layer only sees its own configuration
2. **Type Safety**: Layer-specific settings are properly typed
3. **Maintainability**: Easy to add/modify layer-specific settings
4. **Clarity**: Clear which settings belong to which layer

**Usage**:
```python
from framework.core.config_manager import config

# Access base config
env = config.base.env
log_level = config.base.log_level

# Access layer-specific configs
api_url = config.api.api_base_url
web_url = config.web.web_url
db_host = config.db.db_host
mobile_server = config.mobile.appium_server_url
```

### 2. `logger.py` - Logging Manager

**Purpose**: Centralized logging using loguru for structured, thread-safe logging.

**Features**:
- Structured logging with colors (console) and rotation (file)
- Thread-safe logging for parallel execution
- Automatic log rotation and compression
- Configurable log levels
- Multiple output destinations (console + file)

**Usage**:
```python
from framework.core.logger import Logger, log

# Get logger instance
logger = Logger.get_logger(__name__)

# Use logger
logger.info("Test started")
logger.error("Test failed")
```

## Configuration Structure

```
framework/core/
├── base_config.py          # Base settings (shared)
├── config_manager.py        # Unified config manager
└── logger.py                # Logging utilities

framework/
├── api/config.py            # API-specific config
├── web/config.py            # Web-specific config
├── mobile/config.py         # Mobile-specific config
└── db/config.py             # Database-specific config
```

## Design Principles

1. **Separation of Concerns**: Each layer has its own config
2. **Shared Infrastructure**: Core utilities used by all layers
3. **Type Safety**: Pydantic ensures type validation
4. **Singleton Pattern**: Config manager uses singleton for global access
5. **Thread Safety**: Logger is thread-safe for parallel execution

## Migration from framework/base

If you have code using `framework.base`:
- `framework.base.config` → `framework.core.config_manager`
- `framework.base.logger` → `framework.core.logger`
- `config.settings.*` → `config.base.*` or `config.api.*`, `config.web.*`, etc.
