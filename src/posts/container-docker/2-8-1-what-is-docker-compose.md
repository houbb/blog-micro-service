---
title: What is Docker Compose - Simplifying Multi-Container Applications
date: 2025-08-30
categories: [Write]
tags: [docker, compose, multi-container, orchestration]
published: true
---

## 什么是 Docker Compose？

### Docker Compose 概述

Docker Compose 是 Docker 官方提供的工具，专门用于定义和运行多容器 Docker 应用程序。它通过一个声明式的 YAML 配置文件来管理应用的所有服务，使得复杂应用的部署和管理变得简单而高效。

#### Docker Compose 的核心价值

1. **简化配置**：使用单个 YAML 文件定义整个应用栈
2. **一键部署**：通过一条命令启动所有服务
3. **环境一致性**：确保开发、测试、生产环境的一致性
4. **服务编排**：自动处理服务间的依赖关系和启动顺序
5. **资源管理**：统一管理网络、卷和其他资源

### Docker Compose 的工作原理

#### 架构组成

Docker Compose 由以下几个核心组件组成：

1. **Compose 文件**：YAML 格式的配置文件，定义应用服务
2. **Docker Engine**：实际运行容器的引擎
3. **Compose CLI**：命令行工具，用于与 Compose 文件交互

#### 工作流程

```bash
# 1. 定义 docker-compose.yml 文件
# 2. 使用 docker-compose 命令操作应用
docker-compose up -d    # 启动应用
docker-compose down     # 停止并删除应用
docker-compose ps       # 查看应用状态
```

### 安装和配置 Docker Compose

#### 安装方式

**Docker Desktop（推荐）**
Docker Desktop 已经内置了 Docker Compose，无需额外安装。

**独立安装**
```bash
# Linux 安装
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

#### 基本命令

```bash
# 查看版本
docker-compose --version

# 查看帮助
docker-compose --help

# 查看子命令帮助
docker-compose up --help
```

### Compose 文件结构详解

#### 基本结构

```yaml
# docker-compose.yml
version: '3.8'  # Compose 文件版本

services:       # 服务定义
  web:          # 服务名称
    image: nginx
    ports:
      - "80:80"
  
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password

volumes:        # 卷定义
  db-data:

networks:       # 网络定义
  app-network:
```

#### 主要组成部分

1. **version**：指定 Compose 文件格式版本
2. **services**：定义应用中的各个服务
3. **volumes**：定义数据卷
4. **networks**：定义网络
5. **configs**：定义配置
6. **secrets**：定义密钥

### 服务定义详解

#### 基本服务配置

```yaml
version: '3.8'

services:
  web:
    # 镜像配置
    image: nginx:alpine
    
    # 构建配置（替代 image）
    # build: .
    # build:
    #   context: .
    #   dockerfile: Dockerfile
    
    # 端口映射
    ports:
      - "80:80"
      - "443:443"
    
    # 环境变量
    environment:
      - NODE_ENV=production
      - DATABASE_URL=mysql://db:3306/myapp
    
    # 环境变量文件
    # env_file:
    #   - .env
    
    # 卷挂载
    volumes:
      - web-data:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    
    # 依赖关系
    depends_on:
      - db
    
    # 网络配置
    networks:
      - frontend
      - backend
    
    # 重启策略
    restart: always
    
    # 健康检查
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### 高级服务配置

```yaml
version: '3.8'

services:
  app:
    image: my-app:latest
    
    # 资源限制
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    
    # 容器配置
    container_name: my-app-container
    hostname: my-app-host
    domainname: example.com
    
    # 用户和权限
    user: "1000:1000"
    working_dir: /app
    read_only: true
    
    # 安全配置
    security_opt:
      - no-new-privileges:true
    
    # 系统控制
    sysctls:
      - net.core.somaxconn=1024
    
    # 标签
    labels:
      com.example.description: "My Application"
      com.example.environment: "production"
```

### 网络和卷配置

#### 网络定义

```yaml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - frontend
  
  api:
    image: my-api
    networks:
      - frontend
      - backend
  
  db:
    image: mysql:8.0
    networks:
      - backend

networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
    labels:
      com.example.usage: "frontend"
  
  backend:
    driver: bridge
    internal: true  # 内部网络
    labels:
      com.example.usage: "backend"
```

#### 卷定义

```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    volumes:
      - db-data:/var/lib/mysql
      - ./config:/etc/mysql/conf.d
      - /host/path:/container/path

volumes:
  db-data:
    driver: local
    driver_opts:
      type: none
      device: /host/path
      o: bind
    labels:
      com.example.usage: "database"
```

### 环境和配置管理

#### 环境变量

```yaml
version: '3.8'

services:
  app:
    image: my-app
    environment:
      # 直接设置
      NODE_ENV: production
      
      # 从 shell 获取
      DATABASE_URL: ${DATABASE_URL}
      
      # 设置默认值
      PORT: ${PORT:-3000}
      
      # 从文件读取
    env_file:
      - .env
      - .env.local
```

#### 配置和密钥

```yaml
version: '3.8'

services:
  app:
    image: my-app
    configs:
      - source: app-config
        target: /app/config.json
    secrets:
      - db-password

configs:
  app-config:
    file: ./config/app.json

secrets:
  db-password:
    file: ./secrets/db_password.txt
```

### 实际应用示例

#### Web 应用栈

```yaml
# docker-compose.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - web-content:/usr/share/nginx/html
    networks:
      - frontend
    depends_on:
      - app
    restart: always

  app:
    build: ./app
    environment:
      - NODE_ENV=production
      - DATABASE_URL=mysql://db:3306/myapp
      - REDIS_URL=redis://redis:6379
    volumes:
      - app-logs:/app/logs
    networks:
      - frontend
      - backend
    depends_on:
      - db
      - redis
    restart: always

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: myapp
      MYSQL_USER: appuser
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/mysql
      - ./mysql/conf.d:/etc/mysql/conf.d
    networks:
      - backend
    restart: always

  redis:
    image: redis:alpine
    networks:
      - backend
    restart: always

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true

volumes:
  web-content:
  app-logs:
  db-data:
```

#### 开发环境配置

```yaml
# docker-compose.yml (基础配置)
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp_dev
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

```yaml
# docker-compose.override.yml (开发环境覆盖)
version: '3.8'

services:
  app:
    environment:
      - NODE_ENV=development
      - DEBUG=app:*
    ports:
      - "3000:3000"
      - "9229:9229"  # Node.js 调试端口
```

通过本节内容，您已经深入了解了 Docker Compose 的核心概念、工作原理和基本配置。掌握这些知识将帮助您更好地理解和使用 Docker Compose 来管理多容器应用。