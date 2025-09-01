---
title: Kubernetes体系架构：掌控云原生的核心组件
date: 2025-08-31
categories: [Kubernetes]
tags: [kubernetes, architecture, control-plane, nodes]
published: true
---

理解Kubernetes的体系架构是掌握这一容器编排平台的关键。Kubernetes采用分布式架构设计，通过多个核心组件协同工作，实现了容器化应用的自动化部署、扩展和管理。本章将深入解析Kubernetes的架构组成，帮助读者建立对其工作机制的全面认知。

## 控制平面与节点的架构

Kubernetes集群由两大部分组成：控制平面（Control Plane）和工作节点（Worker Nodes）。控制平面负责整个集群的管理和决策，而工作节点负责运行实际的应用容器。

### 控制平面（Control Plane）

控制平面是Kubernetes集群的大脑，负责维护集群的状态、做出调度决策以及响应集群事件。它通常由多个组件组成，这些组件可以运行在单个节点上（用于学习和测试），也可以分布在多个节点上以实现高可用性。

### 工作节点（Worker Nodes）

工作节点是运行应用容器的实际机器。每个节点都运行着必要的组件来管理Pod和与控制平面通信。在典型的生产环境中，一个Kubernetes集群会包含多个工作节点以提供足够的计算资源和高可用性。

## 核心组件：API Server、Controller Manager、Scheduler、etcd

Kubernetes控制平面的核心组件各司其职，协同工作以维护集群的正常运行。

### API Server

API Server是Kubernetes控制平面的前端，也是整个系统的入口点。它负责处理所有REST请求，验证并配置API对象（如Pod、Service、ReplicationController等）。API Server是唯一与etcd直接通信的组件，确保集群状态的一致性。

API Server的主要功能包括：
- 提供RESTful API接口供用户和组件交互
- 验证API请求的合法性
- 集群状态的存储和查询
- 认证和授权管理

### Controller Manager

Controller Manager运行着控制器进程，这些控制器负责维护集群的状态。逻辑上，每个控制器都是一个独立的进程，但为了降低复杂性，它们都被编译到同一个可执行文件中并运行在同一个进程中。

主要的控制器包括：
- Node Controller：负责节点故障检测和响应
- Replication Controller：维护Pod副本数量
- Deployment Controller：管理Deployment对象
- StatefulSet Controller：管理有状态应用

### Scheduler

Scheduler负责将未调度的Pod分配到合适的节点上运行。它通过资源需求、服务质量要求、亲和性/反亲和性规范、数据局部性、工作负载间的干扰等因素来做出调度决策。

Scheduler的工作流程包括：
1. 过滤阶段：筛选出满足Pod要求的节点
2. 打分阶段：为候选节点打分，选择最优节点
3. 绑定阶段：将Pod绑定到选定的节点

### etcd

etcd是一个分布式键值存储系统，用于存储Kubernetes集群的所有配置数据和状态信息。它是集群的唯一数据源，确保了集群状态的一致性和持久性。

etcd的特性包括：
- 强一致性：使用Raft共识算法保证数据一致性
- 高可用性：支持集群部署，容忍节点故障
- 观察机制：支持键值变化的实时监听

## 工作节点与 Pod 资源

工作节点是运行应用容器的机器，可以是物理机或虚拟机。每个节点都包含运行Pod所需的服务，并由控制平面管理。

### Pod资源

Pod是Kubernetes中最小的可部署单元，代表集群中运行的进程。一个Pod可以包含一个或多个紧密相关的容器，这些容器共享存储、网络和运行规范。

Pod的特性包括：
- 共享网络命名空间：Pod内的容器共享IP地址和端口空间
- 共享存储：Pod内的容器可以共享存储卷
- 生命周期短暂：Pod被创建后不会自愈，需要控制器管理

## kubelet、kube-proxy 及其功能

每个工作节点都运行着两个关键组件：kubelet和kube-proxy。

### kubelet

kubelet是运行在每个节点上的代理，负责确保Pod中的容器按预期运行。它从API Server接收Pod定义，并确保这些Pod在本地节点上正确运行。

kubelet的主要功能包括：
- 与API Server通信，获取分配给节点的Pod配置
- 挂载Pod所需的存储卷
- 下载Pod的Secret
- 运行Pod中的容器
- 定期向API Server报告节点和Pod状态

### kube-proxy

kube-proxy是运行在每个节点上的网络代理，负责实现Kubernetes Service概念的一部分。它维护节点上的网络规则，使得从集群内部或外部到Pod的网络连接能够正常工作。

kube-proxy的工作方式包括：
- 在Linux节点上使用iptables或IPVS实现服务代理
- 负载均衡流量到后端Pod
- 处理服务发现和网络地址转换

## 服务发现与负载均衡

Kubernetes通过Service对象实现服务发现和负载均衡功能。

### 服务发现

Kubernetes中的服务发现通过以下机制实现：
- DNS：集群内的DNS服务器为每个Service创建DNS记录
- 环境变量：kubelet为每个Pod注入相关Service的环境变量
- API Server：应用可以直接查询API Server获取Service信息

### 负载均衡

Kubernetes支持多种负载均衡模式：
- ClusterIP：集群内部的虚拟IP，实现集群内负载均衡
- NodePort：在每个节点上开放端口，实现外部访问
- LoadBalancer：通过云提供商的负载均衡器实现外部访问
- ExternalName：将Service映射到外部DNS名称

通过这些组件的协同工作，Kubernetes实现了强大而灵活的容器编排能力。理解这些核心组件及其交互方式，是深入掌握Kubernetes的关键基础。