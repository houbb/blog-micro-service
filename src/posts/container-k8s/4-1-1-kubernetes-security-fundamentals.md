---
title: Kubernetes安全基础：构建安全可靠的容器化平台
date: 2025-08-31
categories: [Kubernetes]
tags: [kubernetes, security, rbac, authentication, authorization]
published: true
---

在云原生时代，安全性是Kubernetes平台成功部署和运行的关键因素。Kubernetes提供了多层次的安全机制，从身份认证到访问控制，从网络安全到镜像安全，构建了全面的安全防护体系。本章将深入探讨Kubernetes安全模型的核心概念、身份认证与授权机制、RBAC权限管理以及容器镜像安全，帮助读者建立坚实的安全基础。

## Kubernetes 安全模型与身份认证

### Kubernetes 安全模型概述

Kubernetes安全模型基于以下核心原则：

1. **纵深防御**：通过多层安全控制保护系统
2. **最小权限**：用户和应用只拥有完成任务所需的最小权限
3. **默认拒绝**：未明确授权的访问默认被拒绝
4. **安全审计**：记录和审查所有安全相关事件

### 身份认证机制

Kubernetes支持多种身份认证方式：

#### 客户端证书认证

```bash
# 生成客户端证书
openssl genrsa -out user.key 2048
openssl req -new -key user.key -out user.csr -subj "/CN=user/O=group1"
openssl x509 -req -in user.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out user.crt -days 365
```

#### 静态令牌认证

```bash
# 创建令牌文件
echo "token1,user1,uid1,group1" > /etc/kubernetes/auth-tokens.csv

# 在API服务器配置中启用
--token-auth-file=/etc/kubernetes/auth-tokens.csv
```

#### 服务账户令牌

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
---
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  serviceAccountName: my-service-account
  containers:
  - name: app
    image: nginx
```

#### OpenID Connect (OIDC)

```bash
# API服务器配置
--oidc-issuer-url=https://accounts.google.com
--oidc-client-id=my-client-id
--oidc-username-claim=email
--oidc-groups-claim=groups
```

### 身份认证最佳实践

1. **使用强密码和密钥**：确保所有认证凭据的安全性
2. **定期轮换证书**：建立证书轮换机制
3. **启用多因素认证**：提高身份认证的安全性
4. **限制管理员权限**：严格控制管理员账户的使用

## RBAC（基于角色的访问控制）

### RBAC 核心概念

RBAC通过四个API对象实现权限管理：

1. **Role**：定义在命名空间内的权限规则
2. **ClusterRole**：定义集群范围的权限规则
3. **RoleBinding**：将Role绑定到用户或组
4. **ClusterRoleBinding**：将ClusterRole绑定到用户或组

### Role 和 RoleBinding

#### 创建 Role

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

#### 创建 RoleBinding

```yaml
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

### ClusterRole 和 ClusterRoleBinding

#### 创建 ClusterRole

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "watch", "list"]
```

#### 创建 ClusterRoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-secrets-global
subjects:
- kind: Group
  name: manager
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

### RBAC 最佳实践

1. **最小权限原则**：只授予完成任务所需的最小权限
2. **使用组进行权限管理**：通过组来管理用户权限
3. **定期审查权限**：定期检查和清理不必要的权限
4. **使用内置角色**：优先使用Kubernetes内置的角色

```yaml
# 使用内置角色
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-role-binding
  namespace: development
subjects:
- kind: User
  name: jane
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: edit
  apiGroup: rbac.authorization.k8s.io
```

## 网络策略与访问控制

### NetworkPolicy 简介

NetworkPolicy用于控制Pod之间的网络通信，实现微隔离。

#### 基本 NetworkPolicy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

#### 允许特定标签的Pod访问

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend
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
```

#### 允许特定命名空间访问

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-namespace
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: production
```

### 网络策略最佳实践

1. **默认拒绝策略**：默认拒绝所有流量，显式允许必要的通信
2. **分层策略**：按应用、环境、团队等维度制定网络策略
3. **定期审查**：定期审查和更新网络策略
4. **使用标签**：合理使用标签进行策略匹配

### 服务网格集成

通过服务网格（如Istio）实现更细粒度的访问控制：

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: httpbin
  namespace: foo
spec:
  selector:
    matchLabels:
      app: httpbin
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/sleep"]
    to:
    - operation:
        methods: ["GET"]
  - from:
    - source:
        namespaces: ["test"]
```

## 容器镜像安全扫描与加固

### 镜像安全扫描

#### 使用 Trivy 进行扫描

```bash
# 安装Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# 扫描镜像
trivy image nginx:latest
```

#### 集成到CI/CD流程

```yaml
# GitHub Actions示例
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'docker.io/my-company/my-app:${{ github.sha }}'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
```

### 镜像加固

#### 使用非root用户

```dockerfile
FROM alpine:latest
RUN addgroup -g 1001 -S appuser && \
    adduser -u 1001 -S appuser -G appuser
USER appuser
COPY app /app
CMD ["/app"]
```

#### 多阶段构建

```dockerfile
# 构建阶段
FROM golang:1.19 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# 运行阶段
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
CMD ["./main"]
```

#### 使用Distroless镜像

```dockerfile
# 构建阶段
FROM golang:1.19 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# 运行阶段
FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app/main .
USER nonroot:nonroot
ENTRYPOINT ["/main"]
```

### 镜像签名与验证

#### 使用 Cosign 进行签名

```bash
# 生成密钥对
cosign generate-key-pair

# 签名镜像
cosign sign --key cosign.key my-registry/my-image:latest

# 验证签名
cosign verify --key cosign.pub my-registry/my-image:latest
```

#### 在Kubernetes中验证签名

```yaml
apiVersion: policy.sigstore.dev/v1beta1
kind: ClusterImagePolicy
metadata:
  name: image-policy
spec:
  images:
  - glob: "**"
  authorities:
  - key:
      data: |
        -----BEGIN PUBLIC KEY-----
        ...
        -----END PUBLIC KEY-----
```

### 安全最佳实践总结

1. **定期更新**：及时更新Kubernetes版本和组件
2. **安全审计**：启用审计日志并定期审查
3. **网络隔离**：使用NetworkPolicy实现网络隔离
4. **镜像安全**：扫描和加固容器镜像
5. **权限管理**：实施最小权限原则和RBAC
6. **密钥管理**：安全存储和管理敏感信息
7. **监控告警**：建立安全监控和告警机制

通过本章的学习，读者应该能够深入理解Kubernetes安全模型的核心概念，掌握身份认证与授权机制，熟练使用RBAC进行权限管理，理解网络策略的配置和应用，并掌握容器镜像安全扫描与加固的技术。这些知识对于构建安全可靠的Kubernetes平台至关重要。