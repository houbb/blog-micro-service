---
title: Prometheus与Alertmanager实战：构建生产级告警系统
date: 2025-08-31
categories: [Microservices, Alerting, Prometheus]
tags: [log-monitor]
published: true
---

Prometheus作为云原生监控的事实标准，提供了强大的指标收集和告警功能。Alertmanager作为Prometheus的告警管理组件，负责处理、分组、路由和静默告警通知。本文将深入探讨如何在生产环境中配置和使用Prometheus与Alertmanager，构建高可用、可扩展的告警系统。

## Prometheus告警配置

### 1. 告警规则配置

Prometheus通过告警规则文件定义告警条件和触发逻辑：

```yaml
# alert-rules.yml
groups:
- name: example-alerts
  rules:
  # 服务可用性告警
  - alert: ServiceDown
    expr: up == 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "服务 {{ $labels.job }} 不可用"
      description: "服务 {{ $labels.job }} 实例 {{ $labels.instance }} 已经不可用超过2分钟"
      runbook_url: "https://internal.wiki/runbooks/service-down"

  # 高CPU使用率告警
  - alert: HighCPUUsage
    expr: rate(node_cpu_seconds_total{mode!="idle"}[2m]) > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "主机 {{ $labels.instance }} CPU使用率过高"
      description: "主机 {{ $labels.instance }} 的CPU使用率持续5分钟超过80%"
      value: "{{ $value }}"

  # 高内存使用率告警
  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.85
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "主机 {{ $labels.instance }} 内存使用率过高"
      description: "主机 {{ $labels.instance }} 的内存使用率持续10分钟超过85%"
      value: "{{ $value }}"

  # 高磁盘使用率告警
  - alert: HighDiskUsage
    expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes > 0.9
    for: 15m
    labels:
      severity: critical
    annotations:
      summary: "主机 {{ $labels.instance }} 磁盘使用率过高"
      description: "主机 {{ $labels.instance }} 挂载点 {{ $labels.mountpoint }} 的磁盘使用率持续15分钟超过90%"
      value: "{{ $value }}"

  # HTTP错误率告警
  - alert: HighHttpErrorRate
    expr: rate(http_requests_total{code=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "服务 {{ $labels.job }} HTTP错误率过高"
      description: "服务 {{ $labels.job }} 的5xx错误率持续2分钟超过5%"
      value: "{{ $value }}"
```

### 2. Prometheus配置文件

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert-rules.yml"
  - "business-rules.yml"
  - "kubernetes-rules.yml"

alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093
    scheme: http
    timeout: 10s

scrape_configs:
  # Prometheus自身监控
  - job_name: 'prometheus'
    static_configs:
    - targets: ['localhost:9090']

  # Node Exporter监控
  - job_name: 'node-exporter'
    static_configs:
    - targets: ['node-exporter:9100']

  # Kubernetes服务发现
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\d+)?;(\d+)
      replacement: $1:$2
      target_label: __address__
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
```

## Alertmanager配置详解

### 1. 基础配置

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alertmanager@example.com'
  smtp_auth_username: 'alertmanager'
  smtp_auth_password: 'password'
  smtp_require_tls: true

# 模板配置
templates:
  - '/etc/alertmanager/template/*.tmpl'

# 路由配置
route:
  group_by: ['alertname', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 3h
  receiver: 'default-receiver'
  
  routes:
    # Critical告警路由
    - match:
        severity: critical
      group_wait: 0s
      receiver: 'critical-receiver'
      routes:
        - match:
            service: payment-service
          receiver: 'payment-critical-receiver'
    
    # Warning告警路由
    - match:
        severity: warning
      receiver: 'warning-receiver'
    
    # Info告警路由
    - match:
        severity: info
      receiver: 'info-receiver'

# 抑制规则
inhibit_rules:
  # 当服务完全不可用时，抑制相关的性能告警
  - source_match:
      alertname: ServiceDown
      severity: critical
    target_match:
      severity: warning
    equal: ['service', 'namespace']

  # 当主机宕机时，抑制相关的服务告警
  - source_match:
      alertname: HostDown
      severity: critical
    target_match:
      alertname: ServiceDown
    equal: ['instance']

# 静默时间间隔
mute_time_intervals:
  - name: 'business_hours'
    time_intervals:
      - weekdays: ['monday:friday']
        times:
          - start_time: '09:00'
            end_time: '18:00'

  - name: 'outside_business_hours'
    time_intervals:
      - weekdays: ['monday:friday']
        times:
          - start_time: '18:00'
            end_time: '09:00'
      - weekdays: ['saturday', 'sunday']
```

### 2. 接收器配置

```yaml
# 接收器配置
receivers:
  # 默认接收器
  - name: 'default-receiver'
    email_configs:
    - to: 'team@example.com'
      send_resolved: true
    slack_configs:
    - api_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
      channel: '#alerts'
      send_resolved: true

  # Critical告警接收器
  - name: 'critical-receiver'
    email_configs:
    - to: 'critical-team@example.com'
      send_resolved: true
    webhook_configs:
    - url: 'http://pagerduty-proxy:8080/pagerduty'
      send_resolved: true
    slack_configs:
    - api_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
      channel: '#critical-alerts'
      send_resolved: true
      title: '[Critical] {{ .CommonLabels.alertname }}'
      text: '{{ .CommonAnnotations.description }}'

  # Payment服务Critical告警接收器
  - name: 'payment-critical-receiver'
    email_configs:
    - to: 'payment-team@example.com'
      send_resolved: true
    webhook_configs:
    - url: 'http://pagerduty-proxy:8080/pagerduty/payment'
      send_resolved: true
    slack_configs:
    - api_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
      channel: '#payment-alerts'
      send_resolved: true
      title: '[Payment Critical] {{ .CommonLabels.alertname }}'
      text: '{{ .CommonAnnotations.description }}'

  # Warning告警接收器
  - name: 'warning-receiver'
    email_configs:
    - to: 'team@example.com'
      send_resolved: true
    slack_configs:
    - api_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
      channel: '#warnings'
      send_resolved: true

  # Info告警接收器
  - name: 'info-receiver'
    email_configs:
    - to: 'team@example.com'
      send_resolved: true
```

## 高级告警规则示例

### 1. 业务相关告警

```yaml
# business-rules.yml
groups:
- name: business-alerts
  rules:
  # 订单处理延迟告警
  - alert: HighOrderProcessingLatency
    expr: histogram_quantile(0.95, rate(order_processing_duration_seconds_bucket[5m])) > 30
    for: 2m
    labels:
      severity: critical
      team: order-team
    annotations:
      summary: "订单处理延迟过高"
      description: "95%的订单处理时间超过30秒，当前值为 {{ $value }} 秒"
      runbook_url: "https://internal.wiki/runbooks/high-order-latency"

  # 支付成功率告警
  - alert: LowPaymentSuccessRate
    expr: rate(payment_success_total[5m]) / rate(payment_total[5m]) < 0.95
    for: 5m
    labels:
      severity: critical
      team: payment-team
    annotations:
      summary: "支付成功率过低"
      description: "支付成功率低于95%，当前值为 {{ $value | printf \"%.2f\" }}"

  # 用户注册量异常告警
  - alert: AbnormalUserRegistration
    expr: abs(rate(user_registrations_total[1h]) - rate(user_registrations_total[24h] offset 1h)) / rate(user_registrations_total[24h] offset 1h) > 0.5
    for: 10m
    labels:
      severity: warning
      team: user-team
    annotations:
      summary: "用户注册量异常"
      description: "用户注册量与昨日同时段相比变化超过50%，当前变化为 {{ $value | printf \"%.2f\" }}"
```

### 2. Kubernetes相关告警

```yaml
# kubernetes-rules.yml
groups:
- name: kubernetes-alerts
  rules:
  # Pod重启告警
  - alert: PodFrequentlyRestarting
    expr: increase(kube_pod_container_status_restarts_total[1h]) > 5
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Pod {{ $labels.pod }} 频繁重启"
      description: "Pod {{ $labels.pod }} 在1小时内重启次数超过5次，当前为 {{ $value }} 次"

  # Deployment副本不足告警
  - alert: DeploymentReplicasMismatch
    expr: kube_deployment_spec_replicas != kube_deployment_status_replicas_available
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Deployment {{ $labels.deployment }} 副本不匹配"
      description: "Deployment {{ $labels.deployment }} 期望副本数 {{ $labels.kube_deployment_spec_replicas }}，实际可用副本数 {{ $labels.kube_deployment_status_replicas_available }}"

  # PVC存储空间不足告警
  - alert: PersistentVolumeUsageHigh
    expr: kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes > 0.85
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "PersistentVolume {{ $labels.persistentvolumeclaim }} 使用率过高"
      description: "PersistentVolume {{ $labels.persistentvolumeclaim }} 使用率超过85%，当前为 {{ $value | printf \"%.2f\" }}"

  # Node不可用告警
  - alert: NodeDown
    expr: up{job="kubernetes-nodes"} == 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Node {{ $labels.instance }} 不可用"
      description: "Node {{ $labels.instance }} 已经不可用超过2分钟"
```

## 告警模板定制

### 1. Slack通知模板

```gotemplate
{{/* Slack通知模板 */}}
{{ define "slack.critical.text" }}
{
  "channel": "{{ .Channel }}",
  "username": "AlertManager",
  "icon_emoji": ":rotating_light:",
  "attachments": [
    {
      "color": "danger",
      "title": "[Critical] {{ .CommonLabels.alertname }}",
      "text": "{{ .CommonAnnotations.description }}",
      "fields": [
        {
          "title": "告警数量",
          "value": "{{ .Alerts | len }}",
          "short": true
        },
        {
          "title": "影响服务",
          "value": "{{ .CommonLabels.service }}",
          "short": true
        },
        {
          "title": "发生时间",
          "value": "{{ .Alerts.Firing | first | .StartsAt }}",
          "short": true
        }
      ],
      "footer": "AlertManager",
      "footer_icon": "https://avatars3.githubusercontent.com/u/3380462",
      "ts": {{ .Alerts.Firing | first | .StartsAt | unixEpoch }}
    }
  ]
}
{{ end }}
```

### 2. 邮件通知模板

```gotemplate
{{/* 邮件通知模板 */}}
{{ define "email.critical.html" }}
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Critical Alert</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .alert { border-left: 5px solid #d9534f; padding: 10px; margin: 10px 0; }
        .critical { background-color: #fdf7f7; }
        .warning { background-color: #fcf8f2; border-left-color: #f0ad4e; }
        .info { background-color: #f4f8fa; border-left-color: #5bc0de; }
    </style>
</head>
<body>
    <h2>Critical Alert: {{ .CommonLabels.alertname }}</h2>
    
    <div class="alert critical">
        <h3>告警详情</h3>
        <p><strong>描述:</strong> {{ .CommonAnnotations.description }}</p>
        <p><strong>影响服务:</strong> {{ .CommonLabels.service }}</p>
        <p><strong>告警数量:</strong> {{ .Alerts | len }}</p>
        <p><strong>发生时间:</strong> {{ .Alerts.Firing | first | .StartsAt }}</p>
        
        {{ if .CommonAnnotations.runbook_url }}
        <p><strong>处理指南:</strong> <a href="{{ .CommonAnnotations.runbook_url }}">点击查看</a></p>
        {{ end }}
    </div>
    
    <h3>告警列表</h3>
    <ul>
    {{ range .Alerts }}
        <li>
            <strong>{{ .Labels.instance }}</strong>: {{ .Annotations.description }}
            (值: {{ .Value | printf "%.2f" }})
        </li>
    {{ end }}
    </ul>
</body>
</html>
{{ end }}
```

## 生产环境最佳实践

### 1. 高可用配置

```yaml
# 高可用Alertmanager配置
alertmanager:
  replicas: 3
  config:
    global:
      resolve_timeout: 5m
    
    route:
      group_by: ['alertname', 'service']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 3h
      receiver: 'default-receiver'
    
    receivers:
    - name: 'default-receiver'
      webhook_configs:
      - url: 'http://alertmanager-cluster:9093/api/v1/alerts'
        send_resolved: true
```

### 2. 告警测试

```bash
# 告警测试脚本
#!/bin/bash

# 发送测试告警
curl -X POST http://alertmanager:9093/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d '[{
    "status": "firing",
    "labels": {
      "alertname": "TestAlert",
      "service": "test-service",
      "severity": "warning"
    },
    "annotations": {
      "summary": "测试告警",
      "description": "这是一个测试告警，用于验证告警系统是否正常工作"
    },
    "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'"
  }]'

echo "测试告警已发送"
```

### 3. 监控告警系统自身

```yaml
# Alertmanager自身监控告警
groups:
- name: alertmanager-self-monitoring
  rules:
  - alert: AlertmanagerConfigNotLoaded
    expr: alertmanager_config_last_reload_successful != 1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Alertmanager配置加载失败"
      description: "Alertmanager配置加载失败，可能影响告警处理"

  - alert: AlertmanagerClusterDown
    expr: alertmanager_cluster_health_score > 0.5
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Alertmanager集群健康状况不佳"
      description: "Alertmanager集群中部分节点不健康"

  - alert: HighAlertmanagerNotificationsFailed
    expr: rate(alertmanager_notifications_failed_total[5m]) > 0
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Alertmanager通知发送失败"
      description: "Alertmanager通知发送失败率过高，可能影响告警通知"
```

## 故障排查与调试

### 1. 常见问题诊断

```bash
# 检查Prometheus告警状态
curl http://prometheus:9090/api/v1/alerts | jq '.'

# 检查Alertmanager告警状态
curl http://alertmanager:9093/api/v1/alerts | jq '.'

# 检查Alertmanager配置状态
curl http://alertmanager:9093/api/v1/status | jq '.'

# 检查Alertmanager静默规则
curl http://alertmanager:9093/api/v1/silences | jq '.'
```

### 2. 日志分析

```bash
# Prometheus告警日志
kubectl logs -n monitoring prometheus-0 -c prometheus | grep "alerting"

# Alertmanager日志
kubectl logs -n monitoring alertmanager-0 | grep "dispatch"

# 通知发送日志
kubectl logs -n monitoring alertmanager-0 | grep "notify"
```

## 总结

通过本文的详细介绍，我们学习了如何使用Prometheus与Alertmanager构建生产级告警系统。关键要点包括：

1. **合理的告警规则设计**：根据业务需求和系统特点设计告警规则
2. **灵活的路由配置**：通过路由规则将不同类型的告警发送给不同的接收器
3. **有效的抑制机制**：避免告警风暴和重复告警
4. **定制化的通知模板**：提供清晰、有用的通知信息
5. **高可用部署**：确保告警系统的稳定性和可靠性

在实际应用中，需要根据具体的业务场景和技术架构，灵活调整配置，并持续优化告警策略以适应业务发展和系统变化。

在下一节中，我们将探讨异常检测与自动化响应机制，学习如何实现更智能的告警和自动化的故障处理。