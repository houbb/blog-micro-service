---
title: Kubernetes高可用集群：构建企业级可靠容器平台
date: 2025-08-31
categories: [Kubernetes]
tags: [kubernetes, high-availability, etcd, clustering, fault-tolerance]
published: true
---

在生产环境中，Kubernetes集群的高可用性是确保业务连续性和系统稳定性的关键要求。单点故障可能导致整个系统不可用，造成严重的业务影响。本章将深入探讨构建高可用Kubernetes集群的核心组件、Etcd集群的高可用与备份策略、控制平面故障切换与恢复机制，以及集群容错与灾备方案，帮助读者构建企业级可靠的容器平台。

## 构建高可用 Kubernetes 控制平面

### 高可用架构设计

高可用Kubernetes集群的核心是消除单点故障，确保在任何组件出现故障时系统仍能正常运行。

#### 控制平面组件高可用

1. **API Server**：多实例部署，前端负载均衡
2. **Controller Manager**：主备模式或领导者选举
3. **Scheduler**：主备模式或领导者选举
4. **etcd**：奇数节点集群，确保数据一致性

#### 高可用架构图

```
                    ┌─────────────┐
                    │ Load Balancer │
                    └──────┬──────┘
                           │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
│ Control Plane │ │ Control Plane │ │ Control Plane │
│   Node 1      │ │   Node 2      │ │   Node 3      │
└───────────────┘ └───────────────┘ └───────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                   ┌──────▼──────┐
                   │   Worker    │
                   │   Nodes     │
                   └─────────────┘
```

### 控制平面组件配置

#### API Server 高可用配置

```yaml
# kubeadm-config.yaml
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
kubernetesVersion: v1.24.0
controlPlaneEndpoint: "k8s-api.example.com:6443"
apiServer:
  certSANs:
  - "k8s-api.example.com"
  - "192.168.1.100"
  extraArgs:
    authorization-mode: "Node,RBAC"
    enable-admission-plugins: "NodeRestriction"
  extraVolumes:
  - name: audit-log
    hostPath: "/var/log/kubernetes"
    mountPath: "/var/log/kubernetes"
    readOnly: false
    pathType: "DirectoryOrCreate"
```

#### Controller Manager 配置

```yaml
controllerManager:
  extraArgs:
    bind-address: "0.0.0.0"
    cluster-signing-cert-file: "/etc/kubernetes/pki/ca.crt"
    cluster-signing-key-file: "/etc/kubernetes/pki/ca.key"
    profiling: "false"
  extraVolumes:
  - name: etc-kubernetes-pki
    hostPath: "/etc/kubernetes/pki"
    mountPath: "/etc/kubernetes/pki"
    readOnly: true
    pathType: "Directory"
```

#### Scheduler 配置

```yaml
scheduler:
  extraArgs:
    bind-address: "0.0.0.0"
    profiling: "false"
```

### 负载均衡器配置

#### 使用 HAProxy

```bash
# haproxy.cfg
global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

defaults
    log global
    mode tcp
    option tcplog
    option dontlognull
    timeout connect 5000
    timeout client 50000
    timeout server 50000

frontend k8s-api
    bind *:6443
    default_backend k8s-api-backend

backend k8s-api-backend
    balance roundrobin
    server control-plane-1 192.168.1.101:6443 check
    server control-plane-2 192.168.1.102:6443 check
    server control-plane-3 192.168.1.103:6443 check
```

#### 使用 Keepalived

```bash
# keepalived.conf
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
        192.168.1.100/24
    }
}
```

## 高可用 Etcd 集群与备份

### Etcd 高可用架构

Etcd是Kubernetes的核心数据存储，必须保证其高可用性。

#### Etcd 集群要求

1. **奇数节点**：通常3、5或7个节点
2. **网络隔离**：专用网络或TLS加密
3. **存储性能**：SSD存储，低延迟
4. **资源分配**：足够的CPU和内存

#### Etcd 集群配置

```yaml
# etcd 集群配置
etcd:
  local:
    serverCertSANs:
    - "192.168.1.101"
    - "192.168.1.102"
    - "192.168.1.103"
    - "k8s-etcd.example.com"
    peerCertSANs:
    - "192.168.1.101"
    - "192.168.1.102"
    - "192.168.1.103"
    - "k8s-etcd.example.com"
  extraArgs:
    auto-compaction-mode: "periodic"
    auto-compaction-retention: "12h"
    quota-backend-bytes: "8589934592"
```

### Etcd 备份策略

#### 定期备份

```bash
#!/bin/bash
# etcd-backup.sh

# 设置变量
ETCDCTL_API=3
ETCDCTL_CACERT=/etc/kubernetes/pki/etcd/ca.crt
ETCDCTL_CERT=/etc/kubernetes/pki/etcd/server.crt
ETCDCTL_KEY=/etc/kubernetes/pki/etcd/server.key
ETCDCTL_ENDPOINTS=https://127.0.0.1:2379

# 创建备份
etcdctl snapshot save /backup/etcd-snapshot-$(date +%Y%m%d-%H%M%S).db \
  --cacert=$ETCDCTL_CACERT \
  --cert=$ETCDCTL_CERT \
  --key=$ETCDCTL_KEY \
  --endpoints=$ETCDCTL_ENDPOINTS

# 清理旧备份（保留最近7天）
find /backup -name "etcd-snapshot-*.db" -mtime +7 -delete
```

#### 使用 Velero 备份 Etcd

```bash
# 创建VolumeSnapshotClass
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: etcd-snapshot-class
driver: hostpath.csi.k8s.io
deletionPolicy: Delete

---
# 创建VolumeSnapshot
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: etcd-snapshot
spec:
  volumeSnapshotClassName: etcd-snapshot-class
  source:
    persistentVolumeClaimName: etcd-data
```

### Etcd 恢复操作

#### 从快照恢复

```bash
# 停止etcd服务
systemctl stop etcd

# 从快照恢复
ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd-snapshot-20230101-120000.db \
  --data-dir=/var/lib/etcd \
  --initial-cluster="etcd-1=https://192.168.1.101:2380,etcd-2=https://192.168.1.102:2380,etcd-3=https://192.168.1.103:2380" \
  --initial-cluster-token="etcd-cluster-1" \
  --name="etcd-1" \
  --initial-advertise-peer-urls="https://192.168.1.101:2380"

# 启动etcd服务
systemctl start etcd
```

#### 集群重新初始化

```bash
# 在所有etcd节点上执行
kubeadm reset

# 重新初始化第一个节点
kubeadm init --config kubeadm-config.yaml --upload-certs

# 其他节点加入集群
kubeadm join k8s-api.example.com:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash> \
  --control-plane \
  --certificate-key <certificate-key>
```

## 控制平面故障切换与恢复

### 故障检测机制

#### 健康检查端点

```bash
# 检查API Server健康状态
curl -k https://localhost:6443/healthz

# 检查etcd健康状态
ETCDCTL_API=3 etcdctl endpoint health \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  --endpoints=https://127.0.0.1:2379
```

#### 监控告警配置

```yaml
# Prometheus告警规则
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: control-plane-alerts
  namespace: monitoring
spec:
  groups:
  - name: control-plane.rules
    rules:
    - alert: APIServerDown
      expr: up{job="apiserver"} == 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "API Server is down"
        description: "API Server has been down for more than 5 minutes."

    - alert: EtcdClusterUnavailable
      expr: etcd_server_has_leader == 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Etcd cluster is unavailable"
        description: "Etcd cluster has no leader for more than 5 minutes."
```

### 故障切换流程

#### API Server故障切换

```bash
# 检查API Server状态
kubectl get componentstatuses

# 如果API Server无响应，检查负载均衡器
curl -k https://k8s-api.example.com:6443/healthz

# 检查控制平面节点状态
kubectl get nodes -l node-role.kubernetes.io/control-plane=
```

#### Controller Manager故障切换

```bash
# 检查Controller Manager领导者
kubectl get endpoints kube-controller-manager -n kube-system -o yaml

# 重启Controller Manager
systemctl restart kube-controller-manager
```

#### Scheduler故障切换

```bash
# 检查Scheduler领导者
kubectl get endpoints kube-scheduler -n kube-system -o yaml

# 重启Scheduler
systemctl restart kube-scheduler
```

### 自动恢复机制

#### 使用Kubernetes Operator

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: control-plane-operator
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: control-plane-operator
  template:
    metadata:
      labels:
        app: control-plane-operator
    spec:
      containers:
      - name: operator
        image: control-plane-operator:latest
        command:
        - /control-plane-operator
        - --health-check-interval=30s
        - --auto-recovery=true
        volumeMounts:
        - name: kubeconfig
          mountPath: /etc/kubernetes
          readOnly: true
      volumes:
      - name: kubeconfig
        hostPath:
          path: /etc/kubernetes
          type: Directory
```

## 集群容错与灾备方案

### 多区域部署

#### 区域拓扑分布

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: multi-region-app
spec:
  replicas: 6
  template:
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: multi-region-app
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/region
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: multi-region-app
```

#### 跨区域服务发现

```yaml
apiVersion: v1
kind: Service
metadata:
  name: global-service
spec:
  type: ExternalName
  externalName: app.region1.example.com
```

### 灾备恢复方案

#### 冷备方案

```bash
#!/bin/bash
# disaster-recovery-cold.sh

# 备份集群状态
kubectl get all --all-namespaces -o yaml > cluster-backup.yaml

# 备份etcd数据
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot.db \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# 备份配置文件
tar -czf k8s-config-backup.tar.gz /etc/kubernetes/
```

#### 热备方案

```yaml
# 使用Velero进行持续备份
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: daily-backup
  namespace: velero
spec:
  schedule: "0 1 * * *"
  template:
    includedNamespaces:
    - "*"
    includedResources:
    - "*"
    includeClusterResources: true
    storageLocation: default
    ttl: "168h0m0s"
```

### 业务连续性规划

#### RTO和RPO定义

- **RTO（Recovery Time Objective）**：恢复时间目标
- **RPO（Recovery Point Objective）**：恢复点目标

#### 灾备演练

```bash
#!/bin/bash
# disaster-recovery-drill.sh

echo "Starting disaster recovery drill..."

# 1. 模拟主集群故障
echo "Simulating primary cluster failure..."
# (实际操作中需要谨慎执行)

# 2. 激活备用集群
echo "Activating backup cluster..."
kubectl config use-context backup-cluster

# 3. 恢复应用状态
echo "Restoring application state..."
velero restore create --from-backup latest-backup

# 4. 验证应用功能
echo "Verifying application functionality..."
kubectl get pods --all-namespaces

# 5. 记录演练结果
echo "Disaster recovery drill completed at $(date)" >> /var/log/dr-drill.log
```

### 监控与告警

#### 集群健康仪表板

```yaml
# Grafana仪表板配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-health-dashboard
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  cluster-health.json: |-
    {
      "dashboard": {
        "title": "Cluster Health Overview",
        "panels": [
          {
            "title": "Control Plane Health",
            "type": "stat",
            "targets": [
              {
                "expr": "up{job=\"apiserver\"}",
                "legendFormat": "API Server"
              }
            ]
          },
          {
            "title": "Etcd Cluster Health",
            "type": "stat",
            "targets": [
              {
                "expr": "etcd_server_has_leader",
                "legendFormat": "Etcd Leader"
              }
            ]
          }
        ]
      }
    }
```

通过本章的学习，读者应该能够深入理解构建高可用Kubernetes集群的核心原理和实践方法，掌握Etcd集群的高可用配置与备份策略，了解控制平面故障切换与恢复机制，以及制定和实施集群容错与灾备方案。这些知识对于构建企业级可靠的容器平台至关重要。