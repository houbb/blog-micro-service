---
title: Dockerfile Syntax and Usage - Mastering the Art of Image Building
date: 2025-08-30
categories: [Write]
tags: [docker, dockerfile, syntax, build]
published: true
---

## Dockerfile 的基本语法与使用

### Dockerfile 概述

Dockerfile 是一个文本文件，包含了一系列指令，用于自动化构建 Docker 镜像。它是实现"基础设施即代码"的重要工具，通过 Dockerfile 可以确保镜像构建的一致性和可重复性。

#### Dockerfile 的基本结构

一个典型的 Dockerfile 包含以下部分：
1. **基础镜像**：使用 FROM 指令指定
2. **元数据**：使用 LABEL 指令添加
3. **环境配置**：设置工作目录、环境变量等
4. **依赖安装**：安装应用所需的依赖
5. **文件复制**：将应用代码复制到镜像中
6. **启动配置**：定义容器启动时的行为

### Dockerfile 指令详解

#### 基础指令

**FROM**
FROM 指令指定基础镜像，必须是 Dockerfile 中的第一个指令（ARG 指令除外）：

```dockerfile
# 指定具体版本
FROM ubuntu:20.04

# 使用最新版本（不推荐）
FROM node:latest

# 使用轻量级镜像
FROM alpine:latest

# 多平台支持
FROM --platform=linux/amd64 ubuntu:20.04
```

**LABEL**
LABEL 指令为镜像添加元数据，以键值对的形式：

```dockerfile
LABEL maintainer="user@example.com"
LABEL version="1.0"
LABEL description="This is a sample Docker image"
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.name="myapp"
LABEL org.label-schema.description="My application"
LABEL org.label-schema.vcs-url="https://github.com/user/myapp"
LABEL org.label-schema.vendor="My Company"
```

**EXPOSE**
EXPOSE 指令声明容器在运行时监听的端口，但不会实际发布端口：

```dockerfile
# 声明单个端口
EXPOSE 80

# 声明多个端口
EXPOSE 80 443

# 声明特定协议的端口
EXPOSE 80/tcp
EXPOSE 53/udp
```

#### 文件操作指令

**WORKDIR**
WORKDIR 指令设置工作目录，后续的 RUN、CMD、ENTRYPOINT、COPY、ADD 指令都会在这个目录下执行：

```dockerfile
# 设置工作目录
WORKDIR /app

# 可以使用相对路径
WORKDIR /app
WORKDIR subdirectory  # 实际路径为 /app/subdirectory

# 可以使用环境变量
ENV APP_HOME /app
WORKDIR $APP_HOME
```

**COPY**
COPY 指令从构建上下文目录中复制文件或目录到镜像中：

```dockerfile
# 复制单个文件
COPY package.json /app/

# 复制多个文件
COPY package.json README.md /app/

# 复制目录
COPY src/ /app/src/

# 复制所有文件
COPY . /app/

# 使用通配符
COPY *.js /app/src/

# 复制到相对路径（基于 WORKDIR）
WORKDIR /app
COPY package.json .  # 复制到 /app/package.json
```

**ADD**
ADD 指令与 COPY 类似，但具有额外功能：

```dockerfile
# 基本用法（与 COPY 相同）
ADD package.json /app/

# 自动解压本地 tar 文件
ADD file.tar.gz /app/

# 从远程 URL 下载文件
ADD http://example.com/file.txt /app/

# 注意：ADD 的这些额外功能使其更复杂，通常推荐使用 COPY
```

**.dockerignore 文件**
.dockerignore 文件用于指定构建镜像时需要忽略的文件和目录：

```dockerignore
# 忽略 node_modules 目录
node_modules

# 忽略所有 .log 文件
*.log

# 忽略 .git 目录
.git

# 忽略测试文件
test/
*.test.js

# 忽略环境配置文件
.env
config/local.*

# 例外规则
!important.log
```

#### 运行指令

**RUN**
RUN 指令在当前镜像的基础上执行命令并创建新的镜像层：

```dockerfile
# Shell 形式（默认使用 /bin/sh -c）
RUN apt-get update
RUN apt-get install -y nginx

# Exec 形式（推荐）
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "nginx"]

# 合并多个命令（推荐）
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 使用反斜杠换行
RUN echo "Hello World" && \
    echo "This is a long command" && \
    echo "That spans multiple lines"
```

**CMD**
CMD 指令为容器提供默认的执行命令：

```dockerfile
# Exec 形式（推荐）
CMD ["nginx", "-g", "daemon off;"]

# Shell 形式
CMD nginx -g "daemon off;"

# 作为 ENTRYPOINT 的参数
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]

# 设置执行参数
CMD ["--help"]
```

**ENTRYPOINT**
ENTRYPOINT 指令配置容器启动时执行的命令：

```dockerfile
# Exec 形式（推荐）
ENTRYPOINT ["nginx"]

# Shell 形式
ENTRYPOINT nginx

# 与 CMD 结合使用
ENTRYPOINT ["node"]
CMD ["app.js"]

# 可以在运行时覆盖（仅限 shell 形式）
docker run myapp echo "Hello World"
```

#### 环境配置指令

**ENV**
ENV 指令设置环境变量，可以在后续指令中使用：

```dockerfile
# 设置单个环境变量
ENV NODE_ENV=production

# 设置多个环境变量
ENV NODE_ENV=production \
    APP_PORT=3000 \
    DATABASE_URL=postgresql://localhost:5432/myapp

# 在后续指令中使用
ENV APP_HOME=/app
WORKDIR $APP_HOME
```

**ARG**
ARG 指令定义构建时变量，只在构建过程中有效：

```dockerfile
# 定义构建参数
ARG NODE_VERSION=14
FROM node:${NODE_VERSION}

# 定义多个参数
ARG NODE_VERSION=14
ARG ALPINE_VERSION=3.12

# 在运行时传递参数
# docker build --build-arg NODE_VERSION=16 -t myapp .

# 设置默认值和作用域
FROM node:14 AS base
ARG NODE_ENV=development
ENV NODE_ENV=$NODE_ENV

FROM base AS development
# NODE_ENV 在这里可用

FROM base AS production
# NODE_ENV 在这里也可用
```

**VOLUME**
VOLUME 指令创建具有指定名称的挂载点：

```dockerfile
# 创建匿名卷
VOLUME /data

# 创建多个卷
VOLUME ["/var/log", "/data"]

# 注意：VOLUME 指令不能指定主机路径
```

**USER**
USER 指令设置运行镜像时的用户名或 UID：

```dockerfile
# 使用用户名
USER nginx

# 使用 UID
USER 1000

# 使用 UID 和 GID
USER 1000:1000

# 创建并切换用户
RUN groupadd -r mygroup && useradd -r -g mygroup myuser
USER myuser
```

**ONBUILD**
ONBUILD 指令添加触发器指令，当镜像被用作基础镜像时执行：

```dockerfile
# 添加 ONBUILD 触发器
ONBUILD COPY . /app/src
ONBUILD RUN /usr/local/bin/python-build --dir /app/src

# 当其他 Dockerfile 使用这个镜像作为基础镜像时，
# ONBUILD 指令会自动执行
```

### Dockerfile 最佳实践

#### 指令顺序优化

将变化频率较低的指令放在前面，充分利用缓存：

```dockerfile
# 优化前
COPY . /app/
RUN npm install

# 优化后
COPY package*.json /app/
RUN npm install
COPY . /app/
```

#### 减少层数

合并相关的指令以减少镜像层数：

```dockerfile
# 优化前
RUN apt-get update
RUN apt-get install -y nginx
RUN apt-get clean

# 优化后
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean
```

#### 使用多阶段构建

使用多阶段构建减小最终镜像大小：

```dockerfile
# 构建阶段
FROM node:14 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM node:14-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./
RUN npm ci --only=production
CMD ["node", "dist/index.js"]
```

#### 安全性考虑

```dockerfile
# 使用最小基础镜像
FROM alpine:latest

# 以非 root 用户运行
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup
USER appuser

# 避免安装不必要的包
# 只安装运行应用必需的依赖
```

### Dockerfile 调试技巧

#### 构建过程调试

```bash
# 显示详细构建过程
docker build -t myapp --progress=plain .

# 不使用缓存构建
docker build -t myapp --no-cache .

# 指定目标阶段构建
docker build -t myapp --target builder .
```

#### 中间层检查

```bash
# 查看构建历史
docker history myapp

# 运行中间层进行调试
docker run -it <中间层ID> sh
```

### 实际应用示例

#### 完整的 Web 应用 Dockerfile

```dockerfile
# 使用官方 Node.js Alpine 镜像
FROM node:14-alpine AS base

# 设置标签
LABEL maintainer="user@example.com"
LABEL version="1.0.0"

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装生产依赖
RUN npm ci --only=production && \
    npm cache clean --force

# 构建阶段
FROM base AS builder
# 安装构建依赖
RUN apk add --no-cache python3 make g++

# 安装所有依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM base AS production

# 从构建阶段复制构建产物
COPY --from=builder /app/dist ./dist

# 创建非 root 用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 -G nodejs

# 更改文件所有权
RUN chown -R nextjs:nodejs /app
USER nextjs

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# 启动命令
CMD ["node", "dist/index.js"]
```

通过本节内容，您已经掌握了 Dockerfile 的基本语法和使用技巧。理解这些指令的作用和最佳实践将帮助您编写更高效、更安全的 Dockerfile。