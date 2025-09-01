# 《服务发现与负载均衡：从入门到精通》索引

## 第1部分 基础入门 (Foundations)

### 第1章 分布式系统与微服务的背景

1. [1-1-1-introduction-to-service-discovery-and-load-balancing.md](1-1-1-introduction-to-service-discovery-and-load-balancing.md) - 服务发现与负载均衡入门：从基础概念到核心价值
2. [1-1-2-the-need-for-service-discovery-and-load-balancing.md](1-1-2-the-need-for-service-discovery-and-load-balancing.md) - 为什么需要服务发现与负载均衡：从传统架构到微服务的演进
3. [1-1-3-traditional-architecture-vs-microservices-architecture.md](1-1-3-traditional-architecture-vs-microservices-architecture.md) - 传统架构 vs 微服务架构：服务发现与负载均衡的演进之路

### 第2章 服务发现的基本概念

1. [1-2-1-what-is-service-discovery.md](1-2-1-what-is-service-discovery.md) - 什么是服务发现：理解现代分布式系统的核心组件
2. [1-2-2-static-vs-dynamic-service-registration.md](1-2-2-static-vs-dynamic-service-registration.md) - 静态 vs 动态服务注册：服务发现机制的核心差异
3. [1-2-3-client-side-vs-server-side-discovery.md](1-2-3-client-side-vs-server-side-discovery.md) - 客户端发现 vs 服务端发现：服务发现架构模式深度解析

### 第3章 负载均衡的基本概念

1. [1-3-1-what-is-load-balancing.md](1-3-1-what-is-load-balancing.md) - 什么是负载均衡：分布式系统的流量调度核心
2. [1-3-2-static-round-robin-vs-dynamic-awareness.md](1-3-2-static-round-robin-vs-dynamic-awareness.md) - 静态轮询 vs 动态感知：负载均衡策略的核心差异
3. [1-3-3-l4-vs-l7-load-balancing.md](1-3-3-l4-vs-l7-load-balancing.md) - 四层（L4）与七层（L7）负载均衡：技术架构与应用场景深度解析

## 第2部分 核心机制与实现 (Core Mechanisms & Implementations)

### 第4章 服务注册与发现机制

1. [2-4-1-registry-center-role.md](2-4-1-registry-center-role.md) - 注册中心（Registry）的作用：服务发现的核心基础设施
2. [2-4-2-health-check-mechanism.md](2-4-2-health-check-mechanism.md) - 健康检查机制：保障服务高可用的关键技术
3. [2-4-3-common-implementations.md](2-4-3-common-implementations.md) - 常见实现：Eureka、Consul、Zookeeper、etcd深度解析

### 第5章 负载均衡策略

1. [2-5-1-common-algorithms.md](2-5-1-common-algorithms.md) - 常见算法：轮询、最少连接、加权轮询等负载均衡策略详解
2. [2-5-2-consistent-hashing-and-request-affinity.md](2-5-2-consistent-hashing-and-request-affinity.md) - 一致性哈希与请求亲和性：实现高效会话保持的负载均衡策略
3. [2-5-3-dynamic-adjustment-and-adaptive.md](2-5-3-dynamic-adjustment-and-adaptive.md) - 动态调整与自适应：智能负载均衡的前沿技术

### 第6章 客户端 vs 服务端负载均衡

1. [2-6-1-client-side-load-balancing.md](2-6-1-client-side-load-balancing.md) - 客户端负载均衡（Ribbon、gRPC 内置机制）：深入理解客户端负载均衡实现
2. [2-6-2-server-side-load-balancing.md](2-6-2-server-side-load-balancing.md) - 服务端负载均衡（Nginx、HAProxy、Envoy）：深入解析服务端负载均衡实现
3. [2-6-3-api-gateway-integration.md](2-6-3-api-gateway-integration.md) - API Gateway 集成：现代微服务架构中的负载均衡与API管理融合

## 第3部分 进阶与实践 (Advanced Topics & Practices)

### 第7章 容错与高可用设计

1. [3-7-1-health-check-and-circuit-breaker.md](3-7-1-health-check-and-circuit-breaker.md) - 健康检查与熔断：构建高可用微服务系统的关键机制
2. [3-7-2-automatic-removal-and-recovery.md](3-7-2-automatic-removal-and-recovery.md) - 自动摘除与恢复：实现服务自愈能力的关键技术
3. [3-7-3-multi-data-center-and-cross-region-discovery.md](3-7-3-multi-data-center-and-cross-region-discovery.md) - 多数据中心与跨区域发现：构建全球分布式系统的挑战与解决方案

### 第8章 服务发现与容器化/Kubernetes

1. [3-8-1-kubernetes-dns-and-coredns.md](3-8-1-kubernetes-dns-and-coredns.md) - Kubernetes 的 DNS & CoreDNS：容器化环境中的服务发现机制
2. [3-8-2-kube-proxy-and-service.md](3-8-2-kube-proxy-and-service.md) - Kube-Proxy 与 Service：Kubernetes网络流量管理的核心组件
3. [3-8-3-ingress-controller-and-service-mesh.md](3-8-3-ingress-controller-and-service-mesh.md) - Ingress Controller 与 Service Mesh：现代Kubernetes流量管理的双重奏

### 第9章 服务发现与 Service Mesh 的关系

1. [3-9-1-sidecar-service-discovery.md](3-9-1-sidecar-service-discovery.md) - Sidecar 模式下的服务发现：Service Mesh架构中的服务发现机制
2. [3-9-2-envoy-and-istio-load-balancing.md](3-9-2-envoy-and-istio-load-balancing.md) - Envoy 与 Istio 的负载均衡机制：Service Mesh中的智能流量调度
3. [3-9-3-zero-configuration-and-intelligent-routing.md](3-9-3-zero-configuration-and-intelligent-routing.md) - 零配置与智能路由：Service Mesh中的自动化流量管理

## 第4部分 安全与治理 (Security & Governance)

### 第11章 安全性考虑

1. [4-11-1-tls-ssl-and-service-communication.md](4-11-1-tls-ssl-and-service-communication.md) - TLS/SSL 与服务间加密通信：保障微服务安全的基石
2. [4-11-2-authentication-and-access-control.md](4-11-2-authentication-and-access-control.md) - 服务发现中的鉴权与访问控制：构建安全的服务治理体系
3. [4-11-3-zero-trust-architecture.md](4-11-3-zero-trust-architecture.md) - 零信任架构下的服务治理：构建新一代安全微服务生态系统

### 第12章 可观测性与监控

1. [4-12-1-load-balancing-monitoring-metrics.md](4-12-1-load-balancing-monitoring-metrics.md) - 负载均衡监控指标（QPS、延迟、错误率）：构建全面的性能观测体系
2. [4-12-2-service-discovery-monitoring.md](4-12-2-service-discovery-monitoring.md) - 服务发现监控与健康状态追踪：构建可靠的微服务基础设施
3. [4-12-3-logging-and-tracing.md](4-12-3-logging-and-tracing.md) - 日志 & Tracing 的应用：构建全链路可观测性体系

## 第5部分 实战与案例 (Case Studies & Best Practices)

### 第13章 实战案例：Spring Cloud + Eureka + Ribbon

1. [5-13-spring-cloud-eureka-ribbon.md](5-13-spring-cloud-eureka-ribbon.md) - 实战案例：Spring Cloud + Eureka + Ribbon 构建高可用微服务架构

### 第14章 实战案例：Consul + Envoy

1. [5-14-consul-envoy.md](5-14-consul-envoy.md) - 实战案例：Consul + Envoy 构建现代化服务网格架构

### 第15章 实战案例：Kubernetes Ingress + Service Mesh

1. [5-15-kubernetes-ingress-service-mesh.md](5-15-kubernetes-ingress-service-mesh.md) - 实战案例：Kubernetes Ingress + Service Mesh 构建云原生微服务架构

### 第16章 云原生环境下的最佳实践

1. [5-16-cloud-native-best-practices.md](5-16-cloud-native-best-practices.md) - 云原生环境下的最佳实践：构建高可用、可扩展的现代应用架构

## 第6部分 前沿与趋势 (Future Trends)

### 第17章 无服务器架构中的服务发现与负载均衡

1. [6-17-serverless-service-discovery.md](6-17-serverless-service-discovery.md) - 无服务器架构中的服务发现与负载均衡：构建弹性云原生应用

### 第18章 AI 驱动的智能路由与流量调度

1. [6-18-ai-driven-intelligent-routing.md](6-18-ai-driven-intelligent-routing.md) - AI 驱动的智能路由与流量调度：构建自适应的现代化负载均衡系统

### 第19章 未来的发展趋势与挑战

1. [6-19-future-trends.md](6-19-future-trends.md) - 服务发现与负载均衡的未来发展趋势与挑战：探索下一代分布式系统架构