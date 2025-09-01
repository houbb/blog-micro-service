---
title: 数据库高可用与容灾 (Database HA & DR)
date: 2025-08-31
categories: [容错与灾难恢复]
tags: [fault-recovery]
published: true
---

数据库作为信息系统的核心组件，其高可用性和容灾能力直接影响整个系统的可靠性和业务连续性。在现代分布式系统中，数据库故障可能导致严重的业务中断和数据丢失。因此，构建高可用、可容灾的数据库架构是确保业务连续性的关键。本章将深入探讨数据库高可用与容灾的核心技术、实现方案和最佳实践。

## 数据库高可用性概述

数据库高可用性是指数据库系统能够在预定的时间内持续提供服务的能力，即使在面对硬件故障、软件错误或网络问题时也能保持正常运行。

### 高可用性指标

#### 1. 可用性百分比
可用性通常用百分比表示，计算公式为：
```
可用性 = (总时间 - 停机时间) / 总时间 × 100%
```

常见的可用性等级：
- 99% (2个9)：每年停机时间约87.6小时
- 99.9% (3个9)：每年停机时间约8.76小时
- 99.99% (4个9)：每年停机时间约52.6分钟
- 99.999% (5个9)：每年停机时间约5.26分钟

#### 2. 恢复时间目标（RTO）
数据库从故障发生到恢复正常服务所需的时间。

#### 3. 恢复点目标（RPO）
数据库能够恢复到的最远时间点，即最大数据丢失量。

### 高可用性设计原则

#### 1. 冗余设计
通过多副本部署消除单点故障：
- 多实例部署
- 多节点集群
- 多地域分布

#### 2. 故障检测
建立完善的故障检测机制：
- 心跳检测
- 健康检查
- 自动故障发现

#### 3. 自动故障切换
实现故障的自动检测和切换：
- 主备切换
- 负载均衡
- 服务发现

## 主备切换技术

主备切换是数据库高可用性的核心技术，通过维护一个或多个备用数据库实例，在主数据库发生故障时自动切换到备用实例。

### 主从复制架构

#### 1. 异步复制
主数据库将数据变更异步发送给从数据库，不等待从数据库确认。

##### 优势
- 对主数据库性能影响小
- 网络延迟不影响主数据库写入性能
- 实现简单

##### 劣势
- 存在数据丢失风险
- 从数据库数据可能不是最新的
- 切换时可能丢失未同步的数据

##### MySQL异步复制示例
```sql
-- 主数据库配置
[mysqld]
server-id=1
log-bin=mysql-bin
binlog-format=ROW

-- 从数据库配置
[mysqld]
server-id=2
relay-log=relay-bin

-- 在从数据库上配置主从复制
CHANGE MASTER TO
MASTER_HOST='master-db.company.com',
MASTER_USER='repl_user',
MASTER_PASSWORD='repl_password',
MASTER_LOG_FILE='mysql-bin.000001',
MASTER_LOG_POS=107;

START SLAVE;
```

#### 2. 半同步复制
主数据库在提交事务前等待至少一个从数据库确认接收到数据变更。

##### 优势
- 减少数据丢失风险
- 相比同步复制性能影响较小
- 提供更好的数据一致性保证

##### 劣势
- 对主数据库性能有一定影响
- 网络延迟会影响写入性能
- 需要特殊配置支持

##### MySQL半同步复制配置
```sql
-- 在主数据库上安装半同步复制插件
INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';

-- 启用半同步复制
SET GLOBAL rpl_semi_sync_master_enabled = 1;
SET GLOBAL rpl_semi_sync_master_timeout = 1000; -- 1秒超时

-- 在从数据库上安装半同步复制插件
INSTALL PLUGIN rpl_semi_sync_slave SONAME 'semisync_slave.so';

-- 启用从数据库半同步
SET GLOBAL rpl_semi_sync_slave_enabled = 1;
```

#### 3. 同步复制
主数据库在提交事务前必须等待所有从数据库确认接收到数据变更。

##### 优势
- 最强的数据一致性保证
- 零数据丢失风险
- 严格的ACID特性保证

##### 劣势
- 对性能影响最大
- 网络延迟严重影响写入性能
- 任何一个节点故障都会影响整体可用性

### 自动故障检测与切换

#### 1. 心跳检测机制
```python
# 数据库心跳检测示例
import time
import threading
from datetime import datetime

class DatabaseHealthChecker:
    def __init__(self, master_db, slave_dbs, check_interval=10):
        self.master_db = master_db
        self.slave_dbs = slave_dbs
        self.check_interval = check_interval
        self.last_heartbeat = {}
        self.heartbeat_timeout = 30  # 30秒超时
        
    def start_health_check(self):
        def check_loop():
            while True:
                self.check_master_health()
                self.check_slave_health()
                time.sleep(self.check_interval)
                
        checker_thread = threading.Thread(target=check_loop)
        checker_thread.daemon = True
        checker_thread.start()
        
    def check_master_health(self):
        try:
            # 执行简单查询检测主数据库健康状态
            result = self.master_db.execute("SELECT 1")
            self.last_heartbeat["master"] = datetime.now()
            print("Master database is healthy")
        except Exception as e:
            print(f"Master database health check failed: {e}")
            self.handle_master_failure()
            
    def check_slave_health(self):
        for i, slave_db in enumerate(self.slave_dbs):
            try:
                result = slave_db.execute("SELECT 1")
                self.last_heartbeat[f"slave_{i}"] = datetime.now()
                print(f"Slave {i} database is healthy")
            except Exception as e:
                print(f"Slave {i} database health check failed: {e}")
                
    def handle_master_failure(self):
        # 检查是否真的故障（避免网络抖动误判）
        if self.is_master_really_down():
            print("Master database failure confirmed, initiating failover...")
            self.initiate_failover()
            
    def is_master_really_down(self):
        # 多次检测确认故障
        failure_count = 0
        for _ in range(3):
            try:
                self.master_db.execute("SELECT 1")
                return False  # 检测成功，未故障
            except:
                failure_count += 1
                time.sleep(1)
                
        return failure_count >= 3  # 连续3次失败确认故障
        
    def initiate_failover(self):
        # 选择最佳的从数据库作为新的主数据库
        best_slave = self.select_best_slave()
        if best_slave:
            self.promote_slave_to_master(best_slave)
            self.update_application_config(best_slave)
            self.send_failover_notification()
            
    def select_best_slave(self):
        # 选择数据最完整、延迟最小的从数据库
        best_slave = None
        min_lag = float('inf')
        
        for i, slave_db in enumerate(self.slave_dbs):
            try:
                lag = self.get_slave_lag(slave_db)
                if lag < min_lag:
                    min_lag = lag
                    best_slave = i
            except Exception as e:
                print(f"Error checking slave {i} lag: {e}")
                
        return best_slave
        
    def get_slave_lag(self, slave_db):
        # 获取从数据库的复制延迟
        result = slave_db.execute("SHOW SLAVE STATUS")
        return result[0]['Seconds_Behind_Master'] or 0
        
    def promote_slave_to_master(self, slave_index):
        # 将从数据库提升为主数据库
        slave_db = self.slave_dbs[slave_index]
        slave_db.execute("STOP SLAVE")
        slave_db.execute("RESET SLAVE ALL")
        print(f"Slave {slave_index} promoted to master")
        
    def update_application_config(self, new_master_index):
        # 更新应用程序配置指向新的主数据库
        new_master_config = {
            "host": f"slave{new_master_index}.company.com",
            "port": 3306
        }
        self.update_config_service(new_master_config)
        
    def send_failover_notification(self):
        # 发送故障切换通知
        notification = {
            "event": "database_failover",
            "timestamp": datetime.now().isoformat(),
            "old_master": self.master_db.host,
            "new_master": f"slave{self.select_best_slave()}.company.com"
        }
        self.send_notification(notification)
```

#### 2. 负载均衡与故障转移
```python
# 数据库负载均衡与故障转移示例
import random
from datetime import datetime

class DatabaseLoadBalancer:
    def __init__(self, db_instances):
        self.db_instances = db_instances
        self.healthy_instances = db_instances.copy()
        self.unhealthy_instances = []
        self.current_master = None
        self.initialize_master()
        
    def initialize_master(self):
        # 初始化时选择一个健康的实例作为主数据库
        for instance in self.healthy_instances:
            if self.is_instance_healthy(instance):
                self.current_master = instance
                break
                
    def get_connection(self, operation_type="read"):
        if operation_type == "write":
            # 写操作只能连接到主数据库
            if self.is_instance_healthy(self.current_master):
                return self.current_master
            else:
                # 主数据库不健康，触发故障切换
                self.failover()
                return self.current_master
        else:
            # 读操作可以连接到任何健康的实例
            healthy_reads = [inst for inst in self.healthy_instances 
                           if self.is_instance_healthy(inst)]
            if healthy_reads:
                return random.choice(healthy_reads)
            else:
                # 没有健康的读实例，降级到主数据库
                return self.current_master
                
    def is_instance_healthy(self, instance):
        try:
            # 执行健康检查查询
            result = instance.execute("SELECT 1")
            return True
        except Exception:
            return False
            
    def failover(self):
        print("Initiating database failover...")
        
        # 从健康实例中选择新的主数据库
        candidates = [inst for inst in self.healthy_instances 
                     if inst != self.current_master and self.is_instance_healthy(inst)]
                     
        if candidates:
            new_master = random.choice(candidates)
            self.promote_to_master(new_master)
            self.current_master = new_master
            print(f"Failover completed. New master: {new_master.host}")
        else:
            print("No healthy candidates for failover")
            
    def promote_to_master(self, instance):
        # 将实例提升为主数据库
        try:
            instance.execute("STOP SLAVE")
            instance.execute("RESET SLAVE ALL")
            instance.set_read_only(False)
            print(f"Instance {instance.host} promoted to master")
        except Exception as e:
            print(f"Error promoting instance to master: {e}")
            
    def add_instance(self, instance):
        # 添加新的数据库实例
        self.db_instances.append(instance)
        if self.is_instance_healthy(instance):
            self.healthy_instances.append(instance)
        else:
            self.unhealthy_instances.append(instance)
            
    def remove_instance(self, instance):
        # 移除数据库实例
        if instance in self.db_instances:
            self.db_instances.remove(instance)
        if instance in self.healthy_instances:
            self.healthy_instances.remove(instance)
        if instance in self.unhealthy_instances:
            self.unhealthy_instances.remove(instance)
        if instance == self.current_master:
            self.failover()
```

## 分片与多副本技术

分片和多副本是构建大规模、高可用数据库系统的重要技术。

### 数据库分片（Sharding）

#### 1. 水平分片
将数据按行进行分割，不同的数据行存储在不同的数据库实例中。

##### 分片策略
```python
# 数据库分片策略示例
class ShardingStrategy:
    def __init__(self, shard_count):
        self.shard_count = shard_count
        
    def get_shard_key(self, data):
        # 根据业务逻辑确定分片键
        if 'user_id' in data:
            return data['user_id']
        elif 'order_id' in data:
            return data['order_id']
        else:
            raise ValueError("No suitable shard key found")
            
    def get_shard_index(self, shard_key):
        # 使用哈希算法确定分片索引
        return hash(str(shard_key)) % self.shard_count
        
    def route_to_shard(self, data):
        shard_key = self.get_shard_key(data)
        shard_index = self.get_shard_index(shard_key)
        return shard_index
        
# 分片路由示例
class ShardedDatabaseRouter:
    def __init__(self, shard_configs):
        self.shards = []
        for config in shard_configs:
            self.shards.append(self.create_database_connection(config))
        self.sharding_strategy = ShardingStrategy(len(shard_configs))
        
    def create_database_connection(self, config):
        # 创建数据库连接
        return DatabaseConnection(
            host=config['host'],
            port=config['port'],
            database=config['database']
        )
        
    def insert_data(self, table, data):
        shard_index = self.sharding_strategy.route_to_shard(data)
        shard_db = self.shards[shard_index]
        return shard_db.insert(table, data)
        
    def query_data(self, table, conditions):
        # 如果查询条件包含分片键，直接路由到对应分片
        if self.sharding_strategy.get_shard_key(conditions) is not None:
            shard_index = self.sharding_strategy.route_to_shard(conditions)
            shard_db = self.shards[shard_index]
            return shard_db.query(table, conditions)
        else:
            # 否则需要查询所有分片并合并结果
            results = []
            for shard_db in self.shards:
                shard_results = shard_db.query(table, conditions)
                results.extend(shard_results)
            return results
            
    def update_data(self, table, conditions, updates):
        shard_index = self.sharding_strategy.route_to_shard(conditions)
        shard_db = self.shards[shard_index]
        return shard_db.update(table, conditions, updates)
        
    def delete_data(self, table, conditions):
        shard_index = self.sharding_strategy.route_to_shard(conditions)
        shard_db = self.shards[shard_index]
        return shard_db.delete(table, conditions)
```

#### 2. 垂直分片
将数据按列进行分割，不同的表或字段存储在不同的数据库实例中。

##### 垂直分片示例
```python
# 垂直分片策略示例
class VerticalSharding:
    def __init__(self):
        self.user_db = self.connect_to_user_database()
        self.order_db = self.connect_to_order_database()
        self.product_db = self.connect_to_product_database()
        
    def connect_to_user_database(self):
        return DatabaseConnection(
            host="user-db.company.com",
            database="user_service"
        )
        
    def connect_to_order_database(self):
        return DatabaseConnection(
            host="order-db.company.com",
            database="order_service"
        )
        
    def connect_to_product_database(self):
        return DatabaseConnection(
            host="product-db.company.com",
            database="product_service"
        )
        
    def create_user(self, user_data):
        # 用户相关数据存储在用户数据库
        return self.user_db.insert("users", user_data)
        
    def create_order(self, order_data):
        # 订单相关数据存储在订单数据库
        return self.order_db.insert("orders", order_data)
        
    def add_product(self, product_data):
        # 产品相关数据存储在产品数据库
        return self.product_db.insert("products", product_data)
        
    def get_user_orders(self, user_id):
        # 获取用户信息（从用户数据库）
        user = self.user_db.query("users", {"id": user_id})
        
        # 获取用户订单（从订单数据库）
        orders = self.order_db.query("orders", {"user_id": user_id})
        
        # 合并结果
        return {
            "user": user,
            "orders": orders
        }
```

### 多副本技术

#### 1. 主从多副本
一个主数据库和多个从数据库的架构。

```python
# 主从多副本管理示例
class MasterSlaveReplication:
    def __init__(self, master_config, slave_configs):
        self.master = self.create_database_connection(master_config)
        self.slaves = [self.create_database_connection(config) for config in slave_configs]
        self.health_checker = DatabaseHealthChecker(self.master, self.slaves)
        self.health_checker.start_health_check()
        
    def create_database_connection(self, config):
        return DatabaseConnection(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        
    def write_operation(self, query, params=None):
        # 写操作只在主数据库执行
        try:
            result = self.master.execute(query, params)
            return result
        except Exception as e:
            print(f"Write operation failed on master: {e}")
            # 触发故障切换
            self.health_checker.handle_master_failure()
            raise
            
    def read_operation(self, query, params=None):
        # 读操作可以在从数据库执行
        healthy_slaves = [slave for slave in self.slaves 
                         if self.health_checker.is_instance_healthy(slave)]
                         
        if healthy_slaves:
            # 随机选择一个健康的从数据库
            slave = random.choice(healthy_slaves)
            try:
                return slave.execute(query, params)
            except Exception as e:
                print(f"Read operation failed on slave {slave.host}: {e}")
                # 从失败列表中移除，降级到主数据库
                return self.master.execute(query, params)
        else:
            # 没有健康的从数据库，使用主数据库
            return self.master.execute(query, params)
            
    def get_replication_status(self):
        # 获取复制状态信息
        status = {
            "master": {
                "host": self.master.host,
                "status": "healthy" if self.health_checker.is_instance_healthy(self.master) else "unhealthy"
            },
            "slaves": []
        }
        
        for i, slave in enumerate(self.slaves):
            slave_status = {
                "host": slave.host,
                "status": "healthy" if self.health_checker.is_instance_healthy(slave) else "unhealthy",
                "lag": self.health_checker.get_slave_lag(slave) if self.health_checker.is_instance_healthy(slave) else None
            }
            status["slaves"].append(slave_status)
            
        return status
```

#### 2. 多主复制
多个数据库实例都可以作为主数据库接收写操作。

```python
# 多主复制示例
class MultiMasterReplication:
    def __init__(self, master_configs):
        self.masters = [self.create_database_connection(config) for config in master_configs]
        self.conflict_resolver = ConflictResolver()
        self.health_checker = MultiMasterHealthChecker(self.masters)
        self.health_checker.start_health_check()
        
    def create_database_connection(self, config):
        return DatabaseConnection(
            host=config['host'],
            port=config['port'],
            database=config['database']
        )
        
    def write_operation(self, table, data):
        # 在所有健康的主数据库上执行写操作
        results = []
        errors = []
        
        healthy_masters = [master for master in self.masters 
                          if self.health_checker.is_instance_healthy(master)]
                          
        for master in healthy_masters:
            try:
                result = master.insert(table, data)
                results.append({"master": master.host, "result": result})
            except Exception as e:
                errors.append({"master": master.host, "error": str(e)})
                
        if not results and errors:
            raise Exception(f"All write operations failed: {errors}")
            
        return results
        
    def read_operation(self, table, conditions):
        # 从任意一个健康的主数据库读取数据
        healthy_masters = [master for master in self.masters 
                          if self.health_checker.is_instance_healthy(master)]
                          
        if healthy_masters:
            master = random.choice(healthy_masters)
            return master.query(table, conditions)
        else:
            raise Exception("No healthy masters available for read operation")
            
    def resolve_conflicts(self, conflicts):
        # 解决多主复制中的数据冲突
        return self.conflict_resolver.resolve(conflicts)
```

## 数据库集群技术

数据库集群通过将多个数据库实例组织成集群，提供更高的可用性和扩展性。

### MySQL集群示例

```python
# MySQL InnoDB Cluster示例
import mysqlsh

class MySQLClusterManager:
    def __init__(self, cluster_name, admin_user, admin_password):
        self.cluster_name = cluster_name
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.session = None
        
    def connect_to_cluster(self, host, port=3306):
        # 连接到MySQL Shell
        self.session = mysqlsh.mysql.get_session(
            f"{self.admin_user}:{self.admin_password}@{host}:{port}"
        )
        
    def create_cluster(self, instance_configs):
        # 创建InnoDB Cluster
        cluster = self.session.create_cluster(self.cluster_name)
        
        # 添加实例到集群
        for config in instance_configs[1:]:  # 第一个实例已经是主实例
            cluster.add_instance(
                f"{config['user']}:{config['password']}@{config['host']}:{config['port']}"
            )
            
        return cluster
        
    def get_cluster_status(self):
        # 获取集群状态
        if self.session:
            return self.session.get_cluster(self.cluster_name).status()
        return None
        
    def add_instance_to_cluster(self, instance_config):
        # 向集群添加新实例
        cluster = self.session.get_cluster(self.cluster_name)
        cluster.add_instance(
            f"{instance_config['user']}:{instance_config['password']}@{instance_config['host']}:{instance_config['port']}"
        )
        
    def remove_instance_from_cluster(self, instance_address):
        # 从集群移除实例
        cluster = self.session.get_cluster(self.cluster_name)
        cluster.remove_instance(instance_address)
        
    def rejoin_instance(self, instance_config):
        # 重新加入集群
        cluster = self.session.get_cluster(self.cluster_name)
        cluster.rejoin_instance(
            f"{instance_config['user']}:{instance_config['password']}@{instance_config['host']}:{instance_config['port']}"
        )
```

### PostgreSQL集群示例

```python
# PostgreSQL集群管理示例
class PostgreSQLClusterManager:
    def __init__(self, cluster_name):
        self.cluster_name = cluster_name
        self.primary_node = None
        self.standby_nodes = []
        self.witness_node = None
        
    def setup_primary_node(self, config):
        # 配置主节点
        self.primary_node = PostgreSQLNode(config)
        self.primary_node.configure_as_primary()
        
    def add_standby_node(self, config):
        # 添加备用节点
        standby_node = PostgreSQLNode(config)
        standby_node.configure_as_standby(self.primary_node)
        self.standby_nodes.append(standby_node)
        
    def setup_witness_node(self, config):
        # 配置见证节点（用于仲裁）
        self.witness_node = PostgreSQLNode(config)
        self.witness_node.configure_as_witness()
        
    def failover(self):
        # 执行故障切换
        if not self.primary_node.is_healthy():
            # 选择最佳的备用节点作为新主节点
            best_standby = self.select_best_standby()
            if best_standby:
                self.promote_standby(best_standby)
                self.reconfigure_standbys(best_standby)
                
    def select_best_standby(self):
        # 选择数据最完整、延迟最小的备用节点
        best_node = None
        min_lag = float('inf')
        
        for node in self.standby_nodes:
            if node.is_healthy():
                lag = node.get_replication_lag()
                if lag < min_lag:
                    min_lag = lag
                    best_node = node
                    
        return best_node
        
    def promote_standby(self, standby_node):
        # 将备用节点提升为主节点
        standby_node.promote_to_primary()
        
    def reconfigure_standbys(self, new_primary):
        # 重新配置其他备用节点指向新的主节点
        for node in self.standby_nodes:
            if node != new_primary:
                node.reconfigure_replication(new_primary)
```

## 云数据库高可用方案

现代云平台提供了多种数据库高可用解决方案。

### AWS RDS高可用

```python
# AWS RDS高可用配置示例
import boto3

class AWSRDSHighAvailability:
    def __init__(self, region='us-east-1'):
        self.rds_client = boto3.client('rds', region_name=region)
        
    def create_multi_az_instance(self, db_instance_identifier, db_config):
        # 创建多可用区RDS实例
        response = self.rds_client.create_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            AllocatedStorage=db_config['allocated_storage'],
            DBInstanceClass=db_config['instance_class'],
            Engine=db_config['engine'],
            MasterUsername=db_config['master_username'],
            MasterUserPassword=db_config['master_password'],
            MultiAZ=True,  # 启用多可用区
            StorageEncrypted=True,
            BackupRetentionPeriod=7,
            PreferredBackupWindow='03:00-04:00',
            PreferredMaintenanceWindow='sun:04:00-sun:05:00'
        )
        
        return response
        
    def create_read_replica(self, source_db_instance_identifier, replica_identifier):
        # 创建只读副本
        response = self.rds_client.create_db_instance_read_replica(
            DBInstanceIdentifier=replica_identifier,
            SourceDBInstanceIdentifier=source_db_instance_identifier,
            DBInstanceClass='db.t3.medium',
            PubliclyAccessible=False
        )
        
        return response
        
    def failover_db_instance(self, db_instance_identifier):
        # 执行故障切换
        response = self.rds_client.reboot_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            ForceFailover=True
        )
        
        return response
        
    def get_db_instance_status(self, db_instance_identifier):
        # 获取数据库实例状态
        response = self.rds_client.describe_db_instances(
            DBInstanceIdentifier=db_instance_identifier
        )
        
        return response['DBInstances'][0]
```

### 阿里云RDS高可用

```python
# 阿里云RDS高可用配置示例
from aliyunsdkrds.request.v20140815 import CreateDBInstanceRequest
from aliyunsdkcore.client import AcsClient

class AliyunRDSHighAvailability:
    def __init__(self, access_key_id, access_key_secret, region_id):
        self.client = AcsClient(access_key_id, access_key_secret, region_id)
        
    def create_high_availability_instance(self, instance_config):
        # 创建高可用RDS实例
        request = CreateDBInstanceRequest.CreateDBInstanceRequest()
        request.set_DBInstanceClass(instance_config['instance_class'])
        request.set_DBInstanceStorage(instance_config['storage'])
        request.set_Engine(instance_config['engine'])
        request.set_EngineVersion(instance_config['engine_version'])
        request.set_DBInstanceDescription(instance_config['description'])
        request.set_SecurityIPList(instance_config['security_ip_list'])
        request.set_PayType('Postpaid')
        request.set_ZoneId(instance_config['zone_id'])
        request.set_InstanceNetworkType('VPC')
        request.set_VPCId(instance_config['vpc_id'])
        request.set_VSwitchId(instance_config['vswitch_id'])
        
        # 启用高可用特性
        request.set_HighAvailabilityMode('MultiAvailabilityZones')
        
        response = self.client.do_action_with_exception(request)
        return response
        
    def create_read_only_instance(self, source_instance_id, instance_config):
        # 创建只读实例
        from aliyunsdkrds.request.v20140815 import CreateReadOnlyDBInstanceRequest
        
        request = CreateReadOnlyDBInstanceRequest.CreateReadOnlyDBInstanceRequest()
        request.set_ReadOnlyDBInstanceClass(instance_config['instance_class'])
        request.set_DBInstanceId(source_instance_id)
        request.set_ReadOnlyDBInstanceStorage(instance_config['storage'])
        request.set_RegionId(instance_config['region_id'])
        
        response = self.client.do_action_with_exception(request)
        return response
```

## 监控与告警

完善的监控和告警机制是确保数据库高可用性的关键。

### 数据库监控示例

```python
# 数据库监控示例
import psutil
import time
from datetime import datetime

class DatabaseMonitor:
    def __init__(self, database_connections):
        self.db_connections = database_connections
        self.metrics = {}
        self.alert_rules = self.setup_alert_rules()
        
    def setup_alert_rules(self):
        return {
            "high_cpu_usage": 80,  # CPU使用率超过80%告警
            "high_memory_usage": 85,  # 内存使用率超过85%告警
            "slow_query_threshold": 5,  # 慢查询阈值5秒
            "connection_count_threshold": 1000,  # 连接数阈值
            "replication_lag_threshold": 30  # 复制延迟阈值30秒
        }
        
    def collect_metrics(self):
        metrics = {}
        
        for db_name, db_conn in self.db_connections.items():
            db_metrics = {}
            
            # 收集系统指标
            db_metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
            db_metrics['memory_usage'] = psutil.virtual_memory().percent
            
            # 收集数据库指标
            try:
                # 连接数
                conn_result = db_conn.execute("SHOW STATUS LIKE 'Threads_connected'")
                db_metrics['current_connections'] = int(conn_result[0][1])
                
                # 慢查询数
                slow_result = db_conn.execute("SHOW STATUS LIKE 'Slow_queries'")
                db_metrics['slow_queries'] = int(slow_result[0][1])
                
                # 查询响应时间
                db_metrics['avg_query_time'] = self.measure_query_performance(db_conn)
                
                # 复制延迟（如果是从数据库）
                if self.is_slave_database(db_conn):
                    lag_result = db_conn.execute("SHOW SLAVE STATUS")
                    if lag_result:
                        db_metrics['replication_lag'] = lag_result[0]['Seconds_Behind_Master'] or 0
                        
            except Exception as e:
                print(f"Error collecting metrics for {db_name}: {e}")
                db_metrics['error'] = str(e)
                
            metrics[db_name] = db_metrics
            
        self.metrics = metrics
        return metrics
        
    def measure_query_performance(self, db_conn):
        # 测量查询性能
        start_time = time.time()
        try:
            db_conn.execute("SELECT 1")
            end_time = time.time()
            return end_time - start_time
        except:
            return -1  # 查询失败
            
    def is_slave_database(self, db_conn):
        # 判断是否为从数据库
        try:
            result = db_conn.execute("SHOW SLAVE STATUS")
            return len(result) > 0
        except:
            return False
            
    def check_alerts(self):
        alerts = []
        
        for db_name, metrics in self.metrics.items():
            # 检查CPU使用率
            if metrics.get('cpu_usage', 0) > self.alert_rules['high_cpu_usage']:
                alerts.append({
                    'database': db_name,
                    'type': 'high_cpu_usage',
                    'value': metrics['cpu_usage'],
                    'threshold': self.alert_rules['high_cpu_usage'],
                    'timestamp': datetime.now()
                })
                
            # 检查内存使用率
            if metrics.get('memory_usage', 0) > self.alert_rules['high_memory_usage']:
                alerts.append({
                    'database': db_name,
                    'type': 'high_memory_usage',
                    'value': metrics['memory_usage'],
                    'threshold': self.alert_rules['high_memory_usage'],
                    'timestamp': datetime.now()
                })
                
            # 检查连接数
            if metrics.get('current_connections', 0) > self.alert_rules['connection_count_threshold']:
                alerts.append({
                    'database': db_name,
                    'type': 'high_connection_count',
                    'value': metrics['current_connections'],
                    'threshold': self.alert_rules['connection_count_threshold'],
                    'timestamp': datetime.now()
                })
                
            # 检查复制延迟
            if metrics.get('replication_lag', 0) > self.alert_rules['replication_lag_threshold']:
                alerts.append({
                    'database': db_name,
                    'type': 'high_replication_lag',
                    'value': metrics['replication_lag'],
                    'threshold': self.alert_rules['replication_lag_threshold'],
                    'timestamp': datetime.now()
                })
                
        if alerts:
            self.send_alerts(alerts)
            
        return alerts
        
    def send_alerts(self, alerts):
        # 发送告警通知
        for alert in alerts:
            print(f"ALERT: {alert['type']} on {alert['database']} - "
                  f"Current: {alert['value']}, Threshold: {alert['threshold']}")
            # 可以集成邮件、短信、Slack等通知方式
```

## 最佳实践

### 1. 定期备份与恢复演练
```python
# 备份与恢复演练示例
class BackupRestoreDrill:
    def __init__(self, backup_system):
        self.backup_system = backup_system
        self.drill_results = []
        
    def perform_drill(self, drill_config):
        drill_result = {
            "drill_id": self.generate_drill_id(),
            "start_time": datetime.now(),
            "steps": []
        }
        
        try:
            # 步骤1：验证备份完整性
            step1_result = self.verify_backup_integrity(drill_config['backup_set'])
            drill_result["steps"].append({
                "step": 1,
                "description": "Verify backup integrity",
                "result": step1_result,
                "timestamp": datetime.now()
            })
            
            # 步骤2：准备恢复环境
            step2_result = self.prepare_restore_environment(drill_config['target_env'])
            drill_result["steps"].append({
                "step": 2,
                "description": "Prepare restore environment",
                "result": step2_result,
                "timestamp": datetime.now()
            })
            
            # 步骤3：执行恢复
            step3_result = self.execute_restore(drill_config['backup_set'], drill_config['target_env'])
            drill_result["steps"].append({
                "step": 3,
                "description": "Execute restore",
                "result": step3_result,
                "timestamp": datetime.now()
            })
            
            # 步骤4：验证恢复结果
            step4_result = self.verify_restore_result(drill_config['target_env'])
            drill_result["steps"].append({
                "step": 4,
                "description": "Verify restore result",
                "result": step4_result,
                "timestamp": datetime.now()
            })
            
            drill_result["status"] = "completed"
            drill_result["end_time"] = datetime.now()
            
        except Exception as e:
            drill_result["status"] = "failed"
            drill_result["error"] = str(e)
            drill_result["end_time"] = datetime.now()
            
        self.drill_results.append(drill_result)
        return drill_result
        
    def generate_drill_id(self):
        return f"drill_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def verify_backup_integrity(self, backup_set):
        # 验证备份完整性
        return self.backup_system.verify_integrity(backup_set)
        
    def prepare_restore_environment(self, target_env):
        # 准备恢复环境
        # 清理目标环境
        # 准备必要的资源
        return {"status": "success"}
        
    def execute_restore(self, backup_set, target_env):
        # 执行恢复操作
        return self.backup_system.restore(backup_set, target_env)
        
    def verify_restore_result(self, target_env):
        # 验证恢复结果
        # 检查数据完整性
        # 运行功能测试
        return {"status": "success", "data_integrity": "verified"}
```

### 2. 性能优化
```python
# 数据库性能优化示例
class DatabasePerformanceOptimizer:
    def __init__(self, database_connection):
        self.db_conn = database_connection
        
    def analyze_slow_queries(self):
        # 分析慢查询
        slow_queries = self.db_conn.execute("""
            SELECT 
                sql_text,
                execution_time,
                rows_examined,
                rows_sent
            FROM performance_schema.events_statements_history_long
            WHERE execution_time > 1000000  -- 超过1秒的查询
            ORDER BY execution_time DESC
            LIMIT 10
        """)
        
        return slow_queries
        
    def optimize_table_indexes(self, table_name):
        # 优化表索引
        # 分析查询模式
        # 建议添加或删除索引
        index_analysis = self.db_conn.execute(f"""
            ANALYZE TABLE {table_name}
        """)
        
        return index_analysis
        
    def tune_database_parameters(self):
        # 调优数据库参数
        current_params = self.db_conn.execute("SHOW VARIABLES")
        
        # 根据系统资源和负载情况调整参数
        recommended_params = self.calculate_optimal_parameters()
        
        for param, value in recommended_params.items():
            self.db_conn.execute(f"SET GLOBAL {param} = {value}")
            
        return recommended_params
        
    def calculate_optimal_parameters(self):
        # 根据系统资源计算最优参数
        total_memory = psutil.virtual_memory().total
        cpu_count = psutil.cpu_count()
        
        return {
            "innodb_buffer_pool_size": int(total_memory * 0.7),  # 70%内存用于InnoDB缓冲池
            "max_connections": min(1000, cpu_count * 100),  # 最大连接数
            "query_cache_size": 128 * 1024 * 1024,  # 128MB查询缓存
            "tmp_table_size": 64 * 1024 * 1024,  # 64MB临时表大小
            "max_heap_table_size": 64 * 1024 * 1024  # 64MB内存表大小
        }
```

## 总结

数据库高可用与容灾是构建可靠信息系统的关键技术。通过主备切换、分片与多副本、数据库集群等技术，我们可以显著提高数据库系统的可用性和容灾能力。

在实际应用中，需要根据业务需求、技术能力和成本预算选择合适的高可用方案，并建立完善的监控、告警和演练机制，确保数据库系统能够在各种故障场景下保持稳定运行。

下一章我们将探讨应用与中间件层的灾备设计，了解如何构建具备容灾能力的应用架构。