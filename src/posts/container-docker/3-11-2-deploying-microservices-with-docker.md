---
title: Deploying Microservices with Docker - Containerizing and Orchestrating Microservices
date: 2025-08-30
categories: [Docker]
tags: [docker, microservices, deployment, orchestration]
published: true
---

## 使用 Docker 部署微服务应用

### 微服务部署概述

使用 Docker 部署微服务应用涉及将每个服务容器化，然后通过编排工具管理这些容器的生命周期。Docker 提供了从单机部署到集群管理的完整解决方案，使微服务应用的部署变得更加简单和可靠。

#### 部署挑战

1. **服务发现**：如何让服务找到彼此
2. **负载均衡**：如何分发请求到多个服务实例
3. **配置管理**：如何管理不同环境的配置
4. **数据持久化**：如何处理有状态服务的数据
5. **监控和日志**：如何收集和分析服务运行信息

### 单机环境部署

#### 使用 Docker Compose 部署

```yaml
# docker-compose.yml - 完整的微服务应用部署
version: '3.8'

services:
  # API 网关
  api-gateway:
    build: 
      context: ./api-gateway
      dockerfile: Dockerfile
    ports:
      - "80:8080"
    environment:
      - USER_SERVICE_URL=http://user-service:8080
      - ORDER_SERVICE_URL=http://order-service:8080
      - PAYMENT_SERVICE_URL=http://payment-service:8080
    networks:
      - frontend
      - backend
    depends_on:
      - user-service
      - order-service
      - payment-service
    restart: always

  # 用户服务
  user-service:
    build:
      context: ./user-service
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=mongodb://mongo-user:27017/users
      - JWT_SECRET=${JWT_SECRET}
    networks:
      - backend
      - user-network
    depends_on:
      - mongo-user
    restart: always
    deploy:
      replicas: 2

  # 订单服务
  order-service:
    build:
      context: ./order-service
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://postgres:5432/orders
      - USER_SERVICE_URL=http://user-service:8080
    networks:
      - backend
      - order-network
    depends_on:
      - postgres
    restart: always
    deploy:
      replicas: 2

  # 支付服务
  payment-service:
    build:
      context: ./payment-service
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=mysql://mysql:3306/payments
    networks:
      - backend
      - payment-network
    depends_on:
      - mysql
    restart: always

  # 数据库服务
  mongo-user:
    image: mongo:4.4
    volumes:
      - mongo-user-data:/data/db
    networks:
      - user-network
    restart: always

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: orders
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - order-network
    restart: always

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: payments
      MYSQL_USER: mysqluser
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - payment-network
    restart: always

  # 消息队列
  rabbitmq:
    image: rabbitmq:management
    ports:
      - "15672:15672"
    networks:
      - messaging-network
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    restart: always

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
  user-network:
    driver: bridge
  order-network:
    driver: bridge
  payment-network:
    driver: bridge
  messaging-network:
    driver: bridge

volumes:
  mongo-user-data:
  postgres-data:
  mysql-data:
  rabbitmq-data:
```

#### 部署命令

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f

# 扩展服务实例
docker-compose up -d --scale user-service=3

# 停止服务
docker-compose down

# 停止并删除卷
docker-compose down -v
```

### 集群环境部署

#### 使用 Docker Swarm 部署

```bash
# 初始化 Swarm 集群
docker swarm init

# 创建 overlay 网络
docker network create --driver overlay microservices-network

# 部署堆栈
docker stack deploy -c docker-compose.yml microservices
```

```yaml
# docker-compose.swarm.yml - Swarm 部署配置
version: '3.8'

services:
  api-gateway:
    build: ./api-gateway
    ports:
      - "80:8080"
    networks:
      - microservices-network
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
      placement:
        constraints:
          - node.role == worker

  user-service:
    build: ./user-service
    networks:
      - microservices-network
    environment:
      - DATABASE_URL=mongodb://mongo-user:27017/users
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
      update_config:
        parallelism: 1
        delay: 10s
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  mongo-user:
    image: mongo:4.4
    networks:
      - microservices-network
    volumes:
      - mongo-user-data:/data/db
    deploy:
      placement:
        constraints:
          - node.role == manager

networks:
  microservices-network:
    driver: overlay

volumes:
  mongo-user-data:
```

#### 使用 Kubernetes 部署

```yaml
# user-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
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
        image: myregistry/user-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          value: mongodb://mongo-user:27017/users
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
  type: ClusterIP
```

### 配置管理

#### 环境变量管理

```bash
# 创建 .env 文件
cat > .env << EOF
JWT_SECRET=my-secret-key
POSTGRES_PASSWORD=postgres-password
MYSQL_ROOT_PASSWORD=mysql-root-password
MYSQL_PASSWORD=mysql-password
EOF

# 在 docker-compose.yml 中使用
# environment:
#   - JWT_SECRET=${JWT_SECRET}
```

#### 配置文件挂载

```yaml
version: '3.8'
services:
  user-service:
    build: ./user-service
    volumes:
      - ./config/user-service.yml:/app/config/application.yml
    environment:
      - SPRING_CONFIG_LOCATION=/app/config/application.yml
```

#### Docker Secrets

```bash
# 创建 secrets
echo "my-secret-password" | docker secret create db_password -

# 在服务中使用 secrets
version: '3.8'
services:
  user-service:
    build: ./user-service
    secrets:
      - db_password

secrets:
  db_password:
    external: true
```

### 数据持久化

#### 使用命名卷

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:13
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: orders
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

volumes:
  postgres-data:
    driver: local
```

#### 使用绑定挂载

```yaml
version: '3.8'
services:
  mongo-user:
    image: mongo:4.4
    volumes:
      - /host/data/mongo:/data/db
```

### 服务发现和负载均衡

#### 内置服务发现

```bash
# 在同一网络中的服务可以通过服务名称访问
# curl http://user-service:8080/api/users
```

#### 外部负载均衡

```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - user-service

  user-service:
    build: ./user-service
    deploy:
      replicas: 3
```

```nginx
# nginx.conf
upstream user_service {
    server user-service:8080;
}

server {
    listen 80;
    
    location /api/users {
        proxy_pass http://user_service;
    }
}
```

### 监控和日志

#### 集中日志收集

```yaml
version: '3.8'
services:
  user-service:
    build: ./user-service
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: user-service
```

#### 性能监控

```bash
# 使用 cAdvisor 监控容器性能
docker run -d \
  --name=cadvisor \
  -p 8080:8080 \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  gcr.io/cadvisor/cadvisor:v0.45.0
```

### 部署脚本

#### 自动化部署脚本

```bash
#!/bin/bash
# deploy-microservices.sh

set -e

echo "开始部署微服务应用..."

# 检查环境变量
if [ -z "$JWT_SECRET" ]; then
    echo "错误: JWT_SECRET 环境变量未设置"
    exit 1
fi

# 构建镜像
echo "构建 Docker 镜像..."
docker-compose build

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 验证服务可用性
echo "验证服务可用性..."
for i in {1..30}; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo "服务部署成功!"
        exit 0
    fi
    echo "等待服务响应... ($i/30)"
    sleep 10
done

echo "服务部署失败!"
docker-compose logs
exit 1
```

#### 滚动更新脚本

```bash
#!/bin/bash
# rolling-update.sh

SERVICE_NAME=$1
NEW_IMAGE=$2

if [ -z "$SERVICE_NAME" ] || [ -z "$NEW_IMAGE" ]; then
    echo "用法: $0 <service-name> <new-image>"
    exit 1
fi

echo "开始滚动更新服务: $SERVICE_NAME"

# 获取当前服务实例数
CURRENT_REPLICAS=$(docker service ls --filter name=$SERVICE_NAME --format "{{.Replicas}}" | cut -d'/' -f1)

# 逐步更新实例
for i in $(seq 1 $CURRENT_REPLICAS); do
    echo "更新实例 $i/$CURRENT_REPLICAS"
    
    # 更新单个实例
    docker service update --image $NEW_IMAGE --replicas $i $SERVICE_NAME
    
    # 等待实例启动
    echo "等待实例启动..."
    sleep 30
    
    # 验证实例健康
    echo "验证实例健康..."
    # 这里可以添加健康检查逻辑
done

echo "滚动更新完成!"
```

### 部署最佳实践

#### 镜像标签策略

```bash
# 使用语义化版本
docker build -t myapp/user-service:1.2.3 ./user-service

# 使用 Git 提交哈希
docker build -t myapp/user-service:git-$(git rev-parse --short HEAD) ./user-service

# 使用环境标签
docker build -t myapp/user-service:prod ./user-service
```

#### 资源限制

```yaml
version: '3.8'
services:
  user-service:
    build: ./user-service
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

#### 健康检查

```dockerfile
# 在 Dockerfile 中添加健康检查
FROM node:14-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080
CMD ["node", "server.js"]
```

通过本节内容，您已经深入了解了如何使用 Docker 部署微服务应用，包括单机环境和集群环境的部署方法、配置管理、数据持久化、服务发现和负载均衡等关键技术。掌握这些部署技能将帮助您成功运行和管理微服务应用。