---
title: Docker安装与配置详解：Windows、Linux、macOS全平台指南
date: 2025-08-31
categories: [Containerization]
tags: [docker, installation, configuration, windows, linux, macos]
published: true
---

# 第9章：Docker安装与配置详解

Docker作为容器技术的领军者，已经成为了现代软件开发和部署的事实标准。正确安装和配置Docker是使用Docker的第一步，也是确保容器化应用稳定运行的基础。本章将详细介绍在Windows、Linux和macOS等不同操作系统上安装和配置Docker的方法，帮助读者快速上手Docker。

## Docker安装概述

Docker的安装方式因操作系统而异，但核心目标都是为用户提供一个稳定、高效的容器化平台。在安装Docker之前，需要了解不同操作系统的安装要求和限制。

### 系统要求

#### Windows系统要求
- Windows 10 Pro、Enterprise或Education（64位）
- 启用Hyper-V和Containers Windows功能
- 启用硬件虚拟化（BIOS设置）
- 至少4GB RAM

#### Linux系统要求
- 64位操作系统
- Linux内核版本3.10或更高
- 支持的发行版：Ubuntu、Debian、CentOS、RHEL、Fedora等
- 启用硬件虚拟化（可选，但推荐）

#### macOS系统要求
- macOS 10.15或更高版本
- 至少4GB RAM
- 启用硬件虚拟化（默认启用）

### 安装方式选择

#### Docker Desktop
Docker Desktop是Docker官方提供的桌面应用程序，适用于Windows和macOS系统。它提供了一个完整的Docker开发环境，包括Docker Engine、Docker Compose、Kubernetes等组件。

#### Docker Engine
Docker Engine是Docker的核心组件，适用于Linux系统。它可以直接安装在Linux发行版上，提供完整的容器化功能。

#### 其他安装方式
- 使用包管理器安装（适用于Linux）
- 使用脚本安装（适用于Linux）
- 从源码编译安装（适用于高级用户）

## Windows系统Docker安装

Windows系统上的Docker安装主要通过Docker Desktop进行，它为Windows用户提供了完整的容器化开发环境。

### Docker Desktop for Windows安装

#### 系统准备
在安装Docker Desktop之前，需要确保系统满足以下要求：

1. **启用WSL 2**：
   ```powershell
   # 启用WSL功能
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   
   # 启用虚拟机功能
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   
   # 设置WSL 2为默认版本
   wsl --set-default-version 2
   ```

2. **安装Linux发行版**：
   - 从Microsoft Store安装Ubuntu或其他Linux发行版
   - 启动并初始化Linux发行版

3. **启用硬件虚拟化**：
   - 进入BIOS设置
   - 启用Intel VT-x或AMD-V虚拟化技术
   - 保存设置并重启计算机

#### 安装步骤

1. **下载Docker Desktop**：
   - 访问Docker官网（https://www.docker.com/products/docker-desktop）
   - 下载适用于Windows的Docker Desktop安装包

2. **运行安装程序**：
   ```powershell
   # 双击下载的安装包，按照向导完成安装
   # 或使用命令行安装
   Start-Process -FilePath "Docker Desktop Installer.exe" -ArgumentList "install" -Wait
   ```

3. **启动Docker Desktop**：
   - 安装完成后，Docker Desktop会自动启动
   - 在系统托盘中可以看到Docker图标

4. **验证安装**：
   ```bash
   # 打开命令提示符或PowerShell
   docker --version
   docker info
   docker run hello-world
   ```

#### 配置优化

1. **镜像加速配置**：
   ```json
   {
     "registry-mirrors": [
       "https://docker.mirrors.ustc.edu.cn",
       "https://hub-mirror.c.163.com"
     ],
     "insecure-registries": [],
     "debug": false,
     "experimental": false
   }
   ```

2. **资源限制配置**：
   ```json
   {
     "resources": {
       "limits": {
         "cpus": 2,
         "memory": 4096
       }
     }
   }
   ```

3. **文件共享配置**：
   - 在Docker Desktop设置中配置文件共享
   - 添加需要共享的目录

### Windows容器安装

除了Linux容器，Windows还支持Windows容器：

#### 安装Windows容器
```powershell
# 启用容器功能
Enable-WindowsOptionalFeature -Online -FeatureName containers -All

# 重启计算机
Restart-Computer -Force
```

#### 切换容器类型
```powershell
# 切换到Windows容器
& $Env:ProgramFiles\Docker\Docker\DockerCli.exe -SwitchDaemon

# 切换到Linux容器
& $Env:ProgramFiles\Docker\Docker\DockerCli.exe -SwitchDaemon
```

## Linux系统Docker安装

Linux系统上的Docker安装可以通过多种方式进行，包括使用包管理器、安装脚本或从源码编译。

### Ubuntu系统安装

#### 使用APT包管理器安装
```bash
# 1. 更新apt包索引
sudo apt-get update

# 2. 安装必要的包
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. 添加Docker官方GPG密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 4. 设置仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. 更新apt包索引
sudo apt-get update

# 6. 安装Docker Engine
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 7. 验证安装
sudo docker run hello-world
```

#### 使用便捷脚本安装
```bash
# 下载并运行安装脚本
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 验证安装
sudo docker run hello-world
```

### CentOS/RHEL系统安装

#### 使用YUM/DNF包管理器安装
```bash
# 1. 设置仓库（CentOS）
sudo yum install -y yum-utils
sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# 1. 设置仓库（RHEL）
sudo dnf config-manager \
    --add-repo \
    https://download.docker.com/linux/rhel/docker-ce.repo

# 2. 安装Docker Engine
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin
# 或者对于RHEL
sudo dnf install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 3. 启动Docker服务
sudo systemctl start docker

# 4. 设置开机自启
sudo systemctl enable docker

# 5. 验证安装
sudo docker run hello-world
```

### Fedora系统安装

#### 使用DNF包管理器安装
```bash
# 1. 设置仓库
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager \
    --add-repo \
    https://download.docker.com/linux/fedora/docker-ce.repo

# 2. 安装Docker Engine
sudo dnf install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 3. 启动Docker服务
sudo systemctl start docker

# 4. 设置开机自启
sudo systemctl enable docker

# 5. 验证安装
sudo docker run hello-world
```

### Linux系统配置优化

#### 用户权限配置
```bash
# 将用户添加到docker组
sudo usermod -aG docker $USER

# 注销并重新登录，或运行以下命令
newgrp docker

# 验证权限
docker run hello-world
```

#### 镜像加速配置
```bash
# 创建或编辑daemon.json文件
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF

# 重启Docker服务
sudo systemctl daemon-reload
sudo systemctl restart docker
```

#### 存储驱动配置
```bash
# 查看当前存储驱动
docker info | grep "Storage Driver"

# 配置overlay2存储驱动（推荐）
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "storage-driver": "overlay2"
}
EOF

# 重启Docker服务
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## macOS系统Docker安装

macOS系统上的Docker安装主要通过Docker Desktop进行，它为macOS用户提供了完整的容器化开发环境。

### Docker Desktop for Mac安装

#### 系统准备
在安装Docker Desktop之前，需要确保系统满足以下要求：

1. **系统版本**：
   - macOS 10.15或更高版本
   - Apple Silicon或Intel处理器

2. **硬件要求**：
   - 至少4GB RAM
   - 启用硬件虚拟化（默认启用）

#### 安装步骤

1. **下载Docker Desktop**：
   - 访问Docker官网（https://www.docker.com/products/docker-desktop）
   - 下载适用于macOS的Docker Desktop安装包

2. **安装Docker Desktop**：
   ```bash
   # 双击下载的.dmg文件
   # 将Docker拖拽到Applications文件夹
   ```

3. **启动Docker Desktop**：
   - 从Applications文件夹启动Docker Desktop
   - 在菜单栏中可以看到Docker图标

4. **验证安装**：
   ```bash
   # 打开终端
   docker --version
   docker info
   docker run hello-world
   ```

#### 配置优化

1. **镜像加速配置**：
   ```json
   {
     "registry-mirrors": [
       "https://docker.mirrors.ustc.edu.cn",
       "https://hub-mirror.c.163.com"
     ],
     "insecure-registries": [],
     "debug": false,
     "experimental": false
   }
   ```

2. **资源限制配置**：
   ```json
   {
     "resources": {
       "limits": {
         "cpus": 2,
         "memory": 4096
       }
     }
   }
   ```

3. **文件共享配置**：
   - 在Docker Desktop设置中配置文件共享
   - 添加需要共享的目录

### Homebrew安装方式

对于喜欢使用命令行的用户，可以使用Homebrew安装Docker：

```bash
# 安装Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Docker
brew install --cask docker

# 启动Docker Desktop
open /Applications/Docker.app
```

## Docker配置管理

正确的Docker配置能够提高容器化应用的性能和安全性。

### Docker Daemon配置

#### 配置文件位置
- Linux: `/etc/docker/daemon.json`
- Windows: `C:\ProgramData\Docker\config\daemon.json`
- macOS: `~/.docker/daemon.json`

#### 常用配置选项
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ],
  "insecure-registries": [
    "registry.example.com"
  ],
  "debug": false,
  "experimental": false,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "iptables": true,
  "ip-forward": true,
  "userland-proxy": false
}
```

### Docker Client配置

#### 配置文件位置
- Linux/macOS: `~/.docker/config.json`
- Windows: `%USERPROFILE%\.docker\config.json`

#### 常用配置选项
```json
{
  "credsStore": "desktop",
  "experimental": "disabled",
  "stackOrchestrator": "swarm",
  "proxies": {
    "default": {
      "httpProxy": "http://proxy.example.com:8080",
      "httpsProxy": "https://proxy.example.com:8080",
      "noProxy": "localhost,127.0.0.1"
    }
  }
}
```

### 网络配置

#### 桥接网络配置
```bash
# 创建自定义桥接网络
docker network create --driver bridge mynetwork

# 查看网络配置
docker network inspect mynetwork

# 在自定义网络中运行容器
docker run --network mynetwork nginx:latest
```

#### 端口映射配置
```bash
# 映射单个端口
docker run -d -p 8080:80 nginx:latest

# 映射多个端口
docker run -d -p 8080:80 -p 8443:443 nginx:latest

# 映射到特定IP
docker run -d -p 127.0.0.1:8080:80 nginx:latest
```

### 存储配置

#### 数据卷配置
```bash
# 创建数据卷
docker volume create myvolume

# 查看数据卷
docker volume ls

# 使用数据卷
docker run -d -v myvolume:/data nginx:latest

# 删除数据卷
docker volume rm myvolume
```

#### 绑定挂载配置
```bash
# 绑定挂载目录
docker run -d -v /host/path:/container/path nginx:latest

# 绑定挂载文件
docker run -d -v /host/file:/container/file nginx:latest

# 只读挂载
docker run -d -v /host/path:/container/path:ro nginx:latest
```

## Docker安全配置

安全性是容器化应用的重要考虑因素，正确的安全配置能够保护容器环境免受攻击。

### 镜像安全

#### 使用可信镜像
```bash
# 使用官方镜像
docker pull nginx:latest

# 验证镜像签名
docker trust inspect nginx:latest

# 扫描镜像漏洞
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy nginx:latest
```

#### 固定镜像版本
```dockerfile
# 推荐：固定版本
FROM node:16.14.0-alpine

# 不推荐：使用latest标签
FROM node:latest
```

### 容器安全

#### 以非root用户运行
```dockerfile
# 创建非root用户
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# 切换到非root用户
USER nextjs

# 设置工作目录
WORKDIR /app
```

#### 限制容器能力
```bash
# 移除不必要的能力
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx:latest

# 以只读模式运行容器
docker run --read-only nginx:latest

# 启用用户命名空间
docker run --userns=host nginx:latest
```

### 网络安全

#### 使用用户定义网络
```bash
# 创建用户定义网络
docker network create --driver bridge mynetwork

# 在用户定义网络中运行容器
docker run --network mynetwork nginx:latest
```

#### 配置网络策略
```bash
# 限制容器网络访问
docker run --network mynetwork --dns 8.8.8.8 nginx:latest
```

## Docker性能优化

性能优化是确保容器化应用高效运行的关键。

### 资源限制

#### CPU限制
```bash
# 限制CPU使用率
docker run --cpus="1.5" nginx:latest

# 限制CPU份额
docker run --cpu-shares=512 nginx:latest

# 绑定CPU核心
docker run --cpuset-cpus="0-1" nginx:latest
```

#### 内存限制
```bash
# 限制内存使用
docker run --memory="512m" nginx:latest

# 设置内存交换
docker run --memory="512m" --memory-swap="1g" nginx:latest

# 设置内存预留
docker run --memory="512m" --memory-reservation="256m" nginx:latest
```

### 存储优化

#### 使用精简镜像
```dockerfile
# 使用alpine基础镜像
FROM node:16-alpine

# 清理安装缓存
RUN apk add --no-cache python3
```

#### 分层缓存优化
```dockerfile
# 将不经常变化的指令放在前面
COPY package*.json ./
RUN npm ci --only=production

# 将经常变化的指令放在后面
COPY . .
RUN npm run build
```

## Docker故障排除

有效的故障排除能力对于容器化应用的稳定运行至关重要。

### 常见问题及解决方案

#### 容器无法启动
```bash
# 查看容器日志
docker logs container_name

# 以交互模式运行容器
docker run -it image_name /bin/bash

# 检查容器配置
docker inspect container_name
```

#### 端口无法访问
```bash
# 检查端口映射
docker port container_name

# 检查容器网络配置
docker inspect container_name | grep -i network

# 检查防火墙设置
# Linux: iptables -L
# Windows: 检查Windows防火墙设置
```

#### 存储空间不足
```bash
# 查看Docker磁盘使用情况
docker system df

# 清理未使用的资源
docker system prune

# 清理所有未使用的资源（包括镜像）
docker system prune -a

# 删除未使用的卷
docker volume prune
```

### 调试技巧

#### 进入运行中的容器
```bash
# 进入容器执行命令
docker exec -it container_name /bin/bash

# 在容器中执行单个命令
docker exec container_name ps aux
```

#### 查看容器进程
```bash
# 查看容器内的进程
docker top container_name
```

#### 检查容器网络
```bash
# 查看容器网络信息
docker network inspect bridge
```

## 小结

Docker的安装和配置是使用容器技术的基础，正确安装和配置Docker能够确保容器化应用的稳定运行。本章详细介绍了在Windows、Linux和macOS等不同操作系统上安装和配置Docker的方法，包括系统要求、安装步骤、配置优化、安全配置、性能优化和故障排除等内容。

在Windows系统上，Docker Desktop提供了完整的容器化开发环境，支持Linux容器和Windows容器。在Linux系统上，可以通过包管理器、安装脚本等方式安装Docker Engine。在macOS系统上，Docker Desktop同样提供了完整的容器化开发环境。

正确的Docker配置包括Docker Daemon配置、Docker Client配置、网络配置和存储配置等方面，这些配置能够提高容器化应用的性能和安全性。安全配置包括使用可信镜像、以非root用户运行容器、限制容器能力等措施，能够保护容器环境免受攻击。

性能优化包括资源限制、存储优化等措施，能够确保容器化应用的高效运行。故障排除能力对于容器化应用的稳定运行至关重要，掌握常见的故障排除方法和调试技巧能够快速解决容器化应用的问题。

通过本章的学习，读者应该能够熟练掌握在不同操作系统上安装和配置Docker的方法，并能够进行基本的配置优化、安全配置和性能优化，为后续的容器化应用开发和部署打下坚实的基础。