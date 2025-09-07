---
title: 10.3 使用Docker Compose管理多容器环境中的配置：构建复杂的容器化应用环境
date: 2025-08-31
categories: [Configuration Management]
tags: [microservice-configuration-management]
published: true
---

# 10.3 使用Docker Compose管理多容器环境中的配置

Docker Compose是用于定义和运行多容器Docker应用程序的工具。通过一个YAML文件，我们可以配置应用程序的服务，并使用单个命令启动和管理所有服务。在多容器环境中，配置管理变得更加复杂，需要协调不同服务之间的配置依赖关系。

## Docker Compose配置文件结构

Docker Compose配置文件采用YAML格式，具有清晰的层次结构，支持多种配置选项。

### 基本配置结构

```yaml
# docker-compose.yml - 基本配置结构
version: '3.8'

services:
  # Web应用服务
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app
    environment:
      - NGINX_ENV=production

  # 应用服务
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
      - REDIS_URL=redis://cache:6379
    volumes:
      - ./app-config.json:/app/config.json:ro
    depends_on:
      - db
      - cache

  # 数据库服务
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d:ro

  # 缓存服务
  cache:
    image: redis:alpine
    command: redis-server --appendonly yes
    volumes:
      - cache-data:/data

# 数据卷定义
volumes:
  db-data:
  cache-data:

# 网络定义
networks:
  default:
    driver: bridge
```

### 环境变量和.env文件的使用

Docker Compose支持通过.env文件管理环境变量，提高配置的灵活性和安全性。

```bash
# .env - 环境变量文件
# 应用配置
APP_ENV=production
APP_PORT=3000
APP_DEBUG=false

# 数据库配置
DB_HOST=db
DB_PORT=5432
DB_NAME=myapp
DB_USER=myapp
DB_PASSWORD=mysecretpassword

# 缓存配置
REDIS_HOST=cache
REDIS_PORT=6379

# API配置
API_TIMEOUT=30
API_RETRIES=3

# 日志配置
LOG_LEVEL=info
LOG_FORMAT=json
```

```yaml
# docker-compose.yml - 使用.env文件
version: '3.8'

services:
  app:
    build: .
    ports:
      - "${APP_PORT}:${APP_PORT}"
    environment:
      # 直接引用.env文件中的变量
      - NODE_ENV=${APP_ENV}
      - PORT=${APP_PORT}
      - DEBUG=${APP_DEBUG}
      - DATABASE_HOST=${DB_HOST}
      - DATABASE_PORT=${DB_PORT}
      - DATABASE_NAME=${DB_NAME}
      - DATABASE_USER=${DB_USER}
      - DATABASE_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PORT=${REDIS_PORT}
      - API_TIMEOUT=${API_TIMEOUT}
      - API_RETRIES=${API_RETRIES}
      - LOG_LEVEL=${LOG_LEVEL}
      - LOG_FORMAT=${LOG_FORMAT}
    volumes:
      - ./logs:/app/logs
    depends_on:
      - db
      - cache

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  cache:
    image: redis:alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes

volumes:
  db-data:
```

## 外部配置文件的挂载

在复杂的多容器环境中，通常需要挂载外部配置文件来管理不同服务的配置。

### 配置文件组织结构

```
project/
├── docker-compose.yml
├── .env
├── .env.local
├── config/
│   ├── app/
│   │   ├── app.json
│   │   ├── logging.conf
│   │   └── features.json
│   ├── nginx/
│   │   └── nginx.conf
│   ├── postgres/
│   │   ├── postgres.conf
│   │   └── init/
│   │       ├── 01-init.sql
│   │       └── 02-seed.sql
│   └── redis/
│       └── redis.conf
├── secrets/
│   ├── db-password.txt
│   └── api-key.txt
└── scripts/
    └── entrypoint.sh
```

### 配置文件挂载示例

```yaml
# docker-compose.yml - 外部配置文件挂载
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      # Nginx配置文件
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./config/nginx/sites/:/etc/nginx/sites-available/:ro
      # SSL证书
      - ./certs:/etc/nginx/certs:ro
      # 静态文件
      - ./static:/usr/share/nginx/html:ro
    environment:
      - NGINX_ENV=${NGINX_ENV:-production}
    depends_on:
      - app
    restart: unless-stopped

  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "${APP_PORT}:${APP_PORT}"
    environment:
      # 应用环境变量
      - NODE_ENV=${APP_ENV}
      - PORT=${APP_PORT}
      - LOG_LEVEL=${LOG_LEVEL}
      # 数据库连接
      - DATABASE_HOST=${DB_HOST}
      - DATABASE_PORT=${DB_PORT}
      - DATABASE_NAME=${DB_NAME}
      - DATABASE_USER=${DB_USER}
      - DATABASE_PASSWORD_FILE=/run/secrets/db-password
      # 缓存连接
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PORT=${REDIS_PORT}
      # API密钥
      - API_KEY_FILE=/run/secrets/api-key
    volumes:
      # 应用配置文件
      - ./config/app/app.json:/app/config/app.json:ro
      - ./config/app/logging.conf:/app/config/logging.conf:ro
      - ./config/app/features.json:/app/config/features.json:ro
      # 日志目录
      - app-logs:/app/logs
      # 临时文件
      - app-tmp:/tmp
    secrets:
      - db-password
      - api-key
    depends_on:
      - db
      - cache
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${APP_PORT}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD_FILE: /run/secrets/db-password
      # PostgreSQL配置
      POSTGRES_INITDB_ARGS: "--auth-host=scram-sha-256"
    volumes:
      # 数据持久化
      - db-data:/var/lib/postgresql/data
      # 配置文件
      - ./config/postgres/postgres.conf:/etc/postgresql/postgresql.conf:ro
      # 初始化脚本
      - ./config/postgres/init/:/docker-entrypoint-initdb.d/:ro
    secrets:
      - db-password
    ports:
      - "5432:5432"
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  cache:
    image: redis:alpine
    volumes:
      # Redis配置
      - ./config/redis/redis.conf:/usr/local/etc/redis/redis.conf:ro
      # 数据持久化
      - cache-data:/data
    command: redis-server /usr/local/etc/redis/redis.conf
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

# 数据卷定义
volumes:
  app-logs:
  app-tmp:
  db-data:
  cache-data:

# 密钥定义
secrets:
  db-password:
    file: ./secrets/db-password.txt
  api-key:
    file: ./secrets/api-key.txt

# 网络定义
networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 多环境配置管理

在实际项目中，通常需要管理多个环境（开发、测试、预生产、生产）的配置。

### 环境特定的Compose文件

```yaml
# docker-compose.override.yml - 开发环境覆盖配置
version: '3.8'

services:
  app:
    # 开发环境使用本地代码挂载
    volumes:
      - .:/app:cached
      - /app/node_modules
    # 开发环境端口映射
    ports:
      - "3000:3000"
      - "9229:9229"  # Node.js调试端口
    # 开发环境环境变量
    environment:
      - NODE_ENV=development
      - DEBUG=true
      - LOG_LEVEL=debug
    # 开发环境不重启
    restart: "no"
    # 开发环境命令
    command: npm run dev

  db:
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: myapp_dev
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password

  cache:
    ports:
      - "6379:6379"
```

```yaml
# docker-compose.prod.yml - 生产环境配置
version: '3.8'

services:
  web:
    # 生产环境副本数
    deploy:
      replicas: 3
    # 生产环境资源限制
    environment:
      - NGINX_WORKER_PROCESSES=4
      - NGINX_WORKER_CONNECTIONS=1024
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

  app:
    # 生产环境副本数
    deploy:
      replicas: 5
    # 生产环境资源限制
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    # 生产环境环境变量
    environment:
      - NODE_ENV=production
      - LOG_LEVEL=warn
    # 生产环境重启策略
    restart: unless-stopped

  db:
    # 生产环境资源限制
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    # 生产环境备份卷
    volumes:
      - db-data:/var/lib/postgresql/data
      - db-backup:/backups
    # 生产环境备份计划
    environment:
      POSTGRES_BACKUP_SCHEDULE: "0 2 * * *"

  cache:
    # 生产环境资源限制
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

volumes:
  db-backup:
```

### 环境配置管理脚本

```bash
#!/bin/bash
# manage-environments.sh - 环境管理脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 环境变量
ENV=${1:-development}
ACTION=${2:-up}

# 配置文件路径
BASE_COMPOSE="docker-compose.yml"
OVERRIDE_COMPOSE="docker-compose.override.yml"
PROD_COMPOSE="docker-compose.prod.yml"

echo -e "${GREEN}Managing environment: ${ENV}${NC}"
echo -e "${GREEN}Action: ${ACTION}${NC}"

# 根据环境选择配置文件
case $ENV in
  development|dev)
    COMPOSE_FILES="-f ${BASE_COMPOSE} -f ${OVERRIDE_COMPOSE}"
    ENV_FILE=".env"
    ;;
  production|prod)
    COMPOSE_FILES="-f ${BASE_COMPOSE} -f ${PROD_COMPOSE}"
    ENV_FILE=".env.production"
    ;;
  testing|test)
    COMPOSE_FILES="-f ${BASE_COMPOSE} -f docker-compose.test.yml"
    ENV_FILE=".env.testing"
    ;;
  staging)
    COMPOSE_FILES="-f ${BASE_COMPOSE} -f docker-compose.staging.yml"
    ENV_FILE=".env.staging"
    ;;
  *)
    echo -e "${RED}Unknown environment: ${ENV}${NC}"
    echo "Available environments: development, production, testing, staging"
    exit 1
    ;;
esac

# 检查环境文件是否存在
if [ ! -f "$ENV_FILE" ]; then
  echo -e "${YELLOW}Warning: Environment file ${ENV_FILE} not found${NC}"
  echo -e "${YELLOW}Using default .env file${NC}"
  ENV_FILE=".env"
fi

# 执行Docker Compose命令
case $ACTION in
  up)
    echo -e "${GREEN}Starting services...${NC}"
    docker-compose ${COMPOSE_FILES} --env-file ${ENV_FILE} up -d
    ;;
  down)
    echo -e "${GREEN}Stopping services...${NC}"
    docker-compose ${COMPOSE_FILES} --env-file ${ENV_FILE} down
    ;;
  restart)
    echo -e "${GREEN}Restarting services...${NC}"
    docker-compose ${COMPOSE_FILES} --env-file ${ENV_FILE} down
    docker-compose ${COMPOSE_FILES} --env-file ${ENV_FILE} up -d
    ;;
  logs)
    echo -e "${GREEN}Showing logs...${NC}"
    docker-compose ${COMPOSE_FILES} --env-file ${ENV_FILE} logs -f
    ;;
  status)
    echo -e "${GREEN}Service status...${NC}"
    docker-compose ${COMPOSE_FILES} --env-file ${ENV_FILE} ps
    ;;
  build)
    echo -e "${GREEN}Building services...${NC}"
    docker-compose ${COMPOSE_FILES} --env-file ${ENV_FILE} build
    ;;
  *)
    echo -e "${RED}Unknown action: ${ACTION}${NC}"
    echo "Available actions: up, down, restart, logs, status, build"
    exit 1
    ;;
esac

# 检查命令执行结果
if [ $? -eq 0 ]; then
  echo -e "${GREEN}Command executed successfully${NC}"
else
  echo -e "${RED}Command failed${NC}"
  exit 1
fi
```

通过以上内容，我们深入探讨了使用Docker Compose管理多容器环境中的配置，包括配置文件结构、环境变量和.env文件的使用、外部配置文件的挂载，以及多环境配置管理等关键主题。这些实践可以帮助我们构建更加复杂和灵活的容器化应用环境。