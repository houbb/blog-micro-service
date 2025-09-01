---
title: Appendix A - Common Docker Commands and Tools Summary
date: 2025-08-31
categories: [Docker]
tags: [docker, commands, tools, reference]
published: true
---

## 附录A：常用 Docker 命令与工具总结

### Docker 命令分类汇总

Docker 提供了丰富的命令集，用于管理镜像、容器、网络、存储等各个方面。本附录将按功能分类总结常用的 Docker 命令。

#### 镜像管理命令

```bash
# 镜像查看命令
docker images                    # 列出本地所有镜像
docker image ls                 # 同上，推荐使用
docker image ls -a              # 列出所有镜像（包括中间层镜像）
docker image ls ubuntu          # 列出指定镜像

# 镜像拉取和推送
docker pull ubuntu:20.04        # 从仓库拉取镜像
docker push myrepo/myapp:latest # 推送镜像到仓库

# 镜像构建
docker build -t myapp:latest .  # 从Dockerfile构建镜像
docker build -f Dockerfile.prod -t myapp:prod .  # 指定Dockerfile构建

# 镜像删除
docker image rm ubuntu:latest   # 删除指定镜像
docker image prune              # 删除未使用的镜像
docker image prune -a           # 删除所有未使用的镜像

# 镜像信息查看
docker image inspect ubuntu     # 查看镜像详细信息
docker image history ubuntu     # 查看镜像构建历史
```

#### 容器管理命令

```bash
# 容器运行
docker run nginx                # 运行容器
docker run -d nginx             # 后台运行容器
docker run -p 8080:80 nginx     # 端口映射运行容器
docker run -v /host/path:/container/path nginx  # 挂载卷运行容器

# 容器查看
docker ps                       # 查看运行中的容器
docker ps -a                    # 查看所有容器
docker container ls             # 同docker ps，推荐使用

# 容器操作
docker start container_name     # 启动已停止的容器
docker stop container_name      # 停止运行中的容器
docker restart container_name   # 重启容器
docker pause container_name     # 暂停容器
docker unpause container_name   # 恢复暂停的容器

# 容器删除
docker rm container_name        # 删除已停止的容器
docker rm -f container_name     # 强制删除运行中的容器
docker container prune          # 删除所有已停止的容器

# 容器信息查看
docker inspect container_name   # 查看容器详细信息
docker logs container_name      # 查看容器日志
docker top container_name       # 查看容器进程
```

#### 网络管理命令

```bash
# 网络查看
docker network ls               # 列出所有网络
docker network inspect bridge   # 查看网络详细信息

# 网络创建和删除
docker network create mynetwork  # 创建自定义网络
docker network create -d bridge mybridge  # 创建桥接网络
docker network rm mynetwork     # 删除网络

# 容器网络操作
docker network connect mynetwork container_name  # 连接容器到网络
docker network disconnect mynetwork container_name  # 断开容器网络连接
```

#### 存储管理命令

```bash
# 卷管理
docker volume ls                # 列出所有卷
docker volume create myvolume   # 创建卷
docker volume inspect myvolume  # 查看卷详细信息
docker volume rm myvolume       # 删除卷
docker volume prune             # 删除未使用的卷

# 挂载操作
docker run -v myvolume:/app nginx  # 使用卷挂载
docker run -v /host/path:/container/path nginx  # 绑定挂载
```

#### 系统管理命令

```bash
# 系统信息
docker info                     # 查看Docker系统信息
docker version                  # 查看Docker版本信息
docker system df                # 查看Docker磁盘使用情况

# 系统清理
docker system prune             # 清理未使用的数据
docker system prune -a          # 清理所有未使用的数据
```

### Docker Compose 命令

Docker Compose 是管理多容器应用的重要工具：

```bash
# Compose 项目管理
docker-compose up               # 启动并运行所有服务
docker-compose up -d            # 后台启动所有服务
docker-compose down             # 停止并删除所有服务
docker-compose down -v          # 删除服务及卷

# Compose 服务管理
docker-compose start            # 启动服务
docker-compose stop             # 停止服务
docker-compose restart          # 重启服务
docker-compose pause            # 暂停服务
docker-compose unpause          # 恢复服务

# Compose 状态查看
docker-compose ps               # 查看服务状态
docker-compose logs             # 查看服务日志
docker-compose logs service_name  # 查看特定服务日志

# Compose 构建和拉取
docker-compose build            # 构建服务
docker-compose pull             # 拉取服务镜像
```

### Docker Swarm 命令

Docker Swarm 是 Docker 原生的集群管理工具：

```bash
# Swarm 集群管理
docker swarm init               # 初始化Swarm集群
docker swarm join --token TOKEN MANAGER_IP:2377  # 加入Swarm集群
docker swarm leave              # 离开Swarm集群

# 节点管理
docker node ls                  # 列出集群节点
docker node inspect node_name   # 查看节点详细信息
docker node promote node_name   # 提升节点为管理节点
docker node demote node_name    # 降级管理节点为工作节点

# 服务管理
docker service create --replicas 3 nginx  # 创建服务
docker service ls               # 列出服务
docker service inspect service_name  # 查看服务详细信息
docker service scale service_name=5  # 扩展服务副本数
docker service update --image nginx:latest service_name  # 更新服务
docker service rm service_name  # 删除服务
```

### 实用工具和技巧

#### Docker CLI 实用技巧

```bash
# 命令别名设置（在 ~/.bashrc 或 ~/.zshrc 中）
alias dps='docker ps'
alias dimg='docker images'
alias drm='docker rm'
alias drmi='docker rmi'

# 批量操作
docker rm $(docker ps -aq)      # 删除所有容器
docker rmi $(docker images -q)  # 删除所有镜像
docker stop $(docker ps -q)     # 停止所有运行中的容器

# 格式化输出
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

#### Dockerfile 优化技巧

```dockerfile
# 多阶段构建示例
# 构建阶段
FROM golang:1.19 AS builder
WORKDIR /app
COPY . .
RUN go build -o main .

# 运行阶段
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
CMD ["./main"]

# 合理安排指令顺序以利用缓存
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt  # 这行会经常变化
COPY . .
```

#### Docker Compose 最佳实践

```yaml
# docker-compose.yml 示例
version: "3.8"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/code
    environment:
      - DEBUG=1
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=myuser
      - POSTGRES_PASSWORD=mypass
  
  redis:
    image: redis:6-alpine

volumes:
  postgres_data:
```

### 第三方工具推荐

#### 镜像安全扫描工具

```bash
# Trivy - 镜像漏洞扫描工具
trivy image nginx:latest
trivy fs /path/to/project

# Clair - 镜像安全扫描服务
clair-scanner nginx:latest

# Docker Bench Security - Docker 安全检查工具
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/bin/docker:/usr/bin/docker \
  -v /var/lib:/var/lib \
  docker/docker-bench-security
```

#### 镜像优化工具

```bash
# Dive - 镜像层分析工具
dive nginx:latest

# DockerSlim - 镜像瘦身工具
docker-slim build --target nginx:latest --tag nginx:slim
```

#### 监控和日志工具

```bash
# cAdvisor - 容器资源监控
docker run -d --name=cadvisor \
  -p 8080:8080 \
  -v /:/rootfs:ro \
  -v /var/run:/var/run:ro \
  -v /sys:/sys:ro \
  -v /var/lib/docker/:/var/lib/docker:ro \
  gcr.io/cadvisor/cadvisor:latest

# Portainer - Docker 管理UI
docker run -d -p 9000:9000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  portainer/portainer-ce
```

通过本附录的内容，您可以快速查找和使用常用的 Docker 命令和工具，提高 Docker 使用效率。