---
title: Managing Docker Containers with Kubernetes - Mastering Container Orchestration
date: 2025-08-31
categories: [Docker]
tags: [container-docker]
published: true
---

## 使用 Kubernetes 管理 Docker 容器

### Kubernetes 容器管理基础

Kubernetes 作为容器编排平台，提供了强大的容器管理功能。虽然 Kubernetes 可以与多种容器运行时集成，但与 Docker 的集成仍然是最常见的使用场景。通过 Kubernetes，用户可以实现容器的自动化部署、扩展和管理。

#### 核心管理概念

1. **Pod**：
   - Kubernetes 中最小的部署单元
   - 可以包含一个或多个容器
   - 共享网络和存储资源

2. **Deployment**：
   - 声明式管理 Pod 副本
   - 支持滚动更新和回滚

3. **Service**：
   - 提供服务发现和负载均衡
   - 抽象化 Pod 访问方式

### 部署 Docker 容器

#### 基本部署

```yaml
# nginx-deployment.yaml
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

```bash
# 部署应用
kubectl apply -f nginx-deployment.yaml

# 查看部署状态
kubectl get deployments

# 查看 Pod 状态
kubectl get pods
```

#### 配置管理

```yaml
# app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:latest
        ports:
        - containerPort: 8080
        env:
        - name: ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
```

### 容器生命周期管理

#### 启动和停止

```bash
# 启动应用
kubectl apply -f deployment.yaml

# 停止应用
kubectl delete deployment myapp

# 优雅停止
kubectl scale deployment myapp --replicas=0
```

#### 扩展和缩减

```bash
# 扩展副本数
kubectl scale deployment myapp --replicas=5

# 自动扩展
kubectl autoscale deployment myapp --cpu-percent=80 --min=2 --max=10
```

#### 更新和回滚

```bash
# 更新镜像
kubectl set image deployment/myapp app=myapp:v2

# 查看更新状态
kubectl rollout status deployment/myapp

# 回滚到上一个版本
kubectl rollout undo deployment/myapp

# 回滚到指定版本
kubectl rollout undo deployment/myapp --to-revision=2
```

### 容器网络管理

#### Service 配置

```yaml
# app-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: ClusterIP
```

```yaml
# 外部访问 Service
apiVersion: v1
kind: Service
metadata:
  name: app-external-service
spec:
  selector:
    app: myapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

#### Ingress 配置

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-service
            port:
              number: 80
```

### 容器存储管理

#### PersistentVolume 配置

```yaml
# pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: app-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /mnt/data
```

#### PersistentVolumeClaim 配置

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 3Gi
```

#### 在容器中使用存储

```yaml
# deployment-with-storage.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-with-storage
spec:
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:latest
        volumeMounts:
        - name: app-storage
          mountPath: /app/data
      volumes:
      - name: app-storage
        persistentVolumeClaim:
          claimName: app-pvc
```

### 容器安全配置

#### 镜像安全

```yaml
# secure-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
spec:
  selector:
    matchLabels:
      app: secure-app
  template:
    metadata:
      labels:
        app: secure-app
    spec:
      containers:
      - name: app
        image: myapp:v1.0.0  # 使用具体版本而非 latest
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
        ports:
        - containerPort: 8080
```

#### 网络策略

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

### 容器监控和日志

#### 资源监控

```bash
# 查看 Pod 资源使用
kubectl top pods

# 查看节点资源使用
kubectl top nodes

# 查看详细资源信息
kubectl describe pod <pod-name>
```

#### 日志管理

```bash
# 查看 Pod 日志
kubectl logs <pod-name>

# 实时查看日志
kubectl logs -f <pod-name>

# 查看前一个容器实例的日志
kubectl logs --previous <pod-name>

# 查看多个容器的日志
kubectl logs -l app=myapp
```

### 容器调试技巧

#### 进入容器

```bash
# 进入容器执行命令
kubectl exec -it <pod-name> -- /bin/bash

# 在容器中执行单个命令
kubectl exec <pod-name> -- ps aux

# 进入特定容器（多容器 Pod）
kubectl exec -it <pod-name> -c <container-name> -- /bin/bash
```

#### 问题诊断

```bash
# 查看 Pod 详细信息
kubectl describe pod <pod-name>

# 查看事件
kubectl get events

# 检查配置
kubectl get deployment <deployment-name> -o yaml
```

### 最佳实践

#### 资源管理

1. **设置资源限制**：
   - 防止容器消耗过多资源
   - 提高集群稳定性

2. **使用命名空间**：
   - 隔离不同环境或团队的资源
   - 简化资源管理

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
```

#### 配置管理

1. **使用 ConfigMap 管理配置**：
   - 分离配置和应用代码
   - 简化配置更新

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "postgresql://localhost:5432/myapp"
  log_level: "info"
```

2. **使用 Secret 管理敏感信息**：
   - 安全存储密码、密钥等
   - 加密存储敏感数据

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: bXl1c2Vy  # base64 encoded
  password: bXlwYXNzd29yZA==  # base64 encoded
```

#### 健康检查

1. **配置存活探针**：
   - 检测容器是否正常运行
   - 自动重启不健康的容器

2. **配置就绪探针**：
   - 检测容器是否准备好接收流量
   - 控制服务流量分发

```yaml
# health-checks.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-with-health-checks
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

通过本节内容，我们深入了解了如何使用 Kubernetes 管理 Docker 容器，包括部署、扩展、更新、网络配置、存储管理、安全配置等方面。掌握这些技能将帮助您更好地利用 Kubernetes 管理容器化应用。