---
title: Kubernetes网络管理与安全：构建安全高效的容器网络
date: 2025-08-31
categories: [Kubernetes]
tags: [kubernetes, networking, cni, network-policy, security]
published: true
---

Kubernetes网络是容器化应用通信的基础，其复杂性和重要性不言而喻。一个设计良好的网络架构不仅能确保应用间的高效通信，还能提供强大的安全防护。本章将深入探讨Kubernetes网络模型、CNI插件、Pod间通信机制、网络策略以及网络安全配置，帮助读者构建安全高效的容器网络环境。

## Kubernetes 网络模型与 CNI 插件

### Kubernetes 网络模型原则

Kubernetes网络模型基于以下核心原则：

1. **Pod间通信**：所有Pod都可以直接通信，无需NAT
2. **节点与Pod通信**：节点和Pod可以互相通信，无需NAT
3. **Pod可见性**：每个Pod看到自己的IP地址与其他人看到的一样

### CNI（Container Network Interface）简介

CNI是容器网络接口标准，定义了容器网络插件的接口规范。

#### CNI工作原理

1. 容器运行时调用CNI插件
2. CNI插件配置网络命名空间
3. 分配IP地址
4. 配置路由和网络策略

#### 常用CNI插件

##### Calico

Calico是一个纯三层网络解决方案，提供网络策略功能。

```bash
# 安装Calico
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

##### Flannel

Flannel是一个简单的网络覆盖解决方案。

```bash
# 安装Flannel
kubectl apply -f https://github.com/coreos/flannel/raw/master/Documentation/kube-flannel.yml
```

##### Cilium

Cilium基于eBPF技术，提供高性能的网络和安全功能。

```bash
# 安装Cilium
helm repo add cilium https://helm.cilium.io/
helm install cilium cilium/cilium --namespace kube-system
```

### CNI插件选择指南

选择CNI插件时需要考虑以下因素：

1. **网络性能**：延迟、吞吐量、CPU消耗
2. **网络策略支持**：是否支持NetworkPolicy
3. **可扩展性**：支持的节点和Pod数量
4. **功能特性**：服务网格集成、监控等
5. **社区支持**：文档、社区活跃度、更新频率

## Pod 间通信与服务发现

### Pod 网络通信机制

#### 同节点Pod通信

同一节点上的Pod通过虚拟以太网设备（veth pair）和网桥进行通信：

1. Pod通过veth pair连接到网桥
2. 数据包通过网桥转发到目标Pod
3. 无需NAT转换

#### 跨节点Pod通信

跨节点Pod通信依赖于底层网络插件：

1. **路由方式**：通过路由表转发数据包
2. **覆盖网络**：通过隧道封装数据包
3. **BGP**：通过BGP协议传播路由信息

### 服务发现机制

#### DNS服务发现

Kubernetes集群内置CoreDNS服务：

```bash
# 查询Service DNS记录
nslookup my-service.my-namespace.svc.cluster.local
```

#### 环境变量服务发现

Kubernetes为每个Service自动创建环境变量：

```bash
# 查看环境变量
kubectl exec -it <pod-name> -- env | grep SERVICE
```

#### Headless Service

Headless Service直接返回Pod IP地址：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-headless-service
spec:
  clusterIP: None
  selector:
    app: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
```

### 网络性能优化

#### MTU优化

```yaml
# Calico配置MTU
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  calicoNetwork:
    mtu: 1460
```

#### 负载均衡优化

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
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

## 网络策略与流量隔离

### NetworkPolicy 基础

NetworkPolicy用于控制Pod之间的网络流量。

#### 默认拒绝所有流量

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

#### 允许特定Pod访问

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 80
```

#### 允许外部访问

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-external
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 172.17.0.0/16
        except:
        - 172.17.1.0/24
    ports:
    - protocol: TCP
      port: 80
```

### 高级网络策略

#### Egress策略

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

#### 多层策略

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: layered-policy
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: frontend
    - podSelector:
        matchLabels:
          role: api-client
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
```

### 网络策略最佳实践

1. **默认拒绝**：从默认拒绝所有流量开始
2. **渐进式开放**：逐步开放必要的通信
3. **标签管理**：合理使用标签进行策略匹配
4. **定期审查**：定期审查和更新网络策略
5. **文档化**：记录网络策略的设计和变更

## 网络安全与防火墙配置

### 网络安全层

#### 主机网络安全

```bash
# 配置iptables规则
iptables -A INPUT -p tcp --dport 6443 -j ACCEPT
iptables -A INPUT -p tcp --dport 2379:2380 -j ACCEPT
iptables -A INPUT -p tcp --dport 10250 -j ACCEPT
iptables -A INPUT -p tcp --dport 10251 -j ACCEPT
iptables -A INPUT -p tcp --dport 10252 -j ACCEPT
```

#### Pod网络安全

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  containers:
  - name: app
    image: nginx
    securityContext:
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      runAsUser: 1000
```

### 防火墙配置

#### 云平台防火墙

##### AWS Security Groups

```json
{
  "IpPermissions": [
    {
      "FromPort": 6443,
      "ToPort": 6443,
      "IpProtocol": "tcp",
      "UserIdGroupPairs": [
        {
          "GroupId": "sg-12345678"
        }
      ]
    }
  ]
}
```

##### GCP Firewall Rules

```bash
# 创建防火墙规则
gcloud compute firewall-rules create k8s-api-server \
    --allow tcp:6443 \
    --source-ranges 10.0.0.0/8 \
    --target-tags k8s-master
```

#### 节点防火墙

```bash
# 控制平面节点防火墙
ufw allow from 10.0.0.0/8 to any port 6443
ufw allow from 10.0.0.0/8 to any port 2379:2380
ufw allow from 10.0.0.0/8 to any port 10250

# 工作节点防火墙
ufw allow from 10.0.0.0/8 to any port 10250
ufw allow from 10.0.0.0/8 to any port 30000:32767
```

### 网络监控与审计

#### 网络流量监控

使用Cilium Hubble进行网络流量监控：

```bash
# 安装Hubble CLI
export HUBBLE_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/hubble/master/stable.txt)
curl -L --remote-name-all https://github.com/cilium/hubble/releases/download/$HUBBLE_VERSION/hubble-linux-amd64.tar.gz{,.sha256sum}
sha256sum --check hubble-linux-amd64.tar.gz.sha256sum
sudo tar xzvfC hubble-linux-amd64.tar.gz /usr/local/bin

# 查看网络流量
hubble observe --follow
```

#### 网络策略审计

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: RequestResponse
  resources:
  - group: networking.k8s.io
    resources: ["networkpolicies"]
  verbs: ["create", "update", "delete", "patch"]
```

### 安全加固建议

1. **网络分段**：使用命名空间和网络策略实现网络分段
2. **流量加密**：使用TLS加密Pod间通信
3. **入侵检测**：部署网络入侵检测系统
4. **日志审计**：启用网络流量日志和审计
5. **定期扫描**：定期扫描网络漏洞和配置问题

通过本章的学习，读者应该能够深入理解Kubernetes网络模型和CNI插件的工作原理，掌握Pod间通信和服务发现机制，熟练配置和管理网络策略，以及实施网络安全和防火墙配置。这些知识对于构建安全、高效的Kubernetes网络环境至关重要。