---
title: 附录A：容错与容灾术语表
date: 2025-08-31
categories: [Fault Tolerance, Disaster Recovery]
tags: [fault-recovery]
published: true
---

# 附录A：容错与容灾术语表

本术语表收录了容错与灾备领域的重要专业术语及其定义，帮助读者准确理解相关概念。

## A

### Availability (可用性)
系统在需要时能够正常运行和提供服务的概率。通常以百分比表示，如99.9%的可用性。

### Active-Active Architecture (双活架构)
一种系统架构模式，其中多个实例同时处理请求，提供负载分担和故障转移能力。

### Active-Passive Architecture (主备架构)
一种系统架构模式，其中一个实例处于活动状态处理请求，另一个实例处于待机状态，仅在主实例故障时接管服务。

## B

### Byzantine Fault (拜占庭故障)
指系统组件以任意方式失效的故障类型，包括组件产生错误输出、停止响应或表现出恶意行为。

### Bulkhead Pattern (隔板模式)
一种容错设计模式，通过将系统资源分割成独立的隔间，防止故障在系统内传播。

## C

### Chaos Engineering (混沌工程)
一种通过故意引入故障来测试系统韧性的实践方法。

### Circuit Breaker Pattern (熔断器模式)
一种容错设计模式，当检测到服务故障时暂时停止向该服务发送请求，防止故障级联传播。

### Checkpoint (检查点)
在系统运行过程中保存的稳定状态快照，用于故障恢复时恢复到该状态。

### Consensus Algorithm (共识算法)
分布式系统中用于在多个节点间达成一致状态的算法，如Paxos、Raft等。

## D

### Disaster Recovery (灾难恢复)
在发生重大故障或灾难后，恢复系统正常运行的过程和策略。

### Distributed System (分布式系统)
由多个独立计算机组成的系统，这些计算机通过网络通信协作完成共同任务。

## E

### Eventual Consistency (最终一致性)
一种一致性模型，保证在没有新更新的情况下，系统最终会达到一致状态。

### Exponential Backoff (指数退避)
一种重试策略，每次重试的间隔时间按指数增长，以减少系统负载。

## F

### Fault (故障)
系统组件偏离其正常行为的状态。

### Fault Tolerance (容错)
系统在部分组件发生故障时仍能继续正确运行的能力。

### Failure (失效)
系统或组件停止提供其规定功能的事件。

## G

### Graceful Degradation (优雅降级)
当系统部分功能不可用时，以降低服务质量但仍保持核心功能可用的方式继续运行。

## H

### Heartbeat (心跳)
系统组件定期发送的信号，用于表明其处于正常运行状态。

### High Availability (高可用性)
系统能够长时间持续提供服务的能力，通常要求达到99.9%以上的可用性。

## I

### Idempotency (幂等性)
操作可以多次执行而不会产生不同结果的特性。

## L

### Load Balancing (负载均衡)
将工作负载分配到多个计算资源上的过程，以优化资源使用和最大化吞吐量。

## M

### Microservices (微服务)
一种架构风格，将单一应用程序开发为一组小型服务，每个服务运行在自己的进程中。

### Multi-Site Deployment (多站点部署)
在多个地理位置部署系统实例，以提高可用性和灾难恢复能力。

## N

### N+1 Redundancy (N+1冗余)
一种冗余设计，其中N个组件提供所需功能，额外1个组件作为备用。

## P

### Partition Tolerance (分区容忍性)
分布式系统在面临网络分区时仍能继续运行的能力。

### Passive Standby (被动待机)
备用系统处于待机状态，不处理实际请求，仅在主系统故障时接管。

## Q

### Quorum (法定人数)
在分布式系统中，为达成共识所需的最小节点数。

## R

### Redundancy (冗余)
通过重复关键组件来提高系统可靠性的技术。

### Recovery Point Objective (RPO) (恢复点目标)
在灾难发生后，系统能够恢复到的最远时间点，即最大可接受的数据丢失量。

### Recovery Time Objective (RTO) (恢复时间目标)
从灾难发生到系统恢复正常运行所需的最长时间。

### Rollback (回滚)
将系统状态恢复到之前某个检查点的操作。

## S

### Self-Healing System (自愈系统)
能够自动检测、诊断和修复故障的系统。

### Service Level Agreement (SLA) (服务等级协议)
服务提供商与客户之间关于服务质量的正式协议。

### Service Level Objective (SLO) (服务等级目标)
在SLA中定义的具体服务质量目标。

### Split-Brain (脑裂)
在集群系统中，两个或多个节点同时认为自己是主节点的情况。

## T

### Timeout (超时)
在指定时间内未收到预期响应时终止操作的机制。

## U

### Uptime (正常运行时间)
系统处于正常运行状态的时间比例。

## V

### Vertical Scaling (垂直扩展)
通过增加单个服务器的资源（如CPU、内存）来提高系统性能。

### Virtual IP (虚拟IP)
不直接绑定到特定网络接口的IP地址，可用于实现高可用性。

## W

### Warm Standby (温备)
备用系统处于部分运行状态，可以较快接管主系统的工作。

## X

### XA Transaction (XA事务)
分布式事务的标准协议，确保跨多个资源管理器的事务一致性。

## Z

### Zero Downtime Deployment (零停机部署)
在不中断服务的情况下部署新版本应用程序的技术。

---

*本术语表将持续更新，以反映容错与灾备领域的最新发展。*