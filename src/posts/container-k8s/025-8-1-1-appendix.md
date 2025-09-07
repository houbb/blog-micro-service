---
title: Kubernetes附录：实用工具与最佳实践
date: 2025-08-31
categories: [Kubernetes]
tags: [container-k8s]
published: true
---

本附录汇集了Kubernetes使用过程中的实用工具、命令参考、故障排查技巧以及最佳实践，为读者提供快速查阅和实践指导。

## 常用 Kubernetes 命令与工具总结

### 基础命令

#### 集群管理命令

```bash
# 查看集群信息
kubectl cluster-info

# 查看集群状态
kubectl get componentstatuses

# 查看节点信息
kubectl get nodes
kubectl describe node <node-name>

# 查看命名空间
kubectl get namespaces
```

#### Pod管理命令

```bash
# 查看Pod
kubectl get pods
kubectl get pods --all-namespaces
kubectl describe pod <pod-name>

# 进入Pod
kubectl exec -it <pod-name> -- /bin/bash

# 查看Pod日志
kubectl logs <pod-name>
kubectl logs -f <pod-name>

# 删除Pod
kubectl delete pod <pod-name>
```

#### Deployment管理命令

```bash
# 查看Deployment
kubectl get deployments
kubectl describe deployment <deployment-name>

# 更新Deployment
kubectl set image deployment/<deployment-name> <container-name>=<image-name>:<tag>

# 扩缩容Deployment
kubectl scale deployment/<deployment-name> --replicas=<number>

# 回滚Deployment
kubectl rollout undo deployment/<deployment-name>
```

#### Service管理命令

```bash
# 查看Service
kubectl get services
kubectl describe service <service-name>

# 暴露Deployment为Service
kubectl expose deployment <deployment-name> --type=NodePort --port=<port>
```

### 高级命令

#### 资源管理

```bash
# 查看资源使用情况
kubectl top nodes
kubectl top pods

# 查看资源配额
kubectl get resourcequotas
kubectl describe resourcequota <quota-name>

# 查看限制范围
kubectl get limitranges
kubectl describe limitrange <limitrange-name>
```

#### 网络管理

```bash
# 查看网络策略
kubectl get networkpolicies
kubectl describe networkpolicy <policy-name>

# 端口转发
kubectl port-forward <pod-name> <local-port>:<pod-port>

# 代理API服务器
kubectl proxy
```

#### 配置管理

```bash
# 查看配置
kubectl config view

# 切换上下文
kubectl config use-context <context-name>

# 设置别名
alias k='kubectl'
alias kctx='kubectl config use-context'
alias kns='kubectl config set-context --current --namespace'
```

### 实用工具

#### kubectl插件

```bash
# 安装krew插件管理器
curl -fsSLO https://github.com/kubernetes-sigs/krew/releases/latest/download/krew.tar.gz
tar zxvf krew.tar.gz
./krew-linux_amd64 install krew

# 常用插件
kubectl krew install ctx      # 切换上下文
kubectl krew install ns       # 切换命名空间
kubectl krew install tree     # 以树形结构显示资源
kubectl krew install neat     # 清理资源配置
kubectl krew install whoami   # 显示当前用户信息
```

#### Helm工具

```bash
# Helm常用命令
helm list                    # 列出Release
helm status <release-name>   # 查看Release状态
helm upgrade                 # 升级Release
helm rollback <release-name> # 回滚Release
helm uninstall <release-name> # 删除Release
```

#### 监控工具

```bash
# 安装Lens (图形化Kubernetes管理工具)
# 访问 https://k8slens.dev/ 下载安装

# 安装K9s (终端Kubernetes管理工具)
curl -sS https://webinstall.dev/k9s | bash
```

## Kubernetes 集群故障排查技巧

### 节点故障排查

#### 节点状态检查

```bash
# 检查节点状态
kubectl get nodes

# 详细查看节点信息
kubectl describe node <node-name>

# 检查节点资源使用情况
kubectl top nodes
```

#### 常见节点问题

1. **节点NotReady状态**
   ```bash
   # 检查kubelet状态
   systemctl status kubelet
   
   # 查看kubelet日志
   journalctl -u kubelet -f
   ```

2. **节点资源不足**
   ```bash
   # 检查节点资源
   kubectl describe node <node-name>
   
   # 驱逐Pod释放资源
   kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
   ```

### Pod故障排查

#### Pod状态检查

```bash
# 查看Pod状态
kubectl get pods

# 详细查看Pod信息
kubectl describe pod <pod-name>

# 查看Pod日志
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # 查看前一个容器实例日志
```

#### 常见Pod问题

1. **Pod卡在Pending状态**
   ```bash
   # 检查资源请求和限制
   kubectl describe pod <pod-name>
   
   # 检查节点资源
   kubectl describe node <node-name>
   ```

2. **Pod不断重启**
   ```bash
   # 查看详细状态
   kubectl describe pod <pod-name>
   
   # 查看应用日志
   kubectl logs <pod-name> --previous
   ```

3. **Pod CrashLoopBackOff**
   ```bash
   # 检查容器启动命令
   kubectl describe pod <pod-name>
   
   # 进入容器调试
   kubectl exec -it <pod-name> -- /bin/sh
   ```

### 网络故障排查

#### Service访问问题

```bash
# 检查Service配置
kubectl describe service <service-name>

# 检查Endpoints
kubectl get endpoints <service-name>

# 测试Service连通性
kubectl run debug --image=busybox --rm -it --restart=Never -- wget -qO- http://<service-name>:<port>
```

#### 网络策略问题

```bash
# 查看网络策略
kubectl get networkpolicies

# 检查策略配置
kubectl describe networkpolicy <policy-name>

# 测试网络连通性
kubectl run debug --image=busybox --rm -it --restart=Never -- ping <target-ip>
```

### 存储故障排查

#### PV/PVC问题

```bash
# 检查PVC状态
kubectl get pvc
kubectl describe pvc <pvc-name>

# 检查PV状态
kubectl get pv
kubectl describe pv <pv-name>
```

#### 存储类问题

```bash
# 查看存储类
kubectl get storageclasses

# 检查存储类配置
kubectl describe storageclass <storageclass-name>
```

## Kubernetes 配置与管理最佳实践

### 安全最佳实践

#### RBAC配置

```yaml
# 最小权限原则
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

---
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

#### 网络策略

```yaml
# 默认拒绝所有流量
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

#### Pod安全策略

```yaml
# Pod安全上下文
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: app
    image: nginx
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

### 资源管理最佳实践

#### 资源请求和限制

```yaml
# 合理设置资源请求和限制
apiVersion: v1
kind: Pod
metadata:
  name: resource-managed-pod
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

#### 资源配额

```yaml
# 命名空间资源配额
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 1Gi
    limits.cpu: "2"
    limits.memory: 2Gi
    requests.nvidia.com/gpu: 4
```

### 监控与日志最佳实践

#### 健康检查

```yaml
# 配置存活和就绪探针
apiVersion: v1
kind: Pod
metadata:
  name: health-check-pod
spec:
  containers:
  - name: app
    image: nginx
    livenessProbe:
      httpGet:
        path: /healthz
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

#### 日志管理

```yaml
# 结构化日志配置
apiVersion: v1
kind: Pod
metadata:
  name: logging-pod
spec:
  containers:
  - name: app
    image: nginx
    env:
    - name: LOG_FORMAT
      value: "json"
    - name: LOG_LEVEL
      value: "info"
```

### 部署最佳实践

#### 蓝绿部署

```yaml
# 蓝绿部署策略
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: app
        image: myapp:v1.0
```

#### 金丝雀部署

```yaml
# 金丝雀部署策略
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: myapp
      version: stable
  template:
    metadata:
      labels:
        app: myapp
        version: stable
    spec:
      containers:
      - name: app
        image: myapp:v1.0

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
      version: canary
  template:
    metadata:
      labels:
        app: myapp
        version: canary
    spec:
      containers:
      - name: app
        image: myapp:v1.1
```

## 参考文献与进一步阅读资源

### 官方文档

1. **Kubernetes官方文档**: https://kubernetes.io/docs/
2. **Kubernetes GitHub仓库**: https://github.com/kubernetes/kubernetes
3. **Kubernetes博客**: https://kubernetes.io/blog/

### 书籍推荐

1. **《Kubernetes权威指南》** - 龚正等著
2. **《Kubernetes in Action》** - Marko Luksa著
3. **《Programming Kubernetes》** - Stefan Schimanski等著

### 在线课程

1. **Kubernetes官方培训**: https://kubernetes.io/training/
2. **Coursera Kubernetes课程**: https://www.coursera.org/specializations/google-kubernetes-engine
3. **edX容器化课程**: https://www.edx.org/learn/containers

### 社区资源

1. **Kubernetes Slack**: https://slack.k8s.io/
2. **Kubernetes论坛**: https://discuss.kubernetes.io/
3. **Stack Overflow Kubernetes标签**: https://stackoverflow.com/questions/tagged/kubernetes

通过本附录的学习，读者可以快速查阅Kubernetes的常用命令和工具，掌握故障排查的技巧和方法，了解配置与管理的最佳实践，并获取进一步学习的资源。这些内容将帮助读者在实际工作中更高效地使用Kubernetes。