---
title: Deploying and Managing Services with Docker Swarm - Mastering Service Orchestration
date: 2025-08-31
categories: [Docker]
tags: [docker, swarm, services, orchestration]
published: true
---

## 使用 Docker Swarm 部署与管理服务

### 服务（Service）概念详解

在 Docker Swarm 中，服务是应用部署的核心抽象。服务定义了在集群中运行的任务规格，包括使用的镜像、副本数量、网络配置、存储卷等。Swarm 负责确保按照服务定义创建和维护指定数量的任务。

#### 服务与容器的关系

1. **服务**：定义了应用的期望状态
2. **任务**：服务的具体执行单元
3. **容器**：任务的实际运行实例

### 创建和部署服务

#### 基本服务创建

```bash
# 创建简单服务
docker service create --name web nginx

# 创建带副本数的服务
docker service create \
  --name web \
  --replicas 3 \
  nginx

# 创建带端口映射的服务
docker service create \
  --name web \
  --publish 8080:80 \
  nginx
```

#### 服务配置选项

```bash
# 创建带环境变量的服务
docker service create \
  --name web \
  --env NODE_ENV=production \
  --env DATABASE_URL=mysql://db:3306/app \
  nginx

# 创建带命令和参数的服务
docker service create \
  --name app \
  --workdir /app \
  --user 1000:1000 \
  alpine ping docker.com
```

### 服务管理操作

#### 查看服务状态

```bash
# 列出所有服务
docker service ls

# 查看服务详细信息
docker service inspect web

# 查看服务任务
docker service ps web

# 实时查看服务日志
docker service logs -f web
```

#### 更新服务配置

```bash
# 更新服务镜像
docker service update \
  --image nginx:1.21 \
  web

# 更新副本数量
docker service update \
  --replicas 5 \
  web

# 更新环境变量
docker service update \
  --env-add API_KEY=secret123 \
  web

# 更新端口映射
docker service update \
  --publish-add 8443:443 \
  web
```

#### 服务扩缩容

```bash
# 扩展服务副本数
docker service scale web=10

# 缩减服务副本数
docker service scale web=2

# 批量扩缩容
docker service scale web=5 api=3 db=1
```

### 服务网络配置

#### 创建自定义网络

```bash
# 创建 overlay 网络
docker network create \
  --driver overlay \
  --attachable \
  my-overlay-net

# 创建带子网配置的网络
docker network create \
  --driver overlay \
  --subnet=192.168.10.0/24 \
  --gateway=192.168.10.1 \
  app-network
```

#### 服务网络连接

```bash
# 创建连接到自定义网络的服务
docker service create \
  --name web \
  --network my-overlay-net \
  --publish 80:80 \
  nginx

# 更新服务网络配置
docker service update \
  --network-add app-network \
  web

# 移除服务网络
docker service update \
  --network-rm my-overlay-net \
  web
```

### 服务存储配置

#### 使用命名卷

```bash
# 创建命名卷
docker volume create web-data

# 创建使用卷的服务
docker service create \
  --name web \
  --mount type=volume,source=web-data,target=/usr/share/nginx/html \
  nginx
```

#### 使用绑定挂载

```bash
# 创建使用绑定挂载的服务
docker service create \
  --name web \
  --mount type=bind,source=/host/data,target=/container/data \
  nginx
```

### 服务更新策略

#### 滚动更新

```bash
# 配置滚动更新参数
docker service update \
  --update-parallelism 2 \
  --update-delay 10s \
  --update-failure-action rollback \
  web

# 强制更新服务
docker service update \
  --force \
  web
```

#### 回滚操作

```bash
# 回滚到上一个版本
docker service update \
  --rollback \
  web

# 配置回滚策略
docker service update \
  --rollback-parallelism 2 \
  --rollback-monitor 5s \
  --rollback-max-failure-ratio 0.2 \
  web
```

### 服务约束和偏好

#### 节点约束

```bash
# 基于节点标签的约束
docker service create \
  --name web \
  --constraint node.labels.environment==production \
  nginx

# 基于节点角色的约束
docker service create \
  --name db \
  --constraint node.role==manager \
  mysql
```

#### 节点偏好

```bash
# 基于节点标签的偏好
docker service create \
  --name web \
  --placement-pref spread=node.labels.datacenter \
  nginx
```

### 服务健康检查

#### 配置健康检查

```bash
# 配置服务健康检查
docker service create \
  --name web \
  --health-cmd "curl -f http://localhost || exit 1" \
  --health-interval 30s \
  --health-timeout 10s \
  --health-retries 3 \
  --health-start-period 5s \
  nginx
```

### 服务资源限制

#### CPU 和内存限制

```bash
# 设置资源限制
docker service create \
  --name web \
  --limit-cpu 0.5 \
  --limit-memory 512M \
  --reserve-cpu 0.1 \
  --reserve-memory 128M \
  nginx
```

### 多服务应用示例

#### 部署 Web 应用栈

```bash
# 创建网络
docker network create --driver overlay web-network

# 创建数据库服务
docker service create \
  --name db \
  --network web-network \
  --env MYSQL_ROOT_PASSWORD=rootpass \
  --env MYSQL_DATABASE=myapp \
  mysql:8.0

# 创建 Web 应用服务
docker service create \
  --name web \
  --network web-network \
  --publish 80:80 \
  --env DATABASE_URL=mysql://root:rootpass@db:3306/myapp \
  nginx

# 创建负载均衡器服务
docker service create \
  --name lb \
  --network web-network \
  --publish 8080:80 \
  --replicas 2 \
  nginx
```

### 服务故障排除

#### 常见问题诊断

```bash
# 查看服务任务状态
docker service ps web

# 查看节点详细信息
docker node inspect <NODE-ID>

# 查看服务日志
docker service logs web

# 检查服务配置
docker service inspect web
```

#### 性能监控

```bash
# 查看服务资源使用情况
docker stats $(docker service ps --quiet web)
```

### 最佳实践

#### 服务设计原则

1. **单一职责**：每个服务应该只负责一个功能
2. **无状态设计**：尽量设计无状态服务
3. **弹性设计**：服务应该能够处理故障和重启

#### 配置管理

1. **环境变量**：使用环境变量管理配置
2. **密钥管理**：使用 Docker secrets 管理敏感信息
3. **配置文件**：使用 Docker configs 管理配置文件

通过本节内容，我们深入了解了如何在 Docker Swarm 中创建、部署和管理服务。掌握这些技能将帮助您构建可扩展、高可用的容器化应用。