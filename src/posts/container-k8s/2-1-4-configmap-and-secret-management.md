---
title: ConfigMap与Secret管理：安全高效地配置Kubernetes应用
date: 2025-08-31
categories: [Kubernetes]
tags: [kubernetes, configmap, secret, configuration, security]
published: true
---

在云原生应用开发中，配置管理是一个至关重要的环节。Kubernetes提供了ConfigMap和Secret两种机制来管理应用的配置数据和敏感信息。本章将深入探讨如何正确使用ConfigMap和Secret，实现配置与代码的分离，确保敏感信息的安全，并掌握最佳的配置管理实践。

## 使用 ConfigMap 配置应用环境

### ConfigMap 简介

ConfigMap是一种API对象，用于存储非机密性的配置数据。它允许您将配置数据与镜像分离，使应用更具可移植性和灵活性。

#### ConfigMap 的优势

- 配置与镜像分离
- 环境差异化配置
- 动态更新配置
- 多种使用方式

### 创建 ConfigMap

#### 从字面值创建

```bash
kubectl create configmap app-config --from-literal=database.host=localhost --from-literal=database.port=5432
```

#### 从文件创建

```bash
# 从单个文件创建
kubectl create configmap app-config --from-file=app.properties

# 从多个文件创建
kubectl create configmap app-config --from-file=config1.properties --from-file=config2.properties
```

#### 从目录创建

```bash
kubectl create configmap app-config --from-file=./config-dir/
```

#### 从YAML文件创建

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database.host: localhost
  database.port: "5432"
  ui.properties: |
    color.good=purple
    color.bad=yellow
    allow.textmode=true
```

### 使用 ConfigMap

#### 作为环境变量注入

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-pod
spec:
  containers:
  - name: app
    image: nginx
    env:
    - name: DATABASE_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database.host
    - name: DATABASE_PORT
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database.port
```

#### 作为命令行参数

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-pod
spec:
  containers:
  - name: app
    image: nginx
    command: ["/bin/sh", "-c"]
    args:
    - echo "Database host: $(DATABASE_HOST)";
      echo "Database port: $(DATABASE_PORT)";
      sleep 3600;
    env:
    - name: DATABASE_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database.host
    - name: DATABASE_PORT
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database.port
```

#### 作为存储卷挂载

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

### ConfigMap 的更新与动态配置

#### 更新 ConfigMap

```bash
# 更新ConfigMap
kubectl patch configmap app-config --patch '{"data":{"database.host":"new-host"}}'
```

#### 动态更新注意事项

- 通过环境变量注入的配置不会自动更新
- 通过存储卷挂载的配置会在一段时间后自动更新
- 应用需要具备重新读取配置的能力

## 使用 Secret 管理敏感数据

### Secret 简介

Secret是Kubernetes中用于存储敏感信息的对象，如密码、OAuth令牌、SSH密钥等。Secret与ConfigMap类似，但专门用于敏感数据，并提供额外的安全保护。

#### Secret 的类型

- **Opaque**：通用的Secret类型
- **kubernetes.io/service-account-token**：服务账户令牌
- **kubernetes.io/dockercfg**：Docker配置文件
- **kubernetes.io/dockerconfigjson**：Docker配置JSON
- **kubernetes.io/basic-auth**：基本认证凭据
- **kubernetes.io/ssh-auth**：SSH认证凭据
- **kubernetes.io/tls**：TLS证书和密钥

### 创建 Secret

#### 从字面值创建

```bash
kubectl create secret generic db-secret --from-literal=username=admin --from-literal=password=secretpassword
```

#### 从文件创建

```bash
kubectl create secret generic tls-secret --from-file=tls.crt=server.crt --from-file=tls.key=server.key
```

#### 从YAML文件创建（Base64编码）

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=  # admin的Base64编码
  password: c2VjcmV0cGFzc3dvcmQ=  # secretpassword的Base64编码
```

### 使用 Secret

#### 作为环境变量注入

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  containers:
  - name: app
    image: nginx
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
```

#### 作为存储卷挂载

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secret
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: db-secret
```

### Secret 的安全考虑

#### 加密存储

Kubernetes支持对Secret进行加密存储：

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - aescbc:
        keys:
        - name: key1
          secret: <base64-encoded-secret>
    - identity: {}
```

#### 访问控制

通过RBAC控制对Secret的访问：

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "watch", "list"]
```

## 配置文件的挂载与环境变量注入

### 配置文件挂载的最佳实践

#### 挂载单个键值对

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: config-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: config-volume
      mountPath: /etc/app/config.properties
      subPath: config.properties
  volumes:
  - name: config-volume
    configMap:
      name: app-config
      items:
      - key: app.properties
        path: config.properties
```

#### 挂载多个配置文件

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-config-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    projected:
      sources:
      - configMap:
          name: app-config
      - secret:
          name: db-secret
```

### 环境变量注入的模式

#### 简单键值对注入

```yaml
env:
- name: DATABASE_HOST
  valueFrom:
    configMapKeyRef:
      name: app-config
      key: database.host
```

#### 批量注入

```yaml
envFrom:
- configMapRef:
    name: app-config
- secretRef:
    name: db-secret
```

## 安全管理与加密

### Secret 的加密存储

#### 启用加密

在API服务器配置中启用加密：

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - aescbc:
        keys:
        - name: key1
          secret: <32-byte-base64-encoded-key>
    - identity: {}
```

#### 验证加密

```bash
# 检查etcd中存储的Secret
ETCDCTL_API=3 etcdctl get /registry/secrets/default/my-secret
```

### 配置审计与监控

#### 启用审计日志

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets"]
```

#### 监控Secret访问

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: audit-pod
  annotations:
    audit.kubernetes.io/level: RequestResponse
spec:
  containers:
  - name: app
    image: nginx
```

### 最佳安全实践

#### 最小权限原则

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-service-account
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-access-role
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["app-secret"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: secret-access-binding
subjects:
- kind: ServiceAccount
  name: app-service-account
roleRef:
  kind: Role
  name: secret-access-role
  apiGroup: rbac.authorization.k8s.io
```

#### 定期轮换Secret

```bash
# 轮换Secret
kubectl create secret generic new-db-secret --from-literal=username=newuser --from-literal=password=newpassword
kubectl patch deployment/my-app -p '{"spec":{"template":{"spec":{"containers":[{"name":"app","envFrom":[{"secretRef":{"name":"new-db-secret"}}]}]}}}}'
```

通过本章的学习，读者应该能够熟练使用ConfigMap和Secret来管理应用配置和敏感信息，理解不同使用方式的优缺点，掌握安全最佳实践，并能够实现配置的动态更新和安全管理。这些技能对于构建安全、可维护的云原生应用至关重要。