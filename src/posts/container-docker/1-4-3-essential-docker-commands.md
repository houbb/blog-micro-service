---
title: Essential Docker Commands - docker run, docker ps, docker stop and More
date: 2025-08-30
categories: [Docker]
tags: [docker, commands, run, ps, stop]
published: true
---

## 常用的 Docker 命令（`docker run`, `docker ps`, `docker stop`）

### Docker 命令概述

Docker 提供了丰富的命令行工具来管理容器、镜像、网络和卷等资源。掌握常用的 Docker 命令是有效使用 Docker 的基础。本节将详细介绍最常用的几个命令及其使用方法。

### docker run 命令详解

`docker run` 是 Docker 中最重要的命令之一，用于创建并运行容器。

#### 基本语法

```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

#### 常用选项

**容器命名和后台运行：**
```bash
# 为容器指定名称
docker run --name my-container nginx

# 后台运行容器
docker run -d nginx

# 前台运行容器
docker run -it ubuntu bash
```

**端口映射：**
```bash
# 映射单个端口
docker run -p 8080:80 nginx

# 映射多个端口
docker run -p 8080:80 -p 8443:443 nginx

# 随机端口映射
docker run -P nginx

# 指定 IP 地址映射
docker run -p 127.0.0.1:8080:80 nginx
```

**环境变量：**
```bash
# 设置环境变量
docker run -e NODE_ENV=production node

# 从文件读取环境变量
docker run --env-file ./env.list node
```

**数据卷挂载：**
```bash
# 绑定挂载
docker run -v /host/path:/container/path nginx

# 命名卷挂载
docker run -v my-volume:/container/path nginx

# 只读挂载
docker run -v /host/path:/container/path:ro nginx
```

**资源限制：**
```bash
# 限制内存
docker run -m 512m nginx

# 限制 CPU
docker run --cpus="1.5" nginx

# 限制 CPU 核心
docker run --cpuset-cpus="0-2" nginx
```

**网络配置：**
```bash
# 使用自定义网络
docker run --network my-network nginx

# 使用主机网络
docker run --network host nginx

# 设置容器主机名
docker run --hostname my-host nginx
```

**重启策略：**
```bash
# 总是重启
docker run --restart=always nginx

# 失败时重启
docker run --restart=on-failure nginx
```

#### 实际应用示例

```bash
# 运行 MySQL 数据库
docker run -d \
  --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=my-secret-pw \
  -e MYSQL_DATABASE=myapp \
  -p 3306:3306 \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0

# 运行 Node.js 应用
docker run -d \
  --name my-app \
  -p 3000:3000 \
  -e NODE_ENV=production \
  -v /app/data:/app/data \
  --link mysql-db:database \
  my-node-app:latest
```

### docker ps 命令详解

`docker ps` 命令用于列出容器，是查看容器状态的重要工具。

#### 基本用法

```bash
# 查看正在运行的容器
docker ps

# 查看所有容器（包括已停止的）
docker ps -a

# 只显示容器 ID
docker ps -q

# 显示最近创建的容器
docker ps -l
```

#### 格式化输出

```bash
# 自定义输出格式
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# 只显示特定字段
docker ps --format "{{.Names}}: {{.Status}}"

# 使用模板文件
docker ps --format "table {{.Names}}\t{{.RunningFor}}\t{{.Status}}"
```

#### 过滤选项

```bash
# 按名称过滤
docker ps -f name=my-container

# 按状态过滤
docker ps -f status=running
docker ps -f status=exited

# 按镜像过滤
docker ps -f ancestor=nginx

# 按标签过滤
docker ps -f label=env=production
```

#### 显示详细信息

```bash
# 显示容器大小
docker ps -s

# 显示完整信息
docker ps --no-trunc
```

### docker stop 命令详解

`docker stop` 命令用于优雅地停止运行中的容器。

#### 基本用法

```bash
# 停止单个容器
docker stop my-container

# 停止多个容器
docker stop container1 container2 container3

# 指定超时时间（默认 10 秒）
docker stop --time=30 my-container
```

#### 工作原理

`docker stop` 命令的工作流程：
1. 向容器内的主进程发送 SIGTERM 信号
2. 等待指定的超时时间
3. 如果容器仍未停止，则发送 SIGKILL 信号强制停止

#### 批量操作

```bash
# 停止所有运行中的容器
docker stop $(docker ps -q)

# 停止特定镜像的容器
docker stop $(docker ps -q --filter ancestor=nginx)
```

### 其他重要命令

#### docker start 命令

用于启动已创建或已停止的容器：

```bash
# 启动容器
docker start my-container

# 附加到容器
docker start -a my-container

# 启动并连接到容器
docker start -i my-container
```

#### docker restart 命令

用于重启容器：

```bash
# 重启容器
docker restart my-container

# 指定超时时间
docker restart --time=5 my-container
```

#### docker kill 命令

用于强制停止容器：

```bash
# 强制停止容器
docker kill my-container

# 发送特定信号
docker kill --signal=SIGINT my-container
```

#### docker rm 命令

用于删除容器：

```bash
# 删除已停止的容器
docker rm my-container

# 强制删除运行中的容器
docker rm -f my-container

# 删除多个容器
docker rm container1 container2

# 删除所有已停止的容器
docker container prune
```

#### docker logs 命令

用于查看容器日志：

```bash
# 查看容器日志
docker logs my-container

# 实时查看日志
docker logs -f my-container

# 查看最近的日志
docker logs --tail 100 my-container

# 查看指定时间段的日志
docker logs --since="2025-01-01" my-container
```

#### docker exec 命令

用于在运行中的容器内执行命令：

```bash
# 进入容器终端
docker exec -it my-container bash

# 在容器中执行命令
docker exec my-container ls /app

# 以特定用户执行命令
docker exec -u root my-container whoami
```

#### docker inspect 命令

用于查看容器详细信息：

```bash
# 查看容器详细信息
docker inspect my-container

# 查看特定字段
docker inspect --format='{{.State.Status}}' my-container

# 查看网络信息
docker inspect --format='{{.NetworkSettings.IPAddress}}' my-container
```

### 命令组合使用示例

#### 容器管理脚本

```bash
# 创建并运行容器
docker run -d --name web -p 80:80 nginx

# 查看容器状态
docker ps -f name=web

# 查看容器日志
docker logs web

# 停止容器
docker stop web

# 删除容器
docker rm web
```

#### 批量操作

```bash
# 停止所有容器
docker stop $(docker ps -q)

# 删除所有已停止的容器
docker rm $(docker ps -aq -f status=exited)

# 查看所有容器的资源使用情况
docker stats $(docker ps -q)
```

#### 故障排除

```bash
# 查看容器日志
docker logs --tail 50 --follow container-name

# 进入容器调试
docker exec -it container-name bash

# 查看容器详细信息
docker inspect container-name
```

### 命令别名和快捷方式

为了提高效率，可以设置命令别名：

```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
alias dps='docker ps'
alias dpa='docker ps -a'
alias di='docker images'
alias drm='docker rm'
alias drmi='docker rmi'
alias dexec='docker exec -it'
alias dlog='docker logs -f'
```

### 最佳实践

#### 命令使用建议

1. **使用具体标签**：避免使用 latest 标签，使用具体版本号
2. **命名容器**：为容器指定有意义的名称
3. **合理设置资源限制**：防止容器消耗过多系统资源
4. **使用数据卷**：实现数据持久化

#### 安全建议

1. **最小权限原则**：不要以 root 用户运行容器
2. **定期清理**：清理不需要的容器和镜像
3. **监控日志**：定期检查容器日志
4. **更新镜像**：保持镜像更新以修复安全漏洞

通过本节内容，您已经掌握了 Docker 最常用的命令及其使用方法。这些命令是日常使用 Docker 的基础，熟练掌握它们将大大提高您使用 Docker 的效率。