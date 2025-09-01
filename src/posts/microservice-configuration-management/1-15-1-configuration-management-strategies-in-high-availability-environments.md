---
title: 高可用性环境中的配置管理策略：构建稳定可靠的配置管理体系
date: 2025-08-31
categories: [Configuration Management]
tags: [microservice-configuration-management]
published: true
---

# 15.1 高可用性环境中的配置管理策略

在构建高可用性系统时，配置管理策略的合理设计是确保系统稳定运行的关键因素之一。高可用性环境对配置管理提出了更高的要求，不仅需要保证配置的正确性和一致性，还需要在各种故障场景下确保配置服务的持续可用。本节将深入探讨高可用性架构设计原则、配置管理组件的高可用部署、负载均衡与故障转移机制，以及健康检查与自动恢复策略等关键主题。

## 高可用性架构设计原则

设计高可用性配置管理架构需要遵循一系列核心原则，这些原则指导着整个系统的架构决策和实现方案。

### 1. 冗余设计原则

冗余是实现高可用性的基础，通过提供额外的组件和路径来消除单点故障。

```yaml
# ha-architecture-principles.yaml
---
design_principles:
  redundancy:
    description: "冗余设计原则"
    key_points:
      - "消除单点故障"
      - "提供备用组件和路径"
      - "实现故障自动切换"
      - "确保数据多副本存储"
    implementation_patterns:
      - pattern: "主备模式"
        description: "一个主节点处理请求，多个备用节点待命"
        use_cases: ["数据库配置存储", "配置管理服务器"]
        
      - pattern: "主主模式"
        description: "多个节点同时处理请求，负载分担"
        use_cases: ["分布式配置存储", "负载均衡配置服务"]
        
      - pattern: "集群模式"
        description: "多个节点组成集群，协同工作"
        use_cases: ["Kubernetes ConfigMap", "Consul集群"]

  fault_isolation:
    description: "故障隔离原则"
    key_points:
      - "将系统划分为独立的故障域"
      - "限制故障影响范围"
      - "实现故障快速定位"
      - "确保故障不影响其他组件"
    implementation_strategies:
      - "微服务架构隔离"
      - "网络分区隔离"
      - "数据隔离"
      - "资源配置隔离"

  graceful_degradation:
    description: "优雅降级原则"
    key_points:
      - "在部分组件失效时保持核心功能"
      - "提供降级服务级别"
      - "确保用户体验不受严重影响"
      - "支持手动和自动降级"
    degradation_levels:
      - level: "完全功能"
        description: "所有功能正常运行"
        
      - level: "部分功能受限"
        description: "非核心功能暂时不可用"
        
      - level: "只读模式"
        description: "仅提供配置读取，禁止写入操作"
        
      - level: "缓存模式"
        description: "使用本地缓存提供服务"
```

### 2. 高可用性配置管理架构

```python
# ha-config-architecture.py
import threading
import time
import json
from typing import Dict, List, Any
from datetime import datetime

class HighAvailabilityConfigManager:
    def __init__(self, cluster_nodes: List[str], replication_factor: int = 3):
        self.cluster_nodes = cluster_nodes
        self.replication_factor = replication_factor
        self.node_status = {node: 'healthy' for node in cluster_nodes}
        self.config_store = {}
        self.lock = threading.Lock()
        self.heartbeat_interval = 5  # 心跳间隔（秒）
        self.failure_threshold = 3    # 故障阈值
        
    def start_heartbeat_monitoring(self):
        """启动心跳监控"""
        def heartbeat_loop():
            while True:
                self.send_heartbeats()
                self.check_node_health()
                time.sleep(self.heartbeat_interval)
                
        heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        print("✅ Heartbeat monitoring started")
        
    def send_heartbeats(self):
        """发送心跳信号"""
        for node in self.cluster_nodes:
            try:
                # 模拟发送心跳
                status = self.check_node_status(node)
                with self.lock:
                    self.node_status[node] = status
            except Exception as e:
                print(f"❌ Heartbeat failed for node {node}: {e}")
                
    def check_node_status(self, node: str) -> str:
        """检查节点状态"""
        # 模拟节点状态检查
        # 实际应用中应该通过网络请求检查节点健康状态
        import random
        return 'healthy' if random.random() > 0.1 else 'unhealthy'
        
    def check_node_health(self):
        """检查节点健康状态"""
        unhealthy_nodes = []
        with self.lock:
            for node, status in self.node_status.items():
                if status != 'healthy':
                    unhealthy_nodes.append(node)
                    
        if unhealthy_nodes:
            print(f"⚠️ Unhealthy nodes detected: {unhealthy_nodes}")
            self.handle_node_failures(unhealthy_nodes)
            
    def handle_node_failures(self, failed_nodes: List[str]):
        """处理节点故障"""
        for node in failed_nodes:
            print(f"🔄 Handling failure for node {node}")
            # 重新分配该节点的配置数据
            self.reallocate_node_data(node)
            
    def reallocate_node_data(self, failed_node: str):
        """重新分配节点数据"""
        print(f"🔄 Reallocating data from failed node {failed_node}")
        # 这里应该实现数据重新分配逻辑
        # 实际应用中需要将数据复制到其他健康节点
        
    def get_config(self, key: str) -> Any:
        """获取配置值"""
        with self.lock:
            return self.config_store.get(key)
            
    def set_config(self, key: str, value: Any) -> bool:
        """设置配置值"""
        try:
            # 在多个节点上设置配置
            success_count = 0
            for node in self.get_healthy_nodes()[:self.replication_factor]:
                if self.set_config_on_node(node, key, value):
                    success_count += 1
                    
            # 确保大多数节点写入成功
            if success_count >= (self.replication_factor // 2) + 1:
                with self.lock:
                    self.config_store[key] = value
                print(f"✅ Configuration {key} set successfully")
                return True
            else:
                print(f"❌ Failed to set configuration {key}")
                return False
                
        except Exception as e:
            print(f"❌ Error setting configuration {key}: {e}")
            return False
            
    def set_config_on_node(self, node: str, key: str, value: Any) -> bool:
        """在指定节点上设置配置"""
        # 模拟在节点上设置配置
        print(f"📝 Setting config {key} on node {node}")
        return True
        
    def get_healthy_nodes(self) -> List[str]:
        """获取健康节点列表"""
        with self.lock:
            return [node for node, status in self.node_status.items() 
                   if status == 'healthy']
            
    def get_cluster_status(self) -> Dict[str, Any]:
        """获取集群状态"""
        with self.lock:
            healthy_count = sum(1 for status in self.node_status.values() 
                              if status == 'healthy')
            total_count = len(self.node_status)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_nodes': total_count,
                'healthy_nodes': healthy_count,
                'unhealthy_nodes': total_count - healthy_count,
                'node_status': self.node_status.copy(),
                'config_count': len(self.config_store)
            }

# 使用示例
if __name__ == "__main__":
    # 创建高可用配置管理器
    cluster_nodes = ['node1.example.com', 'node2.example.com', 'node3.example.com']
    ha_config_manager = HighAvailabilityConfigManager(cluster_nodes)
    
    # 启动心跳监控
    ha_config_manager.start_heartbeat_monitoring()
    
    # 设置一些配置
    ha_config_manager.set_config('database.host', 'db.example.com')
    ha_config_manager.set_config('cache.redis.host', 'redis.example.com')
    
    # 获取配置
    db_host = ha_config_manager.get_config('database.host')
    print(f"Database host: {db_host}")
    
    # 获取集群状态
    status = ha_config_manager.get_cluster_status()
    print(f"Cluster status: {json.dumps(status, indent=2)}")
    
    # 保持程序运行以观察心跳监控
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("👋 Shutting down...")
```

## 配置管理组件的高可用部署

实现配置管理组件的高可用部署是确保配置服务持续可用的关键步骤。

### 1. 配置存储高可用部署

```bash
# ha-config-storage-deployment.sh

# 高可用配置存储部署脚本
deploy_ha_config_storage() {
    local storage_type=${1:-"etcd"}
    local cluster_size=${2:-3}
    
    echo "Deploying HA configuration storage: $storage_type with $cluster_size nodes"
    
    case "$storage_type" in
        "etcd")
            deploy_etcd_cluster "$cluster_size"
            ;;
        "consul")
            deploy_consul_cluster "$cluster_size"
            ;;
        "zookeeper")
            deploy_zookeeper_cluster "$cluster_size"
            ;;
        *)
            echo "Unsupported storage type: $storage_type"
            return 1
            ;;
    esac
    
    # 验证部署
    verify_storage_deployment "$storage_type"
    
    echo "HA configuration storage deployment completed"
}

# 部署etcd集群
deploy_etcd_cluster() {
    local cluster_size=$1
    echo "Deploying etcd cluster with $cluster_size nodes"
    
    # 创建etcd配置
    create_etcd_config "$cluster_size"
    
    # 部署etcd节点
    for i in $(seq 1 $cluster_size); do
        echo "Deploying etcd node $i"
        deploy_etcd_node $i "$cluster_size"
    done
    
    # 等待集群稳定
    wait_for_etcd_cluster_ready "$cluster_size"
    
    # 验证集群状态
    verify_etcd_cluster_status
}

# 创建etcd配置
create_etcd_config() {
    local cluster_size=$1
    local cluster_tokens=()
    
    # 生成集群令牌
    for i in $(seq 1 $cluster_size); do
        cluster_tokens+=("etcd-node-$i=http://etcd-node-$i:2380")
    done
    
    local cluster_state=$(IFS=','; echo "${cluster_tokens[*]}")
    
    # 为每个节点创建配置
    for i in $(seq 1 $cluster_size); do
        cat > /tmp/etcd-config-node-$i.yaml << EOF
name: 'etcd-node-$i'
data-dir: '/var/lib/etcd'
listen-peer-urls: 'http://0.0.0.0:2380'
listen-client-urls: 'http://0.0.0.0:2379'
initial-advertise-peer-urls: 'http://etcd-node-$i:2380'
advertise-client-urls: 'http://etcd-node-$i:2379'
initial-cluster: '$cluster_state'
initial-cluster-state: 'new'
initial-cluster-token: 'etcd-cluster-1'
EOF
    done
}

# 部署单个etcd节点
deploy_etcd_node() {
    local node_id=$1
    local cluster_size=$2
    
    echo "Deploying etcd node $node_id"
    
    # 使用Docker部署etcd节点
    docker run -d \
        --name etcd-node-$node_id \
        --network host \
        -v /tmp/etcd-config-node-$node_id.yaml:/etc/etcd/etcd.conf.yml \
        -v /var/lib/etcd:/var/lib/etcd \
        quay.io/coreos/etcd:v3.5.0 \
        etcd \
        --config-file=/etc/etcd/etcd.conf.yml
        
    echo "✅ etcd node $node_id deployed"
}

# 等待etcd集群就绪
wait_for_etcd_cluster_ready() {
    local cluster_size=$1
    local timeout=300  # 5分钟超时
    local interval=10
    local elapsed=0
    
    echo "Waiting for etcd cluster to be ready..."
    
    while [ $elapsed -lt $timeout ]; do
        if check_etcd_cluster_health; then
            echo "✅ etcd cluster is ready"
            return 0
        fi
        
        echo "etcd cluster not ready, waiting $interval seconds..."
        sleep $interval
        elapsed=$((elapsed + interval))
    done
    
    echo "❌ etcd cluster failed to become ready within timeout"
    return 1
}

# 检查etcd集群健康状态
check_etcd_cluster_health() {
    # 检查集群成员
    if docker exec etcd-node-1 etcdctl member list >/dev/null 2>&1; then
        # 检查集群健康状态
        if docker exec etcd-node-1 etcdctl endpoint health >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# 验证etcd集群状态
verify_etcd_cluster_status() {
    echo "Verifying etcd cluster status"
    
    # 显示集群成员
    echo "Cluster members:"
    docker exec etcd-node-1 etcdctl member list
    
    # 显示集群状态
    echo "Cluster status:"
    docker exec etcd-node-1 etcdctl endpoint status --write-out=table
    
    echo "✅ etcd cluster verification completed"
}

# 部署Consul集群
deploy_consul_cluster() {
    local cluster_size=$1
    echo "Deploying Consul cluster with $cluster_size nodes"
    
    # 创建Consul配置
    create_consul_config "$cluster_size"
    
    # 部署Consul节点
    for i in $(seq 1 $cluster_size); do
        echo "Deploying Consul node $i"
        deploy_consul_node $i "$cluster_size"
    done
    
    # 等待集群稳定
    wait_for_consul_cluster_ready "$cluster_size"
    
    # 验证集群状态
    verify_consul_cluster_status
}

# 创建Consul配置
create_consul_config() {
    local cluster_size=$1
    
    # 为每个节点创建配置
    for i in $(seq 1 $cluster_size); do
        cat > /tmp/consul-config-node-$i.json << EOF
{
    "datacenter": "dc1",
    "data_dir": "/var/lib/consul",
    "log_level": "INFO",
    "node_name": "consul-node-$i",
    "server": true,
    "ui": true,
    "bind_addr": "0.0.0.0",
    "client_addr": "0.0.0.0",
    "bootstrap_expect": $cluster_size,
    "retry_join": [
        "consul-node-1",
        "consul-node-2",
        "consul-node-3"
    ],
    "ports": {
        "dns": 8600,
        "http": 8500,
        "https": 8501,
        "serf_lan": 8301,
        "serf_wan": 8302,
        "server": 8300
    }
}
EOF
    done
}

# 部署单个Consul节点
deploy_consul_node() {
    local node_id=$1
    local cluster_size=$2
    
    echo "Deploying Consul node $node_id"
    
    # 使用Docker部署Consul节点
    docker run -d \
        --name consul-node-$node_id \
        --network host \
        -v /tmp/consul-config-node-$node_id.json:/consul/config/consul.json \
        -v /var/lib/consul:/var/lib/consul \
        hashicorp/consul:1.10.0 \
        agent -config-file=/consul/config/consul.json
        
    echo "✅ Consul node $node_id deployed"
}

# 等待Consul集群就绪
wait_for_consul_cluster_ready() {
    local cluster_size=$1
    local timeout=300  # 5分钟超时
    local interval=10
    local elapsed=0
    
    echo "Waiting for Consul cluster to be ready..."
    
    while [ $elapsed -lt $timeout ]; do
        if check_consul_cluster_health; then
            echo "✅ Consul cluster is ready"
            return 0
        fi
        
        echo "Consul cluster not ready, waiting $interval seconds..."
        sleep $interval
        elapsed=$((elapsed + interval))
    done
    
    echo "❌ Consul cluster failed to become ready within timeout"
    return 1
}

# 检查Consul集群健康状态
check_consul_cluster_health() {
    # 检查集群成员
    if docker exec consul-node-1 consul members >/dev/null 2>&1; then
        # 检查领导选举
        if docker exec consul-node-1 consul operator raft list-peers >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# 验证Consul集群状态
verify_consul_cluster_status() {
    echo "Verifying Consul cluster status"
    
    # 显示集群成员
    echo "Cluster members:"
    docker exec consul-node-1 consul members
    
    # 显示Raft状态
    echo "Raft status:"
    docker exec consul-node-1 consul operator raft list-peers
    
    echo "✅ Consul cluster verification completed"
}

# 验证存储部署
verify_storage_deployment() {
    local storage_type=$1
    
    echo "Verifying $storage_type deployment"
    
    case "$storage_type" in
        "etcd")
            verify_etcd_deployment
            ;;
        "consul")
            verify_consul_deployment
            ;;
        "zookeeper")
            verify_zookeeper_deployment
            ;;
    esac
}

# 验证etcd部署
verify_etcd_deployment() {
    echo "Verifying etcd deployment"
    
    # 检查节点运行状态
    for container in $(docker ps --filter "name=etcd-node-" --format "{{.Names}}"); do
        if docker inspect $container >/dev/null 2>&1; then
            echo "✅ $container is running"
        else
            echo "❌ $container is not running"
            return 1
        fi
    done
    
    # 检查集群健康
    if check_etcd_cluster_health; then
        echo "✅ etcd cluster is healthy"
    else
        echo "❌ etcd cluster is unhealthy"
        return 1
    fi
}

# 使用示例
# deploy_ha_config_storage "etcd" 3
```

### 2. 配置服务高可用部署

```yaml
# ha-config-service-deployment.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: config-service-ha
  labels:
    app: config-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: config-service
  template:
    metadata:
      labels:
        app: config-service
    spec:
      containers:
      - name: config-service
        image: mycompany/config-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: STORAGE_TYPE
          value: "etcd"
        - name: ETCD_ENDPOINTS
          value: "etcd-node-1:2379,etcd-node-2:2379,etcd-node-3:2379"
        - name: CLUSTER_MODE
          value: "true"
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
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
  name: config-service
  labels:
    app: config-service
spec:
  selector:
    app: config-service
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: config-service-external
  labels:
    app: config-service
spec:
  selector:
    app: config-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

## 负载均衡与故障转移机制

有效的负载均衡和故障转移机制是实现高可用配置管理的关键。

### 1. 负载均衡策略

```python
# load-balancer.py
import random
import time
from typing import List, Dict, Any
from enum import Enum

class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"

class ConfigServiceLoadBalancer:
    def __init__(self, servers: List[Dict[str, Any]], strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN):
        self.servers = servers
        self.strategy = strategy
        self.index = 0
        self.connection_counts = {server['host']: 0 for server in servers}
        self.failure_counts = {server['host']: 0 for server in servers}
        self.failure_threshold = 3
        self.cooldown_period = 60  # 60秒冷却期
        self.last_failure_time = {server['host']: 0 for server in servers}
        
    def get_healthy_server(self) -> Dict[str, Any]:
        """获取健康的服务器"""
        healthy_servers = self.get_healthy_servers()
        
        if not healthy_servers:
            raise Exception("No healthy servers available")
            
        return self.select_server(healthy_servers)
        
    def get_healthy_servers(self) -> List[Dict[str, Any]]:
        """获取所有健康服务器"""
        current_time = time.time()
        healthy_servers = []
        
        for server in self.servers:
            host = server['host']
            
            # 检查是否在冷却期
            if current_time - self.last_failure_time[host] < self.cooldown_period:
                continue
                
            # 检查故障次数
            if self.failure_counts[host] < self.failure_threshold:
                healthy_servers.append(server)
                
        return healthy_servers
        
    def select_server(self, servers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """根据策略选择服务器"""
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self.round_robin_select(servers)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return self.random_select(servers)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self.least_connections_select(servers)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self.weighted_round_robin_select(servers)
        else:
            return servers[0]  # 默认选择第一个
            
    def round_robin_select(self, servers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """轮询选择"""
        server = servers[self.index % len(servers)]
        self.index = (self.index + 1) % len(servers)
        return server
        
    def random_select(self, servers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """随机选择"""
        return random.choice(servers)
        
    def least_connections_select(self, servers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """最少连接选择"""
        min_connections = float('inf')
        selected_server = servers[0]
        
        for server in servers:
            connections = self.connection_counts.get(server['host'], 0)
            if connections < min_connections:
                min_connections = connections
                selected_server = server
                
        return selected_server
        
    def weighted_round_robin_select(self, servers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """加权轮询选择"""
        # 简化实现，实际应用中需要更复杂的权重计算
        return self.round_robin_select(servers)
        
    def mark_server_success(self, host: str):
        """标记服务器请求成功"""
        self.connection_counts[host] = max(0, self.connection_counts[host] - 1)
        self.failure_counts[host] = 0  # 重置故障计数
        
    def mark_server_failure(self, host: str):
        """标记服务器请求失败"""
        self.failure_counts[host] += 1
        self.last_failure_time[host] = time.time()
        print(f"❌ Marked server {host} as failed (count: {self.failure_counts[host]})")
        
    def get_server_stats(self) -> Dict[str, Any]:
        """获取服务器统计信息"""
        return {
            'total_servers': len(self.servers),
            'healthy_servers': len(self.get_healthy_servers()),
            'connection_counts': self.connection_counts.copy(),
            'failure_counts': self.failure_counts.copy(),
            'strategy': self.strategy.value
        }

# 使用示例
if __name__ == "__main__":
    # 配置服务器列表
    servers = [
        {'host': 'config1.example.com', 'port': 8080, 'weight': 1},
        {'host': 'config2.example.com', 'port': 8080, 'weight': 1},
        {'host': 'config3.example.com', 'port': 8080, 'weight': 1}
    ]
    
    # 创建负载均衡器
    lb = ConfigServiceLoadBalancer(servers, LoadBalancingStrategy.ROUND_ROBIN)
    
    # 模拟请求分发
    for i in range(10):
        try:
            server = lb.get_healthy_server()
            print(f"Request {i+1}: Selected server {server['host']}")
            
            # 模拟请求处理
            import random
            if random.random() < 0.2:  # 20%失败率
                lb.mark_server_failure(server['host'])
                print(f"❌ Request {i+1} failed on {server['host']}")
            else:
                lb.mark_server_success(server['host'])
                print(f"✅ Request {i+1} succeeded on {server['host']}")
                
        except Exception as e:
            print(f"❌ No healthy servers available: {e}")
            
        time.sleep(1)
        
    # 显示服务器统计
    stats = lb.get_server_stats()
    print(f"\nServer Statistics: {stats}")
```

### 2. 故障转移实现

```bash
# failover-mechanism.sh

# 故障转移机制脚本
implement_failover_mechanism() {
    local service_name=${1:-"config-service"}
    
    echo "Implementing failover mechanism for $service_name"
    
    # 1. 配置健康检查
    echo "Step 1: Configuring health checks"
    configure_health_checks "$service_name"
    
    # 2. 实施故障检测
    echo "Step 2: Implementing failure detection"
    implement_failure_detection "$service_name"
    
    # 3. 配置故障转移
    echo "Step 3: Configuring failover"
    configure_failover "$service_name"
    
    # 4. 设置恢复机制
    echo "Step 4: Setting up recovery mechanisms"
    setup_recovery_mechanisms "$service_name"
    
    # 5. 验证故障转移
    echo "Step 5: Verifying failover mechanism"
    verify_failover_mechanism "$service_name"
    
    echo "Failover mechanism implementation completed"
}

# 配置健康检查
configure_health_checks() {
    local service_name=$1
    
    echo "Configuring health checks for $service_name"
    
    # 创建健康检查脚本
    cat > /usr/local/bin/health-check-$service_name.sh << 'EOF'
#!/bin/bash
SERVICE_NAME="$1"
HEALTH_ENDPOINT="$2"
TIMEOUT="${3:-10}"

# 检查服务进程是否存在
if ! pgrep -f "$SERVICE_NAME" > /dev/null; then
    echo "❌ Service process not found"
    exit 1
fi

# 检查健康端点
if curl -f -s --max-time $TIMEOUT "$HEALTH_ENDPOINT" > /dev/null; then
    echo "✅ Service is healthy"
    exit 0
else
    echo "❌ Service health check failed"
    exit 1
fi
EOF

    chmod +x /usr/local/bin/health-check-$service_name.sh
    
    # 配置系统级健康检查
    cat > /etc/systemd/system/$service_name-healthcheck.service << EOF
[Unit]
Description=Health check for $service_name
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/health-check-$service_name.sh "$service_name" "http://localhost:8080/health" 10
EOF

    cat > /etc/systemd/system/$service_name-healthcheck.timer << EOF
[Unit]
Description=Run health check for $service_name every 30 seconds
Requires=$service_name-healthcheck.service

[Timer]
OnBootSec=30
OnUnitActiveSec=30

[Install]
WantedBy=timers.target
EOF

    # 启用健康检查定时器
    systemctl daemon-reload
    systemctl enable $service_name-healthcheck.timer
    systemctl start $service_name-healthcheck.timer
    
    echo "✅ Health checks configured for $service_name"
}

# 实施故障检测
implement_failure_detection() {
    local service_name=$1
    
    echo "Implementing failure detection for $service_name"
    
    # 创建故障检测脚本
    cat > /usr/local/bin/failure-detection-$service_name.sh << 'EOF'
#!/bin/bash
SERVICE_NAME="$1"
MAX_FAILURES="${2:-3}"
COOLDOWN_PERIOD="${3:-60}"

STATE_FILE="/var/run/$SERVICE_NAME-failure-state"
LOG_FILE="/var/log/$SERVICE_NAME-failure.log"

# 初始化状态文件
if [ ! -f "$STATE_FILE" ]; then
    echo "0,0,$(date +%s)" > "$STATE_FILE"
fi

# 读取当前状态
read failures last_failure last_cooldown < "$STATE_FILE"

# 检查服务健康状态
if /usr/local/bin/health-check-$SERVICE_NAME.sh "$SERVICE_NAME" "http://localhost:8080/health" 10; then
    # 服务健康，重置失败计数但保持冷却时间
    echo "0,$last_failure,$last_cooldown" > "$STATE_FILE"
    echo "$(date): Service $SERVICE_NAME is healthy" >> "$LOG_FILE"
    exit 0
else
    # 服务不健康，增加失败计数
    current_time=$(date +%s)
    new_failures=$((failures + 1))
    echo "$new_failures,$current_time,$last_cooldown" > "$STATE_FILE"
    echo "$(date): Service $SERVICE_NAME failure detected (count: $new_failures)" >> "$LOG_FILE"
    
    # 检查是否达到故障阈值
    if [ $new_failures -ge $MAX_FAILURES ]; then
        # 检查是否在冷却期内
        if [ $((current_time - last_cooldown)) -ge $COOLDOWN_PERIOD ]; then
            echo "$(date): Failure threshold reached for $SERVICE_NAME, triggering failover" >> "$LOG_FILE"
            # 触发故障转移
            /usr/local/bin/trigger-failover-$SERVICE_NAME.sh
            # 更新冷却时间
            echo "$new_failures,$current_time,$current_time" > "$STATE_FILE"
        else
            echo "$(date): In cooldown period, not triggering failover" >> "$LOG_FILE"
        fi
        exit 1
    fi
    exit 0
fi
EOF

    chmod +x /usr/local/bin/failure-detection-$service_name.sh
    
    # 配置故障检测定时器
    cat > /etc/systemd/system/$service_name-failure-detection.service << EOF
[Unit]
Description=Failure detection for $service_name
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/failure-detection-$service_name.sh "$service_name" 3 60
EOF

    cat > /etc/systemd/system/$service_name-failure-detection.timer << EOF
[Unit]
Description=Run failure detection for $service_name every 10 seconds
Requires=$service_name-failure-detection.service

[Timer]
OnBootSec=10
OnUnitActiveSec=10

[Install]
WantedBy=timers.target
EOF

    # 启用故障检测定时器
    systemctl daemon-reload
    systemctl enable $service_name-failure-detection.timer
    systemctl start $service_name-failure-detection.timer
    
    echo "✅ Failure detection implemented for $service_name"
}

# 配置故障转移
configure_failover() {
    local service_name=$1
    
    echo "Configuring failover for $service_name"
    
    # 创建故障转移脚本
    cat > /usr/local/bin/trigger-failover-$service_name.sh << 'EOF'
#!/bin/bash
SERVICE_NAME="$1"
BACKUP_SERVICE="${2:-$SERVICE_NAME-backup}"

LOG_FILE="/var/log/$SERVICE_NAME-failover.log"

echo "$(date): Starting failover process for $SERVICE_NAME" >> "$LOG_FILE"

# 停止主服务
echo "$(date): Stopping primary service" >> "$LOG_FILE"
systemctl stop "$SERVICE_NAME" 2>> "$LOG_FILE"

# 启动备份服务
echo "$(date): Starting backup service" >> "$LOG_FILE"
systemctl start "$BACKUP_SERVICE" 2>> "$LOG_FILE"

# 检查备份服务状态
if systemctl is-active "$BACKUP_SERVICE" > /dev/null; then
    echo "$(date): Failover successful, backup service is running" >> "$LOG_FILE"
    
    # 发送告警通知
    echo "Failover triggered for $SERVICE_NAME at $(date)" | mail -s "Service Failover Alert" admin@example.com
    
    # 记录故障转移事件
    echo "$(date): Failover completed successfully" >> "/var/log/service-failover-events.log"
    
    exit 0
else
    echo "$(date): Failover failed, backup service did not start" >> "$LOG_FILE"
    
    # 发送紧急告警
    echo "CRITICAL: Failover failed for $SERVICE_NAME at $(date)" | mail -s "CRITICAL: Service Failover Failed" admin@example.com
    
    exit 1
fi
EOF

    chmod +x /usr/local/bin/trigger-failover-$service_name.sh
    
    echo "✅ Failover configured for $service_name"
}

# 设置恢复机制
setup_recovery_mechanisms() {
    local service_name=$1
    
    echo "Setting up recovery mechanisms for $service_name"
    
    # 创建服务恢复脚本
    cat > /usr/local/bin/recovery-$service_name.sh << 'EOF'
#!/bin/bash
SERVICE_NAME="$1"
PRIMARY_SERVICE="$SERVICE_NAME"
BACKUP_SERVICE="${SERVICE_NAME}-backup"

LOG_FILE="/var/log/$SERVICE_NAME-recovery.log"

echo "$(date): Starting recovery process for $SERVICE_NAME" >> "$LOG_FILE"

# 检查主服务是否可以恢复
if /usr/local/bin/can-recover-$SERVICE_NAME.sh; then
    echo "$(date): Primary service can be recovered" >> "$LOG_FILE"
    
    # 停止备份服务
    echo "$(date): Stopping backup service" >> "$LOG_FILE"
    systemctl stop "$BACKUP_SERVICE" 2>> "$LOG_FILE"
    
    # 启动主服务
    echo "$(date): Starting primary service" >> "$LOG_FILE"
    systemctl start "$PRIMARY_SERVICE" 2>> "$LOG_FILE"
    
    # 等待服务启动
    sleep 10
    
    # 验证主服务健康状态
    if /usr/local/bin/health-check-$SERVICE_NAME.sh "$SERVICE_NAME" "http://localhost:8080/health" 10; then
        echo "$(date): Recovery successful, primary service is healthy" >> "$LOG_FILE"
        
        # 发送恢复通知
        echo "Service $SERVICE_NAME recovered at $(date)" | mail -s "Service Recovery Notification" admin@example.com
        
        exit 0
    else
        echo "$(date): Recovery failed, primary service is still unhealthy" >> "$LOG_FILE"
        
        # 重新启动备份服务
        echo "$(date): Restarting backup service" >> "$LOG_FILE"
        systemctl start "$BACKUP_SERVICE" 2>> "$LOG_FILE"
        
        exit 1
    fi
else
    echo "$(date): Primary service cannot be recovered yet" >> "$LOG_FILE"
    exit 1
fi
EOF

    chmod +x /usr/local/bin/recovery-$service_name.sh
    
    # 创建恢复条件检查脚本
    cat > /usr/local/bin/can-recover-$service_name.sh << 'EOF'
#!/bin/bash
SERVICE_NAME="$1"

# 检查故障根本原因是否已解决
# 这里可以添加具体的恢复条件检查逻辑
# 例如：检查依赖服务状态、网络连接、资源配置等

echo "$(date): Checking recovery conditions for $SERVICE_NAME" >> "/var/log/$SERVICE_NAME-recovery-check.log"

# 简化示例：总是可以恢复
exit 0
EOF

    chmod +x /usr/local/bin/can-recover-$service_name.sh
    
    echo "✅ Recovery mechanisms set up for $service_name"
}

# 验证故障转移机制
verify_failover_mechanism() {
    local service_name=$1
    
    echo "Verifying failover mechanism for $service_name"
    
    # 检查相关服务状态
    echo "Checking systemd services:"
    systemctl status $service_name-healthcheck.timer 2>/dev/null || echo "Health check timer not found"
    systemctl status $service_name-failure-detection.timer 2>/dev/null || echo "Failure detection timer not found"
    
    # 检查脚本是否存在
    echo "Checking scripts:"
    for script in health-check-$service_name.sh failure-detection-$service_name.sh trigger-failover-$service_name.sh recovery-$service_name.sh; do
        if [ -f "/usr/local/bin/$script" ]; then
            echo "✅ $script exists"
        else
            echo "❌ $script not found"
        fi
    done
    
    echo "✅ Failover mechanism verification completed"
}

# 使用示例
# implement_failover_mechanism "config-service"
```

## 健康检查与自动恢复策略

建立完善的健康检查和自动恢复策略是确保高可用性系统稳定运行的重要保障。

### 1. 多层次健康检查

```python
# health-check-framework.py
import requests
import subprocess
import psutil
import time
from typing import Dict, List, Any, Callable
from datetime import datetime
from enum import Enum

class HealthCheckType(Enum):
    HTTP = "http"
    TCP = "tcp"
    PROCESS = "process"
    DISK = "disk"
    MEMORY = "memory"
    CUSTOM = "custom"

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class HealthCheckFramework:
    def __init__(self):
        self.checks = []
        self.results = []
        self.alert_handlers = []
        
    def add_health_check(self, name: str, check_type: HealthCheckType, 
                        check_func: Callable, threshold: float = 0.8,
                        critical: bool = False):
        """添加健康检查"""
        check = {
            'name': name,
            'type': check_type,
            'function': check_func,
            'threshold': threshold,
            'critical': critical,
            'last_result': None,
            'failure_count': 0
        }
        self.checks.append(check)
        print(f"✅ Added health check: {name}")
        
    def run_health_checks(self) -> Dict[str, Any]:
        """运行所有健康检查"""
        print("🏃 Running health checks...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_checks': len(self.checks),
            'passed_checks': 0,
            'failed_checks': 0,
            'critical_failures': 0,
            'check_details': []
        }
        
        for check in self.checks:
            try:
                status, message = check['function']()
                check['last_result'] = {
                    'status': status,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }
                
                check_result = {
                    'name': check['name'],
                    'type': check['type'].value,
                    'status': status.value,
                    'message': message
                }
                
                results['check_details'].append(check_result)
                
                if status == HealthStatus.HEALTHY:
                    results['passed_checks'] += 1
                    check['failure_count'] = 0
                else:
                    results['failed_checks'] += 1
                    check['failure_count'] += 1
                    
                    if check['critical']:
                        results['critical_failures'] += 1
                        
                    # 触发告警
                    self.trigger_alerts(check, status, message)
                    
            except Exception as e:
                error_message = f"Health check execution failed: {str(e)}"
                check_result = {
                    'name': check['name'],
                    'type': check['type'].value,
                    'status': HealthStatus.UNKNOWN.value,
                    'message': error_message
                }
                results['check_details'].append(check_result)
                results['failed_checks'] += 1
                
        self.results.append(results)
        return results
        
    def trigger_alerts(self, check: Dict[str, Any], status: HealthStatus, message: str):
        """触发告警"""
        alert_info = {
            'check_name': check['name'],
            'status': status.value,
            'message': message,
            'failure_count': check['failure_count'],
            'timestamp': datetime.now().isoformat()
        }
        
        for handler in self.alert_handlers:
            try:
                handler(alert_info)
            except Exception as e:
                print(f"❌ Alert handler failed: {e}")
                
    def add_alert_handler(self, handler: Callable):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
        print("✅ Alert handler added")
        
    def get_system_health(self) -> HealthStatus:
        """获取系统整体健康状态"""
        if not self.results:
            return HealthStatus.UNKNOWN
            
        latest_result = self.results[-1]
        
        # 如果有关键故障，系统不健康
        if latest_result['critical_failures'] > 0:
            return HealthStatus.UNHEALTHY
            
        # 如果失败检查超过阈值，系统降级
        failure_rate = latest_result['failed_checks'] / latest_result['total_checks']
        if failure_rate > 0.5:
            return HealthStatus.DEGRADED
            
        # 如果有失败检查但不超过阈值，系统降级
        if latest_result['failed_checks'] > 0:
            return HealthStatus.DEGRADED
            
        return HealthStatus.HEALTHY

# 预定义的健康检查函数
def http_health_check(url: str, expected_status: int = 200, timeout: int = 10) -> tuple:
    """HTTP健康检查"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == expected_status:
            return (HealthStatus.HEALTHY, f"HTTP {response.status_code}")
        else:
            return (HealthStatus.DEGRADED, f"HTTP {response.status_code}, expected {expected_status}")
    except requests.exceptions.RequestException as e:
        return (HealthStatus.UNHEALTHY, f"HTTP request failed: {str(e)}")
        
def tcp_health_check(host: str, port: int, timeout: int = 5) -> tuple:
    """TCP端口健康检查"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return (HealthStatus.HEALTHY, f"TCP port {port} is open")
        else:
            return (HealthStatus.UNHEALTHY, f"TCP port {port} is closed")
    except Exception as e:
        return (HealthStatus.UNHEALTHY, f"TCP check failed: {str(e)}")
        
def process_health_check(process_name: str) -> tuple:
    """进程健康检查"""
    try:
        # 检查进程是否存在
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name:
                return (HealthStatus.HEALTHY, f"Process {process_name} is running (PID: {proc.info['pid']})")
                
        return (HealthStatus.UNHEALTHY, f"Process {process_name} is not running")
    except Exception as e:
        return (HealthStatus.UNKNOWN, f"Process check failed: {str(e)}")
        
def disk_health_check(threshold: float = 80.0) -> tuple:
    """磁盘健康检查"""
    try:
        disk_usage = psutil.disk_usage('/')
        usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        if usage_percent > threshold:
            return (HealthStatus.DEGRADED, f"Disk usage is high: {usage_percent:.1f}%")
        else:
            return (HealthStatus.HEALTHY, f"Disk usage is normal: {usage_percent:.1f}%")
    except Exception as e:
        return (HealthStatus.UNKNOWN, f"Disk check failed: {str(e)}")
        
def memory_health_check(threshold: float = 85.0) -> tuple:
    """内存健康检查"""
    try:
        memory = psutil.virtual_memory()
        usage_percent = memory.percent
        
        if usage_percent > threshold:
            return (HealthStatus.DEGRADED, f"Memory usage is high: {usage_percent:.1f}%")
        else:
            return (HealthStatus.HEALTHY, f"Memory usage is normal: {usage_percent:.1f}%")
    except Exception as e:
        return (HealthStatus.UNKNOWN, f"Memory check failed: {str(e)}")

# 告警处理器示例
def email_alert_handler(alert_info: Dict[str, Any]):
    """邮件告警处理器"""
    print(f"📧 Sending email alert: {alert_info}")
    # 这里应该实现实际的邮件发送逻辑
    
def slack_alert_handler(alert_info: Dict[str, Any]):
    """Slack告警处理器"""
    print(f"💬 Sending Slack alert: {alert_info}")
    # 这里应该实现实际的Slack消息发送逻辑
    
def log_alert_handler(alert_info: Dict[str, Any]):
    """日志告警处理器"""
    with open('/var/log/health-alerts.log', 'a') as f:
        f.write(f"{datetime.now().isoformat()}: {alert_info}\n")
    print(f"📝 Logged alert: {alert_info}")

# 使用示例
if __name__ == "__main__":
    # 创建健康检查框架
    health_framework = HealthCheckFramework()
    
    # 添加健康检查
    health_framework.add_health_check(
        "config-service-health",
        HealthCheckType.HTTP,
        lambda: http_health_check("http://localhost:8080/health"),
        critical=True
    )
    
    health_framework.add_health_check(
        "database-connection",
        HealthCheckType.TCP,
        lambda: tcp_health_check("localhost", 5432),
        critical=True
    )
    
    health_framework.add_health_check(
        "config-process",
        HealthCheckType.PROCESS,
        lambda: process_health_check("config-service")
    )
    
    health_framework.add_health_check(
        "disk-usage",
        HealthCheckType.DISK,
        lambda: disk_health_check(85.0)
    )
    
    health_framework.add_health_check(
        "memory-usage",
        HealthCheckType.MEMORY,
        lambda: memory_health_check(90.0)
    )
    
    # 添加告警处理器
    health_framework.add_alert_handler(email_alert_handler)
    health_framework.add_alert_handler(slack_alert_handler)
    health_framework.add_alert_handler(log_alert_handler)
    
    # 运行健康检查
    results = health_framework.run_health_checks()
    print(f"Health check results: {results}")
    
    # 获取系统健康状态
    system_health = health_framework.get_system_health()
    print(f"System health status: {system_health.value}")
```

### 2. 自动恢复机制

```bash
# auto-recovery.sh

# 自动恢复机制脚本
implement_auto_recovery() {
    local service_name=${1:-"config-service"}
    
    echo "Implementing auto recovery for $service_name"
    
    # 1. 配置自动恢复检查
    echo "Step 1: Configuring auto recovery checks"
    configure_auto_recovery_checks "$service_name"
    
    # 2. 实施自动恢复策略
    echo "Step 2: Implementing auto recovery strategies"
    implement_recovery_strategies "$service_name"
    
    # 3. 设置恢复监控
    echo "Step 3: Setting up recovery monitoring"
    setup_recovery_monitoring "$service_name"
    
    # 4. 验证自动恢复
    echo "Step 4: Verifying auto recovery mechanism"
    verify_auto_recovery "$service_name"
    
    echo "Auto recovery implementation completed"
}

# 配置自动恢复检查
configure_auto_recovery_checks() {
    local service_name=$1
    
    echo "Configuring auto recovery checks for $service_name"
    
    # 创建恢复条件检查脚本
    cat > /usr/local/bin/check-recovery-conditions-$service_name.sh << 'EOF'
#!/bin/bash
SERVICE_NAME="$1"
LOG_FILE="/var/log/$SERVICE_NAME-recovery-check.log"

echo "$(date): Checking recovery conditions for $SERVICE_NAME" >> "$LOG_FILE"

# 检查基本条件
RECOVERY_POSSIBLE=true
REASONS=()

# 检查依赖服务
if ! systemctl is-active database.service >/dev/null 2>&1; then
    RECOVERY_POSSIBLE=false
    REASONS+=("Database service is not running")
    echo "$(date): Database service is not running" >> "$LOG_FILE"
fi

# 检查网络连接
if ! ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    RECOVERY_POSSIBLE=false
    REASONS+=("Network connectivity issue")
    echo "$(date): Network connectivity issue detected" >> "$LOG_FILE"
fi

# 检查磁盘空间
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    RECOVERY_POSSIBLE=false
    REASONS+=("Disk space is critically low")
    echo "$(date): Disk space critically low ($DISK_USAGE%)" >> "$LOG_FILE"
fi

# 检查内存使用率
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ "$MEMORY_USAGE" -gt 95 ]; then
    RECOVERY_POSSIBLE=false
    REASONS+=("Memory usage is critically high")
    echo "$(date): Memory usage critically high ($MEMORY_USAGE%)" >> "$LOG_FILE"
fi

if [ "$RECOVERY_POSSIBLE" = true ]; then
    echo "$(date): Recovery conditions are met" >> "$LOG_FILE"
    echo "RECOVERY_POSSIBLE"
else
    echo "$(date): Recovery conditions not met: ${REASONS[*]}" >> "$LOG_FILE"
    echo "RECOVERY_NOT_POSSIBLE"
fi
EOF

    chmod +x /usr/local/bin/check-recovery-conditions-$service_name.sh
    
    echo "✅ Auto recovery checks configured for $service_name"
}

# 实施恢复策略
implement_recovery_strategies() {
    local service_name=$1
    
    echo "Implementing recovery strategies for $service_name"
    
    # 创建服务重启策略
    cat > /usr/local/bin/recovery-strategy-restart-$service_name.sh << 'EOF'
#!/bin/bash
SERVICE_NAME="$1"
LOG_FILE="/var/log/$SERVICE_NAME-recovery.log"

echo "$(date): Executing restart recovery strategy for $SERVICE_NAME" >> "$LOG_FILE"

# 停止服务
echo "$(date): Stopping service" >> "$LOG_FILE"
systemctl stop "$SERVICE_NAME" 2>> "$LOG_FILE"

# 等待服务完全停止
sleep 5

# 清理临时文件
echo "$(date): Cleaning temporary files" >> "$LOG_FILE"
rm -rf /tmp/$SERVICE_NAME-* 2>> "$LOG_FILE"
rm -rf /var/run/$SERVICE_NAME.pid 2>> "$LOG_FILE"

# 重启服务
echo "$(date): Starting service" >> "$LOG_FILE"
systemctl start "$SERVICE_NAME" 2>> "$LOG_FILE"

# 等待服务启动
sleep 10

# 验证服务状态
if systemctl is-active "$SERVICE_NAME" >/dev/null 2>&1; then
    echo "$(date): Service restarted successfully" >> "$LOG_FILE"
    exit 0
else
    echo "$(date): Service restart failed" >> "$LOG_FILE"
    exit 1
fi
EOF

    chmod +x /usr/local/bin/recovery-strategy-restart-$service_name.sh
    
    # 创建配置重载策略
    cat > /usr/local/bin/recovery-strategy-reload-$service_name.sh << 'EOF'
#!/bin/bash
SERVICE_NAME="$1"
LOG_FILE="/var/log/$SERVICE_NAME-recovery.log"

echo "$(date): Executing reload recovery strategy for $SERVICE_NAME" >> "$LOG_FILE"

# 重新加载配置
echo "$(date): Reloading configuration" >> "$LOG_FILE"
systemctl reload "$SERVICE_NAME" 2>> "$LOG_FILE"

# 等待重载完成
sleep 5

# 验证服务状态
if systemctl is-active "$SERVICE_NAME" >/dev/null 2>&1; then
    echo "$(date): Configuration reloaded successfully" >> "$LOG_FILE"
    exit 0
else
    echo "$(date): Configuration reload failed" >> "$LOG_FILE"
    exit 1
fi
EOF

    chmod +x /usr/local/bin/recovery-strategy-reload-$service_name.sh
    
    # 创建完整恢复策略
    cat > /usr/local/bin/recovery-strategy-full-$service_name.sh << 'EOF'
#!/bin/bash
SERVICE_NAME="$1"
LOG_FILE="/var/log/$SERVICE_NAME-recovery.log"

echo "$(date): Executing full recovery strategy for $SERVICE_NAME" >> "$LOG_FILE"

# 停止服务
echo "$(date): Stopping service" >> "$LOG_FILE"
systemctl stop "$SERVICE_NAME" 2>> "$LOG_FILE"

# 备份当前配置
echo "$(date): Backing up current configuration" >> "$LOG_FILE"
cp -r /etc/$SERVICE_NAME /etc/$SERVICE_NAME.backup.$(date +%Y%m%d%H%M%S) 2>> "$LOG_FILE"

# 恢复默认配置
echo "$(date): Restoring default configuration" >> "$LOG_FILE"
cp -r /etc/$SERVICE_NAME.default/* /etc/$SERVICE_NAME/ 2>> "$LOG_FILE"

# 清理数据
echo "$(date): Cleaning service data" >> "$LOG_FILE"
rm -rf /var/lib/$SERVICE_NAME/* 2>> "$LOG_FILE"

# 重启服务
echo "$(date): Starting service with default configuration" >> "$LOG_FILE"
systemctl start "$SERVICE_NAME" 2>> "$LOG_FILE"

# 等待服务启动
sleep 15

# 验证服务状态
if systemctl is-active "$SERVICE_NAME" >/dev/null 2>&1; then
    echo "$(date): Full recovery completed successfully" >> "$LOG_FILE"
    exit 0
else
    echo "$(date): Full recovery failed" >> "$LOG_FILE"
    exit 1
fi
EOF

    chmod +x /usr/local/bin/recovery-strategy-full-$service_name.sh
    
    echo "✅ Recovery strategies implemented for $service_name"
}

# 设置恢复监控
setup_recovery_monitoring() {
    local service_name=$1
    
    echo "Setting up recovery monitoring for $service_name"
    
    # 创建自动恢复监控脚本
    cat > /usr/local/bin/auto-recovery-monitor-$service_name.sh << 'EOF'
#!/bin/bash
SERVICE_NAME="$1"
MAX_RECOVERY_ATTEMPTS="${2:-3}"
COOLDOWN_PERIOD="${3:-300}"  # 5分钟冷却期

STATE_FILE="/var/run/$SERVICE_NAME-recovery-state"
LOG_FILE="/var/log/$SERVICE_NAME-auto-recovery.log"

# 初始化状态文件
if [ ! -f "$STATE_FILE" ]; then
    echo "0,0,$(date +%s)" > "$STATE_FILE"
fi

# 读取当前状态
read recovery_attempts last_recovery last_cooldown < "$STATE_FILE"

echo "$(date): Auto recovery check for $SERVICE_NAME" >> "$LOG_FILE"
echo "$(date): Current recovery attempts: $recovery_attempts" >> "$LOG_FILE"

# 检查服务健康状态
if /usr/local/bin/health-check-$SERVICE_NAME.sh "$SERVICE_NAME" "http://localhost:8080/health" 10; then
    # 服务健康，重置恢复尝试计数
    if [ $recovery_attempts -gt 0 ]; then
        echo "$(date): Service is healthy, resetting recovery attempts" >> "$LOG_FILE"
        echo "0,0,$last_cooldown" > "$STATE_FILE"
    fi
    exit 0
fi

echo "$(date): Service is unhealthy, checking recovery conditions" >> "$LOG_FILE"

# 检查是否可以恢复
RECOVERY_CONDITIONS=$(/usr/local/bin/check-recovery-conditions-$SERVICE_NAME.sh "$SERVICE_NAME")
if [ "$RECOVERY_CONDITIONS" != "RECOVERY_POSSIBLE" ]; then
    echo "$(date): Recovery conditions not met, skipping auto recovery" >> "$LOG_FILE"
    exit 1
fi

# 检查是否在冷却期内
current_time=$(date +%s)
if [ $((current_time - last_cooldown)) -lt $COOLDOWN_PERIOD ]; then
    echo "$(date): In cooldown period, skipping auto recovery" >> "$LOG_FILE"
    exit 1
fi

# 检查恢复尝试次数
if [ $recovery_attempts -ge $MAX_RECOVERY_ATTEMPTS ]; then
    echo "$(date): Maximum recovery attempts reached, manual intervention required" >> "$LOG_FILE"
    
    # 发送紧急告警
    echo "CRITICAL: Maximum recovery attempts reached for $SERVICE_NAME" | \
        mail -s "CRITICAL: Service Recovery Failed" admin@example.com
        
    exit 1
fi

# 执行自动恢复
new_recovery_attempts=$((recovery_attempts + 1))
echo "$(date): Attempting auto recovery (attempt $new_recovery_attempts)" >> "$LOG_FILE"

# 根据失败次数选择恢复策略
RECOVERY_SUCCESS=false
if [ $new_recovery_attempts -eq 1 ]; then
    # 第一次尝试：重启服务
    if /usr/local/bin/recovery-strategy-restart-$SERVICE_NAME.sh "$SERVICE_NAME"; then
        RECOVERY_SUCCESS=true
    fi
elif [ $new_recovery_attempts -eq 2 ]; then
    # 第二次尝试：重新加载配置
    if /usr/local/bin/recovery-strategy-reload-$SERVICE_NAME.sh "$SERVICE_NAME"; then
        RECOVERY_SUCCESS=true
    fi
else
    # 第三次尝试：完整恢复
    if /usr/local/bin/recovery-strategy-full-$SERVICE_NAME.sh "$SERVICE_NAME"; then
        RECOVERY_SUCCESS=true
    fi
fi

if [ "$RECOVERY_SUCCESS" = true ]; then
    echo "$(date): Auto recovery successful" >> "$LOG_FILE"
    # 重置恢复尝试计数，但更新最后恢复时间
    echo "0,$current_time,$current_time" > "$STATE_FILE"
    
    # 发送恢复成功通知
    echo "Service $SERVICE_NAME auto recovery successful at $(date)" | \
        mail -s "Service Recovery Success" admin@example.com
        
    exit 0
else
    echo "$(date): Auto recovery failed" >> "$LOG_FILE"
    # 更新恢复尝试计数和时间
    echo "$new_recovery_attempts,$current_time,$last_cooldown" > "$STATE_FILE"
    
    # 如果达到最大尝试次数，发送紧急告警
    if [ $new_recovery_attempts -ge $MAX_RECOVERY_ATTEMPTS ]; then
        echo "CRITICAL: Auto recovery failed after $MAX_RECOVERY_ATTEMPTS attempts for $SERVICE_NAME" | \
            mail -s "CRITICAL: Service Recovery Failed" admin@example.com
    fi
    
    exit 1
fi
EOF

    chmod +x /usr/local/bin/auto-recovery-monitor-$service_name.sh
    
    # 配置自动恢复定时器
    cat > /etc/systemd/system/$service_name-auto-recovery.service << EOF
[Unit]
Description=Auto recovery for $service_name
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/auto-recovery-monitor-$service_name.sh "$service_name" 3 300
EOF

    cat > /etc/systemd/system/$service_name-auto-recovery.timer << EOF
[Unit]
Description=Run auto recovery for $service_name every 60 seconds
Requires=$service_name-auto-recovery.service

[Timer]
OnBootSec=60
OnUnitActiveSec=60

[Install]
WantedBy=timers.target
EOF

    # 启用自动恢复定时器
    systemctl daemon-reload
    systemctl enable $service_name-auto-recovery.timer
    systemctl start $service_name-auto-recovery.timer
    
    echo "✅ Recovery monitoring set up for $service_name"
}

# 验证自动恢复
verify_auto_recovery() {
    local service_name=$1
    
    echo "Verifying auto recovery for $service_name"
    
    # 检查相关文件
    echo "Checking recovery scripts:"
    for script in check-recovery-conditions-$service_name.sh recovery-strategy-restart-$service_name.sh recovery-strategy-reload-$service_name.sh recovery-strategy-full-$service_name.sh auto-recovery-monitor-$service_name.sh; do
        if [ -f "/usr/local/bin/$script" ]; then
            echo "✅ $script exists"
        else
            echo "❌ $script not found"
        fi
    done
    
    # 检查systemd服务
    echo "Checking systemd services:"
    systemctl status $service_name-auto-recovery.timer 2>/dev/null || echo "Auto recovery timer not found"
    
    echo "✅ Auto recovery verification completed"
}

# 使用示例
# implement_auto_recovery "config-service"
```

## 最佳实践总结

通过以上内容，我们可以总结出高可用性环境中配置管理策略的最佳实践：

### 1. 架构设计原则
- 遵循冗余设计原则，消除单点故障
- 实施故障隔离机制，限制故障影响范围
- 设计优雅降级方案，确保核心功能可用

### 2. 高可用部署
- 采用集群化部署配置存储组件
- 实施负载均衡和故障转移机制
- 配置健康检查和自动恢复策略

### 3. 负载均衡策略
- 选择合适的负载均衡算法
- 实施智能故障检测机制
- 配置合理的冷却期和重试策略

### 4. 健康检查与恢复
- 建立多层次健康检查体系
- 实施自动化恢复机制
- 配置监控告警和日志记录

通过实施这些最佳实践，可以构建一个稳定可靠的高可用性配置管理体系，确保在各种故障场景下系统仍能持续提供服务。

在下一节中，我们将深入探讨配置管理的冗余与容错设计，帮助您掌握更加先进的高可用性配置管理技术。