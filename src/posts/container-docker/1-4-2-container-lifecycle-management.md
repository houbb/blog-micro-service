---
title: Container Lifecycle Management - Start, Stop, Restart and More
date: 2025-08-30
categories: [Docker]
tags: [container-docker]
published: true
---

## 容器的生命周期（启动、停止、重启）

### 容器状态概述

Docker 容器具有明确的生命周期，可以处于多种状态。理解这些状态及其转换对于有效管理容器至关重要。

#### 容器状态

容器可以处于以下状态：
1. **Created**：容器已创建但未启动
2. **Running**：容器正在运行
3. **Paused**：容器已暂停
4. **Restarting**：容器正在重启
5. **Removing**：容器正在被删除
6. **Exited**：容器已停止
7. **Dead**：容器处于死状态

可以通过以下命令查看容器状态：
```bash
docker ps -a
```

### 容器启动管理

#### 创建容器

使用 `docker create` 命令可以创建容器但不启动它：

```bash
# 创建容器但不启动
docker create --name my-nginx nginx

# 查看创建的容器（状态为 Created）
docker ps -a
```

#### 启动容器

使用 `docker start` 命令启动已创建或已停止的容器：

```bash
# 启动单个容器
docker start my-nginx

# 启动多个容器
docker start container1 container2 container3

# 附加到容器（连接到容器的 STDIN/STDOUT/STDERR）
docker start -a my-nginx
```

#### 直接运行容器

使用 `docker run` 命令可以一步完成创建和启动容器：

```bash
# 运行前台容器
docker run nginx

# 运行后台容器
docker run -d nginx

# 运行并命名容器
docker run -d --name web nginx
```

### 容器停止管理

#### 优雅停止容器

使用 `docker stop` 命令可以优雅地停止容器：

```bash
# 停止单个容器
docker stop my-nginx

# 停止多个容器
docker stop container1 container2

# 指定超时时间（默认 10 秒）
docker stop --time=30 my-nginx
```

`docker stop` 命令的工作原理：
1. 首先向容器内的主进程发送 SIGTERM 信号
2. 等待指定的超时时间（默认 10 秒）
3. 如果容器仍未停止，则发送 SIGKILL 信号强制停止

#### 强制停止容器

使用 `docker kill` 命令可以立即强制停止容器：

```bash
# 强制停止容器
docker kill my-nginx

# 发送特定信号
docker kill --signal=SIGINT my-nginx
```

### 容器重启管理

#### 重启容器

使用 `docker restart` 命令可以重启正在运行或已停止的容器：

```bash
# 重启容器
docker restart my-nginx

# 指定超时时间
docker restart --time=5 my-nginx
```

重启过程相当于先执行 `docker stop` 再执行 `docker start`。

#### 自动重启策略

Docker 提供了多种重启策略来自动重启容器：

```bash
# 总是重启
docker run -d --restart=always nginx

# 失败时重启
docker run -d --restart=on-failure nginx

# 失败时重启，最多重启 3 次
docker run -d --restart=on-failure:3 nginx

# 除非手动停止，否则重启
docker run -d --restart=unless-stopped nginx
```

### 容器暂停与恢复

#### 暂停容器

使用 `docker pause` 命令可以暂停容器内的所有进程：

```bash
# 暂停容器
docker pause my-nginx

# 暂停多个容器
docker pause container1 container2
```

暂停操作会冻结容器内的所有进程，但不会停止容器本身。

#### 恢复容器

使用 `docker unpause` 命令可以恢复已暂停的容器：

```bash
# 恢复容器
docker unpause my-nginx

# 恢复多个容器
docker unpause container1 container2
```

### 容器删除管理

#### 删除已停止的容器

使用 `docker rm` 命令可以删除已停止的容器：

```bash
# 删除单个容器
docker rm my-nginx

# 删除多个容器
docker rm container1 container2 container3

# 删除所有已停止的容器
docker container prune
```

#### 强制删除运行中的容器

```bash
# 强制删除运行中的容器
docker rm -f my-nginx

# 强制删除所有容器（谨慎使用）
docker rm -f $(docker ps -aq)
```

### 容器状态监控

#### 查看容器状态

```bash
# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 格式化输出
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

#### 查看容器详细信息

```bash
# 查看容器详细信息
docker inspect my-nginx

# 查看特定字段
docker inspect --format='{{.State.Status}}' my-nginx
docker inspect --format='{{.State.Running}}' my-nginx
```

#### 查看容器日志

```bash
# 查看容器日志
docker logs my-nginx

# 实时查看日志
docker logs -f my-nginx

# 查看最近的日志
docker logs --tail 100 my-nginx

# 查看指定时间段的日志
docker logs --since="2025-01-01" --until="2025-01-02" my-nginx
```

#### 查看容器资源使用情况

```bash
# 查看容器资源使用情况
docker stats my-nginx

# 查看所有容器的资源使用情况
docker stats

# 格式化输出
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### 容器生命周期自动化

#### 使用脚本管理容器

可以编写脚本来自动化容器的生命周期管理：

```bash
#!/bin/bash
# container-manager.sh

CONTAINER_NAME="my-app"

# 启动容器
start_container() {
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo "Container $CONTAINER_NAME is already running"
    else
        echo "Starting container $CONTAINER_NAME"
        docker start $CONTAINER_NAME
    fi
}

# 停止容器
stop_container() {
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo "Stopping container $CONTAINER_NAME"
        docker stop $CONTAINER_NAME
    else
        echo "Container $CONTAINER_NAME is not running"
    fi
}

# 重启容器
restart_container() {
    echo "Restarting container $CONTAINER_NAME"
    docker restart $CONTAINER_NAME
}

# 删除容器
remove_container() {
    if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
        echo "Removing container $CONTAINER_NAME"
        docker rm -f $CONTAINER_NAME
    else
        echo "Container $CONTAINER_NAME does not exist"
    fi
}

# 根据参数执行相应操作
case "$1" in
    start)
        start_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    remove)
        remove_container
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|remove}"
        exit 1
        ;;
esac
```

#### 使用 Docker Compose 管理多容器应用

对于多容器应用，可以使用 Docker Compose 来管理整个应用的生命周期：

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    image: nginx
    ports:
      - "80:80"
    restart: always
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
    restart: always
```

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose stop

# 重启所有服务
docker-compose restart

# 删除所有服务
docker-compose down
```

### 容器生命周期最佳实践

#### 合理设置重启策略

```bash
# 对于 Web 服务，使用 always 策略
docker run -d --restart=always nginx

# 对于批处理任务，使用 on-failure 策略
docker run -d --restart=on-failure:3 my-batch-job

# 对于开发环境，可以不设置重启策略
docker run -d nginx
```

#### 优雅关闭应用程序

在容器内运行的应用程序应该正确处理终止信号：

```dockerfile
# Dockerfile 示例
FROM node:14
COPY . /app
WORKDIR /app
CMD ["node", "app.js"]
```

```javascript
// app.js
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
  });
});
```

#### 定期清理停止的容器

```bash
# 定期清理停止的容器
docker container prune -f

# 清理所有未使用的资源
docker system prune -a -f
```

### 故障排除

#### 容器无法启动

```bash
# 查看容器日志
docker logs container-name

# 查看容器详细信息
docker inspect container-name

# 尝试交互式启动
docker run -it image-name bash
```

#### 容器频繁重启

```bash
# 检查重启策略
docker inspect --format='{{.HostConfig.RestartPolicy}}' container-name

# 查看容器日志
docker logs --tail 50 container-name

# 检查健康检查
docker inspect --format='{{.State.Health}}' container-name
```

通过本节内容，您已经深入了解了 Docker 容器的完整生命周期管理，包括容器的启动、停止、重启、暂停、恢复和删除等操作。掌握这些知识将帮助您更好地管理和维护 Docker 容器。