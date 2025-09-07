---
title: 自动化与智能优化：构建自适应的数据存储性能管理体系
date: 2025-08-31
categories: [DataManagementStorage]
tags: [data-management-storage]
published: true
---

在现代数据存储系统中，随着系统规模的不断扩大和复杂性的持续增加，传统的手动性能调优方式已难以满足高效运维的需求。自动化与智能优化技术通过引入机器学习、人工智能等先进技术，能够实现存储系统的自适应性能管理，显著提升运维效率并降低人为错误风险。本文将深入探讨数据存储系统中自动化与智能优化的核心概念、关键技术实现以及最佳实践方法，帮助读者构建更加智能、高效的存储性能管理体系。

## 自动化性能管理

### 自动化监控与告警

自动化监控与告警是构建智能存储系统的基础，通过自动化的数据收集、分析和预警机制，能够实现对系统状态的实时掌控。

#### 智能监控系统实现
```python
# 智能监控系统示例
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

class IntelligentMonitoringSystem:
    """智能监控系统"""
    
    def __init__(self):
        self.metrics_store = defaultdict(deque)  # 使用deque限制数据量
        self.alert_rules = {}
        self.baseline_metrics = {}
        self.anomaly_detectors = {}
        self.alert_history = deque(maxlen=1000)  # 限制告警历史数量
    
    def add_metric(self, metric_name, value, labels=None, timestamp=None):
        """添加监控指标"""
        if timestamp is None:
            timestamp = datetime.now()
        
        metric_key = self._generate_metric_key(metric_name, labels)
        
        # 存储指标数据（限制每个指标最多存储1000个数据点）
        self.metrics_store[metric_key].append({
            'value': value,
            'timestamp': timestamp
        })
        
        # 保持最多1000个数据点
        if len(self.metrics_store[metric_key]) > 1000:
            self.metrics_store[metric_key].popleft()
        
        # 实时异常检测
        self._detect_anomalies(metric_key, value, timestamp)
    
    def _generate_metric_key(self, metric_name, labels):
        """生成指标键"""
        if labels:
            label_str = ','.join([f"{k}={v}" for k, v in sorted(labels.items())])
            return f"{metric_name}{{{label_str}}}"
        return metric_name
    
    def set_alert_rule(self, metric_name, threshold, operator, duration_minutes=5, severity='warning'):
        """设置告警规则"""
        rule_key = f"{metric_name}_{operator}_{threshold}"
        self.alert_rules[rule_key] = {
            'metric_name': metric_name,
            'threshold': threshold,
            'operator': operator,
            'duration_minutes': duration_minutes,
            'severity': severity,
            'enabled': True
        }
        print(f"已设置告警规则: {rule_key}")
    
    def _detect_anomalies(self, metric_key, value, timestamp):
        """检测异常"""
        # 基于统计的异常检测
        if len(self.metrics_store[metric_key]) > 10:
            recent_values = [point['value'] for point in list(self.metrics_store[metric_key])[-10:]]
            mean_val = statistics.mean(recent_values)
            stdev_val = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
            
            # 3σ原则检测异常
            if stdev_val > 0:
                z_score = abs(value - mean_val) / stdev_val
                if z_score > 3:
                    self._trigger_alert(metric_key, value, 'statistical_anomaly', 
                                      f"统计异常: 值 {value} 超出3σ范围", 'warning', timestamp)
    
    def _trigger_alert(self, metric_key, value, alert_type, message, severity, timestamp=None):
        """触发告警"""
        if timestamp is None:
            timestamp = datetime.now()
        
        alert = {
            'metric_key': metric_key,
            'value': value,
            'alert_type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': timestamp,
            'alert_id': f"alert_{int(timestamp.timestamp())}_{hash(metric_key) % 10000}"
        }
        
        self.alert_history.append(alert)
        print(f"[{severity.upper()}] {metric_key}: {message} (值: {value})")
        
        # 可以在这里集成告警通知系统
        # self._send_notification(alert)
    
    def check_threshold_alerts(self):
        """检查阈值告警"""
        current_time = datetime.now()
        
        for rule_key, rule in self.alert_rules.items():
            if not rule['enabled']:
                continue
            
            metric_name = rule['metric_name']
            threshold = rule['threshold']
            operator = rule['operator']
            duration = timedelta(minutes=rule['duration_minutes'])
            
            # 获取最近的指标数据
            if metric_name in self.metrics_store:
                recent_points = [
                    point for point in self.metrics_store[metric_name]
                    if current_time - point['timestamp'] <= duration
                ]
                
                if recent_points:
                    # 检查是否满足告警条件
                    condition_met = False
                    latest_value = recent_points[-1]['value']
                    
                    if operator == '>':
                        condition_met = latest_value > threshold
                    elif operator == '<':
                        condition_met = latest_value < threshold
                    elif operator == '>=':
                        condition_met = latest_value >= threshold
                    elif operator == '<=':
                        condition_met = latest_value <= threshold
                    elif operator == '==':
                        condition_met = latest_value == threshold
                    
                    if condition_met:
                        self._trigger_alert(
                            metric_name, latest_value, 'threshold_breach',
                            f"阈值告警: 值 {latest_value} {operator} {threshold}",
                            rule['severity'], current_time
                        )
    
    def get_metrics_summary(self, metric_name, time_range_hours=1):
        """获取指标摘要"""
        current_time = datetime.now()
        time_range = timedelta(hours=time_range_hours)
        
        if metric_name not in self.metrics_store:
            return None
        
        recent_points = [
            point for point in self.metrics_store[metric_name]
            if current_time - point['timestamp'] <= time_range
        ]
        
        if not recent_points:
            return None
        
        values = [point['value'] for point in recent_points]
        timestamps = [point['timestamp'] for point in recent_points]
        
        return {
            'metric_name': metric_name,
            'count': len(values),
            'min_value': min(values),
            'max_value': max(values),
            'avg_value': statistics.mean(values),
            'median_value': statistics.median(values),
            'time_range': time_range_hours,
            'latest_timestamp': max(timestamps)
        }
    
    def get_alert_summary(self, time_range_hours=24):
        """获取告警摘要"""
        current_time = datetime.now()
        time_range = timedelta(hours=time_range_hours)
        
        recent_alerts = [
            alert for alert in self.alert_history
            if current_time - alert['timestamp'] <= time_range
        ]
        
        severity_counts = defaultdict(int)
        for alert in recent_alerts:
            severity_counts[alert['severity']] += 1
        
        return {
            'total_alerts': len(recent_alerts),
            'severity_distribution': dict(severity_counts),
            'time_range_hours': time_range_hours,
            'most_recent_alerts': list(recent_alerts)[-10:]  # 最近10个告警
        }

# 使用示例
monitoring_system = IntelligentMonitoringSystem()

# 设置告警规则
monitoring_system.set_alert_rule('cpu_usage', 80, '>', 5, 'warning')
monitoring_system.set_alert_rule('memory_usage', 90, '>', 5, 'critical')
monitoring_system.set_alert_rule('disk_io_latency', 100, '>', 10, 'warning')

# 模拟添加指标数据
import random
for i in range(100):
    # 模拟CPU使用率数据
    cpu_usage = random.normalvariate(50, 15)  # 平均50%，标准差15%
    monitoring_system.add_metric('cpu_usage', min(100, max(0, cpu_usage)))
    
    # 模拟内存使用率数据
    memory_usage = random.normalvariate(60, 20)  # 平均60%，标准差20%
    monitoring_system.add_metric('memory_usage', min(100, max(0, memory_usage)))
    
    # 模拟磁盘IO延迟数据
    disk_latency = random.lognormvariate(4, 1)  # 对数正态分布
    monitoring_system.add_metric('disk_io_latency', disk_latency)
    
    # 检查阈值告警
    if i % 10 == 0:
        monitoring_system.check_threshold_alerts()
    
    time.sleep(0.1)  # 模拟时间间隔

# 获取指标摘要
cpu_summary = monitoring_system.get_metrics_summary('cpu_usage')
if cpu_summary:
    print("CPU使用率摘要:")
    print(f"  数据点数: {cpu_summary['count']}")
    print(f"  最小值: {cpu_summary['min_value']:.2f}%")
    print(f"  最大值: {cpu_summary['max_value']:.2f}%")
    print(f"  平均值: {cpu_summary['avg_value']:.2f}%")
    print(f"  中位数: {cpu_summary['median_value']:.2f}%")

# 获取告警摘要
alert_summary = monitoring_system.get_alert_summary(1)  # 最近1小时
print(f"\n告警摘要 (最近1小时):")
print(f"  总告警数: {alert_summary['total_alerts']}")
print(f"  严重程度分布: {alert_summary['severity_distribution']}")
```

### 自动化故障恢复

自动化故障恢复机制能够在系统出现异常时自动执行预定义的恢复操作，最大程度减少业务中断时间。

#### 故障自愈系统实现
```python
# 故障自愈系统示例
import time
import threading
from datetime import datetime, timedelta
from enum import Enum

class ComponentStatus(Enum):
    """组件状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"

class AutomatedRecoverySystem:
    """自动化故障恢复系统"""
    
    def __init__(self):
        self.components = {}
        self.recovery_policies = {}
        self.recovery_history = []
        self.health_check_interval = 30  # 健康检查间隔（秒）
        self.is_monitoring = False
        self.monitoring_thread = None
    
    def register_component(self, component_id, component_type, health_check_func, recovery_actions):
        """注册组件"""
        self.components[component_id] = {
            'id': component_id,
            'type': component_type,
            'health_check_func': health_check_func,
            'recovery_actions': recovery_actions,
            'status': ComponentStatus.HEALTHY,
            'last_check': None,
            'failure_count': 0,
            'last_recovery': None
        }
        
        print(f"已注册组件: {component_id} ({component_type})")
    
    def set_recovery_policy(self, component_type, max_failures=3, recovery_timeout=300):
        """设置恢复策略"""
        self.recovery_policies[component_type] = {
            'max_failures': max_failures,
            'recovery_timeout': recovery_timeout,
            'cooldown_period': 60  # 冷却期（秒）
        }
        print(f"已设置 {component_type} 类型组件的恢复策略")
    
    def start_monitoring(self):
        """启动监控"""
        if self.is_monitoring:
            print("监控已在运行中")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        print("已启动自动化监控")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        print("已停止自动化监控")
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            self._perform_health_checks()
            self._check_and_recover()
            time.sleep(self.health_check_interval)
    
    def _perform_health_checks(self):
        """执行健康检查"""
        current_time = datetime.now()
        
        for component_id, component in self.components.items():
            try:
                # 执行健康检查
                is_healthy = component['health_check_func']()
                component['last_check'] = current_time
                
                # 更新组件状态
                if is_healthy:
                    component['status'] = ComponentStatus.HEALTHY
                    component['failure_count'] = 0
                else:
                    component['status'] = ComponentStatus.FAILED
                    component['failure_count'] += 1
                
                print(f"组件 {component_id} 健康检查: {'健康' if is_healthy else '故障'}")
                
            except Exception as e:
                print(f"组件 {component_id} 健康检查异常: {e}")
                component['status'] = ComponentStatus.FAILED
                component['failure_count'] += 1
    
    def _check_and_recover(self):
        """检查并执行恢复"""
        current_time = datetime.now()
        
        for component_id, component in self.components.items():
            # 检查是否需要恢复
            if (component['status'] == ComponentStatus.FAILED and 
                component['failure_count'] >= self._get_max_failures(component['type'])):
                
                # 检查冷却期
                if (component['last_recovery'] and 
                    current_time - component['last_recovery'] < timedelta(
                        seconds=self._get_cooldown_period(component['type']))):
                    continue
                
                # 执行恢复
                self._perform_recovery(component_id)
    
    def _perform_recovery(self, component_id):
        """执行恢复操作"""
        if component_id not in self.components:
            return
        
        component = self.components[component_id]
        component['status'] = ComponentStatus.RECOVERING
        component['last_recovery'] = datetime.now()
        
        recovery_record = {
            'component_id': component_id,
            'start_time': component['last_recovery'],
            'actions_performed': [],
            'status': 'in_progress'
        }
        
        print(f"开始恢复组件 {component_id}")
        
        try:
            # 执行恢复动作
            for action_name, action_func in component['recovery_actions'].items():
                print(f"  执行恢复动作: {action_name}")
                recovery_record['actions_performed'].append(action_name)
                
                try:
                    action_func()
                    print(f"    {action_name} 执行成功")
                except Exception as e:
                    print(f"    {action_name} 执行失败: {e}")
                    recovery_record['status'] = 'failed'
                    recovery_record['error'] = str(e)
                    break
            
            # 更新组件状态
            if recovery_record['status'] != 'failed':
                recovery_record['status'] = 'completed'
                recovery_record['end_time'] = datetime.now()
                component['status'] = ComponentStatus.HEALTHY
                component['failure_count'] = 0
                print(f"组件 {component_id} 恢复成功")
            else:
                component['status'] = ComponentStatus.FAILED
                print(f"组件 {component_id} 恢复失败")
                
        except Exception as e:
            recovery_record['status'] = 'failed'
            recovery_record['error'] = str(e)
            recovery_record['end_time'] = datetime.now()
            component['status'] = ComponentStatus.FAILED
            print(f"组件 {component_id} 恢复过程异常: {e}")
        
        self.recovery_history.append(recovery_record)
    
    def _get_max_failures(self, component_type):
        """获取最大失败次数"""
        policy = self.recovery_policies.get(component_type, {})
        return policy.get('max_failures', 3)
    
    def _get_cooldown_period(self, component_type):
        """获取冷却期"""
        policy = self.recovery_policies.get(component_type, {})
        return policy.get('cooldown_period', 60)
    
    def get_component_status(self, component_id=None):
        """获取组件状态"""
        if component_id:
            return self.components.get(component_id)
        return self.components
    
    def get_recovery_history(self, limit=10):
        """获取恢复历史"""
        return list(self.recovery_history)[-limit:]

# 使用示例
# 定义健康检查函数
def check_database_health():
    """检查数据库健康状态"""
    # 模拟健康检查逻辑
    import random
    return random.random() > 0.2  # 80%概率健康

def check_cache_health():
    """检查缓存健康状态"""
    import random
    return random.random() > 0.1  # 90%概率健康

def check_api_health():
    """检查API健康状态"""
    import random
    return random.random() > 0.15  # 85%概率健康

# 定义恢复动作
def restart_database():
    """重启数据库"""
    print("  重启数据库服务...")
    time.sleep(2)  # 模拟重启时间

def clear_cache():
    """清理缓存"""
    print("  清理缓存数据...")
    time.sleep(1)  # 模拟清理时间

def restart_api_service():
    """重启API服务"""
    print("  重启API服务...")
    time.sleep(1.5)  # 模拟重启时间

def reload_config():
    """重新加载配置"""
    print("  重新加载配置文件...")
    time.sleep(0.5)  # 模拟加载时间

# 创建自动化恢复系统
recovery_system = AutomatedRecoverySystem()

# 设置恢复策略
recovery_system.set_recovery_policy('database', max_failures=2, recovery_timeout=300)
recovery_system.set_recovery_policy('cache', max_failures=1, recovery_timeout=120)
recovery_system.set_recovery_policy('api', max_failures=3, recovery_timeout=180)

# 注册组件
recovery_system.register_component(
    'main_database', 
    'database', 
    check_database_health, 
    {'restart_service': restart_database}
)

recovery_system.register_component(
    'redis_cache', 
    'cache', 
    check_cache_health, 
    {'clear_cache': clear_cache, 'reload_config': reload_config}
)

recovery_system.register_component(
    'user_api', 
    'api', 
    check_api_health, 
    {'restart_service': restart_api_service}
)

# 启动监控（在实际使用中启用）
# recovery_system.start_monitoring()

# 模拟运行一段时间
print("自动化恢复系统已就绪")
print("组件注册完成，等待监控触发...")
```

## 智能优化算法

### 机器学习在性能优化中的应用

机器学习技术能够通过对历史性能数据的学习和分析，自动识别性能模式并预测潜在问题，为存储系统的优化提供智能化支持。

#### 性能预测模型实现
```python
# 性能预测模型示例
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from datetime import datetime, timedelta

class PerformancePredictor:
    """性能预测器"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.training_data = {}
        self.prediction_history = []
    
    def prepare_training_data(self, historical_data):
        """准备训练数据"""
        # 假设历史数据格式为字典列表
        # [{'timestamp': datetime, 'cpu_usage': float, 'memory_usage': float, 
        #   'disk_io': float, 'network_traffic': float, 'response_time': float}, ...]
        
        if not historical_data:
            raise ValueError("历史数据不能为空")
        
        # 提取特征和目标变量
        features = []
        targets = []
        
        for record in historical_data:
            # 特征：系统资源使用情况
            feature_vector = [
                record.get('cpu_usage', 0),
                record.get('memory_usage', 0),
                record.get('disk_io', 0),
                record.get('network_traffic', 0),
                record.get('active_connections', 0),
                record.get('queue_length', 0)
            ]
            features.append(feature_vector)
            
            # 目标：响应时间
            targets.append(record.get('response_time', 0))
        
        return np.array(features), np.array(targets)
    
    def train_model(self, model_name, features, targets, model_type='random_forest'):
        """训练预测模型"""
        # 分割训练和测试数据
        X_train, X_test, y_train, y_test = train_test_split(
            features, targets, test_size=0.2, random_state=42
        )
        
        # 标准化特征
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 选择模型
        if model_type == 'linear_regression':
            model = LinearRegression()
        elif model_type == 'random_forest':
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        # 训练模型
        model.fit(X_train_scaled, y_train)
        
        # 评估模型
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # 保存模型和缩放器
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        
        # 保存训练数据摘要
        self.training_data[model_name] = {
            'samples': len(features),
            'features': features.shape[1],
            'mse': mse,
            'r2_score': r2,
            'trained_at': datetime.now()
        }
        
        print(f"模型 {model_name} 训练完成:")
        print(f"  样本数: {len(features)}")
        print(f"  特征数: {features.shape[1]}")
        print(f"  均方误差: {mse:.4f}")
        print(f"  R²得分: {r2:.4f}")
        
        return model, scaler
    
    def predict_performance(self, model_name, current_features):
        """预测性能"""
        if model_name not in self.models:
            raise ValueError(f"模型 {model_name} 不存在")
        
        model = self.models[model_name]
        scaler = self.scalers[model_name]
        
        # 确保输入是正确的形状
        if len(current_features) != self.training_data[model_name]['features']:
            raise ValueError("特征数量不匹配")
        
        # 标准化输入
        features_array = np.array(current_features).reshape(1, -1)
        features_scaled = scaler.transform(features_array)
        
        # 进行预测
        prediction = model.predict(features_scaled)[0]
        
        # 记录预测历史
        prediction_record = {
            'model_name': model_name,
            'input_features': current_features,
            'predicted_value': prediction,
            'timestamp': datetime.now()
        }
        self.prediction_history.append(prediction_record)
        
        return prediction
    
    def get_model_performance(self, model_name):
        """获取模型性能信息"""
        if model_name not in self.training_data:
            return None
        
        return self.training_data[model_name]
    
    def save_model(self, model_name, filepath):
        """保存模型"""
        if model_name not in self.models:
            raise ValueError(f"模型 {model_name} 不存在")
        
        model_data = {
            'model': self.models[model_name],
            'scaler': self.scalers[model_name],
            'training_info': self.training_data[model_name]
        }
        
        joblib.dump(model_data, filepath)
        print(f"模型 {model_name} 已保存到 {filepath}")
    
    def load_model(self, model_name, filepath):
        """加载模型"""
        model_data = joblib.load(filepath)
        
        self.models[model_name] = model_data['model']
        self.scalers[model_name] = model_data['scaler']
        self.training_data[model_name] = model_data['training_info']
        
        print(f"模型 {model_name} 已从 {filepath} 加载")

# 使用示例
predictor = PerformancePredictor()

# 生成模拟历史数据
def generate_historical_data(samples=1000):
    """生成模拟历史数据"""
    data = []
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(samples):
        timestamp = base_time + timedelta(minutes=i*5)  # 每5分钟一个数据点
        
        # 生成相关的系统指标
        cpu_usage = np.random.normal(50, 20)  # 平均50%，标准差20%
        cpu_usage = max(0, min(100, cpu_usage))  # 限制在0-100范围内
        
        memory_usage = np.random.normal(60, 25)  # 平均60%，标准差25%
        memory_usage = max(0, min(100, memory_usage))
        
        disk_io = np.random.exponential(50)  # 磁盘IO使用量
        network_traffic = np.random.exponential(1000)  # 网络流量
        
        active_connections = np.random.poisson(50)  # 活跃连接数
        queue_length = np.random.poisson(10)  # 队列长度
        
        # 响应时间与系统负载相关
        response_time = (
            10 +  # 基础响应时间
            cpu_usage * 0.5 +  # CPU影响
            memory_usage * 0.3 +  # 内存影响
            disk_io * 0.1 +  # 磁盘IO影响
            np.random.normal(0, 5)  # 随机噪声
        )
        response_time = max(1, response_time)  # 确保响应时间为正数
        
        data.append({
            'timestamp': timestamp,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_io': disk_io,
            'network_traffic': network_traffic,
            'active_connections': active_connections,
            'queue_length': queue_length,
            'response_time': response_time
        })
    
    return data

# 生成历史数据
historical_data = generate_historical_data(1000)
print(f"生成了 {len(historical_data)} 条历史数据")

# 准备训练数据
features, targets = predictor.prepare_training_data(historical_data)

# 训练模型
model, scaler = predictor.train_model('response_time_predictor', features, targets, 'random_forest')

# 进行预测
current_system_state = [65, 70, 80, 1200, 60, 15]  # 当前系统状态
predicted_response_time = predictor.predict_performance('response_time_predictor', current_system_state)

print(f"\n性能预测结果:")
print(f"当前系统状态: CPU {current_system_state[0]}%, 内存 {current_system_state[1]}%")
print(f"预测响应时间: {predicted_response_time:.2f} ms")

# 获取模型性能信息
model_perf = predictor.get_model_performance('response_time_predictor')
if model_perf:
    print(f"\n模型性能:")
    print(f"  训练样本数: {model_perf['samples']}")
    print(f"  特征数量: {model_perf['features']}")
    print(f"  均方误差: {model_perf['mse']:.4f}")
    print(f"  R²得分: {model_perf['r2_score']:.4f}")
```

### 自适应资源调度

自适应资源调度能够根据系统负载和性能需求动态调整资源分配，实现资源的最优利用。

#### 智能资源调度器实现
```python
# 智能资源调度器示例
import time
import threading
from datetime import datetime, timedelta
from collections import deque
import heapq

class ResourceRequirement:
    """资源需求"""
    def __init__(self, task_id, cpu_cores, memory_mb, priority=1, deadline=None):
        self.task_id = task_id
        self.cpu_cores = cpu_cores
        self.memory_mb = memory_mb
        self.priority = priority
        self.deadline = deadline
        self.submitted_at = datetime.now()
        self.allocated_at = None
        self.completed_at = None
    
    def __lt__(self, other):
        # 优先级高的任务排在前面，优先级相同时按提交时间排序
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.submitted_at < other.submitted_at

class AdaptiveResourceScheduler:
    """自适应资源调度器"""
    
    def __init__(self, total_cpu_cores=32, total_memory_gb=128):
        self.total_resources = {
            'cpu_cores': total_cpu_cores,
            'memory_mb': total_memory_gb * 1024
        }
        self.available_resources = self.total_resources.copy()
        self.allocated_resources = {}
        self.task_queue = []  # 优先队列
        self.running_tasks = {}
        self.completed_tasks = deque(maxlen=1000)
        self.scheduling_history = deque(maxlen=10000)
        
        # 性能监控
        self.resource_utilization_history = deque(maxlen=100)
        self.scheduling_decisions = 0
        self.scheduler_thread = None
        self.is_running = False
    
    def submit_task(self, task):
        """提交任务"""
        heapq.heappush(self.task_queue, task)
        print(f"任务 {task.task_id} 已提交 (优先级: {task.priority})")
        
        # 记录调度历史
        self.scheduling_history.append({
            'event': 'task_submitted',
            'task_id': task.task_id,
            'timestamp': datetime.now(),
            'priority': task.priority,
            'resources_requested': {
                'cpu_cores': task.cpu_cores,
                'memory_mb': task.memory_mb
            }
        })
    
    def start_scheduler(self):
        """启动调度器"""
        if self.is_running:
            print("调度器已在运行中")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduling_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        print("资源调度器已启动")
    
    def stop_scheduler(self):
        """停止调度器"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        print("资源调度器已停止")
    
    def _scheduling_loop(self):
        """调度循环"""
        while self.is_running:
            self._update_resource_utilization()
            self._check_completed_tasks()
            self._schedule_tasks()
            time.sleep(1)  # 每秒检查一次
    
    def _update_resource_utilization(self):
        """更新资源利用率"""
        cpu_utilization = (self.total_resources['cpu_cores'] - self.available_resources['cpu_cores']) / self.total_resources['cpu_cores'] * 100
        memory_utilization = (self.total_resources['memory_mb'] - self.available_resources['memory_mb']) / self.total_resources['memory_mb'] * 100
        
        utilization_record = {
            'timestamp': datetime.now(),
            'cpu_utilization': cpu_utilization,
            'memory_utilization': memory_utilization,
            'available_cpu': self.available_resources['cpu_cores'],
            'available_memory': self.available_resources['memory_mb']
        }
        
        self.resource_utilization_history.append(utilization_record)
    
    def _check_completed_tasks(self):
        """检查已完成的任务"""
        completed_task_ids = []
        current_time = datetime.now()
        
        for task_id, task in self.running_tasks.items():
            # 检查是否有截止时间且已超时
            if task.deadline and current_time > task.deadline:
                print(f"任务 {task_id} 已超时")
                completed_task_ids.append(task_id)
                continue
            
            # 模拟任务完成（在实际应用中会有实际的完成检测机制）
            # 这里随机完成一些任务
            import random
            if random.random() < 0.02:  # 2%概率完成
                completed_task_ids.append(task_id)
        
        # 处理已完成的任务
        for task_id in completed_task_ids:
            self._complete_task(task_id)
    
    def _complete_task(self, task_id):
        """完成任务并释放资源"""
        if task_id not in self.running_tasks:
            return
        
        task = self.running_tasks[task_id]
        task.completed_at = datetime.now()
        
        # 释放资源
        if task_id in self.allocated_resources:
            resources = self.allocated_resources[task_id]
            self.available_resources['cpu_cores'] += resources['cpu_cores']
            self.available_resources['memory_mb'] += resources['memory_mb']
            del self.allocated_resources[task_id]
        
        # 移动任务到完成队列
        del self.running_tasks[task_id]
        self.completed_tasks.append(task)
        
        print(f"任务 {task_id} 已完成")
        
        # 记录调度历史
        self.scheduling_history.append({
            'event': 'task_completed',
            'task_id': task_id,
            'timestamp': task.completed_at,
            'execution_time': (task.completed_at - task.allocated_at).total_seconds()
        })
    
    def _schedule_tasks(self):
        """调度任务"""
        # 检查是否有足够资源运行新任务
        temp_queue = []
        scheduled_count = 0
        
        while self.task_queue and scheduled_count < 5:  # 每次最多调度5个任务
            task = heapq.heappop(self.task_queue)
            
            # 检查资源是否足够
            if (self.available_resources['cpu_cores'] >= task.cpu_cores and
                self.available_resources['memory_mb'] >= task.memory_mb):
                
                # 分配资源
                self._allocate_resources(task)
                scheduled_count += 1
                self.scheduling_decisions += 1
                
                print(f"任务 {task.task_id} 已调度")
                
                # 记录调度历史
                self.scheduling_history.append({
                    'event': 'task_scheduled',
                    'task_id': task.task_id,
                    'timestamp': datetime.now(),
                    'allocated_resources': {
                        'cpu_cores': task.cpu_cores,
                        'memory_mb': task.memory_mb
                    }
                })
            else:
                # 资源不足，放回队列
                temp_queue.append(task)
        
        # 将未调度的任务放回队列
        for task in temp_queue:
            heapq.heappush(self.task_queue, task)
    
    def _allocate_resources(self, task):
        """分配资源给任务"""
        # 扣除资源
        self.available_resources['cpu_cores'] -= task.cpu_cores
        self.available_resources['memory_mb'] -= task.memory_mb
        
        # 记录资源分配
        self.allocated_resources[task.task_id] = {
            'cpu_cores': task.cpu_cores,
            'memory_mb': task.memory_mb
        }
        
        # 记录任务开始时间
        task.allocated_at = datetime.now()
        
        # 添加到运行队列
        self.running_tasks[task.task_id] = task
    
    def get_system_status(self):
        """获取系统状态"""
        cpu_utilization = (self.total_resources['cpu_cores'] - self.available_resources['cpu_cores']) / self.total_resources['cpu_cores'] * 100
        memory_utilization = (self.total_resources['memory_mb'] - self.available_resources['memory_mb']) / self.total_resources['memory_mb'] * 100
        
        return {
            'total_resources': self.total_resources,
            'available_resources': self.available_resources.copy(),
            'allocated_resources': sum(len(resources) for resources in self.allocated_resources.values()),
            'cpu_utilization': cpu_utilization,
            'memory_utilization': memory_utilization,
            'pending_tasks': len(self.task_queue),
            'running_tasks': len(self.running_tasks),
            'completed_tasks': len(self.completed_tasks),
            'scheduling_decisions': self.scheduling_decisions
        }
    
    def get_resource_utilization_trend(self, hours=1):
        """获取资源利用率趋势"""
        current_time = datetime.now()
        time_window = timedelta(hours=hours)
        
        recent_utilization = [
            record for record in self.resource_utilization_history
            if current_time - record['timestamp'] <= time_window
        ]
        
        if not recent_utilization:
            return []
        
        # 按时间分组统计（每5分钟一个点）
        grouped_data = {}
        for record in recent_utilization:
            time_key = record['timestamp'].replace(minute=record['timestamp'].minute // 5 * 5, second=0, microsecond=0)
            if time_key not in grouped_data:
                grouped_data[time_key] = {
                    'cpu_samples': [],
                    'memory_samples': []
                }
            grouped_data[time_key]['cpu_samples'].append(record['cpu_utilization'])
            grouped_data[time_key]['memory_samples'].append(record['memory_utilization'])
        
        # 计算平均值
        trend_data = []
        for time_key, samples in sorted(grouped_data.items()):
            trend_data.append({
                'timestamp': time_key,
                'avg_cpu_utilization': sum(samples['cpu_samples']) / len(samples['cpu_samples']),
                'avg_memory_utilization': sum(samples['memory_samples']) / len(samples['memory_samples'])
            })
        
        return trend_data

# 使用示例
scheduler = AdaptiveResourceScheduler(total_cpu_cores=16, total_memory_gb=64)

# 提交一些任务
tasks = [
    ResourceRequirement("task_001", 4, 8192, priority=3),  # 高优先级任务
    ResourceRequirement("task_002", 2, 4096, priority=1),  # 低优先级任务
    ResourceRequirement("task_003", 8, 16384, priority=2), # 中优先级任务
    ResourceRequirement("task_004", 1, 2048, priority=1),  # 低优先级任务
    ResourceRequirement("task_005", 6, 12288, priority=3), # 高优先级任务
]

for task in tasks:
    scheduler.submit_task(task)

# 启动调度器
scheduler.start_scheduler()

# 等待一段时间观察调度效果
time.sleep(10)

# 获取系统状态
status = scheduler.get_system_status()
print("系统状态:")
print(f"  CPU利用率: {status['cpu_utilization']:.1f}%")
print(f"  内存利用率: {status['memory_utilization']:.1f}%")
print(f"  待处理任务: {status['pending_tasks']}")
print(f"  运行中任务: {status['running_tasks']}")
print(f"  已完成任务: {status['completed_tasks']}")

# 获取资源利用率趋势
trend = scheduler.get_resource_utilization_trend(0.1)  # 最近6分钟
print(f"\n资源利用率趋势 ({len(trend)} 个数据点):")
for point in trend[-5:]:  # 显示最后5个点
    print(f"  {point['timestamp'].strftime('%H:%M:%S')}: "
          f"CPU {point['avg_cpu_utilization']:.1f}%, "
          f"内存 {point['avg_memory_utilization']:.1f}%")

# 停止调度器
scheduler.stop_scheduler()
```

通过以上自动化与智能优化技术的实现，我们能够构建一个更加智能、高效的数据存储性能管理体系。这些技术不仅能够提升系统的自动化水平，还能通过机器学习和智能算法实现更精准的性能预测和资源调度，为现代存储系统的运维管理提供强有力的技术支撑。