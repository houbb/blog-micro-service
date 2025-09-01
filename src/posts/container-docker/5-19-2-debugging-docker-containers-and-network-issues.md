---
title: Debugging Docker Containers and Network Issues - Mastering Container Troubleshooting Techniques
date: 2025-08-31
categories: [Write]
tags: [docker, debugging, containers, network, troubleshooting]
published: true
---

## 调试 Docker 容器与网络问题

### 容器调试基础

在复杂的容器化环境中，调试问题需要系统性的方法和专业的工具。掌握有效的调试技巧可以帮助快速定位和解决各种容器相关问题。

#### 调试工具概览

1. **Docker 原生命令**：
   - `docker logs`：查看容器日志
   - `docker exec`：进入容器执行命令
   - `docker inspect`：查看容器详细信息

2. **系统级工具**：
   - `ps`、`top`：查看进程状态
   - `netstat`、`ss`：查看网络连接
   - `iptables`：查看防火墙规则

3. **第三方工具**：
   - `ctop`：容器监控仪表板
   - `docker-compose`：多容器应用调试
   - `wireshark`：网络包分析

### 容器启动问题调试

#### 容器无法启动

```bash
# 查看容器状态
docker ps -a

# 查看容器日志
docker logs <container_id>

# 查看容器详细信息
docker inspect <container_id>

# 检查容器配置
docker inspect <container_id> | jq '.[0].Config'

# 检查容器状态
docker inspect <container_id> | jq '.[0].State'
```

#### 启动脚本问题

```bash
# 进入容器调试
docker run -it --entrypoint /bin/bash <image_name>

# 或者覆盖启动命令
docker run -it <image_name> /bin/bash

# 检查启动脚本
docker exec -it <container_id> cat /app/start.sh
```

#### 权限问题

```bash
# 检查文件权限
docker exec -it <container_id> ls -la /app

# 检查用户权限
docker exec -it <container_id> whoami
docker exec -it <container_id> id

# 以特定用户运行
docker run --user 1000:1000 <image_name>
```

### 容器运行时问题调试

#### 应用崩溃调试

```bash
# 实时查看日志
docker logs -f <container_id>

# 查看最近的日志
docker logs --tail 100 <container_id>

# 查看带时间戳的日志
docker logs -t <container_id>

# 导出日志到文件
docker logs <container_id> > container.log
```

#### 资源使用问题

```bash
# 查看容器资源使用
docker stats <container_id>

# 查看所有容器资源使用
docker stats

# 查看容器详细资源信息
docker inspect <container_id> | jq '.[0].Stats'

# 进入容器查看系统资源
docker exec -it <container_id> top
docker exec -it <container_id> free -m
docker exec -it <container_id> df -h
```

#### 性能问题分析

```bash
# 使用 pidstat 监控进程
docker exec -it <container_id> pidstat -u 1 5

# 使用 iostat 监控 I/O
docker exec -it <container_id> iostat -x 1 5

# 使用 sar 监控系统性能
docker exec -it <container_id> sar -u 1 5
```

### 网络问题调试

#### 网络连接问题

```bash
# 检查容器网络配置
docker inspect <container_id> | jq '.[0].NetworkSettings'

# 查看容器 IP 地址
docker inspect <container_id> | jq '.[0].NetworkSettings.IPAddress'

# 查看容器网络端口映射
docker port <container_id>

# 进入容器测试网络连接
docker exec -it <container_id> ping google.com
docker exec -it <container_id> curl -v http://service:8080
docker exec -it <container_id> telnet service 8080
```

#### DNS 解析问题

```bash
# 检查容器 DNS 配置
docker exec -it <container_id> cat /etc/resolv.conf

# 测试 DNS 解析
docker exec -it <container_id> nslookup service
docker exec -it <container_id> dig service

# 检查 Docker DNS 配置
docker inspect <container_id> | jq '.[0].HostConfig.Dns'
```

#### 端口冲突问题

```bash
# 检查端口占用
netstat -tulpn | grep :8080
ss -tulpn | grep :8080

# 检查 Docker 端口映射
docker ps --format "table {{.Names}}\t{{.Ports}}"

# 查看防火墙规则
sudo iptables -L -n -v
```

### 网络配置调试

#### 自定义网络调试

```bash
# 查看网络列表
docker network ls

# 查看网络详细信息
docker network inspect <network_name>

# 创建自定义网络
docker network create --driver bridge --subnet=172.20.0.0/16 my-network

# 连接容器到网络
docker network connect my-network <container_id>

# 断开容器网络连接
docker network disconnect my-network <container_id>
```

#### 网络驱动问题

```bash
# 检查网络驱动
docker info | grep "Network"

# 查看网络插件
docker plugin ls

# 测试不同网络驱动性能
docker run -d --name test-bridge --network bridge nginx
docker run -d --name test-host --network host nginx
```

### 高级调试技巧

#### 使用调试容器

```bash
# 创建调试容器
docker run -it --rm \
  --network container:<target_container> \
  --pid container:<target_container> \
  --ipc container:<target_container> \
  nicolaka/netshoot

# 在调试容器中执行命令
# 查看网络连接
ss -tulpn

# 查看进程
ps aux

# 查看文件系统
ls -la /proc/1/root/
```

#### 进程调试

```bash
# 查看容器进程 ID
docker inspect <container_id> | jq '.[0].State.Pid'

# 在主机上查看容器进程
sudo ps -p <pid> -o pid,ppid,cmd

# 使用 gdb 调试容器进程
sudo nsenter -t <pid> -n -p gdb -p 1
```

#### 文件系统调试

```bash
# 查看容器文件系统挂载点
docker inspect <container_id> | jq '.[0].GraphDriver'

# 在主机上访问容器文件系统
sudo ls /var/lib/docker/containers/<container_id>/

# 导出容器文件系统
docker export <container_id> > container.tar
```

### 网络流量分析

#### 使用 tcpdump

```bash
# 在容器中安装 tcpdump
docker exec -it <container_id> apt-get update && apt-get install -y tcpdump

# 捕获网络流量
docker exec -it <container_id> tcpdump -i any -w /tmp/capture.pcap

# 分析捕获的流量
docker exec -it <container_id> tcpdump -r /tmp/capture.pcap
```

#### 使用 Wireshark

```bash
# 在主机上捕获 Docker 流量
sudo tcpdump -i any -w capture.pcap host <container_ip>

# 使用 Wireshark 分析流量
wireshark capture.pcap
```

### 调试脚本和工具

#### 自动化调试脚本

```bash
#!/bin/bash
# container-debug.sh

CONTAINER_NAME="$1"

if [ -z "$CONTAINER_NAME" ]; then
    echo "用法: $0 <container_name>"
    exit 1
fi

echo "=== 容器调试报告: $CONTAINER_NAME ==="
echo "时间: $(date)"
echo ""

# 检查容器状态
echo "--- 容器状态 ---"
docker ps -a --filter "name=$CONTAINER_NAME"

# 查看容器日志
echo ""
echo "--- 最近日志 ---"
docker logs --tail 50 $CONTAINER_NAME

# 查看容器资源使用
echo ""
echo "--- 资源使用 ---"
docker stats --no-stream $CONTAINER_NAME

# 查看容器网络配置
echo ""
echo "--- 网络配置 ---"
docker inspect $CONTAINER_NAME | jq '.[0].NetworkSettings'

# 查看容器详细信息
echo ""
echo "--- 容器配置 ---"
docker inspect $CONTAINER_NAME | jq '.[0].Config'

# 进入容器执行基本检查
echo ""
echo "--- 容器内部检查 ---"
docker exec $CONTAINER_NAME ps aux
docker exec $CONTAINER_NAME df -h
docker exec $CONTAINER_NAME free -m
```

#### 网络调试脚本

```bash
#!/bin/bash
# network-debug.sh

CONTAINER_NAME="$1"

if [ -z "$CONTAINER_NAME" ]; then
    echo "用法: $0 <container_name>"
    exit 1
fi

echo "=== 网络调试报告: $CONTAINER_NAME ==="
echo "时间: $(date)"
echo ""

# 获取容器 IP
CONTAINER_IP=$(docker inspect $CONTAINER_NAME | jq -r '.[0].NetworkSettings.IPAddress')
echo "容器 IP: $CONTAINER_IP"

# 测试本地连接
echo ""
echo "--- 本地连接测试 ---"
docker exec $CONTAINER_NAME ping -c 4 127.0.0.1

# 测试网关连接
echo ""
echo "--- 网关连接测试 ---"
GATEWAY=$(docker inspect $CONTAINER_NAME | jq -r '.[0].NetworkSettings.Gateway')
docker exec $CONTAINER_NAME ping -c 4 $GATEWAY

# 测试外部连接
echo ""
echo "--- 外部连接测试 ---"
docker exec $CONTAINER_NAME ping -c 4 8.8.8.8

# 测试 DNS 解析
echo ""
echo "--- DNS 解析测试 ---"
docker exec $CONTAINER_NAME nslookup google.com

# 查看网络接口
echo ""
echo "--- 网络接口 ---"
docker exec $CONTAINER_NAME ip addr

# 查看路由表
echo ""
echo "--- 路由表 ---"
docker exec $CONTAINER_NAME ip route
```

### 常见问题解决方案

#### 容器启动失败

```bash
# 检查 Docker 守护进程状态
sudo systemctl status docker

# 查看 Docker 日志
sudo journalctl -u docker

# 重启 Docker 服务
sudo systemctl restart docker
```

#### 网络连接超时

```bash
# 检查防火墙设置
sudo iptables -L -n -v

# 检查网络配置
docker network ls
docker network inspect bridge

# 重启网络
sudo systemctl restart docker
```

#### 磁盘空间不足

```bash
# 检查 Docker 磁盘使用
docker system df

# 清理未使用的资源
docker system prune -a

# 清理未使用的卷
docker volume prune

# 清理未使用的镜像
docker image prune -a
```

### 调试最佳实践

#### 系统化调试方法

1. **观察现象**：
   - 记录错误信息
   - 确定问题范围

2. **收集信息**：
   - 查看日志
   - 检查配置
   - 分析资源使用

3. **假设验证**：
   - 提出可能原因
   - 验证假设
   - 排除不可能原因

4. **解决问题**：
   - 实施解决方案
   - 验证修复效果
   - 记录解决过程

#### 预防性措施

```bash
# 健康检查脚本
#!/bin/bash
# health-check.sh

CONTAINER_NAME="$1"
HEALTH_ENDPOINT="${2:-http://localhost:8080/health}"

# 检查容器是否运行
if ! docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ 容器 $CONTAINER_NAME 未运行"
    exit 1
fi

# 检查健康端点
if docker exec $CONTAINER_NAME curl -f $HEALTH_ENDPOINT > /dev/null 2>&1; then
    echo "✅ 容器 $CONTAINER_NAME 健康检查通过"
    exit 0
else
    echo "❌ 容器 $CONTAINER_NAME 健康检查失败"
    # 查看详细日志
    docker logs --tail 20 $CONTAINER_NAME
    exit 1
fi
```

通过本节内容，我们深入了解了 Docker 容器与网络问题的调试方法，包括容器启动问题、运行时问题、网络连接问题的诊断和解决技巧。掌握这些调试技能将帮助您快速定位和解决容器化环境中的各种问题，提高系统的稳定性和可靠性。