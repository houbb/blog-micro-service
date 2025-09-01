---
title: Performance Monitoring and Diagnostic Tools - Mastering Container Observability
date: 2025-08-31
categories: [Write]
tags: [docker, monitoring, diagnostics, observability, containers]
published: true
---

## 性能监控与故障诊断工具

### 监控工具概述

有效的性能监控是确保容器化应用稳定运行的关键。通过使用专业的监控工具，可以实时了解容器的资源使用情况、应用性能指标和系统健康状态，及时发现并解决潜在问题。

#### 监控维度

1. **基础设施监控**：
   - CPU、内存、磁盘、网络使用情况
   - 容器和主机资源使用统计

2. **应用性能监控**：
   - 应用响应时间、吞吐量
   - 错误率、可用性指标

3. **日志监控**：
   - 应用日志收集和分析
   - 错误日志实时告警

### Docker 原生监控工具

#### docker stats 命令

```bash
# 查看所有容器的资源使用情况
docker stats

# 查看特定容器的资源使用
docker stats myapp

# 格式化输出
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# 实时监控特定容器
docker stats --no-stream myapp

# 批量监控多个容器
docker stats container1 container2 container3
```

#### docker system 命令

```bash
# 查看 Docker 系统信息
docker system info

# 查看磁盘使用情况
docker system df

# 查看详细磁盘使用情况
docker system df -v

# 清理未使用的资源
docker system prune

# 清理所有未使用的资源（包括镜像）
docker system prune -a
```

#### docker events 命令

```bash
# 实时查看 Docker 事件
docker events

# 查看特定时间范围的事件
docker events --since "1h"

# 查看特定容器的事件
docker events --filter container=myapp

# 查看特定事件类型
docker events --filter type=container --filter event=start
```

### 第三方监控工具

#### ctop - 容器监控仪表板

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

#### Prometheus + Grafana 监控栈

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.37.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana-enterprise
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.45.0
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro

volumes:
  prometheus_data:
  grafana_data:
```

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

#### ELK 栈日志监控

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
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "docker-logs-%{+YYYY.MM.dd}"
  }
}
```

### 应用性能监控 (APM)

#### 使用 Datadog

```bash
# 运行 Datadog Agent
docker run -d \
  --name datadog-agent \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /proc/:/host/proc/:ro \
  -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
  -e DD_API_KEY=<YOUR_API_KEY> \
  -e DD_SITE=datadoghq.com \
  -e DD_TAGS="env:production,service:myapp" \
  gcr.io/datadoghq/agent:7

# 为应用容器添加标签
docker run -d \
  --name myapp \
  -l com.datadoghq.ad.check_names='["nginx"]' \
  -l com.datadoghq.ad.init_configs='[{}]' \
  -l com.datadoghq.ad.instances='[{"nginx_status_url": "http://%%host%%/nginx_status"}]' \
  nginx:latest
```

#### 使用 New Relic

```bash
# 运行 New Relic Infrastructure Agent
docker run -d \
  --name newrelic-infra \
  --privileged \
  --pid=host \
  --net=host \
  -v /:/host:ro \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e NRIA_LICENSE_KEY=<YOUR_LICENSE_KEY> \
  -e NRIA_DISPLAY_NAME=MyDockerHost \
  newrelic/infrastructure:latest

# 为应用容器添加监控
docker run -d \
  --name myapp \
  -e NEW_RELIC_LICENSE_KEY=<YOUR_LICENSE_KEY> \
  -e NEW_RELIC_APP_NAME=MyApp \
  myapp:latest
```

### 故障诊断工具

#### 进程诊断工具

```bash
# 查看容器内进程
docker exec myapp ps aux

# 查看容器内进程树
docker exec myapp pstree

# 查看容器内 top 信息
docker exec myapp top

# 实时查看容器内进程
docker exec myapp htop

# 查看容器内进程资源使用
docker exec myapp atop
```

#### 网络诊断工具

```bash
# 查看容器网络配置
docker exec myapp ip addr

# 查看容器网络连接
docker exec myapp netstat -tulpn

# 查看容器网络统计
docker exec myapp ss -tulpn

# 使用 tcpdump 抓包
docker exec myapp tcpdump -i any port 80

# 使用 ping 测试网络连通性
docker exec myapp ping google.com

# 使用 curl 测试 HTTP 连接
docker exec myapp curl -v http://service:8080
```

#### 文件系统诊断工具

```bash
# 查看容器文件系统使用情况
docker exec myapp df -h

# 查看容器目录大小
docker exec myapp du -sh /app

# 查看容器文件系统挂载点
docker exec myapp mount

# 查看容器 inode 使用情况
docker exec myapp df -i

# 查看容器文件系统性能
docker exec myapp iostat -x 1 5
```

#### 内存诊断工具

```bash
# 查看容器内存使用情况
docker exec myapp free -m

# 查看容器内存详细信息
docker exec myapp cat /proc/meminfo

# 查看容器进程内存使用
docker exec myapp ps aux --sort=-%mem

# 查看容器内存映射
docker exec myapp pmap -x <PID>

# 查看容器内存泄漏
docker exec myapp valgrind --leak-check=full --show-leak-kinds=all <program>
```

### 自定义监控脚本

#### 资源监控脚本

```bash
#!/bin/bash
# container-monitor.sh

# 容器监控脚本
CONTAINERS=("web" "db" "cache")
THRESHOLD_CPU=80
THRESHOLD_MEM=80

echo "=== 容器资源监控报告 $(date) ==="

for container in "${CONTAINERS[@]}"; do
    echo "--- 容器: $container ---"
    
    # 获取 CPU 和内存使用率
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
    
    echo ""
done
```

#### 健康检查脚本

```bash
#!/bin/bash
# health-check.sh

# 应用健康检查脚本
CONTAINER_NAME="myapp"
HEALTH_ENDPOINT="http://localhost:3000/health"

echo "=== 应用健康检查 $(date) ==="

# 检查容器是否运行
if ! docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ 容器 $CONTAINER_NAME 未运行"
    exit 1
fi

echo "✅ 容器 $CONTAINER_NAME 正在运行"

# 检查应用健康端点
if docker exec $CONTAINER_NAME curl -f $HEALTH_ENDPOINT > /dev/null 2>&1; then
    echo "✅ 应用健康检查通过"
else
    echo "❌ 应用健康检查失败"
    # 查看应用日志
    echo "=== 最近日志 ==="
    docker logs --tail 20 $CONTAINER_NAME
    exit 1
fi

# 检查资源使用
cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" $CONTAINER_NAME | sed 's/%//')
mem_usage=$(docker stats --no-stream --format "{{.MemPerc}}" $CONTAINER_NAME | sed 's/%//')

echo "📊 CPU 使用率: ${cpu_usage}%"
echo "📊 内存使用率: ${mem_usage}%"

if (( $(echo "$cpu_usage > 90" | bc -l) )); then
    echo "⚠️  CPU 使用率过高: ${cpu_usage}%"
fi

if (( $(echo "$mem_usage > 90" | bc -l) )); then
    echo "⚠️  内存使用率过高: ${mem_usage}%"
fi
```

#### 性能分析脚本

```bash
#!/bin/bash
# performance-analyzer.sh

# 性能分析脚本
CONTAINER_NAME="myapp"

echo "=== 性能分析报告 $(date) ==="

# CPU 性能分析
echo "--- CPU 分析 ---"
docker exec $CONTAINER_NAME top -b -n 1 | head -20

# 内存性能分析
echo "--- 内存分析 ---"
docker exec $CONTAINER_NAME ps aux --sort=-%mem | head -10

# 网络性能分析
echo "--- 网络分析 ---"
docker exec $CONTAINER_NAME netstat -i

# 磁盘 I/O 分析
echo "--- 磁盘 I/O 分析 ---"
docker exec $CONTAINER_NAME iostat -x 1 3

# 文件系统使用情况
echo "--- 文件系统使用情况 ---"
docker exec $CONTAINER_NAME df -h

# 进程分析
echo "--- 进程分析 ---"
docker exec $CONTAINER_NAME pstree
```

### 监控告警配置

#### 基于脚本的告警

```bash
#!/bin/bash
# alert-manager.sh

# 告警管理脚本
ALERT_THRESHOLD_CPU=85
ALERT_THRESHOLD_MEM=85
ALERT_THRESHOLD_DISK=90

send_alert() {
    local message="$1"
    echo "🚨 告警: $message" | tee -a /var/log/container-alerts.log
    
    # 发送邮件告警
    # echo "$message" | mail -s "容器告警" admin@example.com
    
    # 发送 Slack 告警
    # curl -X POST -H 'Content-type: application/json' \
    #   --data "{\"text\":\"🚨 $message\"}" \
    #   $SLACK_WEBHOOK_URL
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

#### 使用 Watchtower 自动更新监控

```yaml
# docker-compose.watchtower.yml
version: '3.8'

services:
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=3600
      - WATCHTOWER_NOTIFICATIONS=slack
      - WATCHTOWER_NOTIFICATION_SLACK_HOOK_URL=${SLACK_WEBHOOK_URL}
      - WATCHTOWER_NOTIFICATION_SLACK_IDENTIFIER=watchtower
    command: --interval 3600 --cleanup
```

### 监控最佳实践

#### 监控策略制定

1. **关键指标监控**：
   - CPU、内存、磁盘、网络使用率
   - 应用响应时间、错误率
   - 容器重启次数

2. **告警阈值设置**：
   - 合理设置告警阈值，避免误报
   - 设置多级告警（警告、严重、紧急）
   - 考虑业务高峰期和低谷期

3. **监控数据保留**：
   - 短期数据高频率保留
   - 长期数据低频率采样
   - 定期清理过期数据

#### 监控仪表板设计

```json
{
  "dashboard": {
    "title": "容器监控仪表板",
    "panels": [
      {
        "title": "CPU 使用率",
        "type": "graph",
        "targets": [
          "rate(container_cpu_usage_seconds_total[1m])"
        ]
      },
      {
        "title": "内存使用率",
        "type": "graph",
        "targets": [
          "container_memory_usage_bytes"
        ]
      },
      {
        "title": "网络流量",
        "type": "graph",
        "targets": [
          "rate(container_network_receive_bytes_total[1m])",
          "rate(container_network_transmit_bytes_total[1m])"
        ]
      }
    ]
  }
}
```

通过本节内容，我们深入了解了 Docker 性能监控与故障诊断工具的使用方法，包括原生工具、第三方监控解决方案、APM 工具、诊断工具以及自定义监控脚本等。掌握这些工具和技巧将帮助您更好地监控和诊断容器化应用的性能问题。