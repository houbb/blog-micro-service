---
title: Kubernetes基本对象与资源：构建云原生应用的核心构件
date: 2025-08-31
categories: [Kubernetes]
tags: [kubernetes, objects, resources, kubectl]
published: true
---

Kubernetes通过一系列对象和资源来表示集群的状态。理解这些基本对象和资源是有效使用Kubernetes的关键。本章将详细介绍Kubernetes中最核心的对象和资源，包括它们的作用、使用方式以及管理方法。

## Pod、ReplicaSet、Deployment、StatefulSet

### Pod

Pod是Kubernetes中最小的可部署单元，代表集群中运行的进程。一个Pod可以包含一个或多个紧密相关的容器，这些容器共享存储、网络和运行规范。

#### Pod的特性

- **共享网络**：Pod内的所有容器共享同一个IP地址和端口空间
- **共享存储**：Pod可以定义存储卷，Pod内的所有容器都可以访问这些存储卷
- **生命周期**：Pod是短暂的，不会自愈，需要控制器来管理
- **原子性**：Pod内的所有容器被当作一个整体进行调度和管理

#### Pod的使用场景

- 单容器应用：最常见的使用方式
- 多容器协作：如应用容器和日志收集容器
- Sidecar模式：辅助容器为主容器提供额外功能

### ReplicaSet

ReplicaSet是确保任何给定时间都有指定数量的Pod副本在运行的控制器。它是下一代Replication Controller，支持基于集合的选择器。

#### ReplicaSet的功能

- **副本管理**：确保指定数量的Pod副本始终运行
- **标签选择**：通过标签选择器识别管理的Pod
- **自动恢复**：当Pod失败时自动创建新的Pod

#### ReplicaSet的局限性

虽然ReplicaSet功能强大，但它通常不直接使用，而是通过Deployment来管理。

### Deployment

Deployment为Pod和ReplicaSet提供声明式更新。它是管理应用部署的推荐方式。

#### Deployment的优势

- **声明式更新**：通过声明期望状态来管理应用
- **滚动更新**：支持无停机的应用更新
- **回滚功能**：可以轻松回滚到之前的版本
- **扩缩容**：可以轻松调整应用副本数量

#### Deployment的使用示例

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

### StatefulSet

StatefulSet是为有状态应用设计的控制器，为Pod提供唯一的标识和持久存储。

#### StatefulSet的特点

- **稳定的网络标识**：每个Pod都有稳定的网络标识
- **持久存储**：支持持久卷的按序创建和删除
- **有序部署和删除**：Pod按序创建和删除
- **有序滚动更新**：支持有序的滚动更新

#### StatefulSet的使用场景

- 数据库集群（如MySQL、PostgreSQL）
- 分布式存储系统（如etcd、Cassandra）
- 消息队列系统（如Kafka、RabbitMQ）

## Service、ConfigMap、Secret、Ingress

### Service

Service是为一组Pod提供稳定的网络访问入口的抽象。

#### Service的类型

- **ClusterIP**：默认类型，在集群内部暴露服务
- **NodePort**：在每个节点上开放端口，从外部访问服务
- **LoadBalancer**：通过云提供商的负载均衡器暴露服务
- **ExternalName**：将服务映射到外部DNS名称

#### Service的使用示例

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
```

### ConfigMap

ConfigMap用于存储非机密性的配置数据，以键值对的形式存储。

#### ConfigMap的使用方式

- **环境变量**：将ConfigMap中的数据作为环境变量注入容器
- **命令行参数**：将ConfigMap中的数据作为命令行参数传递给容器
- **存储卷**：将ConfigMap挂载为存储卷供容器使用

#### ConfigMap示例

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: game-demo
data:
  player_initial_lives: "3"
  ui_properties_file_name: "user-interface.properties"
```

### Secret

Secret用于存储敏感信息，如密码、OAuth令牌和SSH密钥。

#### Secret的类型

- **Opaque**：通用的Secret类型
- **kubernetes.io/service-account-token**：服务账户令牌
- **kubernetes.io/dockercfg**：Docker配置文件
- **kubernetes.io/tls**：TLS证书和密钥

#### Secret的安全性

- Base64编码存储（不是加密）
- 支持加密存储（需要配置）
- 访问控制通过RBAC实现

### Ingress

Ingress管理对集群中服务的外部访问，通常用于HTTP路由。

#### Ingress的功能

- **HTTP路由**：基于主机名和路径的路由
- **TLS终止**：支持SSL/TLS证书
- **负载均衡**：集成负载均衡功能

#### Ingress控制器

需要部署Ingress控制器才能使Ingress资源生效，常用的控制器包括：
- Nginx Ingress Controller
- Traefik
- HAProxy Ingress

## PersistentVolume、PersistentVolumeClaim

### PersistentVolume (PV)

PersistentVolume是集群中的一块存储资源，由管理员配置或使用存储类动态配置。

#### PV的访问模式

- **ReadWriteOnce (RWO)**：单个节点读写
- **ReadOnlyMany (ROX)**：多个节点只读
- **ReadWriteMany (RWX)**：多个节点读写

#### PV的回收策略

- **Retain**：手动回收
- **Recycle**：基本擦除后回收（已弃用）
- **Delete**：删除关联的存储资产

### PersistentVolumeClaim (PVC)

PersistentVolumeClaim是用户对存储的请求，类似于Pod对计算资源的请求。

#### PVC的工作流程

1. 用户创建PVC
2. Kubernetes查找匹配的PV
3. 将PV绑定到PVC
4. Pod使用PVC获取存储

## Namespace、ResourceQuota、LimitRange

### Namespace

Namespace是用于在单个集群中创建多个虚拟集群的机制。

#### Namespace的用途

- **资源隔离**：不同团队或项目的资源隔离
- **访问控制**：基于Namespace的权限控制
- **资源管理**：按Namespace分配资源

#### Namespace的操作

```bash
# 创建Namespace
kubectl create namespace my-namespace

# 查看Namespace
kubectl get namespaces

# 删除Namespace
kubectl delete namespace my-namespace
```

### ResourceQuota

ResourceQuota用于限制Namespace中资源的使用总量。

#### ResourceQuota的限制类型

- **计算资源**：CPU、内存的请求和限制
- **存储资源**：存储请求和持久卷声明数量
- **对象数量**：Pod、Service等对象的数量

#### ResourceQuota示例

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: demo
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 1Gi
    limits.cpu: "2"
    limits.memory: 2Gi
```

### LimitRange

LimitRange用于限制Namespace中单个对象可以使用的资源量。

#### LimitRange的限制类型

- **Container**：限制单个容器的资源使用
- **Pod**：限制单个Pod的资源使用
- **PersistentVolumeClaim**：限制存储请求

## 查看与管理 Kubernetes 资源（kubectl 命令）

kubectl是Kubernetes的命令行工具，用于与集群交互。

### 基本命令

```bash
# 查看资源
kubectl get pods
kubectl get services
kubectl get deployments

# 查看详细信息
kubectl describe pod <pod-name>
kubectl describe service <service-name>

# 创建资源
kubectl create -f <file.yaml>
kubectl apply -f <file.yaml>

# 删除资源
kubectl delete pod <pod-name>
kubectl delete -f <file.yaml>
```

### 高级命令

```bash
# 编辑资源
kubectl edit deployment <deployment-name>

# 查看日志
kubectl logs <pod-name>

# 进入容器
kubectl exec -it <pod-name> -- /bin/bash

# 端口转发
kubectl port-forward <pod-name> 8080:80
```

通过本章的学习，读者应该能够理解Kubernetes的基本对象和资源，掌握它们的使用方法，并能够通过kubectl命令有效地管理这些资源。这些核心概念是后续章节深入学习Kubernetes的基础。