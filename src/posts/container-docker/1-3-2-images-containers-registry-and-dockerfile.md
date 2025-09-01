---
title: Images, Containers, Registry and Dockerfile - The Core Concepts of Docker
date: 2025-08-30
categories: [Docker]
tags: [docker, images, containers, registry, dockerfile]
published: true
---

## 镜像、容器、仓库与 Dockerfile

### Docker 镜像（Image）详解

Docker 镜像是一个轻量级、独立、可执行的软件包，包含了运行应用程序所需的所有内容：代码、运行时环境、系统工具、系统库和设置。镜像是 Docker 容器的基础，容器是镜像的运行实例。

#### 镜像的分层结构

Docker 镜像是分层构建的，这种设计使得镜像构建、共享和存储更加高效。每一层代表镜像的一个变更，这些层是只读的。

**分层优势：**
1. **共享层**：多个镜像可以共享相同的底层
2. **缓存机制**：构建镜像时可以重用未变更的层
3. **增量更新**：只需传输变更的层

**分层结构示例：**
```
+---------------------+
| 应用层 (可写层)      |
+---------------------+
| 配置层               |
+---------------------+
| 应用依赖层           |
+---------------------+
| 系统依赖层           |
+---------------------+
| 基础镜像层 (如 Ubuntu)|
+---------------------+
```

#### 镜像命名规范

Docker 镜像的命名遵循以下格式：
```
[仓库主机地址[:端口]/][用户名/]镜像名[:标签]
```

**示例：**
- `nginx`：官方 nginx 镜像，默认标签为 latest
- `library/nginx`：完整写法，library 是官方镜像的用户名
- `myuser/myapp:1.0`：用户自定义镜像，标签为 1.0
- `registry.example.com:5000/myapp:latest`：私有仓库中的镜像

#### 镜像操作命令

**查看镜像：**
```bash
# 查看所有本地镜像
docker images

# 查看特定镜像
docker images nginx

# 查看镜像详细信息
docker inspect nginx:latest
```

**构建镜像：**
```bash
# 从 Dockerfile 构建镜像
docker build -t myapp:1.0 .

# 指定 Dockerfile 构建
docker build -f Dockerfile.prod -t myapp:prod .
```

**拉取和推送镜像：**
```bash
# 从仓库拉取镜像
docker pull nginx:1.21

# 推送镜像到仓库
docker push myuser/myapp:1.0
```

**删除镜像：**
```bash
# 删除指定镜像
docker rmi nginx:latest

# 强制删除镜像
docker rmi -f nginx:latest
```

### Docker 容器（Container）详解

容器是镜像的运行实例，它包含了应用程序及其运行环境。容器是 Docker 的核心概念，提供了应用程序运行的隔离环境。

#### 容器与镜像的关系

镜像和容器的关系类似于类和对象的关系：
- **镜像**是只读模板，定义了容器的内容
- **容器**是镜像的运行实例，可以被创建、启动、停止、重启和删除

每个容器都包含：
1. **镜像层**：来自基础镜像的只读层
2. **可写层**：容器运行时的读写层

#### 容器状态管理

容器有多种状态，可以通过命令进行管理：

**创建和启动容器：**
```bash
# 创建容器但不启动
docker create nginx

# 启动容器
docker start container_name

# 创建并启动容器（一步完成）
docker run nginx
```

**容器运行模式：**
```bash
# 前台运行（连接到容器）
docker run -it nginx bash

# 后台运行（分离模式）
docker run -d nginx

# 交互式运行
docker run -it --name my-nginx nginx bash
```

**容器状态控制：**
```bash
# 停止容器
docker stop container_name

# 重启容器
docker restart container_name

# 暂停容器
docker pause container_name

# 恢复容器
docker unpause container_name
```

#### 容器资源配置

可以为容器配置资源限制，确保系统稳定性：

```bash
# 限制内存使用
docker run -m 512m nginx

# 限制 CPU 使用
docker run --cpus="1.5" nginx

# 限制 CPU 核心
docker run --cpuset-cpus="0-2" nginx

# 重启策略
docker run --restart=always nginx
```

### Docker 仓库（Registry）详解

Docker 仓库是存储和分发 Docker 镜像的服务。它分为公共仓库和私有仓库两种类型。

#### 公共仓库

**Docker Hub** 是默认的公共仓库，包含大量官方和社区维护的镜像：

```bash
# 登录 Docker Hub
docker login

# 从 Docker Hub 拉取镜像
docker pull ubuntu:20.04

# 推送镜像到 Docker Hub
docker push myuser/myapp:1.0
```

**其他公共仓库：**
- **Google Container Registry (GCR)**
- **Amazon Elastic Container Registry (ECR)**
- **Azure Container Registry (ACR)**

#### 私有仓库

企业通常会搭建私有仓库来存储内部镜像：

**搭建私有仓库：**
```bash
# 运行私有仓库容器
docker run -d -p 5000:5000 --name registry registry:2

# 推送镜像到私有仓库
docker tag myapp:1.0 localhost:5000/myapp:1.0
docker push localhost:5000/myapp:1.0
```

**配置私有仓库：**
```json
{
  "insecure-registries": ["registry.example.com:5000"]
}
```

#### 镜像签名和验证

为了确保镜像的安全性，可以使用内容信任机制：

```bash
# 启用内容信任
export DOCKER_CONTENT_TRUST=1

# 推送签名镜像
docker push myuser/myapp:1.0

# 拉取签名镜像
docker pull myuser/myapp:1.0
```

### Dockerfile 详解

Dockerfile 是一个文本文件，包含一系列指令，用于自动化构建镜像。它是实现"基础设施即代码"的重要工具。

#### 基本指令

**基础指令：**
```dockerfile
# 指定基础镜像
FROM ubuntu:20.04

# 设置维护者信息
LABEL maintainer="user@example.com"

# 设置环境变量
ENV NODE_ENV=production

# 设置工作目录
WORKDIR /app

# 复制文件
COPY . /app

# 添加文件（支持远程 URL）
ADD http://example.com/file.tar.gz /app/

# 运行命令
RUN apt-get update && apt-get install -y nginx

# 暴露端口
EXPOSE 80

# 设置入口点
ENTRYPOINT ["nginx"]

# 设置默认命令
CMD ["-g", "daemon off;"]
```

#### 构建优化技巧

**减少层数：**
```dockerfile
# 不推荐：多层 RUN 指令
RUN apt-get update
RUN apt-get install -y nginx
RUN apt-get clean

# 推荐：合并 RUN 指令
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean
```

**利用缓存：**
```dockerfile
# 将变化较少的指令放在前面
COPY package.json /app/
RUN npm install
COPY . /app/
```

**多阶段构建：**
```dockerfile
# 构建阶段
FROM node:14 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 运行阶段
FROM node:14-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm install --production
CMD ["npm", "start"]
```

#### 最佳实践

**安全性考虑：**
```dockerfile
# 使用最小基础镜像
FROM alpine:latest

# 以非 root 用户运行
RUN adduser -D -s /bin/sh appuser
USER appuser

# 避免安装不必要的包
```

**性能优化：**
```dockerfile
# 合理使用 .dockerignore
# 只复制需要的文件
COPY package*.json ./
```

### 镜像分发和版本管理

#### 标签管理

合理的标签策略有助于镜像管理：

```bash
# 语义化版本标签
docker tag myapp:latest myapp:1.2.3

# 环境标签
docker tag myapp:latest myapp:prod
docker tag myapp:latest myapp:staging

# Git 提交标签
docker tag myapp:latest myapp:git-abc123
```

#### 镜像扫描

安全扫描是镜像管理的重要环节：

```bash
# 使用 Docker Scan
docker scan myapp:latest

# 使用第三方工具
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy myapp:latest
```

### 实际应用示例

#### 完整的 Web 应用 Dockerfile

```dockerfile
# 使用官方 Node.js 运行时作为基础镜像
FROM node:14-alpine

# 设置应用目录
WORKDIR /usr/src/app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制应用源代码
COPY . .

# 暴露端口
EXPOSE 3000

# 创建非 root 用户
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# 更改文件所有权
USER nextjs

# 启动应用
CMD ["npm", "start"]
```

#### 构建和运行流程

```bash
# 构建镜像
docker build -t mywebapp:1.0 .

# 运行容器
docker run -d -p 3000:3000 --name webapp mywebapp:1.0

# 查看日志
docker logs webapp

# 进入容器
docker exec -it webapp sh
```

通过本节内容，我们深入探讨了 Docker 的核心概念：镜像、容器、仓库和 Dockerfile。理解这些概念及其相互关系是掌握 Docker 技术的基础，为后续章节的学习和实践应用奠定了坚实的基础。