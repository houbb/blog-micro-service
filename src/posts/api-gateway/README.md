# 《API 网关从入门到精通：架构、模式与实践》

欢迎阅读《API 网关从入门到精通：架构、模式与实践》一书的技术文章系列。本系列文章深入探讨了 API 网关在现代微服务和云原生架构中的核心作用、实现原理和最佳实践。

## 目录索引

### 第一部分 基础入门

#### 第1章 什么是 API 网关
- [API 网关的定义与作用](1-1-what-is-api-gateway.md)
- [API 网关的核心概念](1-1-1-api-gateway-core-concepts.md)
- [API 网关与微服务架构](1-1-2-api-gateway-and-microservices.md)

#### 第2章 为什么需要 API 网关
- [为什么需要 API 网关](1-2-why-we-need-api-gateway.md)
- [统一入口的价值](1-2-1-unified-entrypoint-value.md)
- [安全性和可观测性](1-2-2-security-and-observability.md)

#### 第3章 API 网关的基本功能
- [API 网关的基本功能](1-3-basic-functions-of-api-gateway.md)
- [请求路由与负载均衡](1-3-1-request-routing-and-load-balancing.md)
- [身份认证与授权](1-3-2-authentication-and-authorization.md)
- [协议转换](1-3-3-protocol-conversion.md)

### 第二部分 核心能力与实现

#### 第4章 流量治理
- [流量治理](1-4-traffic-governance.md)
- [限流、熔断、降级](1-4-1-rate-limiting-circuit-breaking-degradation.md)
- [重试与超时控制](1-4-2-retry-and-timeout-control.md)
- [流量分组与灰度发布](1-4-3-traffic-grouping-and-gray-release.md)

#### 第5章 安全与合规
- [安全与合规](1-5-security-and-compliance.md)
- [身份验证机制](1-5-1-authentication-mechanisms.md)
- [访问控制与 RBAC](1-5-2-access-control-and-rbac.md)
- [防护措施](1-5-3-protection-measures.md)

#### 第6章 协议与数据处理
- [协议与数据处理](1-6-protocol-and-data-processing.md)
- [REST、gRPC、GraphQL 支持](1-6-1-rest-grpc-graphql-support.md)
- [API 聚合与编排](1-6-2-api-aggregation-and-orchestration.md)
- [数据转换与格式化](1-6-3-data-transformation-and-formatting.md)

#### 第7章 可观测性与监控
- [可观测性与监控](1-7-observability-and-monitoring.md)
- [日志采集](1-7-1-log-collection.md)
- [指标监控](1-7-2-metrics-monitoring.md)
- [分布式追踪](1-7-3-distributed-tracing.md)

### 第三部分 架构与模式

#### 第8章 API 网关的架构模式
- [API 网关的架构模式](1-8-api-gateway-architecture-patterns.md)
- [单体网关架构](1-8-1-monolithic-gateway-architecture.md)
- [集群化与高可用设计](1-8-2-clustering-and-high-availability-design.md)
- [去中心化网关与 Service Mesh](1-8-3-decentralized-gateway-and-service-mesh.md)

---

## 书籍简介

本书从 **入门（是什么 & 为什么） → 核心能力 → 架构模式 → 实践工具 → 高阶趋势**，覆盖了 API 网关在微服务和云原生架构下的完整生命周期，既适合入门学习，也能让有经验的架构师深入研究。

## 技术涵盖

- API 网关基础概念与核心组件
- 微服务架构中的 API 网关作用
- 身份认证与授权机制（OAuth2, JWT, API Key）
- 协议转换（REST, gRPC, GraphQL）
- 流量治理（限流、熔断、降级、重试、超时控制）
- 安全防护（WAF, 防爬虫, DDoS 防护）
- 可观测性（日志采集、指标监控、分布式追踪）
- 数据处理和格式转换
- 集群化与高可用设计
- Service Mesh 与去中心化网关

## 适用读者

- 微服务架构师
- 后端开发工程师
- DevOps 工程师
- 系统架构师
- 对 API 网关技术感兴趣的技术人员