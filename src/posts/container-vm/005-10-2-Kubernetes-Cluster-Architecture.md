---
title: Kubernetes集群架构与核心组件深度解析
date: 2025-08-31
categories: [Containerization, Kubernetes]
tags: [container-vm]
published: true
---

# 第10章：Kubernetes集群架构与核心组件深度解析

Kubernetes集群架构是理解Kubernetes工作原理的基础。一个Kubernetes集群由控制平面和工作节点组成，每个组件都有其特定的职责和功能。深入理解这些组件及其交互方式，对于有效管理和运维Kubernetes集群至关重要。本章将详细解析Kubernetes集群的架构设计和核心组件。

## Kubernetes集群架构概述

Kubernetes采用主从架构设计，将集群分为控制平面（Control Plane）和工作节点（Worker Nodes）两个主要部分。这种架构设计确保了集群的高可用性、可扩展性和容错能力。

### 架构设计理念

#### 分层架构
Kubernetes采用分层架构设计，将不同的功能模块分离，每一层都有明确的职责：

1. **基础设施层**：提供计算、存储和网络资源
2. **容器运行时层**：负责容器的创建和管理
3. **节点层**：管理单个节点上的资源和容器
4. **集群管理层**：管理整个集群的状态和调度
5. **应用层**：运行用户的应用程序

#### 声明式管理
Kubernetes采用声明式管理模型，用户通过YAML或JSON文件描述期望的状态，Kubernetes负责将实际状态调整到期望状态。

#### 松耦合设计
各个组件之间通过API进行通信，实现了松耦合设计，提高了系统的可维护性和可扩展性。

### 集群组件交互

Kubernetes集群中的各个组件通过以下方式进行交互：

1. **API Server作为中心枢纽**：所有组件都通过API Server进行通信
2. **etcd存储集群状态**：所有集群状态信息都存储在etcd中
3. **Controller模式**：各种控制器通过监控集群状态来维护期望状态
4. **Watch机制**：组件通过Watch机制实时获取状态变更

## 控制平面详解

控制平面是Kubernetes集群的大脑，负责管理整个集群的状态、调度和协调。控制平面通常运行在一组专用的节点上，这些节点被称为master节点。

### API Server

API Server是Kubernetes控制平面的前端，提供了RESTful API接口，是整个系统的统一入口。

#### 核心功能

1. **API接口提供**：
   - 提供集群状态的统一访问接口
   - 支持标准的HTTP/HTTPS协议
   - 提供Swagger文档和API版本管理

2. **认证与授权**：
   - 支持多种认证方式（证书、令牌、Webhook等）
   - 实施基于角色的访问控制（RBAC）
   - 提供准入控制机制

3. **对象验证与配置**：
   - 验证API对象的合法性
   - 处理对象的创建、更新和删除操作
   - 维护对象的状态一致性

#### 配置示例
```yaml
# API Server配置示例
apiVersion: v1
kind: Pod
metadata:
  name: kube-apiserver
  namespace: kube-system
spec:
  containers:
  - name: kube-apiserver
    image: k8s.gcr.io/kube-apiserver:v1.24.0
    command:
    - kube-apiserver
    - --advertise-address=192.168.1.100
    - --allow-privileged=true
    - --authorization-mode=Node,RBAC
    - --client-ca-file=/etc/kubernetes/pki/ca.crt
    - --enable-admission-plugins=NodeRestriction
    - --enable-bootstrap-token-auth=true
    - --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt
    - --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt
    - --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key
    - --etcd-servers=https://127.0.0.1:2379
    - --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt
    - --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key
    - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
    - --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt
    - --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key
    - --requestheader-allowed-names=front-proxy-client
    - --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt
    - --requestheader-extra-headers-prefix=X-Remote-Extra-
    - --requestheader-group-headers=X-Remote-Group
    - --requestheader-username-headers=X-Remote-User
    - --secure-port=6443
    - --service-account-issuer=https://kubernetes.default.svc.cluster.local
    - --service-account-key-file=/etc/kubernetes/pki/sa.pub
    - --service-account-signing-key-file=/etc/kubernetes/pki/sa.key
    - --service-cluster-ip-range=10.96.0.0/12
    - --tls-cert-file=/etc/kubernetes/pki/apiserver.crt
    - --tls-private-key-file=/etc/kubernetes/pki/apiserver.key
```

#### 高可用配置
```bash
# 多实例API Server配置
# 1. 负载均衡器配置
apiVersion: v1
kind: Service
metadata:
  name: kubernetes
  namespace: default
spec:
  ports:
  - name: https
    port: 443
    protocol: TCP
    targetPort: 6443
  selector:
    component: apiserver
    provider: kubernetes
  type: LoadBalancer

# 2. 多实例部署
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kube-apiserver
  namespace: kube-system
spec:
  replicas: 3
  selector:
    matchLabels:
      component: apiserver
  template:
    metadata:
      labels:
        component: apiserver
    spec:
      containers:
      - name: kube-apiserver
        image: k8s.gcr.io/kube-apiserver:v1.24.0
        # ... 其他配置
```

### etcd

etcd是Kubernetes的分布式键值存储，用于存储集群的所有配置数据和状态信息。它是集群的唯一数据源，所有组件都通过API Server读取和写入etcd。

#### 核心特性

1. **高可用性**：
   - 通过Raft一致性算法实现数据一致性
   - 支持集群部署，通常部署奇数个节点（3、5、7等）
   - 自动故障检测和恢复

2. **高性能**：
   - 支持快速读写操作
   - 内存存储，提供低延迟访问
   - 支持批量操作

3. **安全性**：
   - 支持TLS加密通信
   - 支持客户端证书认证
   - 支持访问控制

#### 部署配置
```yaml
# etcd集群部署配置
apiVersion: v1
kind: Pod
metadata:
  name: etcd
  namespace: kube-system
spec:
  containers:
  - name: etcd
    image: k8s.gcr.io/etcd:3.5.4-0
    command:
    - etcd
    - --advertise-client-urls=https://192.168.1.100:2379
    - --cert-file=/etc/kubernetes/pki/etcd/server.crt
    - --client-cert-auth=true
    - --data-dir=/var/lib/etcd
    - --initial-advertise-peer-urls=https://192.168.1.100:2380
    - --initial-cluster=master-1=https://192.168.1.100:2380,master-2=https://192.168.1.101:2380,master-3=https://192.168.1.102:2380
    - --initial-cluster-state=new
    - --key-file=/etc/kubernetes/pki/etcd/server.key
    - --listen-client-urls=https://127.0.0.1:2379,https://192.168.1.100:2379
    - --listen-metrics-urls=http://127.0.0.1:2381
    - --listen-peer-urls=https://192.168.1.100:2380
    - --name=master-1
    - --peer-cert-file=/etc/kubernetes/pki/etcd/peer.crt
    - --peer-client-cert-auth=true
    - --peer-key-file=/etc/kubernetes/pki/etcd/peer.key
    - --peer-trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt
    - --snapshot-count=10000
    - --trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt
```

#### 备份与恢复
```bash
# etcd备份
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /backup/etcd-snapshot.db

# etcd恢复
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot restore /backup/etcd-snapshot.db \
  --data-dir=/var/lib/etcd-backup
```

### Scheduler

Scheduler负责将Pod调度到合适的节点上运行。它通过一系列算法和策略来决定Pod的最佳部署位置。

#### 调度流程

1. **过滤阶段**：
   - 根据资源需求过滤掉不满足条件的节点
   - 检查节点亲和性/反亲和性
   - 验证节点标签匹配

2. **打分阶段**：
   - 为满足条件的节点计算得分
   - 考虑资源利用率、亲和性等因素
   - 选择得分最高的节点

3. **绑定阶段**：
   - 将Pod绑定到选定的节点
   - 更新etcd中的Pod状态

#### 调度策略配置
```yaml
# 自定义调度器配置
apiVersion: kubescheduler.config.k8s.io/v1beta3
kind: KubeSchedulerConfiguration
profiles:
- schedulerName: default-scheduler
  plugins:
    queueSort:
      enabled:
      - name: PrioritySort
    preFilter:
      enabled:
      - name: NodeResourcesFit
      - name: NodePorts
      - name: PodTopologySpread
    filter:
      enabled:
      - name: NodeResourcesFit
      - name: NodePorts
      - name: PodTopologySpread
    preScore:
      enabled:
      - name: InterPodAffinity
      - name: PodTopologySpread
      - name: TaintToleration
    score:
      enabled:
      - name: NodeResourcesFit
        weight: 1
      - name: ImageLocality
        weight: 1
      - name: InterPodAffinity
        weight: 1
      - name: NodeAffinity
        weight: 1
```

#### 多调度器支持
```yaml
# 使用自定义调度器
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  schedulerName: custom-scheduler
  containers:
  - name: my-container
    image: nginx
```

### Controller Manager

Controller Manager运行各种控制器，这些控制器负责维护集群的期望状态。每个控制器都是一个独立的控制循环，持续监控集群状态并采取必要行动。

#### 主要控制器

1. **Node Controller**：
   - 负责节点状态管理
   - 检测节点故障并标记不可用节点
   - 在节点故障时驱逐Pod

2. **Replication Controller**：
   - 维护Pod副本数量
   - 确保指定数量的Pod始终运行
   - 处理Pod的创建和删除

3. **Deployment Controller**：
   - 管理Deployment资源
   - 实现滚动更新和回滚
   - 维护应用的期望状态

4. **StatefulSet Controller**：
   - 管理有状态应用
   - 维护Pod的身份和存储
   - 确保有序部署和扩展

5. **DaemonSet Controller**：
   - 确保每个节点运行一个Pod副本
   - 处理节点添加和删除
   - 维护系统级服务

#### 配置示例
```yaml
# Controller Manager配置
apiVersion: v1
kind: Pod
metadata:
  name: kube-controller-manager
  namespace: kube-system
spec:
  containers:
  - name: kube-controller-manager
    image: k8s.gcr.io/kube-controller-manager:v1.24.0
    command:
    - kube-controller-manager
    - --allocate-node-cidrs=true
    - --authentication-kubeconfig=/etc/kubernetes/controller-manager.conf
    - --authorization-kubeconfig=/etc/kubernetes/controller-manager.conf
    - --bind-address=127.0.0.1
    - --client-ca-file=/etc/kubernetes/pki/ca.crt
    - --cluster-cidr=10.244.0.0/16
    - --cluster-name=kubernetes
    - --cluster-signing-cert-file=/etc/kubernetes/pki/ca.crt
    - --cluster-signing-key-file=/etc/kubernetes/pki/ca.key
    - --controllers=*,bootstrapsigner,tokencleaner
    - --kubeconfig=/etc/kubernetes/controller-manager.conf
    - --leader-elect=true
    - --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt
    - --root-ca-file=/etc/kubernetes/pki/ca.crt
    - --service-account-private-key-file=/etc/kubernetes/pki/sa.key
    - --service-cluster-ip-range=10.96.0.0/12
    - --use-service-account-credentials=true
```

### Cloud Controller Manager

Cloud Controller Manager运行与底层云提供商交互的控制器，这些控制器负责管理云资源。

#### 主要功能

1. **节点控制器**：
   - 检查云提供商提供的节点是否已停止
   - 更新节点状态信息

2. **路由控制器**：
   - 在云基础设施上设置路由

3. **服务控制器**：
   - 创建、更新和删除云提供商负载均衡器

4. **卷控制器**：
   - 管理云提供商的持久化存储

#### 配置示例
```yaml
# Cloud Controller Manager配置
apiVersion: v1
kind: Pod
metadata:
  name: cloud-controller-manager
  namespace: kube-system
spec:
  containers:
  - name: cloud-controller-manager
    image: k8s.gcr.io/cloud-controller-manager:v1.24.0
    command:
    - cloud-controller-manager
    - --allocate-node-cidrs=true
    - --authentication-kubeconfig=/etc/kubernetes/cloud-controller-manager.conf
    - --authorization-kubeconfig=/etc/kubernetes/cloud-controller-manager.conf
    - --bind-address=127.0.0.1
    - --client-ca-file=/etc/kubernetes/pki/ca.crt
    - --cloud-config=/etc/kubernetes/cloud.conf
    - --cloud-provider=aws
    - --cluster-cidr=10.244.0.0/16
    - --cluster-name=kubernetes
    - --kubeconfig=/etc/kubernetes/cloud-controller-manager.conf
    - --leader-elect=true
    - --node-status-update-frequency=5m0s
    - --route-reconciliation-period=10s
```

## 工作节点详解

工作节点是运行应用程序容器的机器，它们由控制平面管理。每个工作节点都运行必要的组件来与控制平面通信并管理本地的Pod。

### kubelet

kubelet是运行在每个节点上的代理，负责与控制平面通信并管理节点上的Pod。

#### 核心功能

1. **节点注册**：
   - 向API Server注册节点
   - 报告节点状态和资源信息

2. **Pod管理**：
   - 监控Pod状态并报告给API Server
   - 确保容器按期望状态运行
   - 处理Pod的创建、更新和删除

3. **资源管理**：
   - 管理节点上的计算资源
   - 实施资源限制和配额
   - 监控资源使用情况

#### 配置示例
```yaml
# kubelet配置
apiVersion: v1
kind: Pod
metadata:
  name: kubelet
  namespace: kube-system
spec:
  containers:
  - name: kubelet
    image: k8s.gcr.io/kubelet:v1.24.0
    command:
    - kubelet
    - --bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf
    - --config=/var/lib/kubelet/config.yaml
    - --container-runtime=remote
    - --container-runtime-endpoint=unix:///run/containerd/containerd.sock
    - --kubeconfig=/etc/kubernetes/kubelet.conf
    - --node-ip=192.168.1.100
    - --node-labels=
    - --pod-infra-container-image=k8s.gcr.io/pause:3.6
    - --register-node=true
    - --register-with-taints=
    - --rotate-certificates=true
    - --runtime-cgroups=/system.slice/containerd.service
    - --tls-cipher-suites=TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
```

#### 资源管理配置
```yaml
# kubelet资源配置
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
authentication:
  anonymous:
    enabled: false
  webhook:
    cacheTTL: 0s
    enabled: true
  x509:
    clientCAFile: /etc/kubernetes/pki/ca.crt
authorization:
  mode: Webhook
  webhook:
    cacheAuthorizedTTL: 0s
    cacheUnauthorizedTTL: 0s
clusterDNS:
- 10.96.0.10
clusterDomain: cluster.local
cpuManagerReconcilePeriod: 0s
evictionHard:
  imagefs.available: 15%
  memory.available: 100Mi
  nodefs.available: 10%
  nodefs.inodesFree: 5%
evictionPressureTransitionPeriod: 0s
fileCheckFrequency: 0s
healthzBindAddress: 127.0.0.1
healthzPort: 10248
httpCheckFrequency: 0s
imageGCHighThresholdPercent: 85
imageGCLowThresholdPercent: 80
imageMinimumGCAge: 0s
kind: KubeletConfiguration
logging:
  flushFrequency: 0
  options:
    json:
      infoBufferSize: "0"
  verbosity: 0
memorySwap: {}
nodeStatusReportFrequency: 0s
nodeStatusUpdateFrequency: 0s
resolvConf: /run/systemd/resolve/resolv.conf
rotateCertificates: true
runtimeRequestTimeout: 0s
shutdownGracePeriod: 0s
shutdownGracePeriodCriticalPods: 0s
staticPodPath: /etc/kubernetes/manifests
streamingConnectionIdleTimeout: 0s
syncFrequency: 0s
volumeStatsAggPeriod: 0s
```

### kube-proxy

kube-proxy运行在每个节点上，负责网络代理和负载均衡。

#### 核心功能

1. **服务代理**：
   - 维护网络规则
   - 执行服务发现和负载均衡
   - 支持TCP、UDP和SCTP协议

2. **网络策略**：
   - 实施网络访问控制
   - 过滤网络流量
   - 支持网络隔离

3. **连接跟踪**：
   - 跟踪网络连接状态
   - 管理连接表
   - 优化网络性能

#### 配置模式

1. **iptables模式**：
   ```yaml
   # iptables模式配置
   apiVersion: kubeproxy.config.k8s.io/v1alpha1
   kind: KubeProxyConfiguration
   mode: iptables
   ```

2. **ipvs模式**：
   ```yaml
   # ipvs模式配置
   apiVersion: kubeproxy.config.k8s.io/v1alpha1
   kind: KubeProxyConfiguration
   mode: ipvs
   ipvs:
     scheduler: rr
     excludeCIDRs:
     - 10.244.0.0/16
   ```

3. **userspace模式**：
   ```yaml
   # userspace模式配置
   apiVersion: kubeproxy.config.k8s.io/v1alpha1
   kind: KubeProxyConfiguration
   mode: userspace
   ```

#### 配置示例
```yaml
# kube-proxy配置
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
bindAddress: 0.0.0.0
clientConnection:
  acceptContentTypes: ""
  burst: 0
  contentType: ""
  kubeconfig: /var/lib/kube-proxy/kubeconfig.conf
  qps: 0
clusterCIDR: 10.244.0.0/16
configSyncPeriod: 0s
conntrack:
  maxPerCore: 0
  min: null
  tcpCloseWaitTimeout: null
  tcpEstablishedTimeout: null
detectLocalMode: ""
enableProfiling: false
healthzBindAddress: ""
hostnameOverride: ""
iptables:
  masqueradeAll: false
  masqueradeBit: null
  minSyncPeriod: 0s
  syncPeriod: 0s
ipvs:
  excludeCIDRs: null
  minSyncPeriod: 0s
  scheduler: ""
  strictARP: false
  syncPeriod: 0s
  tcpFinTimeout: 0s
  tcpTimeout: 0s
  udpTimeout: 0s
kind: KubeProxyConfiguration
logging:
  flushFrequency: 0
  options:
    json:
      infoBufferSize: "0"
  verbosity: 0
metricsBindAddress: ""
mode: iptables
nodePortAddresses: null
oomScoreAdj: null
portRange: ""
showHiddenMetricsForVersion: ""
udpIdleTimeout: 0s
winkernel:
  enableDSR: false
  forwardHealthCheckVip: false
  networkName: ""
  sourceVip: ""
```

### 容器运行时

容器运行时负责实际运行容器，Kubernetes支持多种容器运行时。

#### 主要容器运行时

1. **Docker**：
   ```bash
   # Docker配置
   # /etc/docker/daemon.json
   {
     "exec-opts": ["native.cgroupdriver=systemd"],
     "log-driver": "json-file",
     "log-opts": {
       "max-size": "100m"
     },
     "storage-driver": "overlay2"
   }
   ```

2. **containerd**：
   ```toml
   # containerd配置
   # /etc/containerd/config.toml
   [plugins."io.containerd.grpc.v1.cri"]
     sandbox_image = "k8s.gcr.io/pause:3.6"
     [plugins."io.containerd.grpc.v1.cri".containerd]
       snapshotter = "overlayfs"
       [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
         runtime_type = "io.containerd.runc.v2"
         [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
           SystemdCgroup = true
   ```

3. **CRI-O**：
   ```toml
   # CRI-O配置
   # /etc/crio/crio.conf
   [crio.runtime]
   default_runtime = "runc"
   [crio.image]
   pause_image = "k8s.gcr.io/pause:3.6"
   ```

## 集群网络架构

Kubernetes集群网络是连接所有组件的基础，它需要满足特定的要求。

### 网络要求

1. **Pod网络**：
   - 所有Pod都能与其他Pod通信
   - 每个Pod都有唯一的IP地址
   - 不需要NAT转换

2. **节点网络**：
   - 所有节点都能与所有Pod通信
   - 节点间通信不需要NAT

3. **外部网络**：
   - 外部能够访问Service
   - Service能够访问外部网络

### 网络插件

#### CNI插件
```yaml
# Calico网络插件配置
apiVersion: v1
kind: Pod
metadata:
  name: calico-node
  namespace: kube-system
spec:
  containers:
  - name: calico-node
    image: docker.io/calico/node:v3.23.0
    env:
    - name: DATASTORE_TYPE
      value: kubernetes
    - name: FELIX_DEFAULTENDPOINTTOHOSTACTION
      value: ACCEPT
    - name: FELIX_HEALTHENABLED
      value: "true"
    - name: FELIX_IPINIPMTU
      value: "1440"
    - name: FELIX_IPV4POOL_CIDR
      value: "10.244.0.0/16"
    - name: FELIX_IPV4POOL_IPIP
      value: Always
    - name: IP
      value: autodetect
    - name: IP_AUTODETECTION_METHOD
      value: can-reach=192.168.1.100
    - name: CALICO_DISABLE_FILE_LOGGING
      value: "true"
    - name: FELIX_LOGSEVERITYSCREEN
      value: info
    - name: FELIX_USAGEREPORTINGENABLED
      value: "false"
    - name: NODENAME
      valueFrom:
        fieldRef:
          fieldPath: spec.nodeName
    - name: CLUSTER_TYPE
      value: k8s,bgp
```

#### Service网络
```yaml
# CoreDNS配置
apiVersion: v1
kind: Service
metadata:
  name: kube-dns
  namespace: kube-system
  annotations:
    prometheus.io/port: "9153"
    prometheus.io/scrape: "true"
  labels:
    k8s-app: kube-dns
    kubernetes.io/cluster-service: "true"
    kubernetes.io/name: "CoreDNS"
spec:
  selector:
    k8s-app: kube-dns
  clusterIP: 10.96.0.10
  ports:
  - name: dns
    port: 53
    protocol: UDP
  - name: dns-tcp
    port: 53
    protocol: TCP
  - name: metrics
    port: 9153
    protocol: TCP
```

## 集群安全架构

安全性是Kubernetes集群设计的重要考虑因素。

### 认证机制

#### 证书认证
```bash
# 生成证书
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -subj "/CN=kubernetes" -days 10000 -out ca.crt
```

#### 令牌认证
```yaml
# 服务账户令牌
apiVersion: v1
kind: Secret
metadata:
  name: default-token
  namespace: default
  annotations:
    kubernetes.io/service-account.name: default
type: kubernetes.io/service-account-token
```

### 授权机制

#### RBAC配置
```yaml
# Role配置
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

# RoleBinding配置
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: jane
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### 网络策略
```yaml
# 网络策略示例
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: test-network-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - ipBlock:
        cidr: 172.17.0.0/16
        except:
        - 172.17.1.0/24
    - namespaceSelector:
        matchLabels:
          project: myproject
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 6379
  egress:
  - to:
    - ipBlock:
        cidr: 10.0.0.0/24
    ports:
    - protocol: TCP
      port: 5978
```

## 集群监控与日志

有效的监控和日志管理对于集群运维至关重要。

### 监控架构

#### Metrics Server
```yaml
# Metrics Server部署
apiVersion: apps/v1
kind: Deployment
metadata:
  name: metrics-server
  namespace: kube-system
spec:
  selector:
    matchLabels:
      k8s-app: metrics-server
  template:
    metadata:
      labels:
        k8s-app: metrics-server
    spec:
      containers:
      - name: metrics-server
        image: k8s.gcr.io/metrics-server/metrics-server:v0.6.1
        args:
        - --cert-dir=/tmp
        - --secure-port=4443
        - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
        - --kubelet-use-node-status-port
        - --metric-resolution=15s
```

#### Prometheus监控
```yaml
# Prometheus部署
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:v2.37.0
        args:
        - --config.file=/etc/prometheus/prometheus.yml
        - --storage.tsdb.path=/prometheus/
        ports:
        - containerPort: 9090
```

### 日志架构

#### Fluentd日志收集
```yaml
# Fluentd DaemonSet
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1.14.6-debian-elasticsearch7-1.0
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch"
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

## 集群高可用架构

高可用性是生产环境Kubernetes集群的重要要求。

### 控制平面高可用

#### 负载均衡配置
```yaml
# 控制平面负载均衡
apiVersion: v1
kind: Service
metadata:
  name: kubernetes
  namespace: default
spec:
  ports:
  - name: https
    port: 443
    protocol: TCP
    targetPort: 6443
  selector:
    component: apiserver
    provider: kubernetes
  type: LoadBalancer
```

#### etcd集群配置
```bash
# etcd集群初始化
etcd --name etcd0 \
  --initial-advertise-peer-urls https://192.168.1.100:2380 \
  --listen-peer-urls https://192.168.1.100:2380 \
  --listen-client-urls https://192.168.1.100:2379,https://127.0.0.1:2379 \
  --advertise-client-urls https://192.168.1.100:2379 \
  --initial-cluster-token etcd-cluster-1 \
  --initial-cluster etcd0=https://192.168.1.100:2380,etcd1=https://192.168.1.101:2380,etcd2=https://192.168.1.102:2380 \
  --initial-cluster-state new \
  --data-dir /var/lib/etcd
```

### 工作节点高可用

#### 节点亲和性
```yaml
# 节点亲和性配置
apiVersion: v1
kind: Pod
metadata:
  name: with-node-affinity
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: kubernetes.io/e2e-az-name
            operator: In
            values:
            - e2e-az1
            - e2e-az2
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        preference:
          matchExpressions:
          - key: another-node-label-key
            operator: In
            values:
            - another-node-label-value
```

## 小结

Kubernetes集群架构是理解Kubernetes工作原理的基础。通过本章的学习，我们深入了解了Kubernetes集群的核心组件和架构设计：

1. **控制平面组件**：
   - **API Server**：作为集群的统一入口，提供RESTful API接口
   - **etcd**：分布式键值存储，保存集群的所有状态信息
   - **Scheduler**：负责Pod的调度决策
   - **Controller Manager**：运行各种控制器维护集群状态
   - **Cloud Controller Manager**：管理云提供商资源

2. **工作节点组件**：
   - **kubelet**：节点代理，管理节点上的Pod
   - **kube-proxy**：网络代理，实现服务发现和负载均衡
   - **容器运行时**：负责实际运行容器

3. **网络架构**：
   - 满足Pod间通信、节点间通信和外部访问的要求
   - 通过CNI插件实现网络功能

4. **安全架构**：
   - 通过认证、授权和准入控制确保集群安全
   - 实施网络策略和RBAC机制

5. **监控与日志**：
   - 通过Metrics Server和Prometheus实现监控
   - 通过Fluentd等工具实现日志收集

6. **高可用架构**：
   - 通过负载均衡和集群部署实现高可用性
   - 通过节点亲和性等机制优化资源分配

理解这些组件及其交互方式，对于有效管理和运维Kubernetes集群至关重要。在实际部署和管理Kubernetes集群时，需要根据具体需求和环境特点，合理配置这些组件，以确保集群的稳定性、安全性和高性能。

随着Kubernetes技术的不断发展，新的组件和功能也在不断涌现。建议读者持续关注Kubernetes技术的发展，学习和应用新的功能和特性，以充分发挥Kubernetes的价值。