---
title: 使用Envoy代理进行日志采集：构建高效的服务网格日志体系
date: 2025-08-31
categories: [Microservices, Service Mesh, Envoy, Logging]
tags: [microservices, service-mesh, envoy, logging, log-collection, observability]
published: true
---

Envoy作为Istio服务网格的数据平面核心组件，提供了强大的日志采集能力。通过其灵活的访问日志服务（ALS）和丰富的日志格式配置选项，Envoy能够捕获服务间通信的详细信息，为微服务架构提供全面的可观测性。本章将深入探讨如何配置和优化Envoy代理的日志采集功能。

## Envoy日志架构

### 日志类型概述

Envoy支持多种类型的日志：

```yaml
# Envoy日志类型
envoy_log_types:
  access_logs:
    description: "访问日志"
    purpose: "记录HTTP和TCP请求的详细信息"
    format: "可配置的文本或JSON格式"
    
  application_logs:
    description: "应用日志"
    purpose: "Envoy代理自身的运行日志"
    format: "结构化日志格式"
    
  admin_logs:
    description: "管理日志"
    purpose: "通过管理接口获取的诊断信息"
    format: "JSON格式"
```

### 访问日志服务（ALS）

Envoy通过访问日志服务提供结构化的日志数据：

```yaml
# ALS配置示例
static_resources:
  listeners:
  - name: listener_0
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 15001
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          access_log:
          - name: envoy.access_loggers.http_grpc
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.access_loggers.grpc.v3.HttpGrpcAccessLogConfig
              common_config:
                log_name: "http_access_log"
                grpc_service:
                  envoy_grpc:
                    cluster_name: "access_log_service"
                transport_api_version: V3
```

## 访问日志配置详解

### 日志格式配置

Envoy支持多种日志格式配置：

```yaml
# 文本格式访问日志
access_log:
- name: envoy.access_loggers.file
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/dev/stdout"
    log_format:
      text_format_source:
        inline_string: "[%START_TIME%] \"%REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)% %PROTOCOL%\" %RESPONSE_CODE% %RESPONSE_FLAGS% %BYTES_RECEIVED% %BYTES_SENT% %DURATION% %RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)% \"%REQ(X-FORWARDED-FOR)%\" \"%REQ(USER-AGENT)%\" \"%REQ(X-REQUEST-ID)%\" \"%REQ(:AUTHORITY)%\" \"%UPSTREAM_HOST%\"\n"
```

```yaml
# JSON格式访问日志
access_log:
- name: envoy.access_loggers.file
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/dev/stdout"
    log_format:
      json_format:
        timestamp: "%START_TIME%"
        method: "%REQ(:METHOD)%"
        path: "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%"
        protocol: "%PROTOCOL%"
        response_code: "%RESPONSE_CODE%"
        response_flags: "%RESPONSE_FLAGS%"
        bytes_received: "%BYTES_RECEIVED%"
        bytes_sent: "%BYTES_SENT%"
        duration: "%DURATION%"
        upstream_service_time: "%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%"
        forwarded_for: "%REQ(X-FORWARDED-FOR)%"
        user_agent: "%REQ(USER-AGENT)%"
        request_id: "%REQ(X-REQUEST-ID)%"
        authority: "%REQ(:AUTHORITY)%"
        upstream_host: "%UPSTREAM_HOST%"
```

### 自定义日志字段

通过自定义格式字符串添加特定字段：

```yaml
# 自定义日志字段配置
access_log:
- name: envoy.access_loggers.file
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/dev/stdout"
    log_format:
      text_format_source:
        inline_string: |
          [%START_TIME%] "%REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)% %PROTOCOL%" 
          %RESPONSE_CODE% %RESPONSE_FLAGS% %BYTES_RECEIVED% %BYTES_SENT% %DURATION% 
          "%REQ(X-FORWARDED-FOR)%" "%REQ(USER-AGENT)%" "%REQ(X-REQUEST-ID)%" 
          "%REQ(:AUTHORITY)%" "%UPSTREAM_HOST%" 
          "SERVICE=%REQ(:AUTHORITY)% VERSION=%REQ(X-SERVICE-VERSION)% CLUSTER=%UPSTREAM_CLUSTER%\n"
```

### 条件日志记录

根据特定条件记录日志：

```yaml
# 条件日志记录配置
access_log:
- name: envoy.access_loggers.file
  filter:
    response_flag_filter:
      flags: ["UF","UO","NR"]
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/dev/stdout"

- name: envoy.access_loggers.file
  filter:
    status_code_filter:
      comparison:
        op: GE
        value:
          default_value: 400
          runtime_key: "access_log.status_code"
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/dev/stderr"
```

## Envoy日志字段详解

### 核心字段说明

```text
# Envoy访问日志核心字段
%START_TIME%                    # 请求开始时间
%REQ(:METHOD)%                  # HTTP方法
%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%  # 请求路径
%PROTOCOL%                      # 协议版本
%RESPONSE_CODE%                 # 响应状态码
%RESPONSE_FLAGS%                # 响应标志
%BYTES_RECEIVED%                # 接收字节数
%BYTES_SENT%                    # 发送字节数
%DURATION%                      # 请求处理时间
%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%  # 上游服务时间
%REQ(X-FORWARDED-FOR)%          # 客户端IP
%REQ(USER-AGENT)%               # 用户代理
%REQ(X-REQUEST-ID)%             # 请求ID
%REQ(:AUTHORITY)%               # 主机头
%UPSTREAM_HOST%                 # 上游主机
%UPSTREAM_CLUSTER%              # 上游集群
%UPSTREAM_LOCAL_ADDRESS%        # 上游本地地址
%DOWNSTREAM_LOCAL_ADDRESS%      # 下游本地地址
%DOWNSTREAM_REMOTE_ADDRESS%     # 下游远程地址
%ROUTE_NAME%                    # 路由名称
```

### 扩展字段配置

```yaml
# 扩展字段配置
access_log:
- name: envoy.access_loggers.file
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/dev/stdout"
    log_format:
      text_format_source:
        inline_string: |
          [%START_TIME%] "%REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)% %PROTOCOL%" 
          %RESPONSE_CODE% %RESPONSE_FLAGS% %BYTES_RECEIVED% %BYTES_SENT% %DURATION% 
          "TLS=%TLS_PRESENT% TLS_VERSION=%TLS_VERSION% TLS_CIPHER=%TLS_CIPHER%" 
          "CONNECTION_TERMINATION_DETAILS=%CONNECTION_TERMINATION_DETAILS%"\n
```

## 日志收集优化

### 性能优化配置

```yaml
# 性能优化配置
access_log:
- name: envoy.access_loggers.file
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/dev/stdout"
    # 缓冲配置
    buffered:
      flush_interval: 1s
      buffer_size_bytes: 16384
    # 异步写入
    async:
      enabled: true
      queue_size: 1000
    log_format:
      text_format_source:
        inline_string: "[%START_TIME%] \"%REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)% %PROTOCOL%\" %RESPONSE_CODE% %DURATION% %BYTES_SENT%\n"
```

### 采样配置

```yaml
# 日志采样配置
access_log:
- name: envoy.access_loggers.file
  filter:
    extension_filter:
      name: envoy.access_loggers.extension_filters.sample
      typed_config:
        "@type": type.googleapis.com/envoy.extensions.access_loggers.extension_filters.sample.v3.Sample
        sampling_rate: 0.1  # 10%采样率
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/dev/stdout"
```

### 分级日志配置

```yaml
# 分级日志配置
access_log:
# 错误日志（详细信息）
- name: envoy.access_loggers.file
  filter:
    status_code_filter:
      comparison:
        op: GE
        value:
          default_value: 500
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/dev/stderr"
    log_format:
      json_format:
        level: "ERROR"
        timestamp: "%START_TIME%"
        method: "%REQ(:METHOD)%"
        path: "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%"
        response_code: "%RESPONSE_CODE%"
        duration: "%DURATION%"
        error_details: "%RESPONSE_FLAGS%"

# 警告日志
- name: envoy.access_loggers.file
  filter:
    and_filter:
      filters:
      - status_code_filter:
          comparison:
            op: GE
            value:
              default_value: 400
      - status_code_filter:
          comparison:
            op: LT
            value:
              default_value: 500
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/dev/stdout"
    log_format:
      json_format:
        level: "WARN"
        timestamp: "%START_TIME%"
        method: "%REQ(:METHOD)%"
        path: "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%"
        response_code: "%RESPONSE_CODE%"
        duration: "%DURATION%"

# 信息日志（简化格式）
- name: envoy.access_loggers.file
  filter:
    status_code_filter:
      comparison:
        op: LT
        value:
          default_value: 400
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/dev/stdout"
    log_format:
      text_format_source:
        inline_string: "[%START_TIME%] %REQ(:METHOD)% %REQ(X-ENVOY-ORIGINAL-PATH?:PATH)% %RESPONSE_CODE% %DURATION%\n"
```

## 与日志收集系统的集成

### Fluentd集成

```yaml
# Fluentd配置
<source>
  @type tail
  path /var/log/istio/access.log
  pos_file /var/log/istio/access.log.pos
  tag istio.access
  <parse>
    @type json
    time_key timestamp
    time_format %Y-%m-%dT%H:%M:%S.%NZ
  </parse>
</source>

<filter istio.access>
  @type record_transformer
  <record>
    service_mesh istio
    log_type access_log
  </record>
</filter>

<match istio.access>
  @type elasticsearch
  host elasticsearch.logging.svc.cluster.local
  port 9200
  logstash_format true
  logstash_prefix istio-access
</match>
```

### Filebeat集成

```yaml
# Filebeat配置
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/istio/*.log
  json.keys_under_root: true
  json.add_error_key: true
  fields:
    service_mesh: istio
    log_type: access_log
  fields_under_root: true

processors:
- add_kubernetes_metadata:
    in_cluster: true

output.elasticsearch:
  hosts: ["elasticsearch.logging.svc.cluster.local:9200"]
  index: "istio-access-%{+yyyy.MM.dd}"
```

### Prometheus集成

```yaml
# 通过Prometheus收集Envoy指标
scrape_configs:
- job_name: 'envoy-stats'
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
  - action: labelmap
    regex: __meta_kubernetes_pod_label_(.+)
  - source_labels: [__meta_kubernetes_namespace]
    action: replace
    target_label: kubernetes_namespace
  - source_labels: [__meta_kubernetes_pod_name]
    action: replace
    target_label: kubernetes_pod_name
```

## 日志安全与合规

### 敏感信息过滤

```yaml
# 敏感信息过滤配置
access_log:
- name: envoy.access_loggers.file
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/dev/stdout"
    log_format:
      json_format:
        timestamp: "%START_TIME%"
        method: "%REQ(:METHOD)%"
        path: "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%"
        # 过滤敏感头信息
        user_agent: "%REQ(USER-AGENT)%"
        # 不记录Authorization头
        # authorization: "%REQ(AUTHORIZATION)%"  # 注释掉敏感字段
        request_id: "%REQ(X-REQUEST-ID)%"
        response_code: "%RESPONSE_CODE%"
        duration: "%DURATION%"
```

### 日志加密传输

```yaml
# 日志加密传输配置
access_log:
- name: envoy.access_loggers.http_grpc
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.grpc.v3.HttpGrpcAccessLogConfig
    common_config:
      log_name: "secure_access_log"
      grpc_service:
        envoy_grpc:
          cluster_name: "secure_access_log_service"
        # 启用TLS
        ssl_context:
          common_tls_context:
            tls_certificates:
            - certificate_chain:
                filename: "/etc/certs/cert.pem"
              private_key:
                filename: "/etc/certs/key.pem"
            validation_context:
              trusted_ca:
                filename: "/etc/certs/ca.pem"
```

## 故障排查与调试

### 日志级别调整

```yaml
# 调整Envoy日志级别
admin:
  access_log_path: "/dev/null"
  address:
    socket_address:
      address: 127.0.0.1
      port_value: 15000

log_level: debug  # 可选: trace, debug, info, warning, error, critical

# 动态调整日志级别
# curl -X POST http://localhost:15000/logging?level=debug
```

### 调试日志配置

```yaml
# 调试日志配置
access_log:
- name: envoy.access_loggers.file
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
    path: "/tmp/envoy_debug.log"
    log_format:
      json_format:
        timestamp: "%START_TIME%"
        method: "%REQ(:METHOD)%"
        path: "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%"
        protocol: "%PROTOCOL%"
        response_code: "%RESPONSE_CODE%"
        response_flags: "%RESPONSE_FLAGS%"
        bytes_received: "%BYTES_RECEIVED%"
        bytes_sent: "%BYTES_SENT%"
        duration: "%DURATION%"
        upstream_service_time: "%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%"
        forwarded_for: "%REQ(X-FORWARDED-FOR)%"
        user_agent: "%REQ(USER-AGENT)%"
        request_id: "%REQ(X-REQUEST-ID)%"
        authority: "%REQ(:AUTHORITY)%"
        upstream_host: "%UPSTREAM_HOST%"
        upstream_cluster: "%UPSTREAM_CLUSTER%"
        downstream_local_address: "%DOWNSTREAM_LOCAL_ADDRESS%"
        downstream_remote_address: "%DOWNSTREAM_REMOTE_ADDRESS%"
        route_name: "%ROUTE_NAME%"
        connection_termination_details: "%CONNECTION_TERMINATION_DETAILS%"
```

### 常见问题诊断

```bash
# 检查Envoy配置
kubectl exec -it <pod-name> -c istio-proxy -- curl http://localhost:15000/config_dump

# 查看统计信息
kubectl exec -it <pod-name> -c istio-proxy -- curl http://localhost:15000/stats/prometheus

# 查看日志
kubectl logs <pod-name> -c istio-proxy

# 检查集群状态
kubectl exec -it <pod-name> -c istio-proxy -- curl http://localhost:15000/clusters

# 动态调整日志级别
kubectl exec -it <pod-name> -c istio-proxy -- curl -X POST http://localhost:15000/logging?level=debug
```

## 最佳实践总结

### 配置管理

```yaml
# 配置管理最佳实践
best_practices:
  format_consistency:
    guidelines:
      - "在整个网格中使用统一的日志格式"
      - "定义标准的日志字段命名规范"
      - "保持JSON和文本格式的一致性"
      
  performance_optimization:
    guidelines:
      - "根据业务需求调整采样率"
      - "使用缓冲和异步写入提升性能"
      - "合理设置日志轮转策略"
      
  security_compliance:
    guidelines:
      - "过滤敏感信息避免泄露"
      - "实施日志加密传输"
      - "定期审查日志内容合规性"
```

### 运维管理

```yaml
# 运维管理最佳实践
operational_best_practices:
  monitoring:
    guidelines:
      - "监控日志收集系统的健康状态"
      - "设置日志存储容量告警"
      - "建立日志收集延迟监控"
      
  troubleshooting:
    guidelines:
      - "保留足够的调试日志信息"
      - "建立日志分析和查询规范"
      - "定期演练故障排查流程"
      
  scaling:
    guidelines:
      - "根据服务规模调整日志配置"
      - "实施分层日志收集策略"
      - "优化日志存储和查询性能"
```

## 总结

Envoy代理作为Istio服务网格的数据平面核心，提供了强大而灵活的日志采集能力。通过合理的配置和优化，可以构建高效、安全、合规的服务网格日志体系。

关键要点包括：
1. 选择合适的日志格式（文本或JSON）
2. 配置适当的采样策略以平衡详细程度和性能
3. 实施条件日志记录以减少不必要的日志量
4. 与主流日志收集系统（如Fluentd、Filebeat）集成
5. 确保日志安全，过滤敏感信息
6. 建立完善的故障排查和调试机制

通过遵循最佳实践，合理配置资源限制，及时进行故障排查和性能优化，可以确保Envoy日志采集系统的稳定运行，为微服务架构提供可靠的可观察性保障。

在下一节中，我们将探讨如何集成Prometheus、Grafana与服务网格。