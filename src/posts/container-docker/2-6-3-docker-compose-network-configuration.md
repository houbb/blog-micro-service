---
title: Docker Compose Network Configuration - Managing Multi-Container Applications
date: 2025-08-30
categories: [Docker]
tags: [docker, compose, networking, multi-container]
published: true
---

## 使用 Docker Compose 配置多容器应用

### Docker Compose 网络概述

Docker Compose 是定义和运行多容器 Docker 应用程序的工具。通过一个 YAML 文件，您可以配置应用程序的所有服务，并使用单个命令创建和启动所有服务。Compose 会自动为应用创建默认网络，并处理服务间的网络连接。

#### Compose 网络默认行为

当使用 Docker Compose 时，系统会自动创建以下网络：

1. **默认网络**：为所有服务创建一个默认的 bridge 网络
2. **服务名称解析**：服务可以通过名称相互访问
3. **环境变量**：自动为链接的服务设置环境变量（旧版本）

### 基本网络配置

#### 简单的 Compose 文件

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    ports:
      - "80:80"
  
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: myapp
```

在这个例子中，Compose 会自动创建一个默认网络，web 和 db 服务都连接到这个网络，并且可以通过服务名称相互访问。

#### 启动和管理应用

```bash
# 启动应用
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看网络信息
docker-compose networks

# 停止应用
docker-compose down
```

### 自定义网络配置

#### 定义自定义网络

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    ports:
      - "80:80"
    networks:
      - frontend
  
  api:
    image: my-api
    networks:
      - frontend
      - backend
  
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
```

#### 网络驱动和配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - webnet

networks:
  webnet:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: docker1
      com.docker.network.bridge.enable_icc: "true"
      com.docker.network.bridge.enable_ip_masquerade: "true"
      com.docker.network.bridge.host_binding_ipv4: "0.0.0.0"
      com.docker.network.driver.mtu: "1500"
    ipam:
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1
    labels:
      com.example.description: "Web network"
```

### 高级网络功能

#### 网络别名和服务发现

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      frontend:
        aliases:
          - web-server
          - nginx-server
  
  api:
    image: my-api
    networks:
      - frontend
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
```

#### 外部网络

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - external-net

networks:
  external-net:
    external:
      name: my-external-network
```

创建外部网络：
```bash
# 创建外部网络
docker network create my-external-network

# 启动 Compose 应用
docker-compose up -d
```

#### 网络标签和配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - appnet

networks:
  appnet:
    driver: bridge
    labels:
      environment: production
      team: backend
      project: myapp
    attachable: true
```

### 网络安全配置

#### 内部网络

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - frontend
  
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  
  backend:
    driver: bridge
    internal: true  # 内部网络，无法访问外部
```

#### 网络访问控制

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - public
  
  api:
    image: my-api
    networks:
      - public
      - private
  
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
    networks:
      - private

networks:
  public:
    driver: bridge
  
  private:
    driver: bridge
    internal: true
```

### 环境特定配置

#### 多环境网络配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - ${NETWORK_NAME:-default}

networks:
  default:
    driver: bridge
```

使用环境变量：
```bash
# 开发环境
NETWORK_NAME=dev-net docker-compose up -d

# 生产环境
NETWORK_NAME=prod-net docker-compose up -d
```

#### 覆盖文件配置

```yaml
# docker-compose.yml (基础配置)
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - frontend

networks:
  frontend:
    driver: bridge
```

```yaml
# docker-compose.prod.yml (生产环境覆盖)
version: '3.8'

services:
  web:
    networks:
      frontend:
        ipv4_address: 172.20.0.10

networks:
  frontend:
    ipam:
      config:
        - subnet: 172.20.0.0/24
```

启动生产环境：
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 网络故障排除

#### 查看网络信息

```bash
# 查看 Compose 应用的网络
docker-compose networks

# 查看网络详细信息
docker network inspect project_frontend

# 查看容器网络配置
docker-compose exec web ip addr
```

#### 网络连接测试

```bash
# 测试服务间连接
docker-compose exec web ping db

# 测试 DNS 解析
docker-compose exec web nslookup api

# 查看路由表
docker-compose exec web ip route
```

#### 日志和调试

```bash
# 查看服务日志
docker-compose logs web

# 实时查看日志
docker-compose logs -f web

# 查看网络驱动日志
docker logs docker-network-driver
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
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    networks:
      - frontend
      - backend
    depends_on:
      - app
  
  app:
    build: ./app
    environment:
      - DATABASE_URL=mysql://db:3306/myapp
      - REDIS_URL=redis://redis:6379
    networks:
      - backend
    depends_on:
      - db
      - redis
  
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: myapp
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - backend
  
  redis:
    image: redis:alpine
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true

volumes:
  db_data:
```

#### 微服务架构

```yaml
# docker-compose.yml
version: '3.8'

services:
  # API 网关
  gateway:
    image: nginx
    ports:
      - "80:80"
    networks:
      - frontend
    volumes:
      - ./gateway.conf:/etc/nginx/conf.d/default.conf
  
  # 用户服务
  user-service:
    image: my-user-service
    environment:
      - DB_HOST=user-db
    networks:
      - user-net
      - message-net
    depends_on:
      - user-db
  
  user-db:
    image: mongo
    networks:
      - user-net
  
  # 订单服务
  order-service:
    image: my-order-service
    environment:
      - DB_HOST=order-db
      - USER_SERVICE_URL=http://user-service:8080
    networks:
      - order-net
      - message-net
    depends_on:
      - order-db
  
  order-db:
    image: postgres
    environment:
      POSTGRES_DB: orders
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    networks:
      - order-net
  
  # 消息队列
  rabbitmq:
    image: rabbitmq:management
    networks:
      - message-net
    ports:
      - "15672:15672"

networks:
  frontend:
    driver: bridge
  user-net:
    driver: bridge
  order-net:
    driver: bridge
  message-net:
    driver: bridge
```

### 网络性能优化

#### 网络驱动优化

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - appnet

networks:
  appnet:
    driver: bridge
    driver_opts:
      com.docker.network.driver.mtu: "1450"
      com.docker.network.bridge.enable_icc: "true"
```

#### 服务间通信优化

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - appnet
    sysctls:
      - net.core.somaxconn=1024
  
  api:
    image: my-api
    networks:
      - appnet
    sysctls:
      - net.core.somaxconn=1024

networks:
  appnet:
    driver: bridge
```

### 最佳实践

#### 网络命名规范

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - myapp-frontend
  
  api:
    image: my-api
    networks:
      - myapp-frontend
      - myapp-backend
  
  db:
    image: mysql:8.0
    networks:
      - myapp-backend

networks:
  myapp-frontend:
    driver: bridge
    labels:
      app: myapp
      tier: frontend
  
  myapp-backend:
    driver: bridge
    internal: true
    labels:
      app: myapp
      tier: backend
```

#### 网络安全最佳实践

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - frontend
    read_only: true
    tmpfs:
      - /tmp
      - /var/cache/nginx
  
  api:
    image: my-api
    networks:
      - frontend
      - backend
    read_only: true
    tmpfs:
      - /tmp
  
  db:
    image: mysql:8.0
    networks:
      - backend
    read_only: false
    volumes:
      - db_data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password

networks:
  frontend:
    driver: bridge
  
  backend:
    driver: bridge
    internal: true

volumes:
  db_data:

secrets:
  db_root_password:
    file: ./secrets/db_root_password.txt
```

通过本节内容，您已经深入了解了如何使用 Docker Compose 配置和管理多容器应用的网络。掌握这些知识将帮助您构建复杂、安全且高性能的容器化应用架构。