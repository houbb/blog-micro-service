---
title: Kubernetes部署与扩缩容：实现应用的弹性与高可用
date: 2025-08-31
categories: [Kubernetes]
tags: [kubernetes, deployment, scaling, replicas, updates]
published: true
---

在云原生时代，应用的部署和扩缩容能力是实现弹性、高可用和成本效益的关键。Kubernetes通过Deployment等控制器提供了强大的部署和扩缩容功能。本章将深入探讨如何使用Kubernetes管理应用的部署生命周期，实现无缝的扩缩容和可靠的更新策略。

## 使用 Deployment 管理应用

### Deployment 的核心概念

Deployment是Kubernetes中用于管理应用部署的高级抽象，它为Pod和ReplicaSet提供了声明式的更新能力。通过Deployment，用户可以轻松地部署应用、更新应用版本以及回滚到之前的版本。

Deployment的主要功能包括：
- 声明式应用管理
- 滚动更新和回滚
- 扩缩容管理
- 版本历史记录

### 创建 Deployment

创建Deployment的基本步骤：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
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

应用Deployment配置：
```bash
kubectl apply -f nginx-deployment.yaml
```

### Deployment 的关键字段

- **replicas**：期望的Pod副本数量
- **selector**：标签选择器，用于识别属于该Deployment的Pod
- **template**：Pod模板，定义了要创建的Pod规格
- **strategy**：更新策略，控制如何执行更新

## 扩展与缩减副本数

### 手动扩缩容

Kubernetes支持通过命令行或修改Deployment配置来手动调整副本数量。

#### 使用 kubectl scale 命令

```bash
# 扩展到5个副本
kubectl scale deployment/nginx-deployment --replicas=5

# 缩减到2个副本
kubectl scale deployment/nginx-deployment --replicas=2
```

#### 通过编辑Deployment配置

```bash
# 编辑Deployment配置
kubectl edit deployment/nginx-deployment
```

然后修改replicas字段的值。

### 自动扩缩容

Kubernetes Horizontal Pod Autoscaler (HPA) 可以根据CPU使用率或其他自定义指标自动调整副本数量。

#### 创建HPA

```bash
# 基于CPU使用率创建HPA
kubectl autoscale deployment/nginx-deployment --cpu-percent=50 --min=1 --max=10
```

#### 自定义指标扩缩容

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
  - type: Pods
    pods:
      metric:
        name: packets-per-second
      target:
        type: AverageValue
        averageValue: 1k
```

### 垂直扩缩容

Vertical Pod Autoscaler (VPA) 可以自动调整Pod的资源请求和限制。

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: nginx-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  updatePolicy:
    updateMode: "Auto"
```

## 滚动更新与回滚

### 滚动更新机制

滚动更新是Deployment的默认更新策略，它通过逐步替换旧Pod来实现无缝更新，确保应用在更新过程中始终可用。

#### 更新过程

1. 创建新的ReplicaSet
2. 逐步增加新ReplicaSet的副本数
3. 逐步减少旧ReplicaSet的副本数
4. 清理旧ReplicaSet

#### 控制滚动更新

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%  # 最大不可用Pod比例
      maxSurge: 25%        # 最大超出期望副本数的比例
```

### 执行更新

#### 通过修改镜像版本

```bash
# 更新Deployment中的镜像版本
kubectl set image deployment/nginx-deployment nginx=nginx:1.16.1
```

#### 通过编辑Deployment配置

```bash
# 编辑Deployment配置
kubectl edit deployment/nginx-deployment
```

### 回滚操作

当更新出现问题时，可以快速回滚到之前的稳定版本。

#### 查看更新历史

```bash
# 查看Deployment的更新历史
kubectl rollout history deployment/nginx-deployment

# 查看特定版本的详细信息
kubectl rollout history deployment/nginx-deployment --revision=2
```

#### 执行回滚

```bash
# 回滚到上一个版本
kubectl rollout undo deployment/nginx-deployment

# 回滚到指定版本
kubectl rollout undo deployment/nginx-deployment --to-revision=2
```

#### 暂停和恢复更新

```bash
# 暂停Deployment的更新
kubectl rollout pause deployment/nginx-deployment

# 恢复Deployment的更新
kubectl rollout resume deployment/nginx-deployment
```

## 自定义更新策略与部署策略

### 更新策略类型

#### RollingUpdate（默认）

逐步替换Pod，确保应用持续可用。

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

#### Recreate

一次性删除所有旧Pod，然后创建新Pod。

```yaml
spec:
  strategy:
    type: Recreate
```

### 部署策略优化

#### 资源请求和限制

为确保更新过程中的稳定性，应合理设置资源请求和限制：

```yaml
spec:
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
```

#### 健康检查

配置合适的健康检查探针确保更新过程的可靠性：

```yaml
spec:
  template:
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 进行多环境（Dev、Test、Prod）部署

### 环境差异化配置

不同环境通常需要不同的配置，可以通过以下方式实现：

#### 使用 ConfigMap 和 Secret

```yaml
# 开发环境配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config-dev
data:
  environment: development
  log.level: debug

---
# 生产环境配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config-prod
data:
  environment: production
  log.level: warn
```

#### 使用命名空间隔离

```bash
# 创建不同环境的命名空间
kubectl create namespace dev
kubectl create namespace test
kubectl create namespace prod
```

### 部署策略

#### 蓝绿部署

通过维护两个相同的生产环境（蓝环境和绿环境）来实现零停机部署：

```bash
# 部署新版本到绿环境
kubectl apply -f app-green.yaml

# 测试通过后切换流量
kubectl patch service/app-service -p '{"spec":{"selector":{"version":"green"}}}'
```

#### 金丝雀部署

逐步将流量从旧版本切换到新版本：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
spec:
  replicas: 1  # 少量副本用于金丝雀测试
  selector:
    matchLabels:
      app: app
      version: canary
  template:
    metadata:
      labels:
        app: app
        version: canary
    spec:
      containers:
      - name: app
        image: app:v2.0
```

通过本章的学习，读者应该能够熟练使用Kubernetes的Deployment控制器管理应用的完整生命周期，实现灵活的扩缩容策略，执行可靠的更新和回滚操作，并在不同环境中部署应用。这些技能对于构建弹性、高可用的云原生应用至关重要。