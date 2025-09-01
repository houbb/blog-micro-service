---
title: Configuring Docker Engine and Daemon - Mastering Docker Infrastructure Settings
date: 2025-08-31
categories: [Docker]
tags: [container-docker]
published: true
---

## 配置 Docker 引擎与守护进程

### Docker 引擎架构

Docker 引擎是 Docker 平台的核心组件，负责容器的创建、运行和管理。理解 Docker 引擎的架构对于进行高级配置至关重要。

#### 引擎组件

1. **Docker Daemon**：
   - 后台运行的服务进程
   - 管理镜像、容器、网络和存储
   - 提供 REST API 接口

2. **Docker Client**：
   - 用户交互的命令行工具
   - 发送命令到 Docker Daemon
   - 支持多种交互方式

3. **Container Runtime**：
   - 实际运行容器的组件
   - 管理容器的生命周期
   - 处理容器的资源隔离

### 守护进程配置文件

#### daemon.json 配置

```json
// /etc/docker/daemon.json
{
  "debug": false,
  "log-level": "info",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "data-root": "/var/lib/docker",
  "exec-opts": ["native.cgroupdriver=systemd"],
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "registry-mirrors": [
    "https://mirror.gcr.io",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "insecure-registries": [
    "registry.internal:5000"
  ],
  "live-restore": true,
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  },
  "default-runtime": "runc",
  "runtimes": {
    "runc": {
      "path": "runc"
    },
    "custom": {
      "path": "/usr/local/bin/my-custom-runtime",
      "runtimeArgs": [
        "--debug"
      ]
    }
  },
  "iptables": true,
  "ip-forward": true,
  "userland-proxy": false,
  "userns-remap": "default",
  "metrics-addr": "0.0.0.0:9323",
  "experimental": true
}
```

#### 配置选项详解

##### 日志配置

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "10",
    "labels": "production_status",
    "env": "os,customer"
  }
}
```

##### 存储配置

```json
{
  "data-root": "/mnt/docker-data",
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.size=20G"
  ]
}
```

##### 网络配置

```json
{
  "bip": "192.168.1.1/24",
  "fixed-cidr": "192.168.1.0/25",
  "fixed-cidr-v6": "2001:db8::/64",
  "default-address-pools": [
    {
      "base": "172.17.0.0/16",
      "size": 24
    }
  ]
}
```

### 性能优化配置

#### 资源限制配置

```json
{
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    },
    "nproc": {
      "Name": "nproc",
      "Hard": 32768,
      "Soft": 32768
    }
  },
  "default-shm-size": "128M",
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 10
}
```

#### 镜像加速配置

```json
{
  "registry-mirrors": [
    "https://dockerhub.azk8s.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

### 安全配置

#### 用户命名空间配置

```json
{
  "userns-remap": "default"
}
```

创建用户映射：

```bash
# 创建用户和组
sudo useradd -r dockremap
sudo groupadd dockremap

# 配置子用户和组 ID
echo "dockremap:165536:65536" | sudo tee -a /etc/subuid
echo "dockremap:165536:65536" | sudo tee -a /etc/subgid
```

#### TLS 配置

```bash
# 生成 CA 证书
openssl genrsa -aes256 -out ca-key.pem 4096
openssl req -new -x509 -days 365 -key ca-key.pem -sha256 -out ca.pem

# 生成服务器证书
openssl genrsa -out server-key.pem 4096
openssl req -subj "/CN=$HOST" -sha256 -new -key server-key.pem -out server.csr
echo subjectAltName = DNS:$HOST,IP:127.0.0.1 >> extfile.cnf
openssl x509 -req -days 365 -sha256 -in server.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -extfile extfile.cnf

# 配置 Docker 守护进程使用 TLS
sudo dockerd \
  --tlsverify \
  --tlscacert=ca.pem \
  --tlscert=server-cert.pem \
  --tlskey=server-key.pem \
  -H=0.0.0.0:2376
```

### 网络高级配置

#### 自定义网络配置

```json
{
  "default-address-pools": [
    {
      "base": "172.17.0.0/16",
      "size": 24
    },
    {
      "base": "172.18.0.0/16",
      "size": 24
    }
  ],
  "iptables": true,
  "ip-forward": true,
  "ip-masq": true,
  "userland-proxy": false
}
```

#### IPv6 配置

```json
{
  "ipv6": true,
  "fixed-cidr-v6": "2001:db8:1::/64",
  "experimental": true
}
```

### 存储驱动配置

#### Overlay2 配置

```json
{
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.size=20G",
    "overlay2.override_kernel_check=true"
  ]
}
```

#### Device Mapper 配置

```json
{
  "storage-driver": "devicemapper",
  "storage-opts": [
    "dm.thinpooldev=/dev/mapper/thin-pool",
    "dm.use_deferred_removal=true",
    "dm.use_deferred_deletion=true"
  ]
}
```

### 运行时配置

#### 自定义运行时

```json
{
  "default-runtime": "runc",
  "runtimes": {
    "runc": {
      "path": "runc"
    },
    "kata-runtime": {
      "path": "/usr/bin/kata-runtime"
    },
    "gvisor": {
      "path": "/usr/bin/runsc"
    }
  }
}
```

#### SELinux 配置

```json
{
  "selinux-enabled": true
}
```

### 监控和指标

#### 启用指标端点

```json
{
  "metrics-addr": "0.0.0.0:9323",
  "experimental": true
}
```

#### Prometheus 监控配置

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']
```

### 调试配置

#### 启用调试模式

```json
{
  "debug": true,
  "log-level": "debug"
}
```

#### 日志配置

```json
{
  "log-driver": "syslog",
  "log-opts": {
    "syslog-address": "tcp://192.168.1.42:123",
    "syslog-facility": "daemon",
    "tag": "docker"
  }
}
```

### 高可用配置

#### Live Restore 配置

```json
{
  "live-restore": true
}
```

#### 集群配置

```json
{
  "cluster-store": "consul://192.168.1.10:8500",
  "cluster-advertise": "192.168.1.20:2376"
}
```

### 配置管理最佳实践

#### 配置文件版本控制

```bash
# 配置文件管理脚本
#!/bin/bash
# config-manager.sh

CONFIG_FILE="/etc/docker/daemon.json"
BACKUP_DIR="/etc/docker/backup"

# 备份当前配置
backup_config() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    sudo cp $CONFIG_FILE $BACKUP_DIR/daemon.json.$timestamp
    echo "配置已备份: $BACKUP_DIR/daemon.json.$timestamp"
}

# 验证配置
validate_config() {
    sudo docker version > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "配置验证通过"
        return 0
    else
        echo "配置验证失败"
        return 1
    fi
}

# 应用配置
apply_config() {
    backup_config
    
    # 重新加载配置
    sudo systemctl reload docker
    
    # 验证配置
    if validate_config; then
        echo "配置应用成功"
    else
        echo "配置应用失败，恢复备份配置"
        sudo cp $BACKUP_DIR/daemon.json.$(ls -t $BACKUP_DIR | head -1) $CONFIG_FILE
        sudo systemctl reload docker
    fi
}
```

#### 环境特定配置

```bash
# 环境配置管理
#!/bin/bash
# env-config.sh

ENVIRONMENT="${1:-development}"
CONFIG_DIR="/etc/docker/config"

# 加载环境特定配置
load_env_config() {
    if [ -f "$CONFIG_DIR/$ENVIRONMENT.json" ]; then
        sudo cp $CONFIG_DIR/$ENVIRONMENT.json /etc/docker/daemon.json
        echo "已加载 $ENVIRONMENT 环境配置"
    else
        echo "环境配置文件不存在: $CONFIG_DIR/$ENVIRONMENT.json"
        exit 1
    fi
}

# 重启 Docker 服务
restart_docker() {
    echo "重启 Docker 服务..."
    sudo systemctl restart docker
    sleep 5
    
    # 检查服务状态
    if sudo systemctl is-active --quiet docker; then
        echo "Docker 服务重启成功"
    else
        echo "Docker 服务重启失败"
        exit 1
    fi
}

# 主函数
main() {
    load_env_config
    restart_docker
}

main
```

### 故障排除

#### 常见配置问题

1. **存储空间不足**：
```bash
# 检查 Docker 存储使用情况
docker system df

# 清理未使用的资源
docker system prune -a
```

2. **网络配置问题**：
```bash
# 检查网络配置
docker network ls
docker network inspect bridge

# 重启网络服务
sudo systemctl restart docker
```

3. **权限问题**：
```bash
# 检查用户组
groups $USER

# 添加用户到 docker 组
sudo usermod -aG docker $USER
```

通过本节内容，我们深入了解了 Docker 引擎与守护进程的高级配置选项，包括日志、存储、网络、安全、性能优化等方面的配置方法。掌握这些配置技巧将帮助您根据具体需求优化 Docker 环境，提高系统的稳定性和性能。