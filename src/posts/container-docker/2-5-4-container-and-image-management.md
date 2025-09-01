---
title: Container and Image Management - Finding, Deleting, and Cleaning Up
date: 2025-08-30
categories: [Docker]
tags: [docker, containers, images, management, cleanup]
published: true
---

## 容器与镜像的管理：查找、删除与清理

### Docker 资源管理概述

有效的 Docker 资源管理对于维护健康的开发和生产环境至关重要。随着使用时间的增长，系统中会积累大量的容器、镜像、卷和网络资源，这些资源可能会占用大量磁盘空间并影响系统性能。

#### 资源类型

Docker 管理的主要资源类型包括：
1. **镜像（Images）**：只读模板，用于创建容器
2. **容器（Containers）**：镜像的运行实例
3. **卷（Volumes）**：持久化数据存储
4. **网络（Networks）**：容器间通信

### 镜像管理

#### 查看镜像

```bash
# 查看所有本地镜像
docker images

# 查看特定镜像
docker images nginx

# 格式化输出
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"

# 查看悬空镜像（无标签的镜像）
docker images -f "dangling=true"

# 查看未使用的镜像
docker images -f "dangling=false" -f "reference=myapp:*"
```

#### 镜像信息查看

```bash
# 查看镜像详细信息
docker inspect nginx:latest

# 查看镜像历史
docker history nginx:latest

# 查看镜像大小
docker system df
docker system df -v  # 详细信息
```

#### 镜像删除

```bash
# 删除指定镜像
docker rmi nginx:latest

# 强制删除镜像（即使有容器在使用）
docker rmi -f nginx:latest

# 删除多个镜像
docker rmi image1 image2 image3

# 删除所有未使用的镜像
docker image prune

# 删除所有未使用的镜像（不提示确认）
docker image prune -a -f

# 删除悬空镜像
docker image prune -f
```

#### 批量镜像操作

```bash
# 删除特定仓库的所有镜像
docker rmi $(docker images -q nginx)

# 删除所有镜像（谨慎使用）
docker rmi $(docker images -q)

# 删除指定时间前的镜像
docker image prune --filter "until=24h"

# 删除特定标签模式的镜像
docker rmi $(docker images "myapp:*" -q)
```

### 容器管理

#### 查看容器

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括已停止的）
docker ps -a

# 格式化输出
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.RunningFor}}"

# 查看最近创建的容器
docker ps -l

# 查看最近 N 个容器
docker ps -n 5

# 查看容器大小
docker ps -s
```

#### 容器过滤

```bash
# 按名称过滤
docker ps -f name=my-container

# 按状态过滤
docker ps -f status=running
docker ps -f status=exited
docker ps -f status=paused

# 按镜像过滤
docker ps -f ancestor=nginx

# 按标签过滤
docker ps -f label=env=production

# 按卷过滤
docker ps -f volume=my-volume

# 组合过滤
docker ps -f status=exited -f ancestor=nginx
```

#### 容器删除

```bash
# 删除已停止的容器
docker rm my-container

# 强制删除运行中的容器
docker rm -f my-container

# 删除多个容器
docker rm container1 container2 container3

# 删除所有已停止的容器
docker container prune

# 删除所有已停止的容器（不提示确认）
docker container prune -f

# 删除特定状态的容器
docker rm $(docker ps -q -f status=exited)
```

#### 批量容器操作

```bash
# 删除特定镜像的所有容器
docker rm $(docker ps -aq -f ancestor=nginx)

# 停止并删除所有容器
docker stop $(docker ps -q)
docker rm $(docker ps -aq)

# 删除指定时间前的容器
docker container prune --filter "until=24h"
```

### 卷管理

#### 查看卷

```bash
# 查看所有卷
docker volume ls

# 查看特定卷
docker volume ls -f name=my-volume

# 查看未使用的卷
docker volume ls -f dangling=true

# 查看卷详细信息
docker volume inspect my-volume
```

#### 卷删除

```bash
# 删除指定卷
docker volume rm my-volume

# 删除多个卷
docker volume rm volume1 volume2 volume3

# 删除所有未使用的卷
docker volume prune

# 删除所有未使用的卷（不提示确认）
docker volume prune -f
```

### 网络管理

#### 查看网络

```bash
# 查看所有网络
docker network ls

# 查看特定网络
docker network ls -f name=my-network

# 查看未使用的网络
docker network ls -f dangling=true

# 查看网络详细信息
docker network inspect bridge
```

#### 网络删除

```bash
# 删除指定网络
docker network rm my-network

# 删除多个网络
docker network rm network1 network2

# 删除所有未使用的网络
docker network prune

# 删除所有未使用的网络（不提示确认）
docker network prune -f
```

### 系统级清理

#### 磁盘使用情况

```bash
# 查看 Docker 磁盘使用情况
docker system df

# 查看详细磁盘使用情况
docker system df -v

# 查看实时资源使用情况
docker stats

# 查看所有容器的资源使用情况
docker stats $(docker ps -q)
```

#### 系统清理

```bash
# 清理所有未使用的资源
docker system prune

# 清理所有未使用的资源（包括镜像）
docker system prune -a

# 清理所有未使用的资源（不提示确认）
docker system prune -f

# 清理所有未使用的资源（包括镜像，不提示确认）
docker system prune -a -f

# 清理特定类型的资源
docker container prune  # 清理容器
docker image prune     # 清理镜像
docker volume prune    # 清理卷
docker network prune   # 清理网络
```

#### 高级清理选项

```bash
# 清理指定时间前的资源
docker system prune --filter "until=24h"

# 清理特定标签的资源
docker system prune --filter "label=env=dev"

# 组合过滤条件
docker system prune --filter "until=24h" --filter "label=env=dev"
```

### 资源管理最佳实践

#### 定期清理策略

```bash
# 创建清理脚本
#!/bin/bash
echo "清理未使用的容器..."
docker container prune -f

echo "清理未使用的卷..."
docker volume prune -f

echo "清理未使用的网络..."
docker network prune -f

echo "清理悬空镜像..."
docker image prune -f

echo "清理完成！"
```

#### 磁盘空间监控

```bash
# 创建磁盘监控脚本
#!/bin/bash
USAGE=$(docker system df --format "{{.Size}}")
echo "当前 Docker 占用空间: $USAGE"

# 设置阈值警告
THRESHOLD="10G"
if [ "$USAGE" -gt "$THRESHOLD" ]; then
    echo "警告：Docker 磁盘使用超过阈值 $THRESHOLD"
    # 执行清理操作
    docker system prune -f
fi
```

#### 标签管理

```bash
# 为资源添加标签便于管理
docker run -d --name web --label env=production --label team=backend nginx
docker volume create --label env=production --label team=database my-volume

# 根据标签过滤资源
docker ps -f label=env=production
docker volume ls -f label=team=database
```

### 故障排除

#### 磁盘空间不足

```bash
# 查看磁盘使用情况
df -h

# 查看 Docker 磁盘使用详情
docker system df -v

# 清理未使用的资源
docker system prune -a -f

# 删除特定的大镜像
docker rmi $(docker images --format "{{.Size}}\t{{.Repository}}:{{.Tag}}" | \
  sort -hr | head -5 | awk '{print $2}')
```

#### 资源删除失败

```bash
# 检查资源是否正在使用
docker inspect resource-name

# 强制删除资源
docker rm -f container-name
docker rmi -f image-name

# 停止所有容器后删除
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
```

#### 权限问题

```bash
# 将用户添加到 docker 组
sudo usermod -aG docker $USER

# 重启系统或重新登录
# 然后重新尝试操作
```

### 自动化管理

#### 使用脚本自动化清理

```bash
#!/bin/bash
# docker-cleanup.sh

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# 清理函数
cleanup() {
    log "开始清理 Docker 资源..."
    
    # 清理已停止的容器
    stopped_containers=$(docker ps -aq -f status=exited)
    if [ -n "$stopped_containers" ]; then
        log "清理已停止的容器..."
        docker rm $stopped_containers
    fi
    
    # 清理未使用的卷
    log "清理未使用的卷..."
    docker volume prune -f
    
    # 清理未使用的网络
    log "清理未使用的网络..."
    docker network prune -f
    
    # 清理悬空镜像
    log "清理悬空镜像..."
    docker image prune -f
    
    log "清理完成！"
    
    # 显示清理后的磁盘使用情况
    log "当前 Docker 磁盘使用情况："
    docker system df
}

# 执行清理
cleanup
```

#### 定时清理任务

```bash
# 添加到 crontab 中，每天凌晨 2 点执行清理
0 2 * * * /path/to/docker-cleanup.sh >> /var/log/docker-cleanup.log 2>&1
```

通过本节内容，您已经掌握了 Docker 资源管理的各个方面，包括如何查找、删除和清理容器、镜像、卷和网络资源。定期进行资源管理可以确保 Docker 环境的健康运行，避免磁盘空间不足等问题。