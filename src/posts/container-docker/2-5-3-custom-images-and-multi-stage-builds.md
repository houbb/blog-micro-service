---
title: Custom Images and Multi-Stage Builds - Advanced Image Creation Techniques
date: 2025-08-30
categories: [Docker]
tags: [docker, images, custom, multi-stage, build]
published: true
---

## 自定义镜像与多阶段构建

### 自定义镜像的重要性

自定义镜像是根据特定应用需求创建的 Docker 镜像，它包含了应用运行所需的所有依赖和配置。与直接使用官方镜像相比，自定义镜像具有以下优势：

1. **应用特定优化**：针对特定应用进行优化
2. **安全性增强**：只包含必需的组件，减少攻击面
3. **性能提升**：移除不必要的组件，减小镜像大小
4. **环境一致性**：确保开发、测试、生产环境的一致性

### 创建自定义镜像的步骤

#### 1. 分析应用需求

在创建自定义镜像之前，需要明确应用的需求：

- 运行时环境（Node.js、Python、Java等）
- 系统依赖（数据库客户端、工具等）
- 应用配置（环境变量、配置文件等）
- 安全要求（用户权限、网络策略等）

#### 2. 选择合适的基础镜像

选择基础镜像是创建自定义镜像的第一步：

```dockerfile
# 选择官方轻量级镜像
FROM node:14-alpine

# 或者选择特定版本的 Ubuntu
FROM ubuntu:20.04

# 或者从 scratch 开始构建最小镜像
FROM scratch
```

#### 3. 安装应用依赖

根据应用需求安装必要的依赖：

```dockerfile
# 对于 Node.js 应用
RUN npm install

# 对于 Python 应用
RUN pip install -r requirements.txt

# 对于 Java 应用
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get clean
```

#### 4. 配置应用环境

设置应用运行所需的环境：

```dockerfile
# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV NODE_ENV=production
ENV PORT=3000

# 复制配置文件
COPY config/ /app/config/
```

#### 5. 定义启动命令

指定容器启动时执行的命令：

```dockerfile
# 对于 Web 应用
CMD ["node", "server.js"]

# 对于后台服务
CMD ["python", "worker.py"]

# 使用 ENTRYPOINT 和 CMD 组合
ENTRYPOINT ["java"]
CMD ["-jar", "app.jar"]
```

### 多阶段构建详解

多阶段构建是 Docker 17.05 版本引入的功能，它允许在单个 Dockerfile 中使用多个 FROM 指令，每个 FROM 指令开始一个新的构建阶段。

#### 多阶段构建的优势

1. **减小镜像大小**：只将必要的文件复制到最终镜像
2. **提高安全性**：构建工具和依赖不会出现在最终镜像中
3. **简化维护**：所有构建逻辑都在一个 Dockerfile 中
4. **优化构建时间**：利用缓存机制提高构建效率

#### 多阶段构建的基本语法

```dockerfile
# 第一阶段：构建阶段
FROM node:14 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 第二阶段：运行阶段
FROM node:14-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./
RUN npm install --only=production
CMD ["node", "dist/index.js"]
```

#### 实际应用示例

##### Go 应用的多阶段构建

```dockerfile
# 构建阶段
FROM golang:1.16 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# 运行阶段
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
CMD ["./main"]
```

##### Java 应用的多阶段构建

```dockerfile
# 构建阶段
FROM maven:3.8.1-openjdk-11 AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package

# 运行阶段
FROM openjdk:11-jre-slim
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
CMD ["java", "-jar", "app.jar"]
```

##### Python 应用的多阶段构建

```dockerfile
# 构建阶段
FROM python:3.9 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 运行阶段
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

### 高级多阶段构建技巧

#### 命名阶段和选择性复制

```dockerfile
# 命名不同的构建阶段
FROM node:14 AS frontend-builder
WORKDIR /app
COPY frontend/ .
RUN npm install && npm run build

FROM node:14 AS backend-builder
WORKDIR /app
COPY backend/ .
RUN npm install && npm run build

# 最终阶段
FROM node:14-alpine
WORKDIR /app
# 从不同阶段复制文件
COPY --from=frontend-builder /app/dist ./public
COPY --from=backend-builder /app/dist ./server
CMD ["node", "server/index.js"]
```

#### 条件构建阶段

```dockerfile
# 根据构建参数选择不同的阶段
ARG BUILD_TYPE=production

FROM node:14 AS base
WORKDIR /app
COPY package*.json ./
RUN npm install

FROM base AS development
COPY . .
CMD ["npm", "run", "dev"]

FROM base AS production
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

#### 使用外部镜像作为构建阶段

```dockerfile
# 使用预构建的工具镜像
FROM node:14 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 使用最小的运行时镜像
FROM gcr.io/distroless/nodejs:14 AS runtime
WORKDIR /app
COPY --from=builder /app/dist ./dist
CMD ["dist/index.js"]
```

### 自定义镜像优化技巧

#### 减小镜像大小

1. **使用轻量级基础镜像**：
```dockerfile
# 使用 Alpine Linux
FROM node:14-alpine

# 或者使用 Distroless 镜像
FROM gcr.io/distroless/nodejs:14
```

2. **清理构建缓存**：
```dockerfile
RUN apt-get update && \
    apt-get install -y build-essential && \
    # 构建完成后清理
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

3. **合并层**：
```dockerfile
# 合并相关命令
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean
```

#### 提高构建效率

1. **优化指令顺序**：
```dockerfile
# 将变化较少的指令放在前面
COPY package*.json /app/
RUN npm install
COPY . /app/
```

2. **使用构建缓存**：
```dockerfile
# 利用 Docker 的层缓存机制
COPY package*.json /app/
RUN npm install  # 这一层会被缓存，除非 package.json 变化
```

#### 增强安全性

1. **以非 root 用户运行**：
```dockerfile
# 创建非 root 用户
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# 切换到非 root 用户
USER appuser
```

2. **最小化攻击面**：
```dockerfile
# 只安装必需的依赖
RUN apk add --no-cache nginx

# 移除不必要的工具
RUN apt-get remove --purge -y build-essential
```

### 自定义镜像的最佳实践

#### 镜像标签策略

```bash
# 使用语义化版本
docker build -t myapp:1.2.3 .

# 使用 Git 提交哈希
docker build -t myapp:git-$(git rev-parse --short HEAD) .

# 使用环境标签
docker build -t myapp:prod .
docker build -t myapp:staging .
```

#### 镜像扫描和验证

```bash
# 使用 Docker Scan 扫描漏洞
docker scan myapp:latest

# 使用第三方工具扫描
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy myapp:latest
```

#### 镜像文档化

```dockerfile
# 添加详细的标签信息
LABEL maintainer="team@example.com"
LABEL version="1.0.0"
LABEL description="My application description"
LABEL org.opencontainers.image.source="https://github.com/user/myapp"
LABEL org.opencontainers.image.licenses="MIT"
```

### 故障排除

#### 构建失败

```bash
# 查看详细构建日志
docker build --progress=plain .

# 不使用缓存重新构建
docker build --no-cache .

# 进入中间层调试
docker run -it <中间层ID> sh
```

#### 运行时问题

```bash
# 检查镜像内容
docker run -it myapp:latest sh

# 查看容器日志
docker logs container-name

# 进入运行中的容器
docker exec -it container-name sh
```

通过本节内容，您已经深入了解了自定义镜像的创建方法和多阶段构建技术。掌握这些高级技巧将帮助您创建更小、更安全、更高效的 Docker 镜像。