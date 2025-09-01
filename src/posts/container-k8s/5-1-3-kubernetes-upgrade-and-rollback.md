---
title: Kubernetes升级与回滚：确保集群平滑演进的策略
date: 2025-08-31
categories: [Kubernetes]
tags: [kubernetes, upgrade, rollback, kubeadm, version-management]
published: true
---

在快速发展的云原生生态系统中，Kubernetes版本的持续更新是不可避免的。新版本带来了功能增强、安全修复和性能改进，但升级过程也伴随着风险。本章将深入探讨Kubernetes集群升级的步骤、使用Kubeadm升级集群版本的方法、回滚与恢复集群状态的策略，以及版本管理与兼容性考虑，帮助读者确保集群平滑演进。

## 升级 Kubernetes 集群的步骤

### 升级前准备

#### 版本兼容性检查

在升级之前，必须检查当前版本与目标版本的兼容性：

```bash
# 检查当前Kubernetes版本
kubectl version

# 查看可用的升级版本
kubeadm upgrade plan
```

#### 升级策略选择

Kubernetes支持两种升级策略：

1. **滚动升级**：逐个节点升级，保持集群可用性
2. **蓝绿升级**：创建新集群，迁移工作负载

#### 备份准备

```bash
# 备份etcd数据
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot-$(date +%Y%m%d-%H%M%S).db \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  --endpoints=https://127.0.0.1:2379

# 备份集群资源
kubectl get all --all-namespaces -o yaml > cluster-backup-$(date +%Y%m%d-%H%M%S).yaml
```

### 升级顺序

Kubernetes升级必须按照特定顺序进行：

1. **控制平面节点**：首先升级控制平面组件
2. **工作节点**：然后逐个升级工作节点
3. **应用兼容性**：最后验证应用兼容性

### 升级验证

#### 升级前验证

```bash
# 检查集群健康状态
kubectl get nodes
kubectl get componentstatuses
kubectl get pods --all-namespaces

# 检查关键应用状态
kubectl get deployments --all-namespaces
kubectl get services --all-namespaces
```

#### 升级后验证

```bash
# 验证版本升级
kubectl version

# 验证组件状态
kubectl get componentstatuses

# 验证应用功能
kubectl run test-pod --image=nginx --restart=Never
kubectl wait --for=condition=ready pod/test-pod
kubectl delete pod test-pod
```

## 使用 Kubeadm 升级集群版本

### 控制平面升级

#### 升级kubeadm工具

```bash
# 卸载旧版本kubeadm
apt-mark unhold kubeadm && \
apt-get update && apt-get install -y kubeadm=1.25.0-00 && \
apt-mark hold kubeadm

# 验证kubeadm版本
kubeadm version
```

#### 查看升级计划

```bash
# 查看可用的升级版本
kubeadm upgrade plan

# 查看特定版本的升级计划
kubeadm upgrade plan v1.25.0
```

#### 执行控制平面升级

```bash
# 应用升级
kubeadm upgrade apply v1.25.0

# 仅升级第一个控制平面节点
kubeadm upgrade apply v1.25.0 --certificate-renewal=true

# 升级其他控制平面节点
kubeadm upgrade node
```

#### 升级控制平面组件

```bash
# 升级kubelet和kubectl
apt-mark unhold kubelet kubectl && \
apt-get update && apt-get install -y kubelet=1.25.0-00 kubectl=1.25.0-00 && \
apt-mark hold kubelet kubectl

# 重启kubelet
systemctl daemon-reload
systemctl restart kubelet
```

### 工作节点升级

#### 升级工作节点kubeadm

```bash
# 在工作节点上升级kubeadm
apt-mark unhold kubeadm && \
apt-get update && apt-get install -y kubeadm=1.25.0-00 && \
apt-mark hold kubeadm
```

#### 排空节点

```bash
# 排空节点上的Pod
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 强制排空（谨慎使用）
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --force
```

#### 升级节点组件

```bash
# 在工作节点上执行升级
kubeadm upgrade node

# 升级kubelet和kubectl
apt-mark unhold kubelet kubectl && \
apt-get update && apt-get install -y kubelet=1.25.0-00 kubectl=1.25.0-00 && \
apt-mark hold kubelet kubectl

# 重启kubelet
systemctl daemon-reload
systemctl restart kubelet
```

#### 恢复节点调度

```bash
# 恢复节点调度
kubectl uncordon <node-name>
```

### 升级验证与监控

#### 升级后验证

```bash
# 验证节点版本
kubectl get nodes

# 验证组件版本
kubectl get componentstatuses

# 验证Pod状态
kubectl get pods --all-namespaces
```

#### 监控升级过程

```bash
# 监控节点状态
watch kubectl get nodes

# 监控Pod状态
watch kubectl get pods --all-namespaces

# 查看升级日志
journalctl -u kubelet -f
```

## 回滚与恢复集群状态

### 回滚策略

#### 版本回滚

当升级出现问题时，可以回滚到之前的稳定版本：

```bash
# 回滚kubeadm版本
apt-mark unhold kubeadm && \
apt-get update && apt-get install -y kubeadm=1.24.0-00 && \
apt-mark hold kubeadm
```

#### 控制平面回滚

```bash
# 回滚控制平面
kubeadm upgrade apply v1.24.0

# 回滚节点
kubeadm upgrade node
```

### 数据恢复

#### 从etcd快照恢复

```bash
# 停止etcd服务
systemctl stop etcd

# 从快照恢复
ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd-snapshot.db \
  --data-dir=/var/lib/etcd \
  --initial-cluster="etcd-1=https://192.168.1.101:2380,etcd-2=https://192.168.1.102:2380,etcd-3=https://192.168.1.103:2380" \
  --initial-cluster-token="etcd-cluster-1" \
  --name="etcd-1" \
  --initial-advertise-peer-urls="https://192.168.1.101:2380"

# 启动etcd服务
systemctl start etcd
```

#### 从备份恢复资源

```bash
# 恢复集群资源
kubectl apply -f cluster-backup.yaml
```

### 应用回滚

#### 使用Deployment回滚

```bash
# 查看部署历史
kubectl rollout history deployment/<deployment-name>

# 回滚到上一个版本
kubectl rollout undo deployment/<deployment-name>

# 回滚到指定版本
kubectl rollout undo deployment/<deployment-name> --to-revision=2
```

#### 使用Helm回滚

```bash
# 查看Release历史
helm history <release-name>

# 回滚到上一个版本
helm rollback <release-name> 0

# 回滚到指定版本
helm rollback <release-name> 2
```

## 版本管理与兼容性考虑

### 版本策略

#### Kubernetes版本命名

Kubernetes版本采用语义化版本控制：
- **主版本**：重大变化
- **次版本**：新增功能
- **修订版本**：错误修复

#### 支持策略

Kubernetes通常支持最近的三个次要版本：
- **当前版本**：最新稳定版本
- **前一个版本**：仍在支持期内
- **前两个版本**：仍在支持期内

### 兼容性考虑

#### 组件版本兼容性

```bash
# 检查kubeadm、kubelet、kubectl版本兼容性
kubeadm version
kubectl version
kubelet --version
```

#### API版本兼容性

```yaml
# 使用稳定的API版本
apiVersion: apps/v1  # 推荐
kind: Deployment
metadata:
  name: app-deployment
```

避免使用已弃用的API版本：

```bash
# 检查已弃用的API使用情况
kubectl api-resources --deprecated=true
```

### 升级规划

#### 升级时间窗口

```bash
# 检查集群维护窗口
# 通常选择业务低峰期进行升级
```

#### 升级测试

```bash
# 在测试环境中验证升级
# 1. 创建测试集群
# 2. 部署应用
# 3. 执行升级
# 4. 验证功能
```

#### 回滚计划

```bash
# 制定详细的回滚计划
# 1. 确定回滚触发条件
# 2. 准备回滚脚本
# 3. 验证回滚流程
# 4. 文档化回滚步骤
```

### 自动化升级

#### 使用Kubernetes Operator

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: upgrade-operator
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: upgrade-operator
  template:
    metadata:
      labels:
        app: upgrade-operator
    spec:
      containers:
      - name: operator
        image: upgrade-operator:latest
        command:
        - /upgrade-operator
        - --upgrade-schedule="0 2 * * 0"  # 每周日凌晨2点
        - --backup-before-upgrade=true
        - --health-check-after-upgrade=true
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

#### 升级脚本自动化

```bash
#!/bin/bash
# automated-upgrade.sh

set -e

echo "Starting automated Kubernetes upgrade..."

# 1. 检查当前版本
CURRENT_VERSION=$(kubectl version --short | grep Server | awk '{print $3}')
echo "Current version: $CURRENT_VERSION"

# 2. 检查可用升级
UPGRADE_PLAN=$(kubeadm upgrade plan)
echo "Upgrade plan: $UPGRADE_PLAN"

# 3. 备份集群
echo "Creating backup..."
./backup-cluster.sh

# 4. 升级控制平面
echo "Upgrading control plane..."
./upgrade-control-plane.sh

# 5. 升级工作节点
echo "Upgrading worker nodes..."
./upgrade-worker-nodes.sh

# 6. 验证升级
echo "Verifying upgrade..."
./verify-upgrade.sh

echo "Upgrade completed successfully!"
```

通过本章的学习，读者应该能够深入理解Kubernetes集群升级的重要性和复杂性，掌握使用Kubeadm进行集群版本升级的详细步骤，了解回滚与恢复集群状态的策略和方法，以及制定版本管理与兼容性考虑的规划。这些知识对于确保集群平滑演进和业务连续性至关重要。