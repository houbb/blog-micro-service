---
title: Configuring Docker Environment and Common Commands - A Practical Guide
date: 2025-08-30
categories: [Docker]
tags: [container-docker]
published: true
---

## 配置 Docker 环境与常用命令

### Docker 环境配置

Docker 安装完成后，需要进行一些基本的环境配置以确保其正常运行并满足特定需求。正确的配置不仅能提高 Docker 的性能，还能增强安全性。

#### 配置文件位置

Docker 的主要配置文件位于以下位置：

- **Linux**: `/etc/docker/daemon.json`
- **Windows**: `C:\ProgramData\docker\config\daemon.json`
- **macOS**: 通过 Docker Desktop 的设置界面配置

#### 基本配置选项

##### 镜像仓库配置

为了提高镜像拉取速度，特别是对于国内用户，可以配置镜像加速器：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

##### 存储驱动配置

Docker 支持多种存储驱动，可以根据文件系统类型选择合适的驱动：

```json
{
  "storage-driver": "overlay2"
}
```

常见的存储驱动包括：
- **overlay2**：推荐用于 ext4 和 xfs 文件系统
- **aufs**：较老的驱动，性能一般
- **devicemapper**：适用于没有 overlay2 支持的系统
- **btrfs**：适用于 Btrfs 文件系统
- **zfs**：适用于 ZFS 文件系统

##### 日志配置

为了避免容器日志占用过多磁盘空间，可以配置日志轮转：

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

##### 网络配置

可以配置默认的网络设置：

```json
{
  "default-address-pools": [
    {
      "base": "172.17.0.0/16",
      "size": 24
    }
  ]
}
```

#### 高级配置选项

##### 资源限制

可以为 Docker 守护进程设置资源限制：

```json
{
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
```

##### 安全配置

增强 Docker 的安全性：

```json
{
  "userns-remap": "default",
  "live-restore": true,
  "userland-proxy": false
}
```

##### 实验性功能

启用实验性功能（谨慎使用）：

```json
{
  "experimental": true
}
```

#### 重启 Docker 服务

修改配置文件后，需要重启 Docker 服务使配置生效：

**Linux**:
```bash
sudo systemctl restart docker
```

**Windows/macOS**:
通过 Docker Desktop 重启 Docker

### 常用 Docker 命令详解

#### 镜像管理命令

##### docker pull

从镜像仓库拉取镜像：

```bash
# 拉取最新版本
docker pull nginx

# 拉取指定版本
docker pull nginx:1.21

# 拉取特定平台的镜像
docker pull --platform linux/arm64 nginx
```

##### docker push

将本地镜像推送到镜像仓库：

```bash
# 推送镜像到 Docker Hub
docker push username/my-app:latest

# 推送镜像到私有仓库
docker push registry.example.com/my-app:latest
```

##### docker images

查看本地镜像列表：

```bash
# 查看所有镜像
docker images

# 查看特定镜像
docker images nginx

# 以表格形式显示
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# 只显示悬空镜像（无标签的镜像）
docker images -f "dangling=true"
```

##### docker rmi

删除本地镜像：

```bash
# 删除指定镜像
docker rmi nginx:latest

# 强制删除镜像（即使有容器在使用）
docker rmi -f nginx:latest

# 删除所有未使用的镜像
docker image prune -a
```

##### docker build

从 Dockerfile 构建镜像：

```bash
# 从当前目录构建
docker build -t my-app .

# 指定 Dockerfile
docker build -f Dockerfile.prod -t my-app .

# 构建参数
docker build --build-arg NODE_ENV=production -t my-app .

# 不使用缓存构建
docker build --no-cache -t my-app .
```

#### 容器管理命令

##### docker run

创建并运行容器：

```bash
# 基本运行
docker run nginx

# 后台运行
docker run -d nginx

# 端口映射
docker run -d -p 8080:80 nginx

# 命名容器
docker run -d --name my-nginx nginx

# 环境变量
docker run -d -e NODE_ENV=production nginx

# 挂载卷
docker run -d -v /host/path:/container/path nginx

# 限制资源
docker run -d --memory=512m --cpus=0.5 nginx
```

##### docker ps

查看容器状态：

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 显示容器大小
docker ps -s

# 格式化输出
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

##### docker start/stop/restart

控制容器状态：

```bash
# 启动容器
docker start my-container

# 停止容器
docker stop my-container

# 重启容器
docker restart my-container

# 强制停止容器
docker kill my-container
```

##### docker rm

删除容器：

```bash
# 删除停止的容器
docker rm my-container

# 强制删除运行中的容器
docker rm -f my-container

# 删除所有停止的容器
docker container prune

# 删除所有容器（谨慎使用）
docker rm -f $(docker ps -aq)
```

##### docker exec

在运行的容器中执行命令：

```bash
# 进入容器终端
docker exec -it my-container bash

# 执行单个命令
docker exec my-container ls /app

# 以特定用户执行
docker exec -u root my-container whoami
```

#### 网络管理命令

##### docker network create

创建网络：

```bash
# 创建桥接网络
docker network create my-network

# 创建自定义子网
docker network create --subnet=172.20.0.0/16 my-network

# 创建覆盖网络（用于 Swarm）
docker network create --driver overlay my-overlay-network
```

##### docker network ls

查看网络列表：

```bash
# 查看所有网络
docker network ls

# 查看特定网络
docker network ls --filter name=my-network
```

##### docker network connect/disconnect

连接/断开容器与网络：

```bash
# 连接容器到网络
docker network connect my-network my-container

# 断开容器与网络的连接
docker network disconnect my-network my-container
```

#### 卷管理命令

##### docker volume create

创建卷：

```bash
# 创建命名卷
docker volume create my-volume

# 创建具有特定驱动的卷
docker volume create --driver local my-volume
```

##### docker volume ls

查看卷列表：

```bash
# 查看所有卷
docker volume ls

# 查看特定卷
docker volume ls --filter name=my-volume
```

##### docker volume inspect

查看卷详细信息：

```bash
# 查看卷详细信息
docker volume inspect my-volume
```

##### docker volume rm

删除卷：

```bash
# 删除卷
docker volume rm my-volume

# 删除所有未使用的卷
docker volume prune
```

#### 系统管理命令

##### docker info

查看 Docker 系统信息：

```bash
# 查看系统信息
docker info

# 格式化输出
docker info --format '{{.ContainersRunning}} containers are running'
```

##### docker version

查看 Docker 版本信息：

```bash
# 查看版本
docker version

# 只查看客户端版本
docker version --format '{{.Client.Version}}'
```

##### docker system prune

清理系统资源：

```bash
# 清理所有未使用的资源
docker system prune -a

# 清理但不提示确认
docker system prune -a -f

# 清理特定资源
docker container prune  # 清理容器
docker image prune     # 清理镜像
docker volume prune    # 清理卷
docker network prune   # 清理网络
```

### 实用命令组合示例

#### 开发环境快速搭建

```bash
# 启动数据库
docker run -d --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=myapp \
  -p 3306:3306 \
  mysql:8.0

# 启动 Redis
docker run -d --name redis-cache \
  -p 6379:6379 \
  redis:alpine

# 启动应用
docker run -d --name my-app \
  -p 3000:3000 \
  --link mysql-db:mysql \
  --link redis-cache:redis \
  my-app:latest
```

#### 批量操作

```bash
# 停止所有容器
docker stop $(docker ps -aq)

# 删除所有容器
docker rm $(docker ps -aq)

# 删除所有未使用的镜像
docker image prune -a

# 删除所有未使用的卷
docker volume prune
```

#### 容器调试

```bash
# 查看容器日志
docker logs my-container

# 实时查看日志
docker logs -f my-container

# 进入容器终端
docker exec -it my-container bash

# 查看容器资源使用情况
docker stats my-container
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
```

### 最佳实践

#### 命令使用建议

1. **使用具体标签**：避免使用 latest 标签，使用具体版本号
2. **定期清理**：定期使用 prune 命令清理未使用的资源
3. **资源限制**：为容器设置合理的资源限制
4. **日志管理**：配置日志轮转避免磁盘空间耗尽

#### 安全建议

1. **最小权限原则**：不要以 root 用户运行容器
2. **镜像验证**：使用可信的镜像源
3. **定期更新**：保持 Docker 和镜像的更新
4. **网络安全**：合理配置端口映射和网络策略

通过本节内容，我们详细介绍了 Docker 环境的配置方法和常用命令的使用。掌握这些配置和命令是有效使用 Docker 的基础，能够帮助用户更好地管理容器化应用。