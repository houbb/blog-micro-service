---
title: Appendix B - Docker Common Issues and Troubleshooting Guide
date: 2025-08-31
categories: [Write]
tags: [docker, troubleshooting, issues, debug]
published: true
---

## 附录B：Docker 常见问题与故障排查

### 启动和安装问题

#### Docker 无法启动

```bash
# 检查 Docker 服务状态
systemctl status docker  # Linux
brew services list | grep docker  # macOS

# 查看 Docker 服务日志
journalctl -u docker.service  # Linux
tail -f /var/log/docker.log   # 查看Docker日志文件

# 重启 Docker 服务
sudo systemctl restart docker  # Linux
brew services restart docker   # macOS

# Windows 上重启 Docker Desktop 服务
# 通过任务管理器或服务管理器重启 Docker Desktop 服务
```

常见启动问题及解决方案：

1. **权限问题**：
   ```bash
   # 将用户添加到 docker 组
   sudo usermod -aG docker $USER
   # 重新登录或执行
   newgrp docker
   ```

2. **端口冲突**：
   ```bash
   # 检查占用端口的进程
   sudo lsof -i :2375
   sudo lsof -i :2376
   # 杀死占用端口的进程
   sudo kill -9 <PID>
   ```

3. **存储空间不足**：
   ```bash
   # 检查磁盘空间
   df -h
   # 清理未使用的 Docker 数据
   docker system prune -a
   ```

#### 镜像拉取失败

```bash
# 检查网络连接
ping registry-1.docker.io

# 配置镜像加速器（中国用户）
# 在 /etc/docker/daemon.json 中添加：
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}

# 重启 Docker 服务使配置生效
sudo systemctl restart docker
```

### 容器运行问题

#### 容器启动后立即退出

```bash
# 查看容器退出原因
docker logs container_name

# 以交互模式运行容器进行调试
docker run -it ubuntu:latest /bin/bash

# 检查容器的启动命令
docker inspect container_name | grep Cmd
```

常见原因及解决方案：

1. **主进程退出**：
   ```dockerfile
   # 错误示例：容器会立即退出
   FROM ubuntu:latest
   RUN echo "Hello World"
   
   # 正确示例：保持容器运行
   FROM ubuntu:latest
   CMD ["tail", "-f", "/dev/null"]
   ```

2. **应用程序错误**：
   ```bash
   # 检查应用程序日志
   docker logs container_name
   
   # 进入容器调试
   docker exec -it container_name /bin/bash
   ```

#### 端口无法访问

```bash
# 检查端口映射是否正确
docker port container_name

# 检查容器是否在运行
docker ps

# 检查宿主机防火墙设置
sudo ufw status  # Ubuntu
sudo firewall-cmd --list-all  # CentOS

# 检查容器内服务是否正常监听端口
docker exec container_name netstat -tlnp
```

#### 容器间网络通信问题

```bash
# 检查容器网络配置
docker network ls
docker network inspect network_name

# 测试容器间连通性
docker exec container1 ping container2

# 使用自定义网络确保容器间通信
docker network create mynetwork
docker run -d --name web --network mynetwork nginx
docker run -d --name db --network mynetwork postgres
```

### 存储和卷问题

#### 数据卷挂载失败

```bash
# 检查挂载点权限
ls -la /host/path

# 确保挂载点存在
mkdir -p /host/path

# 检查 SELinux 设置（CentOS/RHEL）
ls -Z /host/path
# 临时禁用 SELinux
sudo setenforce 0
```

#### 容器数据丢失

```bash
# 使用命名卷持久化数据
docker volume create mydata
docker run -v mydata:/app/data ubuntu

# 备份卷数据
docker run --rm -v mydata:/data -v /backup:/backup ubuntu tar czf /backup/data.tar.gz -C /data .

# 恢复卷数据
docker run --rm -v mydata:/data -v /backup:/backup ubuntu tar xzf /backup/data.tar.gz -C /data
```

### 镜像构建问题

#### 构建过程失败

```bash
# 查看详细的构建日志
docker build --no-cache -t myapp .

# 分步构建调试
docker build --target build-stage -t myapp:build .

# 检查构建上下文大小
du -sh .

# 使用 .dockerignore 排除不必要的文件
echo "node_modules" > .dockerignore
echo "*.log" >> .dockerignore
```

#### 镜像过大问题

```dockerfile
# 使用多阶段构建减小镜像大小
# 构建阶段
FROM golang:1.19 AS builder
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

```bash
# 使用 dive 工具分析镜像层
dive myapp:latest

# 清理构建缓存
docker builder prune
```

### 性能问题

#### 容器运行缓慢

```bash
# 监控容器资源使用情况
docker stats container_name

# 限制容器资源使用
docker run -m 512m --cpus="1.0" nginx

# 检查宿主机资源使用情况
htop
iostat -x 1
```

#### Docker Desktop 占用资源过高

```bash
# 调整 Docker Desktop 资源限制
# 在 Docker Desktop 设置中调整 CPU 和内存限制

# 清理未使用的数据
docker system prune -a

# 重启 Docker Desktop
# 通过系统托盘重启 Docker Desktop
```

### 安全问题

#### 容器安全漏洞

```bash
# 扫描镜像安全漏洞
trivy image nginx:latest

# 运行安全扫描
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest nginx:latest

# 使用非 root 用户运行容器
docker run --user 1000:1000 ubuntu id
```

#### 权限提升风险

```dockerfile
# 避免以 root 用户运行容器
FROM ubuntu:latest
RUN useradd -m appuser
USER appuser
WORKDIR /app
COPY . .
CMD ["./app"]
```

```bash
# 限制容器能力
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx
```

### 网络问题

#### DNS 解析失败

```bash
# 检查容器 DNS 配置
docker exec container_name cat /etc/resolv.conf

# 自定义 DNS 服务器
docker run --dns 8.8.8.8 nginx

# 使用自定义网络
docker network create --driver bridge \
  --subnet=172.20.0.0/16 \
  --ip-range=172.20.240.0/20 \
  mynetwork
```

#### 网络连接超时

```bash
# 检查网络驱动
docker network ls

# 重启 Docker 网络
docker network prune

# 检查 iptables 规则
sudo iptables -L

# 重启网络服务
sudo systemctl restart docker
```

### 日志和监控问题

#### 日志文件过大

```bash
# 配置日志轮转
docker run --log-driver json-file --log-opt max-size=10m --log-opt max-file=3 nginx

# 在 docker-compose.yml 中配置
services:
  app:
    image: nginx
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### 日志收集困难

```bash
# 使用 ELK 栈收集日志
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" elasticsearch:7.10.1

docker run -d --name kibana --link elasticsearch -p 5601:5601 \
  kibana:7.10.1

# 使用 Fluentd 收集 Docker 日志
docker run -d --name fluentd \
  -p 24224:24224 \
  -v /var/lib/docker/containers:/var/lib/docker/containers \
  fluentd:latest
```

### Docker Compose 问题

#### 服务依赖问题

```yaml
# 正确配置服务依赖
version: "3.8"
services:
  web:
    image: nginx
    depends_on:
      - db
      - redis
    # 等待数据库就绪的健康检查
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: example
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

#### 环境变量问题

```bash
# 创建 .env 文件
echo "DATABASE_URL=postgresql://user:pass@localhost/db" > .env

# 在 docker-compose.yml 中使用
services:
  app:
    image: myapp
    env_file:
      - .env
    environment:
      - DEBUG=1
```

### 调试技巧和工具

#### 使用调试容器

```bash
# 运行调试容器
docker run -it --rm ubuntu:latest /bin/bash

# 进入运行中的容器调试
docker exec -it container_name /bin/bash

# 使用专用调试镜像
docker run -it --rm nicolaka/netshoot
```

#### 监控和诊断工具

```bash
# 使用 ctop 监控容器
docker run --rm -ti \
  --name=ctop \
  -v /var/run/docker.sock:/var/run/docker.sock \
  quay.io/vektorlab/ctop:latest

# 使用 docker stats 监控
docker stats

# 使用 sysdig 进行系统级监控
docker run -it --rm \
  --privileged \
  -v /var/run/docker.sock:/host/var/run/docker.sock \
  -v /dev:/host/dev \
  -v /proc:/host/proc:ro \
  -v /boot:/host/boot:ro \
  -v /lib/modules:/host/lib/modules:ro \
  -v /usr:/host/usr:ro \
  --net=host \
  sysdig/sysdig
```

通过本附录的内容，您可以快速识别和解决 Docker 使用过程中遇到的常见问题，提高故障排查效率。