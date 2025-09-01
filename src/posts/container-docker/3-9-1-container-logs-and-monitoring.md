---
title: Container Logs and Monitoring - Mastering Docker Log Management and Performance Monitoring
date: 2025-08-30
categories: [Docker]
tags: [docker, logs, monitoring, containers]
published: true
---

## 容器日志与监控

### Docker 日志管理概述

在容器化应用的运维过程中，日志管理和性能监控是确保系统稳定性和可维护性的关键环节。Docker 提供了丰富的日志管理功能和监控工具，帮助开发者和运维人员深入了解容器的运行状态。

#### 日志的重要性

1. **故障诊断**：快速定位和解决应用问题
2. **性能分析**：识别性能瓶颈和优化点
3. **安全审计**：监控安全事件和异常行为
4. **合规要求**：满足行业标准和法规要求

### Docker 日志驱动

Docker 支持多种日志驱动，每种驱动都有其特定的用途和优势。

#### 日志驱动类型

```bash
# 查看支持的日志驱动
docker info | grep "Logging Driver"

# 查看可用的日志驱动
docker system info | grep "Logging Drivers"
```

#### 常用日志驱动

1. **json-file**：默认驱动，将日志保存为 JSON 格式
2. **syslog**：将日志发送到 syslog 服务器
3. **journald**：将日志发送到 systemd journald
4. **gelf**：将日志发送到 GELF 兼容的日志收集器
5. **fluentd**：将日志发送到 Fluentd
6. **awslogs**：将日志发送到 AWS CloudWatch Logs
7. **splunk**：将日志发送到 Splunk HTTP Event Collector

#### 配置日志驱动

```bash
# 使用 json-file 驱动（默认）
docker run -d --name web nginx

# 指定日志驱动和选项
docker run -d --name web \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  nginx

# 使用 syslog 驱动
docker run -d --name web \
  --log-driver syslog \
  --log-opt syslog-address=tcp://192.168.1.42:123 \
  nginx

# 使用 fluentd 驱动
docker run -d --name web \
  --log-driver fluentd \
  --log-opt fluentd-address=192.168.1.42:24224 \
  --log-opt tag=docker.web \
  nginx
```

### 日志查看和管理

#### 基本日志操作

```bash
# 查看容器日志
docker logs web

# 实时查看日志
docker logs -f web

# 查看最近的日志行数
docker logs --tail 100 web

# 查看指定时间后的日志
docker logs --since="2025-01-01T00:00:00" web

# 查看指定时间范围的日志
docker logs --since="1h" --until="30m" web

# 查看带时间戳的日志
docker logs -t web
```

#### 日志格式化输出

```bash
# 使用模板格式化日志输出
docker logs --format "{{.Timestamp}} {{.Message}}" web

# 查看详细日志信息
docker logs --details web
```

### 日志轮转和清理

#### 配置日志轮转

```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

```bash
# 重启 Docker 服务使配置生效
sudo systemctl restart docker
```

#### 手动日志清理

```bash
# 查看日志文件大小
docker inspect web | grep LogPath
ls -lh $(docker inspect web | grep LogPath | cut -d'"' -f4)

# 清理特定容器的日志
echo "" > $(docker inspect web | grep LogPath | cut -d'"' -f4)

# 批量清理停止容器的日志
docker ps -aq | xargs -I {} sh -c 'echo "" > $(docker inspect {} | grep LogPath | cut -d"\"" -f4)'
```

### 集中式日志管理

#### 使用 ELK Stack

```yaml
# docker-compose.yml for ELK stack
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - es-data:/usr/share/elasticsearch/data

  logstash:
    image: logstash:7.17.0
    ports:
      - "5000:5000"
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:7.17.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

volumes:
  es-data:
```

#### 配置应用容器发送日志到 ELK

```bash
# 使用 gelf 驱动发送日志到 Logstash
docker run -d --name web \
  --log-driver gelf \
  --log-opt gelf-address=udp://localhost:12201 \
  nginx
```

### 容器性能监控

#### 使用 docker stats

```bash
# 查看单个容器的资源使用情况
docker stats web

# 查看所有容器的资源使用情况
docker stats

# 限制输出的容器
docker stats web db redis

# 格式化输出
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
```

#### 使用 ctop 工具

```bash
# 安装 ctop
sudo wget https://github.com/bcicen/ctop/releases/download/v0.7.7/ctop-0.7.7-linux-amd64 -O /usr/local/bin/ctop
sudo chmod +x /usr/local/bin/ctop

# 运行 ctop
ctop
```

### 高级监控解决方案

#### 使用 Prometheus 和 Grafana

```yaml
# docker-compose.yml for monitoring stack
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.37.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana-enterprise
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.45.0
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro

volumes:
  prometheus-data:
  grafana-data:
```

#### 自定义监控脚本

```bash
#!/bin/bash
# container-monitor.sh

CONTAINERS=("web" "db" "redis")
THRESHOLD_CPU=80
THRESHOLD_MEM=80

for container in "${CONTAINERS[@]}"; do
    # 获取 CPU 和内存使用率
    cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" $container | sed 's/%//')
    mem_usage=$(docker stats --no-stream --format "{{.MemPerc}}" $container | sed 's/%//')
    
    # 检查 CPU 使用率
    if (( $(echo "$cpu_usage > $THRESHOLD_CPU" | bc -l) )); then
        echo "警告: 容器 $container CPU 使用率过高: ${cpu_usage}%"
        # 发送告警通知
    fi
    
    # 检查内存使用率
    if (( $(echo "$mem_usage > $THRESHOLD_MEM" | bc -l) )); then
        echo "警告: 容器 $container 内存使用率过高: ${mem_usage}%"
        # 发送告警通知
    fi
done
```

### 日志和监控最佳实践

#### 日志管理最佳实践

1. **结构化日志**：使用 JSON 格式记录日志
2. **日志级别**：合理使用不同的日志级别
3. **日志轮转**：配置适当的日志轮转策略
4. **敏感信息**：避免在日志中记录敏感信息

```dockerfile
# Dockerfile 中的日志最佳实践
FROM nginx:alpine

# 配置应用输出日志到 stdout/stderr
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log
```

#### 监控最佳实践

1. **关键指标监控**：CPU、内存、磁盘、网络
2. **应用层监控**：HTTP 状态码、响应时间、错误率
3. **告警策略**：设置合理的告警阈值
4. **历史数据分析**：保留足够的历史数据用于趋势分析

#### 安全考虑

```bash
# 限制日志文件权限
chmod 640 /var/lib/docker/containers/*/*.log

# 使用专用日志用户
useradd -r -s /bin/false dockerlogs

# 配置日志审计
auditctl -w /var/lib/docker/containers/ -p rwxa -k docker_logs
```

### 故障排除

#### 常见日志问题

1. **日志文件过大**：
```bash
# 检查日志文件大小
du -sh /var/lib/docker/containers/*/

# 配置日志轮转
# 在 daemon.json 中配置 max-size 和 max-file
```

2. **日志丢失**：
```bash
# 检查日志驱动配置
docker info | grep "Logging Driver"

# 验证日志收集服务状态
systemctl status rsyslog
```

3. **日志格式问题**：
```bash
# 检查应用日志输出格式
docker logs web | head -10

# 验证日志驱动配置
docker inspect web | grep LogConfig
```

通过本节内容，您已经深入了解了 Docker 容器的日志管理和性能监控技术，包括日志驱动配置、日志查看和管理、集中式日志收集以及性能监控等高级主题。掌握这些技能将帮助您更好地运维容器化应用。