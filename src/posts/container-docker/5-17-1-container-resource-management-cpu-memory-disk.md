---
title: Container Resource Management - Mastering CPU, Memory, and Disk Optimization
date: 2025-08-31
categories: [Write]
tags: [docker, resources, cpu, memory, disk, optimization]
published: true
---

## 容器资源管理（CPU、内存、磁盘）

### 资源管理的重要性

在容器化环境中，合理的资源管理是确保应用性能和系统稳定性的关键。通过精确控制容器的 CPU、内存和磁盘资源使用，可以避免资源争用、提高系统效率并降低运营成本。

#### 资源管理挑战

1. **资源争用**：
   - 多个容器竞争同一资源
   - 资源分配不均导致性能问题

2. **资源浪费**：
   - 过度分配资源
   - 资源利用率低

3. **性能瓶颈**：
   - 资源限制导致应用性能下降
   - 缺乏监控导致问题难以发现

### CPU 资源管理

#### CPU 限制和预留

```bash
# 设置 CPU 限制
docker run -d \
  --name myapp \
  --cpus="1.5" \
  myapp:latest

# 设置 CPU 预留
docker run -d \
  --name myapp \
  --cpu-shares=512 \
  myapp:latest

# 设置 CPU 集
docker run -d \
  --name myapp \
  --cpuset-cpus="0-1" \
  myapp:latest

# 设置 CPU 配额
docker run -d \
  --name myapp \
  --cpu-period=100000 \
  --cpu-quota=50000 \
  myapp:latest
```

#### CPU 性能监控

```bash
# 实时监控容器 CPU 使用
docker stats myapp

# 查看详细 CPU 信息
docker exec myapp top -b -n 1 | head -20

# 使用 ctop 工具
# 安装 ctop
sudo wget https://github.com/bcicen/ctop/releases/download/v0.7.7/ctop-0.7.7-linux-amd64 -O /usr/local/bin/ctop
sudo chmod +x /usr/local/bin/ctop
ctop
```

#### CPU 优化策略

```dockerfile
# 优化 CPU 使用的 Dockerfile
FROM node:14-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# 复制应用代码
COPY . .

# 设置多进程应用的进程数
ENV UV_THREADPOOL_SIZE=4

EXPOSE 3000

# 使用生产模式启动
CMD ["node", "--max-old-space-size=1024", "server.js"]
```

```yaml
# docker-compose.cpu-optimized.yml
version: '3.8'

services:
  app:
    image: myapp:latest
    deploy:
      resources:
        limits:
          cpus: '1.0'
        reservations:
          cpus: '0.5'
    environment:
      - NODE_ENV=production
      - UV_THREADPOOL_SIZE=4
```

### 内存资源管理

#### 内存限制和预留

```bash
# 设置内存限制
docker run -d \
  --name myapp \
  --memory="512m" \
  myapp:latest

# 设置内存和交换区内存限制
docker run -d \
  --name myapp \
  --memory="512m" \
  --memory-swap="1g" \
  myapp:latest

# 设置内存预留
docker run -d \
  --name myapp \
  --memory-reservation="256m" \
  myapp:latest

# 设置内存软限制
docker run -d \
  --name myapp \
  --memory="512m" \
  --memory-reservation="256m" \
  myapp:latest
```

#### 内存性能监控

```bash
# 监控内存使用
docker stats myapp

# 查看容器内存详细信息
docker exec myapp cat /proc/meminfo

# 使用系统工具监控
docker exec myapp free -m

# 监控内存使用趋势
watch -n 5 'docker stats --no-stream myapp'
```

#### 内存优化策略

```dockerfile
# 内存优化的 Dockerfile
FROM node:14-alpine

WORKDIR /app
COPY package*.json ./

# 只安装生产依赖
RUN npm ci --only=production

COPY . .

# 设置 Node.js 内存限制
ENV NODE_OPTIONS="--max-old-space-size=512"

# 使用轻量级基础镜像
EXPOSE 3000

# 启用垃圾回收日志（调试时使用）
# ENV NODE_OPTIONS="--max-old-space-size=512 --trace_gc"

CMD ["node", "server.js"]
```

```bash
# 运行时内存优化
docker run -d \
  --name myapp \
  --memory="512m" \
  --memory-swap="1g" \
  --oom-kill-disable=false \
  -e NODE_OPTIONS="--max-old-space-size=384" \
  myapp:latest
```

### 磁盘资源管理

#### 磁盘空间限制

```bash
# 设置容器根文件系统大小限制
docker run -d \
  --name myapp \
  --storage-opt size=10G \
  myapp:latest

# 使用卷管理持久化数据
docker run -d \
  --name myapp \
  -v myapp-data:/app/data \
  myapp:latest

# 限制临时文件系统大小
docker run -d \
  --name myapp \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  myapp:latest
```

#### 磁盘 I/O 限制

```bash
# 限制磁盘 I/O 速度
docker run -d \
  --name myapp \
  --device-read-bps /dev/sda:1mb \
  --device-write-bps /dev/sda:1mb \
  myapp:latest

# 限制 I/O 操作次数
docker run -d \
  --name myapp \
  --device-read-iops /dev/sda:1000 \
  --device-write-iops /dev/sda:1000 \
  myapp:latest
```

#### 磁盘使用监控

```bash
# 查看容器磁盘使用情况
docker system df -v

# 查看特定容器的磁盘使用
docker ps -s

# 进入容器查看磁盘使用
docker exec myapp df -h

# 监控容器日志大小
docker inspect myapp | grep LogPath
ls -lh $(docker inspect myapp | grep LogPath | cut -d'"' -f4)
```

#### 磁盘优化策略

```dockerfile
# 磁盘优化的 Dockerfile
FROM node:14-alpine

# 清理构建缓存
RUN apk add --no-cache python3 make g++ && \
    # 安装依赖
    npm ci --only=production && \
    # 清理构建工具
    apk del python3 make g++ && \
    # 清理 npm 缓存
    npm cache clean --force

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

# 配置日志轮转
ENV LOG_LEVEL=info

EXPOSE 3000
CMD ["node", "server.js"]
```

```yaml
# docker-compose.disk-optimized.yml
version: '3.8'

services:
  app:
    image: myapp:latest
    volumes:
      # 使用命名卷管理数据
      - app-data:/app/data
      # 使用 tmpfs 临时存储
      - type: tmpfs
        target: /tmp
        tmpfs:
          size: 100M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

volumes:
  app-data:
```

### 资源管理最佳实践

#### 资源规划

```bash
# 分析应用资源需求
# 使用压力测试工具确定资源需求
docker run --rm -it \
  --name load-test \
  -v $PWD:/app \
  node:14-alpine \
  sh -c "cd /app && npm install autocannon && npx autocannon -c 100 -d 30 http://target:3000"

# 监控资源使用峰值
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
```

#### 动态资源调整

```bash
# 动态调整容器资源
docker update \
  --cpus="2.0" \
  --memory="1g" \
  myapp

# 批量更新多个容器
docker update \
  --cpus="1.5" \
  --memory="768m" \
  container1 container2 container3
```

#### 资源配额管理

```yaml
# Kubernetes 资源配额示例
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 1Gi
    limits.cpu: "2"
    limits.memory: 2Gi
    requests.storage: 10Gi
---
apiVersion: v1
kind: LimitRange
metadata:
  name: cpu-min-max-demo
spec:
  limits:
  - max:
      cpu: "800m"
    min:
      cpu: "100m"
    type: Container
```

#### 资源监控和告警

```bash
#!/bin/bash
# resource-monitor.sh

# 监控脚本示例
CONTAINERS=("web" "db" "cache")
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80

for container in "${CONTAINERS[@]}"; do
    # 获取 CPU 和内存使用率
    cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" $container | sed 's/%//')
    mem_usage=$(docker stats --no-stream --format "{{.MemPerc}}" $container | sed 's/%//')
    
    # 检查 CPU 使用率
    if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )); then
        echo "警告: 容器 $container CPU 使用率过高: ${cpu_usage}%"
        # 发送告警通知
    fi
    
    # 检查内存使用率
    if (( $(echo "$mem_usage > $MEMORY_THRESHOLD" | bc -l) )); then
        echo "警告: 容器 $container 内存使用率过高: ${mem_usage}%"
        # 发送告警通知
    fi
done
```

#### 资源优化检查清单

1. **CPU 优化**：
   - 设置合理的 CPU 限制和预留
   - 避免 CPU 密集型任务长时间占用
   - 使用多核处理提高并发性能

2. **内存优化**：
   - 设置内存限制防止 OOM
   - 优化应用内存使用
   - 定期监控内存泄漏

3. **磁盘优化**：
   - 使用日志轮转防止日志文件过大
   - 清理不必要的临时文件
   - 使用卷管理持久化数据

4. **网络优化**：
   - 优化网络配置减少延迟
   - 使用合适的网络驱动
   - 监控网络带宽使用

通过本节内容，我们深入了解了容器资源管理的各个方面，包括 CPU、内存和磁盘资源的限制、监控和优化策略。掌握这些技能将帮助您构建高效、稳定的容器化应用。