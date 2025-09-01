---
title: Docker Applications in AWS, Azure, and Google Cloud - Mastering Multi-Cloud Container Deployment
date: 2025-08-31
categories: [Docker]
tags: [container-docker]
published: true
---

## Docker 在 AWS、Azure 与 Google Cloud 中的应用

### 云平台容器服务概览

主流云平台都提供了丰富的容器服务，支持 Docker 容器的部署和管理。每个平台都有其独特的特性和优势，了解这些差异有助于选择最适合的平台来部署容器化应用。

#### AWS 容器服务

1. **Amazon ECS (Elastic Container Service)**：
   - 完全托管的容器编排服务
   - 与 AWS 生态系统深度集成
   - 支持 Fargate 无服务器模式

2. **Amazon EKS (Elastic Kubernetes Service)**：
   - 托管的 Kubernetes 服务
   - 兼容标准 Kubernetes API
   - 企业级安全和合规性

3. **AWS Fargate**：
   - 无服务器计算引擎
   - 无需管理底层基础设施
   - 按需付费模式

#### Azure 容器服务

1. **Azure Container Instances (ACI)**：
   - 最快捷的容器部署方式
   - 按秒计费
   - 无需管理虚拟机

2. **Azure Kubernetes Service (AKS)**：
   - 托管的 Kubernetes 服务
   - 集成 Azure Active Directory
   - 企业级安全功能

3. **Azure Container Registry (ACR)**：
   - 托管的 Docker 镜像仓库
   - 地理复制支持
   - 与 Azure 服务集成

#### Google Cloud 容器服务

1. **Google Kubernetes Engine (GKE)**：
   - 托管的 Kubernetes 服务
   - 自动化集群管理
   - 集成 Google Cloud 服务

2. **Cloud Run**：
   - 完全托管的无服务器平台
   - 支持容器化应用
   - 自动扩缩容

3. **Container Registry**：
   - 托管的 Docker 镜像仓库
   - 与 Google Cloud 服务集成
   - 安全扫描功能

### AWS 容器部署实践

#### Amazon ECS 部署

```json
// task-definition.json
{
  "family": "myapp",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "myapp",
      "image": "123456789012.dkr.ecr.us-west-2.amazonaws.com/myapp:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENV",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/myapp",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

```bash
# 部署到 ECS
# 创建集群
aws ecs create-cluster --cluster-name myapp-cluster

# 注册任务定义
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 创建服务
aws ecs create-service \
  --cluster myapp-cluster \
  --service-name myapp-service \
  --task-definition myapp \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678],securityGroups=[sg-87654321],assignPublicIp=ENABLED}"
```

#### Amazon EKS 部署

```yaml
# eks-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: 123456789012.dkr.ecr.us-west-2.amazonaws.com/myapp:latest
        ports:
        - containerPort: 80
        env:
        - name: ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

```bash
# 部署到 EKS
kubectl apply -f eks-deployment.yaml

# 查看部署状态
kubectl get deployments
kubectl get services
```

### Azure 容器部署实践

#### Azure Container Instances 部署

```bash
# 部署到 ACI
az container create \
  --resource-group mygroup \
  --name myapp-container \
  --image myregistry.azurecr.io/myapp:latest \
  --dns-name-label myapp-demo \
  --ports 80 \
  --environment-variables ENV=production \
  --registry-login-server myregistry.azurecr.io \
  --registry-username myregistry \
  --registry-password $(az acr credential show --name myregistry --query passwords[0].value -o tsv)
```

#### Azure Kubernetes Service 部署

```yaml
# aks-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myregistry.azurecr.io/myapp:latest
        ports:
        - containerPort: 80
        env:
        - name: ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

```bash
# 部署到 AKS
kubectl apply -f aks-deployment.yaml

# 查看部署状态
kubectl get deployments
kubectl get services
```

### Google Cloud 容器部署实践

#### Cloud Run 部署

```bash
# 部署到 Cloud Run
gcloud run deploy myapp \
  --image gcr.io/myproject/myapp:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENV=production \
  --port 80
```

#### Google Kubernetes Engine 部署

```yaml
# gke-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: gcr.io/myproject/myapp:latest
        ports:
        - containerPort: 80
        env:
        - name: ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

```bash
# 部署到 GKE
kubectl apply -f gke-deployment.yaml

# 查看部署状态
kubectl get deployments
kubectl get services
```

### 跨云平台部署策略

#### 多云架构设计

```yaml
# 多云部署配置
# docker-compose.multi-cloud.yml
version: '3.8'

services:
  web:
    image: myapp:latest
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.labels.cloud == aws
      labels:
        - "com.docker.stack.namespace=myapp-aws"
  
  web-azure:
    image: myapp:latest
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.labels.cloud == azure
      labels:
        - "com.docker.stack.namespace=myapp-azure"
  
  web-gcp:
    image: myapp:latest
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.labels.cloud == gcp
      labels:
        - "com.docker.stack.namespace=myapp-gcp"
```

#### 统一镜像管理

```bash
#!/bin/bash
# multi-cloud-deploy.sh

IMAGE_TAG="myapp:$(git rev-parse --short HEAD)"

# 构建镜像
docker build -t $IMAGE_TAG .

# 推送到各云平台镜像仓库
# AWS ECR
docker tag $IMAGE_TAG 123456789012.dkr.ecr.us-west-2.amazonaws.com/$IMAGE_TAG
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/$IMAGE_TAG

# Azure Container Registry
docker tag $IMAGE_TAG myregistry.azurecr.io/$IMAGE_TAG
docker push myregistry.azurecr.io/$IMAGE_TAG

# Google Container Registry
docker tag $IMAGE_TAG gcr.io/myproject/$IMAGE_TAG
docker push gcr.io/myproject/$IMAGE_TAG
```

#### 跨云平台服务发现

```yaml
# 跨云平台服务发现配置
version: '3.8'

services:
  web:
    image: myapp:latest
    environment:
      - SERVICE_DISCOVERY_URL=https://service-discovery.example.com
      - CLOUD_PROVIDER=${CLOUD_PROVIDER}
    deploy:
      labels:
        - "com.example.cloud=${CLOUD_PROVIDER}"
        - "com.example.version=${IMAGE_TAG}"
```

### 云平台特定功能集成

#### AWS 特定集成

```dockerfile
# AWS 特定功能集成
FROM node:14-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

# 安装 AWS SDK
RUN npm install @aws-sdk/client-s3 @aws-sdk/client-dynamodb

# 配置 AWS X-Ray
RUN npm install aws-xray-sdk

EXPOSE 3000
CMD ["node", "server.js"]
```

```javascript
// aws-integration.js
const AWS = require('aws-sdk');
const AWSXRay = require('aws-xray-sdk');

// 启用 X-Ray 跟踪
AWSXRay.captureAWS(AWS);

// 使用 DynamoDB
const dynamodb = new AWS.DynamoDB.DocumentClient({ region: 'us-west-2' });

// 使用 S3
const s3 = new AWS.S3({ region: 'us-west-2' });
```

#### Azure 特定集成

```dockerfile
# Azure 特定功能集成
FROM node:14-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

# 安装 Azure SDK
RUN npm install @azure/storage-blob @azure/cosmos

EXPOSE 3000
CMD ["node", "server.js"]
```

```javascript
// azure-integration.js
const { BlobServiceClient } = require('@azure/storage-blob');
const { CosmosClient } = require('@azure/cosmos');

// 使用 Azure Blob Storage
const blobServiceClient = BlobServiceClient.fromConnectionString(process.env.AZURE_STORAGE_CONNECTION_STRING);

// 使用 Azure Cosmos DB
const cosmosClient = new CosmosClient(process.env.COSMOS_DB_CONNECTION_STRING);
```

#### Google Cloud 特定集成

```dockerfile
# Google Cloud 特定功能集成
FROM node:14-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

# 安装 Google Cloud SDK
RUN npm install @google-cloud/storage @google-cloud/firestore

EXPOSE 3000
CMD ["node", "server.js"]
```

```javascript
// gcp-integration.js
const { Storage } = require('@google-cloud/storage');
const { Firestore } = require('@google-cloud/firestore');

// 使用 Google Cloud Storage
const storage = new Storage();

// 使用 Firestore
const firestore = new Firestore();
```

### 成本管理和优化

#### AWS 成本优化

```bash
# 使用 Spot 实例
aws ecs register-task-definition \
  --family myapp-spot \
  --requires-compatibilities EC2 \
  --cpu 256 \
  --memory 512 \
  --network-mode awsvpc \
  --execution-role-arn arn:aws:iam::123456789012:role/ecsTaskExecutionRole \
  --container-definitions '[{
    "name": "myapp",
    "image": "123456789012.dkr.ecr.us-west-2.amazonaws.com/myapp:latest",
    "memory": 512,
    "cpu": 256
  }]'

# 配置自动扩缩容
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/mycluster/myservice \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name myapp-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    }
  }'
```

#### Azure 成本优化

```bash
# 使用 Azure 虚拟机规模集
az container create \
  --resource-group mygroup \
  --name myapp-container \
  --image myregistry.azurecr.io/myapp:latest \
  --cpu 1 \
  --memory 1.5 \
  --ports 80

# 配置自动缩放
az monitor autoscale create \
  --resource myscale \
  --resource-type Microsoft.Compute/virtualMachineScaleSets \
  --min-count 1 \
  --max-count 10 \
  --count 2
```

#### Google Cloud 成本优化

```bash
# 配置 Cloud Run 自动扩缩容
gcloud run services update myapp \
  --max-instances=100 \
  --concurrency=80 \
  --cpu=1 \
  --memory=512Mi

# 使用抢占式 VM
gcloud container clusters create mycluster \
  --preemptible \
  --num-nodes=3
```

### 安全最佳实践

#### 跨云平台安全配置

```yaml
# 统一安全配置
version: '3.8'

services:
  app:
    image: myapp:latest
    environment:
      - NODE_ENV=production
    secrets:
      - db-password
      - api-key
    deploy:
      placement:
        constraints:
          - node.labels.security == high
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

secrets:
  db-password:
    external: true
  api-key:
    external: true
```

#### 云平台安全服务集成

```bash
# AWS Security Hub 集成
aws securityhub enable-security-hub

# Azure Security Center 集成
az security auto-provisioning-setting update --name default --auto-provision on

# Google Cloud Security Command Center 集成
gcloud scc notifications create my-notification \
  --organization=123456789012 \
  --description="Security notifications" \
  --pubsub-topic=projects/myproject/topics/my-topic
```

通过本节内容，我们深入了解了 Docker 在 AWS、Azure 和 Google Cloud 中的应用，包括各平台的容器服务特性、部署实践、跨云平台策略以及成本优化和安全配置等方面。掌握这些知识将帮助您在多云环境中高效地部署和管理容器化应用。