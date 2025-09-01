---
title: 配置管理与容器化平台的结合：在Kubernetes中实现高效配置管理
date: 2025-08-31
categories: [Configuration Management]
tags: [kubernetes, docker, containerization, configuration-management, devops]
published: true
---

# 17.4 配置管理与容器化平台的结合

容器化平台，特别是Kubernetes，已经成为现代应用部署的主流选择。在容器化环境中，配置管理面临着新的挑战和机遇。本节将深入探讨Kubernetes中的配置管理机制，包括ConfigMap和Secret的使用、Helm和Kustomize在配置管理中的应用，以及服务网格中的配置管理等关键主题。

## Kubernetes中的配置管理

Kubernetes提供了多种原生资源来管理配置，其中最重要的是ConfigMap和Secret。

### 1. ConfigMap详解

ConfigMap用于存储非敏感的配置数据，可以以键值对或文件的形式存储。

#### ConfigMap基本操作

```yaml
# configmap-example.yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
  labels:
    app: myapp
    environment: production
data:
  # 简单键值对配置
  database.host: "db.example.com"
  database.port: "5432"
  log.level: "INFO"
  
  # 复杂配置（多行）
  app.properties: |
    server.port=8080
    management.port=8081
    spring.profiles.active=prod
    
  # JSON配置
  config.json: |
    {
      "database": {
        "host": "db.example.com",
        "port": 5432
      },
      "cache": {
        "host": "redis.example.com",
        "port": 6379
      }
    }
    
  # YAML配置
  app-config.yaml: |
    server:
      port: 8080
    database:
      host: db.example.com
      port: 5432
    logging:
      level: INFO
```

#### 在Pod中使用ConfigMap

```yaml
# pod-with-configmap.yaml
---
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
  labels:
    app: myapp
spec:
  containers:
  - name: app-container
    image: myapp:latest
    env:
    # 从ConfigMap中注入环境变量
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
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: log.level
          
    # 将ConfigMap作为卷挂载
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
    - name: properties-volume
      mountPath: /app/config
      
  volumes:
  # 配置卷
  - name: config-volume
    configMap:
      name: app-config
      items:
      - key: app-config.yaml
        path: app-config.yaml
      - key: config.json
        path: config.json
        
  # 属性文件卷
  - name: properties-volume
    configMap:
      name: app-config
      items:
      - key: app.properties
        path: app.properties
```

#### ConfigMap管理脚本

```bash
# configmap-manager.sh

# Kubernetes ConfigMap管理脚本
k8s_configmap_manager() {
    echo "Starting Kubernetes ConfigMap management..."
    
    # 1. 创建ConfigMap
    echo "1. Creating ConfigMaps..."
    create_configmaps
    
    # 2. 更新ConfigMap
    echo "2. Setting up ConfigMap update mechanisms..."
    setup_configmap_updates
    
    # 3. 监控ConfigMap变化
    echo "3. Setting up ConfigMap change monitoring..."
    setup_configmap_monitoring
    
    # 4. ConfigMap备份和恢复
    echo "4. Setting up ConfigMap backup and recovery..."
    setup_configmap_backup_recovery
    
    echo "Kubernetes ConfigMap management initialized"
}

# 创建ConfigMap
create_configmaps() {
    echo "Creating ConfigMaps from various sources..."
    
    # 从字面值创建
    kubectl create configmap literal-config \
        --from-literal=database.host=db.example.com \
        --from-literal=database.port=5432 \
        --from-literal=log.level=INFO
    
    # 从文件创建
    echo "server.port=8080" > server.properties
    echo "logging.level=INFO" >> server.properties
    
    kubectl create configmap file-config \
        --from-file=server.properties
    
    # 从目录创建
    mkdir -p app-config
    echo "database.host=db.example.com" > app-config/db.properties
    echo "cache.host=redis.example.com" > app-config/cache.properties
    echo "api.endpoint=https://api.example.com" > app-config/api.yaml
    
    kubectl create configmap dir-config \
        --from-file=app-config/
    
    # 从YAML文件创建
    cat > app-configmap.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: yaml-config
data:
  app.yaml: |
    server:
      port: 8080
    database:
      host: db.example.com
      port: 5432
    features:
      - user-management
      - order-processing
EOF
    
    kubectl apply -f app-configmap.yaml
    
    echo "ConfigMaps created successfully"
}

# 设置ConfigMap更新机制
setup_configmap_updates() {
    echo "Setting up ConfigMap update mechanisms..."
    
    # 创建自动更新脚本
    cat > update-configmap.sh << 'EOF'
#!/bin/bash

# ConfigMap自动更新脚本
CONFIGMAP_NAME=$1
NAMESPACE=${2:-default}

echo "Updating ConfigMap: $CONFIGMAP_NAME in namespace: $NAMESPACE"

# 获取当前ConfigMap
kubectl get configmap $CONFIGMAP_NAME -n $NAMESPACE -o yaml > current-configmap.yaml

# 备份当前配置
cp current-configmap.yaml backup-configmap-$(date +%Y%m%d-%H%M%S).yaml

# 更新配置（示例：更新时间戳）
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
sed -i "s/last-updated:.*/last-updated: \"$TIMESTAMP\"/" current-configmap.yaml

# 应用更新
kubectl apply -f current-configmap.yaml

echo "ConfigMap updated successfully"
EOF
    
    chmod +x update-configmap.sh
    
    # 创建定期更新的CronJob
    cat > configmap-update-cronjob.yaml << EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: configmap-updater
spec:
  schedule: "0 */6 * * *"  # 每6小时执行一次
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: configmap-updater
            image: bitnami/kubectl:latest
            command:
            - /bin/sh
            - -c
            - |
              TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
              kubectl patch configmap yaml-config -p="{\"data\":{\"last-updated\":\"$TIMESTAMP\"}}"
          restartPolicy: OnFailure
          serviceAccountName: configmap-updater
EOF
    
    echo "ConfigMap update mechanisms set up"
}

# 设置ConfigMap变化监控
setup_configmap_monitoring() {
    echo "Setting up ConfigMap change monitoring..."
    
    # 创建监控脚本
    cat > monitor-configmap.sh << 'EOF'
#!/bin/bash

# ConfigMap变化监控脚本
CONFIGMAP_NAME=$1
NAMESPACE=${2:-default}

echo "Monitoring ConfigMap: $CONFIGMAP_NAME in namespace: $NAMESPACE"

# 获取初始资源版本
RESOURCE_VERSION=$(kubectl get configmap $CONFIGMAP_NAME -n $NAMESPACE -o jsonpath='{.metadata.resourceVersion}')
echo "Initial resource version: $RESOURCE_VERSION"

# 监控变化
while true; do
    CURRENT_VERSION=$(kubectl get configmap $CONFIGMAP_NAME -n $NAMESPACE -o jsonpath='{.metadata.resourceVersion}')
    
    if [ "$CURRENT_VERSION" != "$RESOURCE_VERSION" ]; then
        echo "ConfigMap changed! New resource version: $CURRENT_VERSION"
        
        # 发送通知（示例：写入日志）
        echo "$(date): ConfigMap $CONFIGMAP_NAME changed" >> /var/log/configmap-changes.log
        
        # 更新资源版本
        RESOURCE_VERSION=$CURRENT_VERSION
    fi
    
    sleep 30
done
EOF
    
    chmod +x monitor-configmap.sh
    
    # 创建监控Deployment
    cat > configmap-monitor-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: configmap-monitor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: configmap-monitor
  template:
    metadata:
      labels:
        app: configmap-monitor
    spec:
      containers:
      - name: monitor
        image: bitnami/kubectl:latest
        command:
        - /bin/sh
        - -c
        - |
          while true; do
            kubectl get configmap --watch -o name | while read resource; do
              echo "ConfigMap changed: $resource at $(date)" >> /var/log/configmap-monitor.log
            done
          done
        volumeMounts:
        - name: log-volume
          mountPath: /var/log
      volumes:
      - name: log-volume
        emptyDir: {}
      serviceAccountName: configmap-monitor
EOF
    
    echo "ConfigMap change monitoring set up"
}

# 设置ConfigMap备份和恢复
setup_configmap_backup_recovery() {
    echo "Setting up ConfigMap backup and recovery..."
    
    # 创建备份脚本
    cat > backup-configmaps.sh << 'EOF'
#!/bin/bash

# ConfigMap备份脚本
BACKUP_DIR="/backup/configmaps/$(date +%Y%m%d)"
NAMESPACE=${1:-default}

mkdir -p $BACKUP_DIR

echo "Backing up ConfigMaps in namespace: $NAMESPACE"

# 备份所有ConfigMaps
kubectl get configmap -n $NAMESPACE -o yaml > $BACKUP_DIR/all-configmaps.yaml

# 分别备份每个ConfigMap
kubectl get configmap -n $NAMESPACE -o name | while read cm; do
    cm_name=$(echo $cm | cut -d/ -f2)
    kubectl get configmap $cm_name -n $NAMESPACE -o yaml > $BACKUP_DIR/$cm_name.yaml
done

# 创建备份归档
tar -czf $BACKUP_DIR.tar.gz -C /backup/configmaps $(date +%Y%m%d)

echo "ConfigMap backup completed: $BACKUP_DIR.tar.gz"
EOF
    
    chmod +x backup-configmaps.sh
    
    # 创建恢复脚本
    cat > restore-configmap.sh << 'EOF'
#!/bin/bash

# ConfigMap恢复脚本
BACKUP_FILE=$1
NAMESPACE=${2:-default}

echo "Restoring ConfigMaps from: $BACKUP_FILE to namespace: $NAMESPACE"

# 解压备份文件
tar -xzf $BACKUP_FILE -C /tmp

# 获取备份日期
BACKUP_DATE=$(basename $BACKUP_FILE .tar.gz)

# 恢复ConfigMaps
for file in /tmp/$BACKUP_DATE/*.yaml; do
    if [ -f "$file" ]; then
        echo "Restoring ConfigMap from: $file"
        kubectl apply -f $file -n $NAMESPACE
    fi
done

echo "ConfigMap restoration completed"
EOF
    
    chmod +x restore-configmap.sh
    
    echo "ConfigMap backup and recovery mechanisms set up"
}

# 使用示例
# k8s_configmap_manager
```

### 2. Secret详解

Secret用于存储敏感信息，如密码、密钥、证书等。

#### Secret基本操作

```yaml
# secret-example.yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
  namespace: default
  labels:
    app: myapp
    environment: production
type: Opaque
data:
  # 敏感数据需要进行base64编码
  database.password: c3VwZXJzZWNyZXRwYXNzd29yZA==  # supersecretpassword
  api.key: YV92ZXJ5X3NlY3JldF9hcGlfa2V5  # a_very_secret_api_key
  tls.crt: <base64-encoded-certificate>
  tls.key: <base64-encoded-private-key>

stringData:
  # stringData中的数据会自动进行base64编码
  database.username: dbuser
  config.yaml: |
    database:
      username: dbuser
      password: supersecretpassword
    api:
      key: a_very_secret_api_key
```

#### 在Pod中使用Secret

```yaml
# pod-with-secret.yaml
---
apiVersion: v1
kind: Pod
metadata:
  name: app-pod-with-secret
  labels:
    app: myapp
spec:
  containers:
  - name: app-container
    image: myapp:latest
    env:
    # 从Secret中注入环境变量
    - name: DATABASE_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: database.password
    - name: API_KEY
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: api.key
    - name: DATABASE_USERNAME
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: database.username
          
    # 将Secret作为卷挂载
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secret
      readOnly: true
      
  volumes:
  # Secret卷
  - name: secret-volume
    secret:
      secretName: app-secret
      items:
      - key: config.yaml
        path: config.yaml
      - key: tls.crt
        path: tls.crt
      - key: tls.key
        path: tls.key
        mode: 256  # 0400 权限
```

#### Secret管理脚本

```python
# k8s-secret-manager.py
import base64
import json
import subprocess
import yaml
from typing import Dict, Any, List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class K8sSecretManager:
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        
    def create_secret_from_literals(self, name: str, literals: Dict[str, str], 
                                  secret_type: str = "Opaque") -> Dict[str, Any]:
        """从字面值创建Secret"""
        try:
            # 构建kubectl命令
            cmd = ["kubectl", "create", "secret", "generic", name, "-n", self.namespace]
            
            # 添加字面值
            for key, value in literals.items():
                cmd.extend(["--from-literal", f"{key}={value}"])
                
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Secret {name} created successfully")
            return {
                'success': True,
                'secret_name': name,
                'namespace': self.namespace,
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create secret {name}: {e.stderr}")
            return {
                'success': False,
                'error': e.stderr
            }
            
    def create_secret_from_files(self, name: str, files: List[str], 
                               secret_type: str = "Opaque") -> Dict[str, Any]:
        """从文件创建Secret"""
        try:
            # 构建kubectl命令
            cmd = ["kubectl", "create", "secret", "generic", name, "-n", self.namespace]
            
            # 添加文件
            for file_path in files:
                cmd.extend(["--from-file", file_path])
                
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Secret {name} created from files successfully")
            return {
                'success': True,
                'secret_name': name,
                'namespace': self.namespace,
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create secret {name} from files: {e.stderr}")
            return {
                'success': False,
                'error': e.stderr
            }
            
    def get_secret(self, name: str) -> Dict[str, Any]:
        """获取Secret"""
        try:
            # 获取Secret的YAML表示
            cmd = ["kubectl", "get", "secret", name, "-n", self.namespace, "-o", "yaml"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # 解析YAML
            secret_data = yaml.safe_load(result.stdout)
            
            # 解码base64数据
            decoded_data = {}
            if 'data' in secret_data:
                for key, value in secret_data['data'].items():
                    try:
                        decoded_data[key] = base64.b64decode(value).decode('utf-8')
                    except Exception:
                        # 如果解码失败，保持原始值
                        decoded_data[key] = value
                        
            return {
                'success': True,
                'secret_name': name,
                'namespace': self.namespace,
                'data': decoded_data,
                'metadata': secret_data.get('metadata', {})
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get secret {name}: {e.stderr}")
            return {
                'success': False,
                'error': e.stderr
            }
            
    def update_secret(self, name: str, new_data: Dict[str, str]) -> Dict[str, Any]:
        """更新Secret"""
        try:
            # 首先获取现有Secret
            existing_secret = self.get_secret(name)
            if not existing_secret['success']:
                return existing_secret
                
            # 创建新的Secret YAML
            secret_yaml = {
                'apiVersion': 'v1',
                'kind': 'Secret',
                'metadata': {
                    'name': name,
                    'namespace': self.namespace
                },
                'data': {}
            }
            
            # 添加现有数据
            if 'data' in existing_secret:
                secret_yaml['data'].update(existing_secret['data'])
                
            # 添加新数据（进行base64编码）
            for key, value in new_data.items():
                secret_yaml['data'][key] = base64.b64encode(value.encode('utf-8')).decode('utf-8')
                
            # 写入临时文件
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(secret_yaml, f)
                temp_file = f.name
                
            # 应用更新
            cmd = ["kubectl", "apply", "-f", temp_file]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # 清理临时文件
            os.unlink(temp_file)
            
            logger.info(f"Secret {name} updated successfully")
            return {
                'success': True,
                'secret_name': name,
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to update secret {name}: {e.stderr}")
            return {
                'success': False,
                'error': e.stderr
            }
            
    def delete_secret(self, name: str) -> Dict[str, Any]:
        """删除Secret"""
        try:
            cmd = ["kubectl", "delete", "secret", name, "-n", self.namespace]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"Secret {name} deleted successfully")
            return {
                'success': True,
                'secret_name': name,
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete secret {name}: {e.stderr}")
            return {
                'success': False,
                'error': e.stderr
            }
            
    def list_secrets(self) -> Dict[str, Any]:
        """列出所有Secrets"""
        try:
            cmd = ["kubectl", "get", "secrets", "-n", self.namespace, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            secrets_data = json.loads(result.stdout)
            secrets = []
            
            for item in secrets_data.get('items', []):
                secrets.append({
                    'name': item['metadata']['name'],
                    'type': item['type'],
                    'created': item['metadata']['creationTimestamp']
                })
                
            return {
                'success': True,
                'secrets': secrets,
                'count': len(secrets)
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list secrets: {e.stderr}")
            return {
                'success': False,
                'error': e.stderr
            }

# 使用示例
# secret_manager = K8sSecretManager("default")

# # 从字面值创建Secret
# result = secret_manager.create_secret_from_literals(
#     "app-credentials",
#     {
#         "database-password": "supersecretpassword",
#         "api-key": "a_very_secret_api_key",
#         "username": "dbuser"
#     }
# )

# # 获取Secret
# secret = secret_manager.get_secret("app-credentials")

# # 更新Secret
# update_result = secret_manager.update_secret(
#     "app-credentials",
#     {"new-password": "evenmoresecretpassword"}
# )

# # 列出所有Secrets
# secrets = secret_manager.list_secrets()
```

## Helm在配置管理中的应用

Helm是Kubernetes的包管理器，可以简化复杂应用的部署和配置管理。

### 1. Helm Chart结构

```yaml
# Chart.yaml
---
apiVersion: v2
name: myapp
version: 1.0.0
appVersion: "1.0"
description: A Helm chart for my application
type: application
keywords:
  - application
  - web
home: https://example.com
sources:
  - https://github.com/example/myapp
maintainers:
  - name: Example Team
    email: team@example.com
```

### 2. Values配置文件

```yaml
# values.yaml
---
# 应用配置
app:
  name: myapp
  version: "1.0"
  replicas: 3
  image:
    repository: myapp
    tag: latest
    pullPolicy: Always
    
# 数据库配置
database:
  enabled: true
  host: db.example.com
  port: 5432
  name: myapp
  username: dbuser
  password: supersecretpassword
  
# 缓存配置
cache:
  enabled: true
  host: redis.example.com
  port: 6379
  password: cache_password
  
# 日志配置
logging:
  level: INFO
  format: json
  
# 资源限制
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
    
# 服务配置
service:
  type: ClusterIP
  port: 8080
  targetPort: 8080
  
# 环境特定配置
env:
  production:
    replicas: 5
    resources:
      limits:
        cpu: 2000m
        memory: 2Gi
      requests:
        cpu: 1000m
        memory: 1Gi
        
  staging:
    replicas: 2
    resources:
      limits:
        cpu: 500m
        memory: 512Mi
      requests:
        cpu: 250m
        memory: 256Mi
```

### 3. Helm模板文件

```yaml
# templates/deployment.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.app.replicas }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.app.image.repository }}:{{ .Values.app.image.tag }}"
        imagePullPolicy: {{ .Values.app.image.pullPolicy }}
        ports:
        - containerPort: {{ .Values.service.targetPort }}
        env:
        # 从Values注入环境变量
        - name: DATABASE_HOST
          value: {{ .Values.database.host | quote }}
        - name: DATABASE_PORT
          value: {{ .Values.database.port | quote }}
        - name: DATABASE_NAME
          value: {{ .Values.database.name | quote }}
        - name: DATABASE_USERNAME
          value: {{ .Values.database.username | quote }}
        - name: LOG_LEVEL
          value: {{ .Values.logging.level | quote }}
          
        # 从Secret注入敏感环境变量
        envFrom:
        - secretRef:
            name: {{ include "myapp.fullname" . }}-secrets
            
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
          
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
          
      volumes:
      - name: config-volume
        configMap:
          name: {{ include "myapp.fullname" . }}-config
```

```yaml
# templates/configmap.yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "myapp.fullname" . }}-config
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
data:
  app.yaml: |
    server:
      port: {{ .Values.service.targetPort }}
    database:
      host: {{ .Values.database.host }}
      port: {{ .Values.database.port }}
      name: {{ .Values.database.name }}
    cache:
      host: {{ .Values.cache.host }}
      port: {{ .Values.cache.port }}
    logging:
      level: {{ .Values.logging.level }}
      format: {{ .Values.logging.format }}
```

```yaml
# templates/secret.yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "myapp.fullname" . }}-secrets
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
type: Opaque
data:
  database-password: {{ .Values.database.password | b64enc | quote }}
  database-username: {{ .Values.database.username | b64enc | quote }}
  cache-password: {{ .Values.cache.password | b64enc | quote }}
```

### 4. Helm管理脚本

```bash
# helm-config-manager.sh

# Helm配置管理脚本
helm_config_manager() {
    echo "Starting Helm configuration management..."
    
    # 1. 初始化Helm
    echo "1. Initializing Helm..."
    initialize_helm
    
    # 2. 创建Helm Chart
    echo "2. Creating Helm Chart..."
    create_helm_chart
    
    # 3. 管理Helm Values
    echo "3. Managing Helm Values..."
    manage_helm_values
    
    # 4. 部署和升级应用
    echo "4. Deploying and upgrading applications..."
    deploy_upgrade_applications
    
    echo "Helm configuration management initialized"
}

# 初始化Helm
initialize_helm() {
    echo "Initializing Helm..."
    
    # 添加常用仓库
    helm repo add stable https://charts.helm.sh/stable
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    
    # 更新仓库
    helm repo update
    
    echo "Helm initialized successfully"
}

# 创建Helm Chart
create_helm_chart() {
    echo "Creating Helm Chart..."
    
    # 创建新的Chart
    helm create myapp-chart
    
    # 进入Chart目录
    cd myapp-chart
    
    # 更新Chart.yaml
    cat > Chart.yaml << EOF
apiVersion: v2
name: myapp
description: A Helm chart for my application
type: application
version: 0.1.0
appVersion: "1.0"
maintainers:
  - name: DevOps Team
    email: devops@example.com
EOF
    
    # 创建环境特定的values文件
    cat > values-production.yaml << EOF
# Production values
app:
  replicas: 5
  
resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 1000m
    memory: 1Gi
    
database:
  host: prod-db.example.com
  password: {{ required "Production database password is required!" .Values.database.password }}
  
service:
  type: LoadBalancer
EOF
    
    cat > values-staging.yaml << EOF
# Staging values
app:
  replicas: 2
  
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi
    
database:
  host: staging-db.example.com
  
service:
  type: ClusterIP
EOF
    
    echo "Helm Chart created successfully"
    cd ..
}

# 管理Helm Values
manage_helm_values() {
    echo "Managing Helm Values..."
    
    # 创建Values管理脚本
    cat > manage-values.sh << 'EOF'
#!/bin/bash

# Helm Values管理脚本
CHART_NAME=$1
ACTION=$2
ENVIRONMENT=$3

case $ACTION in
    "validate")
        echo "Validating values for $CHART_NAME in $ENVIRONMENT environment..."
        helm template $CHART_NAME --values values-$ENVIRONMENT.yaml > /dev/null
        if [ $? -eq 0 ]; then
            echo "Values validation passed"
        else
            echo "Values validation failed"
            exit 1
        fi
        ;;
        
    "lint")
        echo "Linting values for $CHART_NAME..."
        helm lint $CHART_NAME --values values-$ENVIRONMENT.yaml
        ;;
        
    "diff")
        echo "Showing differences for $CHART_NAME..."
        helm diff upgrade $CHART_NAME $CHART_NAME --values values-$ENVIRONMENT.yaml
        ;;
        
    *)
        echo "Usage: $0 <chart-name> <validate|lint|diff> <environment>"
        exit 1
        ;;
esac
EOF
    
    chmod +x manage-values.sh
    
    echo "Helm Values management set up"
}

# 部署和升级应用
deploy_upgrade_applications() {
    echo "Setting up application deployment and upgrade..."
    
    # 创建部署脚本
    cat > deploy-app.sh << 'EOF'
#!/bin/bash

# 应用部署脚本
CHART_NAME=$1
RELEASE_NAME=$2
ENVIRONMENT=$3
NAMESPACE=${4:-default}

echo "Deploying $RELEASE_NAME in $ENVIRONMENT environment to namespace $NAMESPACE..."

# 检查Release是否已存在
if helm status $RELEASE_NAME -n $NAMESPACE > /dev/null 2>&1; then
    echo "Release exists, performing upgrade..."
    helm upgrade $RELEASE_NAME $CHART_NAME \
        --namespace $NAMESPACE \
        --values values-$ENVIRONMENT.yaml \
        --set database.password=$(kubectl get secret db-password -n $NAMESPACE -o jsonpath='{.data.password}' | base64 -d) \
        --atomic \
        --timeout 300s
else
    echo "Release does not exist, performing install..."
    helm install $RELEASE_NAME $CHART_NAME \
        --namespace $NAMESPACE \
        --create-namespace \
        --values values-$ENVIRONMENT.yaml \
        --set database.password=$(kubectl get secret db-password -n $NAMESPACE -o jsonpath='{.data.password}' | base64 -d) \
        --atomic \
        --timeout 300s
fi

if [ $? -eq 0 ]; then
    echo "Deployment/Upgrade successful"
else
    echo "Deployment/Upgrade failed"
    exit 1
fi
EOF
    
    chmod +x deploy-app.sh
    
    # 创建回滚脚本
    cat > rollback-app.sh << 'EOF'
#!/bin/bash

# 应用回滚脚本
RELEASE_NAME=$1
REVISION=${2:-0}
NAMESPACE=${3:-default}

echo "Rolling back $RELEASE_NAME in namespace $NAMESPACE..."

if [ $REVISION -eq 0 ]; then
    # 回滚到上一个版本
    helm rollback $RELEASE_NAME -n $NAMESPACE
else
    # 回滚到指定版本
    helm rollback $RELEASE_NAME $REVISION -n $NAMESPACE
fi

if [ $? -eq 0 ]; then
    echo "Rollback successful"
else
    echo "Rollback failed"
    exit 1
fi
EOF
    
    chmod +x rollback-app.sh
    
    echo "Application deployment and upgrade mechanisms set up"
}

# 使用示例
# helm_config_manager
```

## Kustomize在配置管理中的应用

Kustomize是Kubernetes原生的配置定制工具，可以管理不同环境的配置差异。

### 1. Kustomize基础结构

```yaml
# kustomization.yaml (base)
---
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

# 资源文件
resources:
- deployment.yaml
- service.yaml
- configmap.yaml
- secret.yaml

# 通用配置
namespace: myapp
namePrefix: myapp-

# 标签
commonLabels:
  app: myapp
  version: v1.0

# 注解
commonAnnotations:
  app-description: "My Application"
  maintained-by: "DevOps Team"

# 配置映射生成器
configMapGenerator:
- name: app-config
  literals:
  - DATABASE_HOST=db.example.com
  - DATABASE_PORT=5432
  - LOG_LEVEL=INFO
  files:
  - app.properties

# 密钥生成器
secretGenerator:
- name: app-secrets
  literals:
  - DATABASE_PASSWORD=supersecretpassword
  - API_KEY=a_very_secret_api_key
  files:
  - tls.crt
  - tls.key
```

### 2. 环境覆盖配置

```yaml
# overlays/production/kustomization.yaml
---
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

# 基础配置
bases:
- ../../base

# 覆盖配置
namespace: myapp-production
namePrefix: prod-myapp-

# 资源补丁
patchesStrategicMerge:
- deployment-patch.yaml
- service-patch.yaml

# 配置映射生成器覆盖
configMapGenerator:
- name: app-config
  behavior: merge
  literals:
  - DATABASE_HOST=prod-db.example.com
  - DATABASE_PORT=5432
  - LOG_LEVEL=WARN

# 密钥生成器覆盖
secretGenerator:
- name: app-secrets
  behavior: replace
  literals:
  - DATABASE_PASSWORD=production_supersecretpassword
  - API_KEY=production_api_key

# 镜像标签
images:
- name: myapp
  newTag: v1.0.0-production
```

```yaml
# overlays/production/deployment-patch.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deployment
spec:
  replicas: 5
  template:
    spec:
      containers:
      - name: app
        resources:
          limits:
            cpu: "2"
            memory: 2Gi
          requests:
            cpu: "1"
            memory: 1Gi
```

```yaml
# overlays/staging/kustomization.yaml
---
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

# 基础配置
bases:
- ../../base

# 覆盖配置
namespace: myapp-staging
namePrefix: staging-myapp-

# 资源补丁
patchesStrategicMerge:
- deployment-patch.yaml

# 配置映射生成器覆盖
configMapGenerator:
- name: app-config
  behavior: merge
  literals:
  - DATABASE_HOST=staging-db.example.com
  - DATABASE_PORT=5432
  - LOG_LEVEL=INFO

# 镜像标签
images:
- name: myapp
  newTag: v1.0.0-staging
```

```yaml
# overlays/staging/deployment-patch.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deployment
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: app
        resources:
          limits:
            cpu: "0.5"
            memory: 512Mi
          requests:
            cpu: "0.25"
            memory: 256Mi
```

### 3. Kustomize管理脚本

```python
# kustomize-manager.py
import subprocess
import yaml
import json
import os
from typing import Dict, Any, List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KustomizeManager:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        
    def build_kustomization(self, overlay_path: str, output_file: str = None) -> Dict[str, Any]:
        """构建Kustomization"""
        try:
            cmd = ["kustomize", "build", overlay_path]
            
            if output_file:
                cmd.extend(["-o", output_file])
                
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=self.base_path)
            
            logger.info(f"Kustomization built successfully for {overlay_path}")
            return {
                'success': True,
                'overlay_path': overlay_path,
                'output_file': output_file,
                'output': result.stdout if not output_file else f"Output written to {output_file}"
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to build kustomization for {overlay_path}: {e.stderr}")
            return {
                'success': False,
                'error': e.stderr
            }
            
    def edit_kustomization(self, overlay_path: str, key: str, value: Any) -> Dict[str, Any]:
        """编辑Kustomization配置"""
        try:
            # 使用kustomize edit命令
            cmd = ["kustomize", "edit", "set", key, str(value)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=overlay_path)
            
            logger.info(f"Kustomization edited successfully: {key}={value}")
            return {
                'success': True,
                'overlay_path': overlay_path,
                'key': key,
                'value': value,
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to edit kustomization {overlay_path}: {e.stderr}")
            return {
                'success': False,
                'error': e.stderr
            }
            
    def create_overlay(self, overlay_name: str, base_path: str = "base") -> Dict[str, Any]:
        """创建新的overlay"""
        try:
            overlay_path = os.path.join(self.base_path, "overlays", overlay_name)
            os.makedirs(overlay_path, exist_ok=True)
            
            # 创建kustomization.yaml
            kustomization = {
                'apiVersion': 'kustomize.config.k8s.io/v1beta1',
                'kind': 'Kustomization',
                'bases': [f'../../{base_path}'],
                'namespace': f'myapp-{overlay_name}',
                'namePrefix': f'{overlay_name}-myapp-'
            }
            
            with open(os.path.join(overlay_path, "kustomization.yaml"), 'w') as f:
                yaml.dump(kustomization, f)
                
            logger.info(f"Overlay {overlay_name} created successfully")
            return {
                'success': True,
                'overlay_path': overlay_path
            }
        except Exception as e:
            logger.error(f"Failed to create overlay {overlay_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def validate_kustomization(self, overlay_path: str) -> Dict[str, Any]:
        """验证Kustomization"""
        try:
            # 构建但不输出，只验证
            cmd = ["kustomize", "build", overlay_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=self.base_path)
            
            # 检查输出是否为有效的YAML
            try:
                yaml.safe_load_all(result.stdout)
                logger.info(f"Kustomization validated successfully for {overlay_path}")
                return {
                    'success': True,
                    'overlay_path': overlay_path,
                    'valid': True
                }
            except yaml.YAMLError as e:
                logger.error(f"Invalid YAML in kustomization output for {overlay_path}: {str(e)}")
                return {
                    'success': True,
                    'overlay_path': overlay_path,
                    'valid': False,
                    'error': f"Invalid YAML: {str(e)}"
                }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to validate kustomization for {overlay_path}: {e.stderr}")
            return {
                'success': False,
                'error': e.stderr
            }
            
    def diff_kustomizations(self, overlay1: str, overlay2: str) -> Dict[str, Any]:
        """比较两个Kustomization的差异"""
        try:
            # 构建两个overlay
            cmd1 = ["kustomize", "build", overlay1]
            result1 = subprocess.run(cmd1, capture_output=True, text=True, check=True, cwd=self.base_path)
            
            cmd2 = ["kustomize", "build", overlay2]
            result2 = subprocess.run(cmd2, capture_output=True, text=True, check=True, cwd=self.base_path)
            
            # 保存到临时文件进行比较
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f1, \
                 tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2:
                f1.write(result1.stdout)
                f2.write(result2.stdout)
                file1 = f1.name
                file2 = f2.name
                
            # 使用diff比较
            cmd = ["diff", "-u", file1, file2]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 清理临时文件
            os.unlink(file1)
            os.unlink(file2)
            
            return {
                'success': True,
                'overlay1': overlay1,
                'overlay2': overlay2,
                'differences': result.stdout,
                'has_differences': result.returncode != 0
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to diff kustomizations: {e.stderr}")
            return {
                'success': False,
                'error': e.stderr
            }

# 使用示例
# kustomize_manager = KustomizeManager(".")

# # 构建生产环境配置
# result = kustomize_manager.build_kustomization("overlays/production", "production-manifests.yaml")

# # 创建新的测试环境overlay
# create_result = kustomize_manager.create_overlay("testing")

# # 验证配置
# validate_result = kustomize_manager.validate_kustomization("overlays/production")

# # 比较环境差异
# diff_result = kustomize_manager.diff_kustomizations("overlays/production", "overlays/staging")
```

## 服务网格中的配置管理

服务网格（如Istio）为微服务提供了额外的配置管理需求。

### 1. Istio配置示例

```yaml
# istio-gateway.yaml
---
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: myapp-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "myapp.example.com"
  - port:
      number: 443
      name: https
      protocol: HTTPS
    hosts:
    - "myapp.example.com"
    tls:
      mode: SIMPLE
      credentialName: myapp-credential
```

```yaml
# istio-virtual-service.yaml
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: myapp-virtual-service
spec:
  hosts:
  - "myapp.example.com"
  gateways:
  - myapp-gateway
  http:
  - match:
    - uri:
        prefix: /api/v1/users
    route:
    - destination:
        host: user-service
        port:
          number: 8080
  - match:
    - uri:
        prefix: /api/v1/orders
    route:
    - destination:
        host: order-service
        port:
          number: 8080
  - route:
    - destination:
        host: frontend-service
        port:
          number: 8080
```

```yaml
# istio-destination-rule.yaml
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: user-service-destination-rule
spec:
  host: user-service
  trafficPolicy:
    loadBalancer:
      simple: LEAST_CONN
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 1000
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### 2. 服务网格配置管理脚本

```bash
# service-mesh-config-manager.sh

# 服务网格配置管理脚本
service_mesh_config_manager() {
    echo "Starting service mesh configuration management..."
    
    # 1. 部署Istio组件
    echo "1. Deploying Istio components..."
    deploy_istio_components
    
    # 2. 管理网格配置
    echo "2. Managing mesh configurations..."
    manage_mesh_configurations
    
    # 3. 监控和调试
    echo "3. Setting up monitoring and debugging..."
    setup_mesh_monitoring
    
    echo "Service mesh configuration management initialized"
}

# 部署Istio组件
deploy_istio_components() {
    echo "Deploying Istio components..."
    
    # 下载Istio
    curl -L https://istio.io/downloadIstio | sh -
    
    # 进入Istio目录
    cd istio-*
    
    # 部署Istio
    kubectl apply -f manifests/charts/base/crds/crd-all.gen.yaml
    kubectl apply -f manifests/charts/base/files/gen-istio-cluster.yaml
    kubectl apply -f manifests/charts/istio-control/istio-discovery/files/gen-istio.yaml
    kubectl apply -f manifests/charts/gateways/istio-ingress/files/gen-istio-ingress.yaml
    
    # 等待部署完成
    kubectl wait --for=condition=ready pod -l app=istiod -n istio-system --timeout=300s
    
    echo "Istio components deployed successfully"
    cd ..
}

# 管理网格配置
manage_mesh_configurations() {
    echo "Managing mesh configurations..."
    
    # 创建配置应用脚本
    cat > apply-mesh-config.sh << 'EOF'
#!/bin/bash

# 网格配置应用脚本
CONFIG_FILE=$1
NAMESPACE=${2:-default}

echo "Applying mesh configuration from $CONFIG_FILE to namespace $NAMESPACE..."

# 应用配置
kubectl apply -f $CONFIG_FILE -n $NAMESPACE

# 验证配置
CONFIG_NAME=$(kubectl get -f $CONFIG_FILE -n $NAMESPACE -o jsonpath='{.metadata.name}')
CONFIG_KIND=$(kubectl get -f $CONFIG_FILE -n $NAMESPACE -o jsonpath='{.kind}')

echo "Verifying $CONFIG_KIND/$CONFIG_NAME..."
kubectl get $CONFIG_KIND $CONFIG_NAME -n $NAMESPACE -o yaml

echo "Mesh configuration applied successfully"
EOF
    
    chmod +x apply-mesh-config.sh
    
    # 创建配置验证脚本
    cat > validate-mesh-config.sh << 'EOF'
#!/bin/bash

# 网格配置验证脚本
echo "Validating mesh configurations..."

# 检查Istio组件状态
echo "Checking Istio component status..."
kubectl get pods -n istio-system

# 检查配置状态
echo "Checking configuration status..."
istioctl proxy-status

# 验证配置
echo "Validating configurations..."
istioctl validate -f *.yaml

echo "Mesh configuration validation completed"
EOF
    
    chmod +x validate-mesh-config.sh
    
    echo "Mesh configuration management set up"
}

# 设置网格监控
setup_mesh_monitoring() {
    echo "Setting up mesh monitoring..."
    
    # 启用指标收集
    cat > enable-metrics.yaml << EOF
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-default
  namespace: istio-system
spec:
  metrics:
  - providers:
    - name: prometheus
EOF
    
    kubectl apply -f enable-metrics.yaml
    
    # 创建监控Dashboard配置
    cat > mesh-dashboard.json << EOF
{
  "dashboard": {
    "title": "Istio Service Mesh Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(istio_requests_total[5m])) by (destination_service)",
            "legendFormat": "{{destination_service}}"
          }
        ]
      },
      {
        "title": "Request Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, sum(rate(istio_request_duration_milliseconds_bucket[5m])) by (destination_service, le))",
            "legendFormat": "{{destination_service}}"
          }
        ]
      }
    ]
  }
}
EOF
    
    echo "Mesh monitoring set up"
}

# 使用示例
# service_mesh_config_manager
```

## 最佳实践总结

通过以上内容，我们可以总结出配置管理与容器化平台结合的最佳实践：

### 1. Kubernetes ConfigMap和Secret管理
- 合理使用ConfigMap存储非敏感配置，Secret存储敏感信息
- 实施配置版本控制和变更管理
- 建立配置备份和恢复机制
- 使用标签和注解进行配置分类

### 2. Helm配置管理
- 使用Helm管理复杂应用的配置
- 实施环境特定的values文件
- 利用Helm模板实现配置复用
- 建立部署和回滚流程

### 3. Kustomize配置管理
- 使用Kustomize管理环境差异
- 实施基础配置和overlay模式
- 利用补丁机制进行配置定制
- 建立配置验证机制

### 4. 服务网格配置管理
- 合理配置服务网格组件
- 实施流量管理和安全策略
- 建立监控和调试机制
- 利用网格特性增强配置管理

通过实施这些最佳实践，企业可以在容器化平台中实现高效、安全、可靠的配置管理，为云原生应用的成功部署和运行提供保障。

第17章完整地介绍了云平台中的配置管理，从主流云平台的配置管理工具到云原生应用的配置管理挑战，再到使用云原生工具和容器化平台进行配置管理的实践方法。这些知识和技能对于现代DevOps实践和云原生应用开发至关重要。