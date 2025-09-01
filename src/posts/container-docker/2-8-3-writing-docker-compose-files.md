---
title: Writing docker-compose.yml Files - Mastering Compose Configuration
date: 2025-08-30
categories: [Write]
tags: [docker, compose, yaml, configuration]
published: true
---

## 编写 `docker-compose.yml` 文件

### Compose 文件基础

docker-compose.yml 文件是 Docker Compose 的核心配置文件，使用 YAML 格式编写。它定义了应用的所有服务、网络、卷和其他资源。理解 Compose 文件的结构和语法对于有效使用 Docker Compose 至关重要。

#### YAML 语法基础

YAML（YAML Ain't Markup Language）是一种人类可读的数据序列化标准，具有以下特点：

1. **缩进敏感**：使用空格进行缩进，不使用制表符
2. **层次结构**：通过缩进表示数据的层次关系
3. **数据类型**：支持字符串、数字、布尔值、数组和对象

```yaml
# 基本数据类型示例
string_value: "Hello World"
number_value: 42
boolean_value: true
array_value:
  - item1
  - item2
  - item3
object_value:
  key1: value1
  key2: value2
```

### Compose 文件版本和结构

#### 文件版本选择

```yaml
# 推荐使用 3.x 版本
version: '3.8'

# 或者使用最新的 Compose 规范（无需 version 字段）
# services:
#   web:
#     image: nginx
```

#### 基本文件结构

```yaml
version: '3.8'

services:        # 服务定义（必需）
  service1:      # 服务名称
    # 服务配置
  service2:
    # 服务配置

volumes:         # 卷定义（可选）
  volume1:       # 卷名称
    # 卷配置

networks:        # 网络定义（可选）
  network1:      # 网络名称
    # 网络配置

configs:         # 配置定义（可选）
  config1:       # 配置名称
    # 配置内容

secrets:         # 密钥定义（可选）
  secret1:       # 密钥名称
    # 密钥内容
```

### 服务配置详解

#### 基本服务配置

```yaml
version: '3.8'

services:
  web:
    # 镜像配置
    image: nginx:alpine
    
    # 或者构建配置
    # build:
    #   context: ./web
    #   dockerfile: Dockerfile
    
    # 容器名称
    container_name: my-web-container
    
    # 端口映射
    ports:
      - "80:80"           # 短格式
      - "443:443"
      - target: 8080      # 长格式
        published: 8080
        protocol: tcp
        mode: host
    
    # 环境变量
    environment:
      - NODE_ENV=production
      - DATABASE_URL=mysql://db:3306/app
      # 或者使用字典格式
      # environment:
      #   NODE_ENV: production
      #   DATABASE_URL: mysql://db:3306/app
    
    # 环境变量文件
    env_file:
      - .env
      - .env.local
    
    # 卷挂载
    volumes:
      - web-data:/usr/share/nginx/html    # 命名卷
      - ./nginx.conf:/etc/nginx/nginx.conf # 绑定挂载
      - /tmp/cache                        # 匿名卷
    
    # 依赖关系
    depends_on:
      - db
      - redis
    
    # 网络配置
    networks:
      - frontend
      - backend
    
    # 重启策略
    restart: always  # no, always, on-failure, unless-stopped
    
    # 命令覆盖
    command: nginx -g 'daemon off;'
    
    # 入口点覆盖
    # entrypoint: ["nginx", "-g", "daemon off;"]
```

#### 高级服务配置

```yaml
version: '3.8'

services:
  app:
    image: my-app:latest
    
    # 资源限制
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    
    # 健康检查
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # 容器配置
    hostname: my-app-host
    domainname: example.com
    user: "1000:1000"
    working_dir: /app
    read_only: true
    
    # 安全配置
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - SYS_PTRACE
    
    # 系统控制
    sysctls:
      - net.core.somaxconn=1024
    
    # 标签
    labels:
      com.example.description: "My Application"
      com.example.version: "1.0"
    
    # 设备访问
    devices:
      - "/dev/ttyUSB0:/dev/ttyUSB0"
    
    # tmpfs 挂载
    tmpfs:
      - /tmp
      - /var/run
    
    # DNS 配置
    dns:
      - 8.8.8.8
      - 8.8.4.4
    dns_search:
      - example.com
```

### 网络配置

#### 基本网络配置

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
    # 驱动特定选项
    driver_opts:
      com.docker.network.bridge.name: docker1
    # IPAM 配置
    ipam:
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1
    # 标签
    labels:
      com.example.usage: "frontend"
  
  backend:
    driver: bridge
    internal: true  # 内部网络，无法访问外部
    attachable: true  # 允许独立容器连接
```

#### 外部网络引用

```yaml
version: '3.8'

services:
  web:
    image: nginx
    networks:
      - external-network

networks:
  external-network:
    external:
      name: my-existing-network
```

### 卷配置

#### 基本卷配置

```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    volumes:
      - db-data:/var/lib/mysql
      - ./config:/etc/mysql/conf.d
      - /host/path:/container/path:ro  # 只读挂载

volumes:
  db-data:
    driver: local
    # 驱动选项
    driver_opts:
      type: none
      device: /host/data/path
      o: bind
    # 标签
    labels:
      com.example.usage: "database"
```

#### 外部卷引用

```yaml
version: '3.8'

services:
  app:
    image: my-app
    volumes:
      - external-data:/app/data

volumes:
  external-data:
    external: true
    # 或者指定名称
    # external:
    #   name: my-existing-volume
```

### 配置和密钥

#### 配置管理

```yaml
version: '3.8'

services:
  app:
    image: my-app
    configs:
      - source: app-config
        target: /app/config.json
        uid: '1000'
        gid: '1000'
        mode: 0444

configs:
  app-config:
    file: ./config/app.json
    # 或者使用外部配置
    # external: true
```

#### 密钥管理

```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db-root-password
    secrets:
      - db-root-password
      - db-user-password

secrets:
  db-root-password:
    file: ./secrets/db_root_password.txt
  db-user-password:
    external: true
    name: my-existing-secret
```

### 实际应用示例

#### 完整的 Web 应用栈

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 负载均衡器
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf:/etc/nginx/conf.d
      - web-content:/usr/share/nginx/html
    networks:
      - frontend
    depends_on:
      - app
    restart: always
    labels:
      com.example.service: "nginx"
      com.example.role: "frontend"

  # 应用服务器
  app:
    build:
      context: ./app
      dockerfile: Dockerfile
    environment:
      - NODE_ENV=production
      - DATABASE_URL=mysql://db:3306/myapp
      - REDIS_URL=redis://redis:6379
      - SESSION_SECRET=${SESSION_SECRET}
    volumes:
      - app-logs:/app/logs
      - ./app/uploads:/app/uploads
    networks:
      - frontend
      - backend
    depends_on:
      - db
      - redis
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 数据库
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: myapp
      MYSQL_USER: appuser
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/mysql
      - ./mysql/init:/docker-entrypoint-initdb.d
    networks:
      - backend
    restart: always
    command: --default-authentication-plugin=mysql_native_password
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 缓存服务
  redis:
    image: redis:alpine
    networks:
      - backend
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 消息队列
  rabbitmq:
    image: rabbitmq:management
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    ports:
      - "15672:15672"  # 管理界面
    networks:
      - backend
    restart: always
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq

networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24
    labels:
      com.example.network: "frontend"
  
  backend:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.21.0.0/24
    labels:
      com.example.network: "backend"

volumes:
  web-content:
    driver: local
    labels:
      com.example.volume: "web-content"
  
  app-logs:
    driver: local
    labels:
      com.example.volume: "app-logs"
  
  db-data:
    driver: local
    driver_opts:
      type: none
      device: /host/mysql/data
      o: bind
    labels:
      com.example.volume: "db-data"
  
  rabbitmq-data:
    driver: local
    labels:
      com.example.volume: "rabbitmq-data"
```

#### 开发环境配置

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  app:
    build:
      context: ./app
      dockerfile: Dockerfile.dev
    environment:
      - NODE_ENV=development
      - DEBUG=app:*
    volumes:
      - ./app:/app
      - /app/node_modules  # 避免覆盖 node_modules
    ports:
      - "3000:3000"
      - "9229:9229"  # Node.js 调试端口
    command: npm run dev

  db:
    ports:
      - "3306:3306"  # 暴露数据库端口用于本地连接
```

### 最佳实践

#### 文件组织

```bash
# 推荐的项目结构
project/
├── docker-compose.yml          # 基础配置
├── docker-compose.override.yml # 开发环境覆盖
├── docker-compose.prod.yml     # 生产环境覆盖
├── .env                        # 环境变量
├── .env.sample                 # 环境变量示例
├── nginx/
│   └── conf/
│       └── default.conf
├── mysql/
│   └── init/
│       └── init.sql
└── app/
    ├── Dockerfile
    ├── Dockerfile.dev
    └── ...
```

#### 配置验证

```bash
# 验证配置文件语法
docker-compose config

# 查看合并后的配置
docker-compose config > full-config.yml

# 验证配置但不输出
docker-compose config -q
```

通过本节内容，您已经深入了解了如何编写 docker-compose.yml 文件，包括服务、网络、卷、配置和密钥的详细配置方法。掌握这些配置技巧将帮助您创建高效、安全且易于维护的多容器应用配置。