---
title: Service Lifecycle Management - Starting, Stopping, and Restarting Services
date: 2025-08-30
categories: [Write]
tags: [docker, compose, lifecycle, management]
published: true
---

## 管理服务的生命周期（启动、停止、重启）

### 服务生命周期概述

Docker Compose 提供了完整的命令集来管理多容器应用的生命周期。理解这些命令的使用方法和最佳实践对于有效运维容器化应用至关重要。服务生命周期管理包括启动、停止、重启、扩展和删除等操作。

#### 生命周期阶段

1. **创建阶段**：定义服务配置
2. **启动阶段**：创建并启动容器
3. **运行阶段**：服务正常运行
4. **维护阶段**：更新、扩展、重启服务
5. **停止阶段**：停止并清理服务

### 启动服务

#### 基本启动命令

```bash
# 启动所有服务（前台模式）
docker-compose up

# 启动所有服务（后台模式）
docker-compose up -d

# 启动特定服务
docker-compose up -d web db

# 强制重新创建容器
docker-compose up -d --force-recreate

# 重新构建镜像后启动
docker-compose up -d --build

# 不启动依赖服务
docker-compose up -d --no-deps web
```

#### 启动选项详解

```bash
# 指定配置文件
docker-compose -f docker-compose.yml up -d

# 使用多个配置文件
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 指定项目名称
docker-compose -p myproject up -d

# 指定环境文件
docker-compose --env-file .env.prod up -d

# 跳过镜像拉取
docker-compose up -d --no-build

# 不启动已存在的容器
docker-compose up -d --no-start
```

#### 启动过程监控

```bash
# 实时查看启动日志
docker-compose up

# 查看特定服务日志
docker-compose logs -f web

# 查看最近日志
docker-compose logs --tail=100

# 查看健康检查状态
docker-compose ps
```

### 停止服务

#### 基本停止命令

```bash
# 停止所有服务
docker-compose stop

# 停止特定服务
docker-compose stop web db

# 指定超时时间（默认 10 秒）
docker-compose stop -t 30

# 强制停止服务
docker-compose kill
```

#### 停止选项详解

```bash
# 优雅停止（发送 SIGTERM）
docker-compose stop

# 强制停止（发送 SIGKILL）
docker-compose kill

# 发送特定信号
docker-compose kill -s SIGINT web

# 停止并删除容器
docker-compose down

# 停止并删除容器、网络、卷
docker-compose down -v

# 停止并删除所有相关资源
docker-compose down -v --rmi all
```

#### 停止过程监控

```bash
# 查看服务状态
docker-compose ps

# 查看停止日志
docker-compose logs --since="1min"

# 监控资源释放
docker stats $(docker-compose ps -q)
```

### 重启服务

#### 基本重启命令

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart web db

# 指定超时时间
docker-compose restart -t 30
```

#### 重启策略

```bash
# 在 docker-compose.yml 中定义重启策略
version: '3.8'

services:
  web:
    image: nginx
    restart: always  # no, always, on-failure, unless-stopped
```

#### 重启场景

```bash
# 重启失败的服务
docker-compose restart $(docker-compose ps | grep Exit | awk '{print $1}')

# 定期重启服务（用于清理内存）
docker-compose restart web

# 应用配置更新后重启
docker-compose up -d  # 自动重启已更改的服务
```

### 服务扩展

#### 扩展服务实例

```bash
# 扩展服务到指定实例数
docker-compose up -d --scale web=3

# 查看扩展后的服务
docker-compose ps

# 缩减服务实例
docker-compose up -d --scale web=1

# 扩展多个服务
docker-compose up -d --scale web=3 --scale worker=2
```

#### 负载均衡配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  nginx:
    image: nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
  
  web:
    image: my-app
    # 不直接暴露端口，通过 nginx 访问
```

```nginx
# nginx.conf
upstream app {
    server web:3000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://app;
    }
}
```

### 服务更新

#### 镜像更新

```bash
# 拉取最新镜像
docker-compose pull

# 更新特定服务镜像
docker-compose pull web

# 拉取并重启服务
docker-compose pull
docker-compose up -d

# 强制重新创建容器
docker-compose up -d --force-recreate
```

#### 配置更新

```bash
# 修改 docker-compose.yml 后更新
docker-compose up -d

# 重新构建并更新
docker-compose up -d --build

# 更新特定服务
docker-compose up -d web
```

#### 环境变量更新

```bash
# 更新 .env 文件后重启服务
docker-compose up -d

# 使用新的环境文件
docker-compose --env-file .env.prod up -d
```

### 服务删除

#### 删除容器和资源

```bash
# 停止并删除容器
docker-compose down

# 删除容器和网络
docker-compose down

# 删除容器、网络和卷
docker-compose down -v

# 删除容器、网络、卷和镜像
docker-compose down -v --rmi all

# 删除特定服务
docker-compose rm web
```

#### 清理操作

```bash
# 清理未使用的资源
docker system prune -f

# 清理未使用的卷
docker volume prune -f

# 清理未使用的网络
docker network prune -f
```

### 状态监控和管理

#### 查看服务状态

```bash
# 查看所有服务状态
docker-compose ps

# 查看特定服务状态
docker-compose ps web

# 格式化输出
docker-compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"
```

#### 查看服务日志

```bash
# 查看所有服务日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs web

# 查看最近日志
docker-compose logs --tail=100

# 查看指定时间后的日志
docker-compose logs --since="1h"
```

#### 性能监控

```bash
# 查看资源使用情况
docker-compose top

# 查看实时统计
docker stats $(docker-compose ps -q)

# 查看网络使用情况
docker network inspect $(docker network ls -f name=project_default -q)
```

### 故障排除

#### 常见问题诊断

```bash
# 检查服务状态
docker-compose ps

# 查看服务日志
docker-compose logs service-name

# 进入服务容器调试
docker-compose exec service-name bash

# 运行一次性命令
docker-compose run --rm service-name command
```

#### 健康检查

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
# 查看健康状态
docker-compose ps

# 手动检查健康
docker-compose exec web curl -f http://localhost
```

#### 依赖关系管理

```yaml
# 确保依赖服务启动顺序
version: '3.8'

services:
  web:
    image: nginx
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
```

### 自动化管理

#### 脚本化操作

```bash
#!/bin/bash
# service-manager.sh

PROJECT_NAME="myapp"
COMPOSE_FILE="docker-compose.yml"

start_services() {
    echo "Starting services..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
    echo "Services started"
}

stop_services() {
    echo "Stopping services..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME stop
    echo "Services stopped"
}

restart_services() {
    echo "Restarting services..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME restart
    echo "Services restarted"
}

update_services() {
    echo "Updating services..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME pull
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
    echo "Services updated"
}

case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    update)
        update_services
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|update}"
        exit 1
        ;;
esac
```

#### 定时任务

```bash
# 添加到 crontab 中，每天凌晨重启服务
0 2 * * * /path/to/service-manager.sh restart >> /var/log/service-manager.log 2>&1

# 每小时检查服务健康状态
0 * * * * docker-compose -f /path/to/docker-compose.yml ps | grep -q "healthy" || /path/to/service-manager.sh restart
```

### 最佳实践

#### 启动最佳实践

```bash
# 1. 使用后台模式启动
docker-compose up -d

# 2. 检查服务状态
docker-compose ps

# 3. 查看启动日志
docker-compose logs --tail=50
```

#### 停止最佳实践

```bash
# 1. 优雅停止服务
docker-compose stop

# 2. 确认服务已停止
docker-compose ps

# 3. 必要时清理资源
docker-compose down -v
```

#### 重启最佳实践

```bash
# 1. 重启前检查服务状态
docker-compose ps

# 2. 执行重启
docker-compose restart

# 3. 验证重启结果
docker-compose ps
```

#### 监控最佳实践

```bash
# 1. 定期检查服务状态
docker-compose ps

# 2. 监控关键服务日志
docker-compose logs -f --tail=10 critical-service

# 3. 设置健康检查告警
# 结合监控工具实现自动告警
```

通过本节内容，您已经深入了解了如何管理 Docker Compose 服务的完整生命周期，包括启动、停止、重启、扩展和删除等操作。掌握这些生命周期管理技巧将帮助您更有效地运维容器化应用。