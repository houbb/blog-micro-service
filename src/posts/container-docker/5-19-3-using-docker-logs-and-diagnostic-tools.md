---
title: Using Docker Logs and Diagnostic Tools - Mastering Container Observability and Analysis
date: 2025-08-31
categories: [Docker]
tags: [docker, logs, diagnostics, observability, containers]
published: true
---

## 使用 Docker 的日志与诊断工具

### 日志管理基础

有效的日志管理是容器化应用运维的核心组成部分。Docker 提供了多种日志驱动和工具，帮助用户收集、分析和监控容器日志。

#### 日志驱动类型

1. **json-file**：默认驱动，将日志保存为 JSON 格式
2. **syslog**：将日志发送到 syslog 服务器
3. **journald**：将日志发送到 systemd journald
4. **gelf**：将日志发送到 GELF 兼容的日志收集器
5. **fluentd**：将日志发送到 Fluentd
6. **awslogs**：将日志发送到 AWS CloudWatch Logs

### 基础日志操作

#### 查看日志

```bash
# 查看容器日志
docker logs <container_name>

# 实时查看日志
docker logs -f <container_name>

# 查看最近的日志行数
docker logs --tail 100 <container_name>

# 查看指定时间后的日志
docker logs --since="2023-01-01T00:00:00" <container_name>

# 查看指定时间范围的日志
docker logs --since="1h" --until="30m" <container_name>

# 查看带时间戳的日志
docker logs -t <container_name>
```

#### 日志格式化输出

```bash
# 使用模板格式化日志输出
docker logs --format "{{.Timestamp}} {{.Message}}" <container_name>

# 查看详细日志信息
docker logs --details <container_name>
```

### 高级日志配置

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

#### 全局日志配置

```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3",
    "labels": "production_status",
    "env": "os,customer"
  }
}
```

### 日志轮转和清理

#### 配置日志轮转

```json
// 容器特定的日志轮转配置
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "10"
  }
}
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
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms1g -Xmx1g
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - es_data:/usr/share/elasticsearch/data

  logstash:
    image: logstash:7.17.0
    ports:
      - "5000:5000"
      - "9600:9600"
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
  es_data:
```

```ruby
# logstash/pipeline/logstash.conf
input {
  gelf {
    port => 12201
  }
}

filter {
  if [log][file][path] {
    mutate {
      add_field => { "filename" => "%{[log][file][path]}" }
    }
  }
  
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} \[%{DATA:service}\] %{LOGLEVEL:level}: %{GREEDYDATA:message}" }
  }
  
  date {
    match => [ "timestamp", "ISO8601" ]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "docker-logs-%{+YYYY.MM.dd}"
  }
  
  stdout {
    codec => rubydebug
  }
}
```

#### 配置应用容器发送日志到 ELK

```bash
# 使用 gelf 驱动发送日志到 Logstash
docker run -d --name web \
  --log-driver gelf \
  --log-opt gelf-address=udp://localhost:12201 \
  nginx
```

### 诊断工具

#### Docker 原生诊断工具

```bash
# 查看 Docker 系统信息
docker system info

# 查看磁盘使用情况
docker system df

# 查看详细磁盘使用情况
docker system df -v

# 查看 Docker 事件
docker events

# 查看特定时间范围的事件
docker events --since "1h"

# 查看特定容器的事件
docker events --filter container=myapp
```

#### 使用 ctop 工具

```bash
# 安装 ctop
sudo wget https://github.com/bcicen/ctop/releases/download/v0.7.7/ctop-0.7.7-linux-amd64 -O /usr/local/bin/ctop
sudo chmod +x /usr/local/bin/ctop

# 运行 ctop
ctop

# 使用特定 Docker 主机
ctop -H tcp://remote-host:2375

# 只显示运行中的容器
ctop -a
```

#### 使用 dive 分析镜像

```bash
# 安装 dive
wget https://github.com/wagoodman/dive/releases/download/v0.10.0/dive_0.10.0_linux_amd64.deb
sudo apt install ./dive_0.10.0_linux_amd64.deb

# 分析镜像
dive myapp:latest

# 批量分析镜像
dive myapp:v1.0 myapp:v1.1 myapp:v1.2
```

### 性能诊断工具

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

#### 使用 sysdig

```bash
# 安装 sysdig
curl -s https://s3.amazonaws.com/download.draios.com/stable/install-sysdig | sudo bash

# 监控容器系统调用
sudo sysdig -pc container.name=web

# 查看容器网络活动
sudo sysdig -pc -c topprocs_net container.name=web

# 查看容器文件 I/O
sudo sysdig -pc -c topfiles_bytes container.name=web
```

### 自定义诊断脚本

#### 容器健康检查脚本

```bash
#!/bin/bash
# health-checker.sh

# 容器健康检查脚本
CONTAINERS=("web" "db" "redis")
THRESHOLD_CPU=80
THRESHOLD_MEM=80

echo "=== 容器健康检查报告 $(date) ==="

for container in "${CONTAINERS[@]}"; do
    echo "--- 容器: $container ---"
    
    # 检查容器是否运行
    if ! docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
        echo "❌ 容器未运行"
        continue
    fi
    
    # 获取资源使用情况
    cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" $container | sed 's/%//')
    mem_usage=$(docker stats --no-stream --format "{{.MemPerc}}" $container | sed 's/%//')
    
    echo "CPU 使用率: ${cpu_usage}%"
    echo "内存使用率: ${mem_usage}%"
    
    # 检查 CPU 使用率
    if (( $(echo "$cpu_usage > $THRESHOLD_CPU" | bc -l) )); then
        echo "⚠️  警告: CPU 使用率过高"
    fi
    
    # 检查内存使用率
    if (( $(echo "$mem_usage > $THRESHOLD_MEM" | bc -l) )); then
        echo "⚠️  警告: 内存使用率过高"
    fi
    
    # 检查应用健康端点
    if docker exec $container curl -f http://localhost:80/health > /dev/null 2>&1; then
        echo "✅ 应用健康检查通过"
    else
        echo "❌ 应用健康检查失败"
    fi
    
    echo ""
done
```

#### 系统资源监控脚本

```bash
#!/bin/bash
# system-monitor.sh

# 系统资源监控脚本
echo "=== Docker 系统监控报告 $(date) ==="

# Docker 系统信息
echo "--- Docker 系统信息 ---"
docker info | grep -E "Server Version|Storage Driver|Logging Driver|Kernel Version"

# 磁盘使用情况
echo ""
echo "--- 磁盘使用情况 ---"
docker system df

# 运行中的容器
echo ""
echo "--- 运行中的容器 ---"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# 资源使用情况
echo ""
echo "--- 资源使用情况 ---"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemPerc}}\t{{.NetIO}}"

# 最近的事件
echo ""
echo "--- 最近的事件 ---"
docker events --since "1h" --until "0s" | tail -10
```

#### 网络诊断脚本

```bash
#!/bin/bash
# network-diagnostic.sh

# 网络诊断脚本
CONTAINER_NAME="$1"

if [ -z "$CONTAINER_NAME" ]; then
    echo "用法: $0 <container_name>"
    exit 1
fi

echo "=== 网络诊断报告: $CONTAINER_NAME ==="
echo "时间: $(date)"
echo ""

# 检查容器网络配置
echo "--- 容器网络配置 ---"
docker inspect $CONTAINER_NAME | jq '.[0].NetworkSettings'

# 获取容器 IP
CONTAINER_IP=$(docker inspect $CONTAINER_NAME | jq -r '.[0].NetworkSettings.IPAddress')
echo "容器 IP: $CONTAINER_IP"

# 测试网络连通性
echo ""
echo "--- 网络连通性测试 ---"
docker exec $CONTAINER_NAME ping -c 4 127.0.0.1
docker exec $CONTAINER_NAME ping -c 4 $CONTAINER_IP

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
echo "--- 网络接口信息 ---"
docker exec $CONTAINER_NAME ip addr

# 查看路由表
echo ""
echo "--- 路由表 ---"
docker exec $CONTAINER_NAME ip route

# 查看端口监听
echo ""
echo "--- 端口监听情况 ---"
docker exec $CONTAINER_NAME ss -tulpn
```

### 日志分析工具

#### 使用 Logstash 进行日志分析

```bash
# 安装 Logstash
curl -L -O https://artifacts.elastic.co/downloads/logstash/logstash-7.17.0-linux-x86_64.tar.gz
tar -xzf logstash-7.17.0-linux-x86_64.tar.gz

# 创建日志分析配置
cat > log-analysis.conf << EOF
input {
  file {
    path => "/var/lib/docker/containers/*/*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => "json"
  }
}

filter {
  # 解析 Docker 日志
  json {
    source => "message"
    target => "docker"
  }
  
  # 添加时间戳
  date {
    match => [ "docker.time", "ISO8601" ]
  }
  
  # 解析应用日志
  grok {
    match => { "docker.log" => "%{TIMESTAMP_ISO8601:timestamp} \[%{DATA:service}\] %{LOGLEVEL:level}: %{GREEDYDATA:message}" }
  }
}

output {
  # 输出到 Elasticsearch
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "app-logs-%{+YYYY.MM.dd}"
  }
  
  # 输出到标准输出
  stdout {
    codec => rubydebug
  }
}
EOF

# 运行 Logstash
./bin/logstash -f log-analysis.conf
```

#### 使用 Fluentd 进行日志收集

```bash
# 创建 Fluentd 配置
cat > fluentd.conf << EOF
<source>
  @type forward
  port 24224
  bind 0.0.0.0
</source>

<source>
  @type http
  port 9880
  bind 0.0.0.0
</source>

<filter docker.**>
  @type parser
  key_name log
  reserve_data true
  <parse>
    @type json
  </parse>
</filter>

<match docker.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  logstash_format true
  logstash_prefix docker
  logstash_dateformat %Y%m%d
  include_tag_key true
  type_name access_log
  tag_key @log_name
  flush_interval 1s
</match>
EOF

# 运行 Fluentd
fluentd -c fluentd.conf
```

### 监控和告警

#### 基于日志的告警

```bash
#!/bin/bash
# log-alert.sh

# 基于日志的告警脚本
LOG_FILE="/var/log/docker-alerts.log"
ALERT_KEYWORDS=("ERROR" "FATAL" "CRITICAL" "exception")

# 监控日志文件
tail -f /var/lib/docker/containers/*/*.log | while read line; do
    for keyword in "${ALERT_KEYWORDS[@]}"; do
        if echo "$line" | grep -q "$keyword"; then
            echo "$(date): 告警 - 发现关键词 '$keyword'" | tee -a $LOG_FILE
            # 发送告警通知
            # curl -X POST -H 'Content-type: application/json' \
            #   --data "{\"text\":\"告警: $line\"}" \
            #   $SLACK_WEBHOOK_URL
        fi
    done
done
```

#### 性能告警脚本

```bash
#!/bin/bash
# performance-alert.sh

# 性能告警脚本
ALERT_THRESHOLD_CPU=85
ALERT_THRESHOLD_MEM=85

send_alert() {
    local message="$1"
    echo "🚨 告警: $message" | tee -a /var/log/performance-alerts.log
    
    # 发送邮件告警
    # echo "$message" | mail -s "性能告警" admin@example.com
}

# 检查所有容器
docker stats --no-stream --format "table {{.Container}}\t{{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}" | \
while read line; do
    container=$(echo $line | awk '{print $1}')
    name=$(echo $line | awk '{print $2}')
    cpu=$(echo $line | awk '{print $3}' | sed 's/%//')
    mem=$(echo $line | awk '{print $4}' | sed 's/%//')
    
    # 跳过标题行
    if [[ "$container" == "CONTAINER" ]]; then
        continue
    fi
    
    # 检查 CPU 使用率
    if (( $(echo "$cpu > $ALERT_THRESHOLD_CPU" | bc -l) )); then
        send_alert "容器 $name (ID: $container) CPU 使用率过高: ${cpu}%"
    fi
    
    # 检查内存使用率
    if (( $(echo "$mem > $ALERT_THRESHOLD_MEM" | bc -l) )); then
        send_alert "容器 $name (ID: $container) 内存使用率过高: ${mem}%"
    fi
done
```

### 日志和诊断最佳实践

#### 日志管理最佳实践

1. **结构化日志**：
   - 使用 JSON 格式记录日志
   - 包含时间戳、级别、服务名等元数据

2. **日志级别管理**：
   - 合理使用不同的日志级别
   - 生产环境避免过多调试日志

3. **日志轮转策略**：
   - 配置适当的日志大小限制
   - 设置合理的保留文件数量

#### 诊断工具使用建议

1. **工具选择**：
   - 根据需求选择合适的工具
   - 结合多种工具进行全面诊断

2. **自动化监控**：
   - 设置自动化的监控和告警
   - 定期生成诊断报告

3. **性能优化**：
   - 定期分析日志和性能数据
   - 根据分析结果优化系统配置

通过本节内容，我们深入了解了 Docker 的日志与诊断工具使用方法，包括日志管理、诊断工具、性能监控、自定义脚本等方面。掌握这些工具和技巧将帮助您更好地监控和维护容器化应用，确保系统的稳定性和可靠性。