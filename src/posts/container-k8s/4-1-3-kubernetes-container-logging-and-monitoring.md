---
title: Kubernetes容器日志与监控：实现全面的可观测性
date: 2025-08-31
categories: [Kubernetes]
tags: [kubernetes, logging, monitoring, prometheus, grafana, efk]
published: true
---

在云原生环境中，可观测性是确保应用稳定运行和快速故障排查的关键。Kubernetes通过日志、指标和追踪三大支柱提供了全面的可观测性解决方案。本章将深入探讨Kubernetes容器日志管理、监控系统架构、Prometheus与Grafana集成以及集群状态监控与告警配置，帮助读者构建完整的可观测性体系。

## 容器日志管理（Fluentd、ElasticSearch、Kibana）

### Kubernetes 日志架构

Kubernetes日志管理通常采用以下架构：

1. **日志收集**：使用DaemonSet在每个节点上部署日志收集器
2. **日志传输**：将收集的日志传输到中央存储系统
3. **日志存储**：使用高性能存储系统保存日志数据
4. **日志分析**：提供日志查询和分析界面

### Fluentd 部署与配置

Fluentd是一个开源的数据收集器，广泛用于Kubernetes日志收集。

#### 部署 Fluentd DaemonSet

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: kube-logging
  labels:
    k8s-app: fluentd-logging
    version: v1
spec:
  selector:
    matchLabels:
      k8s-app: fluentd-logging
      version: v1
  template:
    metadata:
      labels:
        k8s-app: fluentd-logging
        version: v1
    spec:
      serviceAccount: fluentd
      serviceAccountName: fluentd
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1.14.6-debian-elasticsearch7-1.0
        env:
          - name: FLUENT_ELASTICSEARCH_HOST
            value: "elasticsearch"
          - name: FLUENT_ELASTICSEARCH_PORT
            value: "9200"
          - name: FLUENT_ELASTICSEARCH_SCHEME
            value: "http"
          - name: FLUENT_UID
            value: "0"
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      terminationGracePeriodSeconds: 30
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

#### Fluentd 配置文件

```xml
<source>
  @type tail
  path /var/log/containers/*.log
  pos_file /var/log/fluentd-containers.log.pos
  tag kubernetes.*
  read_from_head true
  <parse>
    @type json
    time_format %Y-%m-%dT%H:%M:%S.%NZ
  </parse>
</source>

<filter kubernetes.**>
  @type kubernetes_metadata
</filter>

<match kubernetes.**>
  @type elasticsearch
  host "#{ENV['FLUENT_ELASTICSEARCH_HOST']}"
  port "#{ENV['FLUENT_ELASTICSEARCH_PORT']}"
  scheme "#{ENV['FLUENT_ELASTICSEARCH_SCHEME'] || 'http'}"
  logstash_format true
</match>
```

### ElasticSearch 部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elasticsearch
  namespace: kube-logging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
        env:
        - name: discovery.type
          value: single-node
        ports:
        - containerPort: 9200
          name: http
        - containerPort: 9300
          name: transport
        volumeMounts:
        - name: elasticsearch-storage
          mountPath: /usr/share/elasticsearch/data
      volumes:
      - name: elasticsearch-storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch
  namespace: kube-logging
spec:
  selector:
    app: elasticsearch
  ports:
  - port: 9200
    name: http
  - port: 9300
    name: transport
```

### Kibana 部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kibana
  namespace: kube-logging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kibana
  template:
    metadata:
      labels:
        app: kibana
    spec:
      containers:
      - name: kibana
        image: docker.elastic.co/kibana/kibana:7.17.0
        env:
        - name: ELASTICSEARCH_HOSTS
          value: '["http://elasticsearch:9200"]'
        ports:
        - containerPort: 5601
          name: http
---
apiVersion: v1
kind: Service
metadata:
  name: kibana
  namespace: kube-logging
spec:
  selector:
    app: kibana
  ports:
  - port: 5601
    name: http
```

### 日志管理最佳实践

1. **结构化日志**：使用JSON格式输出日志
2. **日志级别**：合理使用不同的日志级别
3. **日志轮转**：配置日志轮转避免磁盘占满
4. **敏感信息过滤**：过滤日志中的敏感信息
5. **保留策略**：制定日志保留和清理策略

## Prometheus 与 Grafana 监控

### Prometheus 架构

Prometheus是一个开源的系统监控和告警工具包，采用拉取模式收集指标。

#### 核心组件

1. **Prometheus Server**：负责指标收集、存储和查询
2. **Client Libraries**：应用端集成的指标库
3. **Push Gateway**：用于短期任务的指标推送
4. **Exporter**：第三方系统指标导出器
5. **Alertmanager**：处理告警通知

### 部署 Prometheus Operator

```bash
# 添加Prometheus Operator Helm仓库
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# 安装Prometheus Operator
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### Prometheus 配置

#### ServiceMonitor 配置

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: example-app
  namespace: default
spec:
  selector:
    matchLabels:
      app: example-app
  endpoints:
  - port: web
    interval: 30s
```

#### PrometheusRule 配置

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: example-rules
  namespace: default
spec:
  groups:
  - name: example.rules
    rules:
    - alert: HighRequestLatency
      expr: job:request_latency_seconds:mean5m{job="myjob"} > 0.5
      for: 10m
      labels:
        severity: page
      annotations:
        summary: High request latency
```

### Grafana 配置

#### 创建 Grafana Dashboard

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  kubernetes-dashboard.json: |-
    {
      "dashboard": {
        "id": null,
        "title": "Kubernetes Cluster Metrics",
        "panels": [
          {
            "title": "CPU Usage",
            "type": "graph",
            "targets": [
              {
                "expr": "sum(rate(container_cpu_usage_seconds_total[5m])) by (pod)",
                "legendFormat": "{{pod}}"
              }
            ]
          }
        ]
      }
    }
```

#### 配置数据源

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: grafana-datasources
  namespace: monitoring
stringData:
  datasources.yaml: |
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      url: http://prometheus-kube-prometheus-prometheus:9090
      access: proxy
      isDefault: true
```

## 集群状态监控与告警配置

### 核心指标监控

#### 节点指标

```yaml
# 节点CPU使用率
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 节点内存使用率
100 * (1 - ((avg_over_time(node_memory_MemFree_bytes[5m]) + avg_over_time(node_memory_Cached_bytes[5m]) + avg_over_time(node_memory_Buffers_bytes[5m])) / avg_over_time(node_memory_MemTotal_bytes[5m])))

# 节点磁盘使用率
100 - ((node_filesystem_avail_bytes{mountpoint="/",fstype!="rootfs"} * 100) / node_filesystem_size_bytes{mountpoint="/",fstype!="rootfs"})
```

#### Pod指标

```yaml
# Pod重启次数
rate(kube_pod_container_status_restarts_total[5m]) > 0

# Pod CPU使用率
sum(rate(container_cpu_usage_seconds_total[5m])) by (pod, namespace)

# Pod内存使用率
sum(container_memory_usage_bytes) by (pod, namespace)
```

#### 应用指标

```yaml
# HTTP请求延迟
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# HTTP错误率
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

### 告警规则配置

#### 节点告警

```yaml
groups:
- name: node-alerts
  rules:
  - alert: NodeDown
    expr: up{job="node-exporter"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Node {{ $labels.instance }} is down"
      description: "{{ $labels.instance }} has been down for more than 5 minutes."

  - alert: NodeCPUHigh
    expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage on {{ $labels.instance }}"
      description: "{{ $labels.instance }} CPU usage is above 80% for more than 5 minutes."
```

#### Pod告警

```yaml
- name: pod-alerts
  rules:
  - alert: PodRestarting
    expr: rate(kube_pod_container_status_restarts_total[5m]) > 0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Pod {{ $labels.pod }} is restarting"
      description: "{{ $labels.pod }} in namespace {{ $labels.namespace }} has been restarting."

  - alert: PodHighMemory
    expr: sum(container_memory_usage_bytes{container!="",container!="POD"}) by (pod, namespace) > 1024*1024*1024
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.pod }}"
      description: "{{ $labels.pod }} in namespace {{ $labels.namespace }} is using more than 1GB of memory."
```

### Alertmanager 配置

```yaml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'localhost:25'
  smtp_from: 'alertmanager@example.org'
  smtp_require_tls: false

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'webhook'

receivers:
- name: 'webhook'
  webhook_configs:
  - url: 'http://localhost:5001/'
```

## Kubernetes 内建监控与日志收集

### Metrics Server

Metrics Server是Kubernetes内建的资源指标聚合器。

#### 部署 Metrics Server

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

#### 使用 kubectl top 命令

```bash
# 查看节点资源使用情况
kubectl top nodes

# 查看Pod资源使用情况
kubectl top pods
```

### Kubernetes Dashboard

Kubernetes Dashboard提供了一个Web界面来管理集群。

#### 部署 Dashboard

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
```

#### 创建管理员用户

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
```

### 自定义指标监控

#### 部署 Prometheus Adapter

```bash
helm install prometheus-adapter prometheus-community/prometheus-adapter \
  --namespace monitoring \
  --set prometheus.url=http://prometheus-kube-prometheus-prometheus.monitoring.svc \
  --set prometheus.port=9090
```

#### 配置自定义指标

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: custom-metrics-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: example-app
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: 100
```

### 监控最佳实践

1. **分层监控**：从基础设施到应用的分层监控
2. **关键指标**：关注关键业务指标而非技术指标
3. **告警分级**：根据严重程度分级告警
4. **告警抑制**：避免告警风暴
5. **定期审查**：定期审查和优化监控配置

通过本章的学习，读者应该能够深入理解Kubernetes日志和监控的重要性，掌握EFK（ElasticSearch、Fluentd、Kibana）日志解决方案的部署和配置，熟练使用Prometheus和Grafana进行监控，配置集群状态监控和告警规则，并了解Kubernetes内建的监控和日志收集机制。这些知识对于构建全面的可观测性体系至关重要。