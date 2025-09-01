---
title: Docker Network Models and Types - Understanding Bridge, Host, Overlay and More
date: 2025-08-30
categories: [Docker]
tags: [docker, networking, bridge, host, overlay]
published: true
---

## Docker 网络模型与类型（bridge, host, overlay 等）

### Docker 网络架构概述

Docker 网络是容器化应用的核心组件之一，它负责容器间的通信以及容器与外部网络的连接。Docker 提供了多种网络驱动来满足不同的使用场景，每种驱动都有其特定的用途和优势。

#### 网络驱动类型

Docker 支持以下几种主要的网络驱动：

1. **Bridge**：默认网络驱动，适用于同一主机上的容器通信
2. **Host**：移除网络隔离，容器直接使用主机网络
3. **Overlay**：用于跨多个 Docker 主机的网络通信
4. **Macvlan**：为容器分配 MAC 地址，使其在网络中表现为物理设备
5. **None**：禁用容器的所有网络功能
6. **Third-party plugins**：由第三方提供的网络插件

### Bridge 网络详解

Bridge 网络是 Docker 的默认网络驱动，适用于同一主机上容器间的通信。

#### 默认 Bridge 网络

当 Docker 安装完成后，会自动创建一个名为 `bridge` 的默认网络：

```bash
# 查看默认网络
docker network ls

# 查看默认 bridge 网络详细信息
docker network inspect bridge
```

默认 bridge 网络的特点：
- 所有容器默认连接到此网络
- 容器间可以通过 IP 地址通信
- 容器无法通过名称直接通信（需要 `--link` 参数，但已废弃）

#### 自定义 Bridge 网络

创建自定义 bridge 网络可以提供更好的网络隔离和容器名称解析：

```bash
# 创建自定义 bridge 网络
docker network create my-network

# 创建带有子网配置的网络
docker network create --driver bridge \
  --subnet=172.20.0.0/16 \
  --ip-range=172.20.240.0/20 \
  my-custom-network

# 运行容器并连接到自定义网络
docker run -d --name web --network my-network nginx
docker run -d --name db --network my-network mysql
```

自定义 bridge 网络的优势：
- 容器间可以通过名称直接通信
- 提供更好的网络隔离
- 支持网络级别的 DNS 解析

### Host 网络详解

Host 网络模式移除了容器与主机之间的网络隔离，容器直接使用主机的网络栈。

#### 使用 Host 网络

```bash
# 使用 host 网络运行容器
docker run -d --network host nginx

# 注意：host 网络不支持端口映射
# -p 和 -P 参数在 host 网络中无效
```

Host 网络的特点：
- 性能最佳，无网络地址转换开销
- 容器直接使用主机端口
- 不支持端口映射
- 安全性较低，容器网络与主机网络无隔离

适用场景：
- 性能要求极高的应用
- 需要监听大量端口的应用
- 网络调试和监控工具

### Overlay 网络详解

Overlay 网络用于跨多个 Docker 主机的容器通信，是 Docker Swarm 模式的基础。

#### 创建 Overlay 网络

```bash
# 初始化 Swarm 集群
docker swarm init

# 创建 overlay 网络
docker network create --driver overlay my-overlay-network

# 创建带有特定子网的 overlay 网络
docker network create --driver overlay \
  --subnet=10.0.10.0/24 \
  --attachable \
  my-overlay-network
```

Overlay 网络的特点：
- 支持跨主机容器通信
- 自动处理网络加密（可选）
- 集成服务发现和负载均衡
- 适用于 Docker Swarm 模式

#### 在 Swarm 服务中使用 Overlay 网络

```bash
# 创建 Swarm 服务并使用 overlay 网络
docker service create \
  --name web \
  --network my-overlay-network \
  --replicas 3 \
  nginx
```

### Macvlan 网络详解

Macvlan 网络为容器分配 MAC 地址，使其在网络中表现为物理设备。

#### 创建 Macvlan 网络

```bash
# 创建 macvlan 网络
docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 \
  my-macvlan-network

# 运行容器并连接到 macvlan 网络
docker run -d --name my-container --network my-macvlan-network nginx
```

Macvlan 网络的特点：
- 容器获得独立的 IP 和 MAC 地址
- 容器可以直接从网络 DHCP 服务器获取 IP
- 适用于需要直接接入物理网络的场景

### None 网络详解

None 网络模式禁用容器的所有网络功能。

#### 使用 None 网络

```bash
# 使用 none 网络运行容器
docker run -d --network none --name my-container alpine

# 进入容器查看网络状态
docker exec -it my-container ip addr
# 输出将显示只有 loopback 接口
```

None 网络的特点：
- 容器无网络连接
- 适用于不需要网络连接的应用
- 提供最高的网络安全性

### 网络配置管理

#### 查看网络信息

```bash
# 查看所有网络
docker network ls

# 查看网络详细信息
docker network inspect bridge

# 格式化输出网络信息
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"
```

#### 网络连接管理

```bash
# 将运行中的容器连接到网络
docker network connect my-network my-container

# 断开容器与网络的连接
docker network disconnect my-network my-container

# 查看容器的网络连接
docker inspect my-container | grep -A 20 NetworkSettings
```

#### 网络删除

```bash
# 删除网络
docker network rm my-network

# 删除所有未使用的网络
docker network prune

# 删除所有未使用的网络（不提示确认）
docker network prune -f
```

### 网络安全配置

#### 网络隔离

```bash
# 创建隔离的网络
docker network create --internal isolated-network

# 运行容器在隔离网络中
docker run -d --name secure-container --network isolated-network nginx
```

#### 网络访问控制

```bash
# 使用网络别名
docker run -d --name web --network my-network --network-alias web-server nginx

# 配置网络标签
docker network create --label env=production --label team=backend prod-network
```

### 网络故障排除

#### 常见网络问题

1. **DNS 解析失败**：
```bash
# 检查容器 DNS 配置
docker exec -it container-name cat /etc/resolv.conf

# 测试 DNS 解析
docker exec -it container-name nslookup google.com
```

2. **网络连接超时**：
```bash
# 检查容器网络连接
docker exec -it container-name ping 8.8.8.8

# 查看容器路由表
docker exec -it container-name ip route
```

3. **端口无法访问**：
```bash
# 检查端口映射
docker port container-name

# 检查主机端口监听
netstat -tlnp | grep :8080
```

#### 网络调试工具

```bash
# 使用 netshoot 镜像进行网络调试
docker run -it --network container:my-container nicolaka/netshoot

# 在调试容器中执行网络命令
# ping, traceroute, tcpdump, nslookup 等
```

### 网络性能优化

#### 网络驱动选择

根据使用场景选择合适的网络驱动：
- **Bridge**：适用于单主机容器通信
- **Host**：适用于高性能需求
- **Overlay**：适用于多主机集群
- **Macvlan**：适用于直接物理网络接入

#### 网络配置优化

```bash
# 配置网络 MTU
docker network create --opt com.docker.network.driver.mtu=1450 my-network

# 配置网络标签
docker network create --label com.example.usage=web my-network
```

通过本节内容，您已经深入了解了 Docker 的各种网络模型和类型，包括它们的特点、使用场景和配置方法。掌握这些知识将帮助您为容器化应用设计合适的网络架构。