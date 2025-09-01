# 服务网格（Service Mesh）从入门到精通

本仓库包含《服务网格（Service Mesh）从入门到精通》一书的所有章节内容，按照书籍目录结构组织，方便读者系统学习服务网格相关知识。

## 目录结构

### 前言

* [0-0-0_Preface.md](0-0-0_Preface.md) - 前言

### 第一部分：服务网格基础与核心概念

#### 第1章：服务网格简介

* [1-1-0_Service-Mesh-Introduction.md](1-1-0_Service-Mesh-Introduction.md) - 第1章 服务网格简介（概述）
* [1-1-1_What-is-Service-Mesh.md](1-1-1_What-is-Service-Mesh.md) - 什么是服务网格？
* [1-1-2_Background-and-Development-of-Service-Mesh.md](1-1-2_Background-and-Development-of-Service-Mesh.md) - 服务网格的背景与发展
* [1-1-3_Key-Objectives-of-Service-Mesh.md](1-1-3_Key-Objectives-of-Service-Mesh.md) - 服务网格的关键目标：微服务通信、可观察性、安全性
* [1-1-4_Service-Mesh-vs-Traditional-Architecture.md](1-1-4_Service-Mesh-vs-Traditional-Architecture.md) - 服务网格与传统架构的对比
* [1-1-5_Service-Mesh-Use-Cases-and-Advantages.md](1-1-5_Service-Mesh-Use-Cases-and-Advantages.md) - 服务网格的应用场景与优势

#### 第2章：服务网格的基本架构

* [1-2-0_Service-Mesh-Basic-Architecture.md](1-2-0_Service-Mesh-Basic-Architecture.md) - 第2章 服务网格的基本架构（概述）
* [1-2-1_Core-Components-of-Service-Mesh.md](1-2-1_Core-Components-of-Service-Mesh.md) - 服务网格的核心组件：数据平面、控制平面
* [1-2-2_Sidecar-Pattern-and-Working-Principle.md](1-2-2_Sidecar-Pattern-and-Working-Principle.md) - 代理（Sidecar）模式与工作原理
* [1-2-3_Control-Plane-Roles-and-Mechanisms.md](1-2-3_Control-Plane-Roles-and-Mechanisms.md) - 控制平面的作用与工作机制
* [1-2-4_Separation-of-Data-Flow-and-Control-Flow.md](1-2-4_Separation-of-Data-Flow-and-Control-Flow.md) - 数据流与控制流在服务网格中的分离
* [1-2-5_Service-Mesh-vs-API-Gateway.md](1-2-5_Service-Mesh-vs-API-Gateway.md) - 服务网格与 API 网关的区别

#### 第3章：服务网格的主要功能

* [1-3-0_Main-Functions-of-Service-Mesh.md](1-3-0_Main-Functions-of-Service-Mesh.md) - 第3章 服务网格的主要功能（概述）
* [1-3-1_Traffic-Management-Load-Balancing-Routing-Traffic-Control.md](1-3-1_Traffic-Management-Load-Balancing-Routing-Traffic-Control.md) - 流量管理：负载均衡、路由、流量控制
* [1-3-2_Security-Authentication-Encryption-Access-Control.md](1-3-2_Security-Authentication-Encryption-Access-Control.md) - 安全性：身份认证、加密、访问控制
* [1-3-3_Observability-Monitoring-Logging-Tracing.md](1-3-3_Observability-Monitoring-Logging-Tracing.md) - 可观察性：监控、日志、追踪
* [1-3-4_Resilience-Retry-Timeout-Circuit-Breaker.md](1-3-4_Resilience-Retry-Timeout-Circuit-Breaker.md) - 弹性：重试、超时、断路器
* [1-3-5_Distributed-Transactions-and-Compensation.md](1-3-5_Distributed-Transactions-and-Compensation.md) - 分布式事务与补偿

### 第二部分：服务网格实现与部署

#### 第4章：服务网格的部署方式

* [2-4-0_Service-Mesh-Deployment-Methods.md](2-4-0_Service-Mesh-Deployment-Methods.md) - 第4章 服务网格的部署方式（概述）
* [2-4-1_Containerized-Environment-and-Service-Mesh-Integration.md](2-4-1_Containerized-Environment-and-Service-Mesh-Integration.md) - 容器化环境与服务网格的结合
* [2-4-2_Kubernetes-and-Service-Mesh-Integration.md](2-4-2_Kubernetes-and-Service-Mesh-Integration.md) - Kubernetes 与服务网格的集成
* [2-4-3_Service-Mesh-on-VMs-and-Bare-Metal.md](2-4-3_Service-Mesh-on-VMs-and-Bare-Metal.md) - 基于虚拟机与裸金属环境的服务网格
* [2-4-4_Deploying-Service-Mesh-with-Helm.md](2-4-4_Deploying-Service-Mesh-with-Helm.md) - 使用 Helm 部署服务网格
* [2-4-5_Service-Mesh-Tools-Istio-Linkerd-Consul.md](2-4-5_Service-Mesh-Tools-Istio-Linkerd-Consul.md) - 使用 Istio、Linkerd、Consul 等服务网格工具

#### 第5章：服务网格的代理与控制平面

* [2-5-0_Service-Mesh-Proxy-and-Control-Plane.md](2-5-0_Service-Mesh-Proxy-and-Control-Plane.md) - 第5章 服务网格的代理与控制平面（概述）
* [2-5-1_Sidecar-Proxy-Roles-and-Deployment.md](2-5-1_Sidecar-Proxy-Roles-and-Deployment.md) - Sidecar 代理的作用与部署
* [2-5-2_Control-Plane-Architecture-and-Mechanisms.md](2-5-2_Control-Plane-Architecture-and-Mechanisms.md) - 控制平面：Istio Pilot、Mixer、Citadel 等组件
* [2-5-3_Control-Plane-Architecture-Comparison.md](2-5-3_Control-Plane-Architecture-Comparison.md) - 各大服务网格的控制平面架构对比
* [2-5-4_Distributed-Deployment-and-High-Availability.md](2-5-4_Distributed-Deployment-and-High-Availability.md) - 服务网格的分布式部署与高可用性设计

#### 第6章：服务网格与微服务架构

* [2-6-0_Service-Mesh-and-Microservices-Architecture.md](2-6-0_Service-Mesh-and-Microservices-Architecture.md) - 第6章 服务网格与微服务架构（概述）
* [2-6-1_Microservices-Architecture-and-Service-Mesh-Integration.md](2-6-1_Microservices-Architecture-and-Service-Mesh-Integration.md) - 微服务架构与服务网格的结合
* [2-6-2_Service-Mesh-Roles-in-Microservices-Architecture.md](2-6-2_Service-Mesh-Roles-in-Microservices-Architecture.md) - 服务网格在微服务架构中的作用
* [2-6-3_Service-Discovery-and-Load-Balancing-Implementation.md](2-6-3_Service-Discovery-and-Load-Balancing-Implementation.md) - 实现服务发现与负载均衡
* [2-6-4_Reliable-Communication-and-Fault-Tolerance.md](2-6-4_Reliable-Communication-and-Fault-Tolerance.md) - 服务之间的可靠通信与容错处理

### 第三部分：服务网格的流量管理

#### 第7章：流量路由与负载均衡

* [3-7-0_Traffic-Routing-and-Load-Balancing.md](3-7-0_Traffic-Routing-and-Load-Balancing.md) - 第7章 流量路由与负载均衡（概述）
* [3-7-1_Basic-Routing-Patterns.md](3-7-1_Basic-Routing-Patterns.md) - 基本路由模式（如请求转发、基于内容的路由）
* [3-7-2_Canary-Release-and-Traffic-Splitting.md](3-7-2_Canary-Release-and-Traffic-Splitting.md) - 灰度发布与流量拆分
* [3-7-3_Weight-Based-Traffic-Control.md](3-7-3_Weight-Based-Traffic-Control.md) - 基于权重的流量控制
* [3-7-4_AB-Testing-and-Canary-Release.md](3-7-4_AB-Testing-and-Canary-Release.md) - A/B 测试与 Canary 发布

#### 第8章：流量控制与故障恢复

* [3-8-0_Traffic-Control-and-Fault-Recovery.md](3-8-0_Traffic-Control-and-Fault-Recovery.md) - 第8章 流量控制与故障恢复（概述）
* [3-8-1_Traffic-Control-Policies.md](3-8-1_Traffic-Control-Policies.md) - 流量控制策略：超时、重试、回退
* [3-8-2_Circuit-Breaker-Pattern.md](3-8-2_Circuit-Breaker-Pattern.md) - 断路器模式（Circuit Breaker）
* [3-8-3_Rate-Limiting-and-Circuit-Breaker-Configuration.md](3-8-3_Rate-Limiting-and-Circuit-Breaker-Configuration.md) - 限流与熔断器配置
* [3-8-4_Fault-Injection-and-Chaos-Engineering.md](3-8-4_Fault-Injection-and-Chaos-Engineering.md) - 故障注入与混沌工程
* [3-8-5_Service-Degradation-and-Recovery-Strategies.md](3-8-5_Service-Degradation-and-Recovery-Strategies.md) - 服务降级与恢复策略

#### 第9章：服务网格中的流量镜像与代理

* [3-9-0_Service-Mesh-Traffic-Mirroring-and-Proxy.md](3-9-0_Service-Mesh-Traffic-Mirroring-and-Proxy.md) - 第9章 服务网格中的流量镜像与代理（概述）
* [3-9-1_Traffic-Mirroring-and-Canary-Release.md](3-9-1_Traffic-Mirroring-and-Canary-Release.md) - 流量镜像与金丝雀发布

### 第四部分：服务网格的安全性

#### 第10章：服务网格的安全架构

* [4-10-0_Service-Mesh-Security-Architecture.md](4-10-0_Service-Mesh-Security-Architecture.md) - 第10章 服务网格的安全架构（概述）
* [4-10-1_TLS-Communication-Encryption.md](4-10-1_TLS-Communication-Encryption.md) - 使用 TLS 进行通信加密
* [4-10-2_Authentication-and-Authorization-JWT-OAuth2-mTLS.md](4-10-2_Authentication-and-Authorization-JWT-OAuth2-mTLS.md) - 身份认证与授权：JWT、OAuth2、mTLS
* [4-10-3_Service-to-Service-Security-Communication-and-Policies.md](4-10-3_Service-to-Service-Security-Communication-and-Policies.md) - 服务间安全通信与策略
* [4-10-4_Fine-Grained-Access-Control-RBAC.md](4-10-4_Fine-Grained-Access-Control-RBAC.md) - 细粒度访问控制（RBAC）

#### 第11章：服务网格中的认证与授权

* [4-11-0_Service-Mesh-Authentication-and-Authorization.md](4-11-0_Service-Mesh-Authentication-and-Authorization.md) - 第11章 服务网格中的认证与授权（概述）
* [4-11-1_Service-Mesh-Access-Control-Policies.md](4-11-1_Service-Mesh-Access-Control-Policies.md) - 使用 Istio 与 Linkerd 实现服务间认证
* [4-11-2_Microservices-Security-Architecture-and-Multi-Tenant-Support.md](4-11-2_Microservices-Security-Architecture-and-Multi-Tenant-Support.md) - 服务网格中的访问控制策略
* [4-11-3_API-Security-and-Service-Governance.md](4-11-3_API-Security-and-Service-Governance.md) - 微服务安全架构与多租户支持

#### 第12章：服务网格的漏洞与防护

* [4-12-0_Service-Mesh-Vulnerabilities-and-Protection.md](4-12-0_Service-Mesh-Vulnerabilities-and-Protection.md) - 第12章 服务网格的漏洞与防护（概述）
* [4-12-1_Preventing-Internal-Abuse-and-Unauthorized-Access.md](4-12-1_Preventing-Internal-Abuse-and-Unauthorized-Access.md) - 防止内部滥用与越权访问
* [4-12-2_Strengthening-Service-Mesh-Security-Protection-and-Monitoring.md](4-12-2_Strengthening-Service-Mesh-Security-Protection-and-Monitoring.md) - 加强服务网格的安全防护与监控
* [4-12-3_Security-Audit-and-Log-Management.md](4-12-3_Security-Audit-and-Log-Management.md) - 安全审计与日志管理

### 第五部分：服务网格的可观察性

#### 第13章：服务网格的监控与日志管理

* [5-13-0_Service-Mesh-Monitoring-and-Log-Management.md](5-13-0_Service-Mesh-Monitoring-and-Log-Management.md) - 第13章 服务网格的监控与日志管理（概述）
* [5-13-1_Using-Prometheus-to-Monitor-Service-Mesh.md](5-13-1_Using-Prometheus-to-Monitor-Service-Mesh.md) - 服务网格中的监控需求与解决方案
* [5-13-2_Integrating-Grafana-for-Visual-Monitoring.md](5-13-2_Integrating-Grafana-for-Visual-Monitoring.md) - 集成 Grafana 进行可视化监控
* [5-13-3_Log-Management-and-Fluentd-Configuration.md](5-13-3_Log-Management-and-Fluentd-Configuration.md) - 日志管理与 Fluentd 配置
* [5-13-4_Using-ELK-Stack-to-Collect-and-Analyze-Logs.md](5-13-4_Using-ELK-Stack-to-Collect-and-Analyze-Logs.md) - 使用 ELK 堆栈收集与分析日志
* [5-13-5_Log-Analysis-and-Troubleshooting.md](5-13-5_Log-Analysis-and-Troubleshooting.md) - 使用 ELK 堆栈收集与分析日志

#### 第14章：分布式追踪与故障排查

* [5-14-0_Distributed-Tracing-and-Fault-Troubleshooting.md](5-14-0_Distributed-Tracing-and-Fault-Troubleshooting.md) - 第14章 分布式追踪与故障排查（概述）
* [5-14-1_Distributed-Tracing-Overview-and-Working-Principle.md](5-14-1_Distributed-Tracing-Overview-and-Working-Principle.md) - 分布式追踪概述与工作原理
* [5-14-2_Integrating-Jaeger-and-Zipkin-for-Distributed-Tracing.md](5-14-2_Integrating-Jaeger-and-Zipkin-for-Distributed-Tracing.md) - 集成 Jaeger 与 Zipkin 进行分布式追踪
* [5-14-3_Visualizing-Microservice-Call-Chains.md](5-14-3_Visualizing-Microservice-Call-Chains.md) - 可视化微服务调用链
* [5-14-4_Fault-Troubleshooting-and-Performance-Bottleneck-Analysis.md](5-14-4_Fault-Troubleshooting-and-Performance-Bottleneck-Analysis.md) - 故障排查与性能瓶颈分析

#### 第15章：服务网格的性能优化

* [5-15-0_Service-Mesh-Performance-Optimization.md](5-15-0_Service-Mesh-Performance-Optimization.md) - 第15章 服务网格的性能优化（概述）
* [5-15-1_Performance-Monitoring-and-Metrics-Analysis.md](5-15-1_Performance-Monitoring-and-Metrics-Analysis.md) - 性能监控与指标分析
* [5-15-2_Latency-and-Throughput-Optimization-in-Service-Mesh.md](5-15-2_Latency-and-Throughput-Optimization-in-Service-Mesh.md) - 服务网格中的延迟与吞吐量优化
* [5-15-3_Performance-Bottleneck-Identification-and-Solutions.md](5-15-3_Performance-Bottleneck-Identification-and-Solutions.md) - 性能瓶颈识别与解决方案

### 第六部分：服务网格的高级应用与模式

#### 第16章：服务网格与多集群管理

* [6-16-0_Service-Mesh-and-Multi-Cluster-Management.md](6-16-0_Service-Mesh-and-Multi-Cluster-Management.md) - 第16章 服务网格与多集群管理（概述）
* [6-16-1_Multi-Cluster-Deployment-and-Service-Mesh-Architecture-Design.md](6-16-1_Multi-Cluster-Deployment-and-Service-Mesh-Architecture-Design.md) - 多集群部署与服务网格的架构设计
* [6-16-2_Multi-Cluster-Traffic-Management-and-Communication.md](6-16-2_Multi-Cluster-Traffic-Management-and-Communication.md) - 多集群间的流量管理与通信
* [6-16-3_Cross-Cluster-Service-Discovery-and-Routing.md](6-16-3_Cross-Cluster-Service-Discovery-and-Routing.md) - 跨集群服务发现与路由
* [6-16-4_Service-Mesh-in-Multi-Cloud-Environments.md](6-16-4_Service-Mesh-in-Multi-Cloud-Environments.md) - 多云环境中的服务网格应用

#### 第17章：服务网格与无服务器架构（Serverless）

* [6-17-0_Service-Mesh-and-Serverless-Architecture.md](6-17-0_Service-Mesh-and-Serverless-Architecture.md) - 第17章 服务网格与无服务器架构（概述）
* [6-17-1_Serverless-Architecture-Basic-Concepts.md](6-17-1_Serverless-Architecture-Basic-Concepts.md) - 无服务器架构的基本概念
* [6-17-2_Service-Mesh-Application-in-Serverless-Architecture.md](6-17-2_Service-Mesh-Application-in-Serverless-Architecture.md) - 服务网格在无服务器架构中的应用
* [6-17-3_Managing-Serverless-Functions-with-Service-Mesh.md](6-17-3_Managing-Serverless-Functions-with-Service-Mesh.md) - 通过服务网格管理无服务器函数
* [6-17-4_Combining-Service-Mesh-and-Serverless-for-Elasticity-and-Scalability.md](6-17-4_Combining-Service-Mesh-and-Serverless-for-Elasticity-and-Scalability.md) - 结合服务网格与无服务器架构实现弹性与可扩展性

#### 第18章：服务网格与微服务治理

* [6-18-0_Service-Mesh-and-Microservices-Governance.md](6-18-0_Service-Mesh-and-Microservices-Governance.md) - 第18章 服务网格与微服务治理（概述）
* [6-18-1_Core-Requirements-of-Microservices-Governance.md](6-18-1_Core-Requirements-of-Microservices-Governance.md) - 微服务治理的核心需求
* [6-18-2_Service-Mesh-Governance-Capabilities.md](6-18-2_Service-Mesh-Governance-Capabilities.md) - 服务网格的治理能力：服务发现、路由、熔断、限流
* [6-18-3_Microservices-Version-Management-and-Governance-Strategies.md](6-18-3_Microservices-Version-Management-and-Governance-Strategies.md) - 微服务版本管理与治理策略
* [6-18-4_Service-Mesh-and-Microservices-Lifecycle-Management.md](6-18-4_Service-Mesh-and-Microservices-Lifecycle-Management.md) - 服务网格与微服务生命周期管理

### 第七部分：服务网格的未来发展与趋势

#### 第19章：服务网格的未来趋势

* [7-19-0_Future-Trends-of-Service-Mesh.md](7-19-0_Future-Trends-of-Service-Mesh.md) - 第19章 服务网格的未来趋势（概述）
* [7-19-1_From-Traditional-Service-Mesh-to-Next-Generation-Service-Mesh.md](7-19-1_From-Traditional-Service-Mesh-to-Next-Generation-Service-Mesh.md) - 从传统服务网格到下一代服务网格
* [7-19-2_Service-Mesh-and-AI-ML.md](7-19-2_Service-Mesh-and-AI-ML.md) - 服务网格与人工智能、机器学习的结合
* [7-19-3_Quantum-Computing-and-Service-Mesh.md](7-19-3_Quantum-Computing-and-Service-Mesh.md) - 量子计算与服务网格的潜力
* [7-19-4_Service-Mesh-Automation-and-Self-Healing.md](7-19-4_Service-Mesh-Automation-and-Self-Healing.md) - 服务网格的自动化与自愈能力

#### 第20章：服务网格的市场前景与挑战

* [7-20-0_Service-Mesh-Market-Prospects-and-Challenges.md](7-20-0_Service-Mesh-Market-Prospects-and-Challenges.md) - 第20章 服务网格的市场前景与挑战（概述）
* [7-20-1_Service-Mesh-Market-Applications-and-Trend-Analysis.md](7-20-1_Service-Mesh-Market-Applications-and-Trend-Analysis.md) - 服务网格的市场应用与趋势分析
* [7-20-2_Future-Development-Directions-of-Service-Mesh.md](7-20-2_Future-Development-Directions-of-Service-Mesh.md) - 未来服务网格的发展方向
* [7-20-3_Service-Mesh-Challenges-Performance-Scalability-Usability.md](7-20-3_Service-Mesh-Challenges-Performance-Scalability-Usability.md) - 服务网格的挑战：性能、扩展性与易用性

### 附录

* [8-0-0_Appendix.md](8-0-0_Appendix.md) - 附录
* [10-0-0_Additional-Content.md](10-0-0_Additional-Content.md) - 实战案例与企业实践
* [10-0-1_Online-Learning-Resources-and-Hands-on-Projects.md](10-0-1_Online-Learning-Resources-and-Hands-on-Projects.md) - 在线学习资源与实战项目

### 后记

* [9-0-0_Afterword.md](9-0-0_Afterword.md) - 后记

## 说明

1. 本书按照从基础到高级的顺序组织内容，建议按章节顺序阅读。
2. 每章包含概述和具体小节内容，文件名采用编号+英文标题的格式。
3. 所有文章均采用Markdown格式编写，方便阅读和转换。
4. 随着内容的不断完善，本目录将持续更新。

## 贡献

欢迎对本书内容提出建议和改进意见，可以通过提交Issue或Pull Request的方式参与贡献。