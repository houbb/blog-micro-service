---
title: 9.4 使用 Kubernetes 管理微服务配置：ConfigMap和Secret的最佳实践
date: 2025-08-31
categories: [Configuration Management]
tags: [microservice-configuration-management]
published: true
---

# 9.4 使用 Kubernetes 管理微服务配置

Kubernetes作为主流的容器编排平台，提供了强大的配置管理机制，主要包括ConfigMap和Secret两种资源类型。通过合理使用这些机制，可以有效地管理微服务应用的配置信息，确保应用的安全性和可维护性。

## ConfigMap和Secret的使用

ConfigMap用于存储非敏感的配置数据，而Secret用于存储敏感信息如密码、令牌等。

### ConfigMap的创建和使用

```yaml
# user-service-configmap.yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: user-service-config
  namespace: default
  labels:
    app: user-service
    tier: backend
data:
  # 应用配置
  app.properties: |
    server.port=8080
    spring.profiles.active=production
    logging.level.com.example=INFO
    
  # 数据库配置
  database.properties: |
    database.host=user-db.example.com
    database.port=5432
    database.name=user_service
    database.pool.size=20
    
  # 缓存配置
  cache.properties: |
    cache.host=redis.example.com
    cache.port=6379
    cache.ttl=3600
    
  # 环境变量
  ENV: production
  DEBUG: "false"
  LOG_LEVEL: INFO
  
  # JSON格式配置
  service-config.json: |
    {
      "api": {
        "timeout": "30s",
        "retry": 3,
        "rateLimit": 1000
      },
      "features": {
        "userProfile": true,
        "notifications": true,
        "analytics": false
      }
    }

---
# user-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  labels:
    app: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: example/user-service:1.0.0
        ports:
        - containerPort: 8080
        env:
        # 从ConfigMap注入环境变量
        - name: ENV
          valueFrom:
            configMapKeyRef:
              name: user-service-config
              key: ENV
        - name: DEBUG
          valueFrom:
            configMapKeyRef:
              name: user-service-config
              key: DEBUG
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: user-service-config
              key: LOG_LEVEL
        volumeMounts:
        # 挂载ConfigMap为文件
        - name: config-volume
          mountPath: /etc/user-service/config
        - name: app-config
          mountPath: /app/config
          readOnly: true
      volumes:
      - name: config-volume
        configMap:
          name: user-service-config
          items:
          - key: app.properties
            path: app.properties
          - key: database.properties
            path: database/database.properties
          - key: cache.properties
            path: cache/cache.properties
          - key: service-config.json
            path: service-config.json
      - name: app-config
        configMap:
          name: user-service-config
          items:
          - key: service-config.json
            path: config.json
```

### Secret的创建和使用

```yaml
# user-service-secrets.yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: user-service-secrets
  namespace: default
  labels:
    app: user-service
type: Opaque
data:
  # 敏感数据需要进行base64编码
  database.password: bXlzZWNyZXRwYXNzd29yZA==  # mysecretpassword
  database.username: dXNlcl9zZXJ2aWNl        # user_service
  api.key: YWJjZGVmZ2hpams=               # abcdefghijk
  jwt.secret: eW91ci1zZWNyZXQtand0LXRva2Vu  # your-secret-jwt-token

---
# user-service-deployment-with-secrets.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  labels:
    app: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: example/user-service:1.0.0
        ports:
        - containerPort: 8080
        env:
        # 从Secret注入环境变量
        - name: DATABASE_USERNAME
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: database.username
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: database.password
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: api.key
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: user-service-secrets
              key: jwt.secret
        volumeMounts:
        # 挂载Secret为文件
        - name: secret-volume
          mountPath: /etc/user-service/secrets
          readOnly: true
      volumes:
      - name: secret-volume
        secret:
          secretName: user-service-secrets
          items:
          - key: database.password
            path: db_password
          - key: jwt.secret
            path: jwt_secret
```

## Helm Charts配置管理

Helm是Kubernetes的包管理工具，可以帮助我们更好地管理复杂的配置。

### Helm Chart结构示例

```yaml
# Chart.yaml
---
apiVersion: v2
name: user-service
description: A Helm chart for User Service
type: application
version: 1.0.0
appVersion: "1.0.0"
```

```yaml
# values.yaml
---
# Default values for user-service chart

# 应用配置
replicaCount: 3

image:
  repository: example/user-service
  pullPolicy: IfNotPresent
  tag: "1.0.0"

# 环境配置
env:
  ENV: production
  DEBUG: false
  LOG_LEVEL: INFO

# 资源配置
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 200m
    memory: 256Mi

# 服务配置
service:
  type: ClusterIP
  port: 8080

# 配置参数
config:
  server:
    port: 8080
    timeout: 30s
  database:
    host: user-db.example.com
    port: 5432
    name: user_service
    pool:
      size: 20
  cache:
    host: redis.example.com
    port: 6379
    ttl: 3600

# 敏感配置
secrets:
  enabled: true
  database:
    username: user_service
    password: mysecretpassword
  api:
    key: abcdefghijk
  jwt:
    secret: your-secret-jwt-token
```

```yaml
# templates/configmap.yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "user-service.fullname" . }}
  labels:
    {{- include "user-service.labels" . | nindent 4 }}
data:
  app.properties: |
    server.port={{ .Values.config.server.port }}
    spring.profiles.active={{ .Values.env.ENV }}
    logging.level.com.example={{ .Values.env.LOG_LEVEL }}
    
  database.properties: |
    database.host={{ .Values.config.database.host }}
    database.port={{ .Values.config.database.port }}
    database.name={{ .Values.config.database.name }}
    database.pool.size={{ .Values.config.database.pool.size }}
    
  cache.properties: |
    cache.host={{ .Values.config.cache.host }}
    cache.port={{ .Values.config.cache.port }}
    cache.ttl={{ .Values.config.cache.ttl }}
    
  ENV: {{ .Values.env.ENV | quote }}
  DEBUG: {{ .Values.env.DEBUG | quote }}
  LOG_LEVEL: {{ .Values.env.LOG_LEVEL | quote }}
```

```yaml
# templates/secrets.yaml
{{- if .Values.secrets.enabled }}
---
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "user-service.fullname" . }}-secrets
  labels:
    {{- include "user-service.labels" . | nindent 4 }}
type: Opaque
data:
  database.username: {{ .Values.secrets.database.username | b64enc | quote }}
  database.password: {{ .Values.secrets.database.password | b64enc | quote }}
  api.key: {{ .Values.secrets.api.key | b64enc | quote }}
  jwt.secret: {{ .Values.secrets.jwt.secret | b64enc | quote }}
{{- end }}
```

```yaml
# templates/deployment.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "user-service.fullname" . }}
  labels:
    {{- include "user-service.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "user-service.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "user-service.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - containerPort: {{ .Values.service.port }}
        env:
        - name: ENV
          valueFrom:
            configMapKeyRef:
              name: {{ include "user-service.fullname" . }}
              key: ENV
        {{- if .Values.secrets.enabled }}
        - name: DATABASE_USERNAME
          valueFrom:
            secretKeyRef:
              name: {{ include "user-service.fullname" . }}-secrets
              key: database.username
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: {{ include "user-service.fullname" . }}-secrets
              key: database.password
        {{- end }}
        volumeMounts:
        - name: config-volume
          mountPath: /etc/user-service/config
        {{- if .Values.secrets.enabled }}
        - name: secret-volume
          mountPath: /etc/user-service/secrets
          readOnly: true
        {{- end }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
      volumes:
      - name: config-volume
        configMap:
          name: {{ include "user-service.fullname" . }}
      {{- if .Values.secrets.enabled }}
      - name: secret-volume
        secret:
          secretName: {{ include "user-service.fullname" . }}-secrets
      {{- end }}
```

## Kustomize配置定制

Kustomize是Kubernetes原生的配置定制工具，允许我们基于基础配置创建不同的变体。

### Kustomize配置示例

```yaml
# base/kustomization.yaml
---
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
- configmap.yaml
- secret.yaml

configMapGenerator:
- name: user-service-config
  files:
  - config/app.properties
  - config/database.properties
  - config/cache.properties
  literals:
  - ENV=base
  - LOG_LEVEL=INFO

secretGenerator:
- name: user-service-secrets
  literals:
  - database.username=user_service
  - database.password=mysecretpassword
  - api.key=abcdefghijk
  - jwt.secret=your-secret-jwt-token

images:
- name: example/user-service
  newTag: 1.0.0
```

```yaml
# overlays/production/kustomization.yaml
---
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
- ../../base

namePrefix: prod-

patchesStrategicMerge:
- deployment-patch.yaml

configMapGenerator:
- name: user-service-config
  behavior: merge
  literals:
  - ENV=production
  - LOG_LEVEL=WARN
  - DATABASE_HOST=prod-user-db.example.com

secretGenerator:
- name: user-service-secrets
  behavior: replace
  literals:
  - database.username=prod_user_service
  - database.password=prod-secret-password
  - api.key=prod-api-key
  - jwt.secret=prod-jwt-secret

replicas:
- name: user-service
  count: 5
```

```yaml
# overlays/production/deployment-patch.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  template:
    spec:
      containers:
      - name: user-service
        resources:
          limits:
            cpu: "1"
            memory: 1Gi
          requests:
            cpu: 500m
            memory: 512Mi
```

## Operator模式的配置管理

Operator模式通过扩展Kubernetes API来管理复杂应用的配置和生命周期。

### 自定义资源定义(CRD)示例

```yaml
# user-service-crd.yaml
---
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: userservices.config.example.com
spec:
  group: config.example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              replicas:
                type: integer
                minimum: 1
              config:
                type: object
                properties:
                  database:
                    type: object
                    properties:
                      host:
                        type: string
                      port:
                        type: integer
                      name:
                        type: string
              secrets:
                type: object
                properties:
                  database:
                    type: object
                    properties:
                      username:
                        type: string
                      password:
                        type: string
          status:
            type: object
            properties:
              phase:
                type: string
              replicas:
                type: integer
  scope: Namespaced
  names:
    plural: userservices
    singular: userservice
    kind: UserService
    shortNames:
    - us
```

```yaml
# user-service-custom-resource.yaml
---
apiVersion: config.example.com/v1
kind: UserService
metadata:
  name: my-user-service
  namespace: default
spec:
  replicas: 3
  config:
    database:
      host: user-db.example.com
      port: 5432
      name: user_service
  secrets:
    database:
      username: user_service
      password: mysecretpassword
```

通过以上内容，我们深入探讨了在Kubernetes中管理微服务配置的各种方法，包括ConfigMap和Secret的使用、Helm Charts配置管理、Kustomize配置定制以及Operator模式的配置管理。这些方法可以帮助我们构建更加灵活、安全和可维护的微服务配置管理体系。