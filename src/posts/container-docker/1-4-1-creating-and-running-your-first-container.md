---
title: Creating and Running Your First Container - A Hands-On Guide
date: 2025-08-30
categories: [Docker]
tags: [container-docker]
published: true
---

## 创建与运行第一个容器

### 准备工作

在创建第一个容器之前，确保您已经完成了 Docker 的安装和基本配置。您可以通过以下命令验证 Docker 是否正常工作：

```bash
# 检查 Docker 版本
docker --version

# 查看 Docker 系统信息
docker info

# 运行测试容器
docker run hello-world
```

如果以上命令都能成功执行，说明 Docker 已经正确安装并配置。

### 运行第一个简单容器

让我们从最简单的容器开始 - 运行一个输出 "Hello World" 的容器：

```bash
docker run hello-world
```

这个命令会：
1. 检查本地是否存在 `hello-world` 镜像
2. 如果不存在，则从 Docker Hub 拉取该镜像
3. 创建并运行一个基于该镜像的容器
4. 容器执行完毕后自动停止

### 运行 Web 服务器容器

让我们尝试运行一个更实用的容器 - Nginx Web 服务器：

```bash
# 基本运行命令
docker run nginx

# 后台运行并映射端口
docker run -d -p 8080:80 --name my-nginx nginx
```

参数解释：
- `-d`：以后台模式运行容器
- `-p 8080:80`：将主机的 8080 端口映射到容器的 80 端口
- `--name my-nginx`：为容器指定一个名称
- `nginx`：要运行的镜像名称

运行成功后，您可以通过浏览器访问 `http://localhost:8080` 查看 Nginx 默认页面。

### 交互式容器

有些容器需要与用户交互，可以使用以下命令运行交互式容器：

```bash
# 运行 Ubuntu 容器并进入终端
docker run -it ubuntu bash

# 在容器中执行命令
root@container-id:/# ls
root@container-id:/# cat /etc/os-release
root@container-id:/# exit
```

参数解释：
- `-i`：保持 STDIN 开放（即使没有附加）
- `-t`：分配一个伪终端
- `ubuntu`：基础镜像
- `bash`：在容器中执行的命令

### 容器运行参数详解

#### 端口映射

端口映射是容器与外部通信的重要机制：

```bash
# 基本端口映射
docker run -p 8080:80 nginx

# 映射多个端口
docker run -p 8080:80 -p 8443:443 nginx

# 随机端口映射
docker run -P nginx  # 将容器所有暴露端口映射到主机随机端口

# 指定 IP 地址映射
docker run -p 127.0.0.1:8080:80 nginx
```

#### 环境变量

通过环境变量可以配置容器内的应用程序：

```bash
# 设置单个环境变量
docker run -e NODE_ENV=production node

# 设置多个环境变量
docker run -e NODE_ENV=production -e PORT=3000 node

# 从文件读取环境变量
echo "NODE_ENV=production" > env.list
echo "PORT=3000" >> env.list
docker run --env-file ./env.list node
```

#### 数据卷挂载

通过数据卷挂载可以实现数据持久化和主机与容器间的数据共享：

```bash
# 绑定挂载
docker run -v /host/path:/container/path nginx

# 命名卷挂载
docker run -v my-volume:/container/path nginx

# 只读挂载
docker run -v /host/path:/container/path:ro nginx

# 挂载工作目录
docker run -v $(pwd):/app -w /app node npm start
```

#### 资源限制

为容器设置资源限制可以防止容器消耗过多系统资源：

```bash
# 限制内存使用
docker run -m 512m nginx

# 限制 CPU 使用
docker run --cpus="1.5" nginx

# 限制 CPU 核心
docker run --cpuset-cpus="0-2" nginx
```

### 容器网络配置

Docker 提供了多种网络模式来满足不同的网络需求：

#### 默认桥接网络

```bash
# 使用默认桥接网络
docker run -d --name web nginx

# 查看容器网络信息
docker inspect web
```

#### 自定义网络

```bash
# 创建自定义网络
docker network create my-network

# 在自定义网络中运行容器
docker run -d --name web --network my-network nginx
docker run -d --name db --network my-network mysql
```

#### 主机网络

```bash
# 使用主机网络
docker run -d --network host nginx
```

### 容器健康检查

通过健康检查可以监控容器内应用程序的状态：

```bash
# 在运行时添加健康检查
docker run -d \
  --name web \
  --health-cmd="curl -f http://localhost || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  nginx
```

### 容器重启策略

设置重启策略可以确保容器在意外停止后自动重启：

```bash
# 总是重启
docker run -d --restart=always nginx

# 失败时重启，最多重启 5 次
docker run -d --restart=on-failure:5 nginx

# 除非手动停止，否则重启
docker run -d --restart=unless-stopped nginx
```

### 实际应用示例

#### 运行数据库容器

```bash
# 运行 MySQL 容器
docker run -d \
  --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=my-secret-pw \
  -e MYSQL_DATABASE=myapp \
  -p 3306:3306 \
  mysql:8.0
```

#### 运行应用容器

```bash
# 运行 Node.js 应用
docker run -d \
  --name my-app \
  -p 3000:3000 \
  -e NODE_ENV=production \
  -v /app/data:/app/data \
  my-node-app:latest
```

#### 多容器应用

```bash
# 运行 Web 服务器
docker run -d --name web -p 80:80 nginx

# 运行数据库
docker run -d --name db -e MYSQL_ROOT_PASSWORD=pass mysql

# 运行应用服务器
docker run -d --name app --link db:database my-app
```

### 容器运行监控

运行容器后，可以通过以下命令监控容器状态：

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 查看容器详细信息
docker inspect my-nginx

# 查看容器日志
docker logs my-nginx

# 实时查看容器日志
docker logs -f my-nginx

# 查看容器资源使用情况
docker stats my-nginx
```

### 故障排除

#### 常见问题及解决方案

**端口冲突：**
```bash
# 错误信息：port is already allocated
# 解决方案：更改端口映射
docker run -d -p 8081:80 nginx
```

**镜像拉取失败：**
```bash
# 检查网络连接
ping registry-1.docker.io

# 使用镜像加速器
# 在 daemon.json 中配置 registry-mirrors
```

**权限问题：**
```bash
# 将用户添加到 docker 组
sudo usermod -aG docker $USER
# 然后注销并重新登录
```

通过本节内容，您已经学会了如何创建和运行 Docker 容器，包括基本的运行命令、参数配置、网络设置和故障排除。这些知识将帮助您在实际项目中有效地使用 Docker 容器。