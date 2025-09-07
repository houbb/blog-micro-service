---
title: 配置管理与智能化运维：AI驱动的配置优化与自动化
date: 2025-08-31
categories: [Configuration Management]
tags: [microservice-configuration-management]
published: true
---

# 18.1 配置管理与智能化运维

随着人工智能技术的快速发展，智能化运维(AI Ops)正在成为现代IT运维的新范式。在配置管理领域，AI技术的应用正在带来革命性的变化，从智能配置优化到异常检测，再到预测性维护，AI正在重塑配置管理的方式和效率。本节将深入探讨人工智能在配置管理中的应用、机器学习驱动的配置优化、智能异常检测和预测性维护，以及自主运维和自适应配置等关键主题。

## 人工智能在配置管理中的应用

人工智能技术为配置管理带来了前所未有的智能化能力，使得配置管理从被动响应转变为主动预测和优化。

### 1. AI驱动的配置分析

```python
# ai-config-analyzer.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import json
from typing import Dict, Any, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIConfigAnalyzer:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_config_data(self, config_history: List[Dict[str, Any]]) -> pd.DataFrame:
        """准备配置数据用于机器学习"""
        # 将配置历史转换为特征矩阵
        data = []
        for record in config_history:
            row = {
                'timestamp': pd.to_datetime(record['timestamp']),
                'cpu_usage': record.get('metrics', {}).get('cpu_usage', 0),
                'memory_usage': record.get('metrics', {}).get('memory_usage', 0),
                'response_time': record.get('metrics', {}).get('response_time', 0),
                'error_rate': record.get('metrics', {}).get('error_rate', 0),
                'requests_per_second': record.get('metrics', {}).get('requests_per_second', 0),
            }
            
            # 添加配置参数
            config_params = record.get('config', {})
            for key, value in config_params.items():
                if isinstance(value, (int, float)):
                    row[f'config_{key}'] = value
                elif isinstance(value, bool):
                    row[f'config_{key}'] = int(value)
                    
            data.append(row)
            
        df = pd.DataFrame(data)
        return df
        
    def train_performance_model(self, config_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """训练性能预测模型"""
        try:
            # 准备数据
            df = self.prepare_config_data(config_history)
            
            # 选择特征和目标变量
            feature_columns = [col for col in df.columns if col.startswith('config_')]
            target_columns = ['response_time', 'error_rate', 'cpu_usage']
            
            X = df[feature_columns]
            y = df[target_columns].mean(axis=1)  # 综合性能指标
            
            # 数据标准化
            X_scaled = self.scaler.fit_transform(X)
            
            # 分割训练和测试数据
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # 训练模型
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            # 评估模型
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            
            logger.info(f"Model trained successfully. Train score: {train_score:.4f}, Test score: {test_score:.4f}")
            
            return {
                'success': True,
                'train_score': train_score,
                'test_score': test_score,
                'feature_importance': dict(zip(feature_columns, self.model.feature_importances_)),
                'model_params': self.model.get_params()
            }
        except Exception as e:
            logger.error(f"Failed to train performance model: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def predict_config_performance(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """预测配置性能"""
        if not self.is_trained:
            return {
                'success': False,
                'error': 'Model not trained yet'
            }
            
        try:
            # 构造特征向量
            features = []
            for key, value in config.items():
                if isinstance(value, (int, float, bool)):
                    features.append(float(value))
                    
            # 标准化特征
            features_scaled = self.scaler.transform([features])
            
            # 预测性能
            prediction = self.model.predict(features_scaled)[0]
            
            return {
                'success': True,
                'predicted_performance': prediction,
                'confidence': 'high' if abs(prediction) < 100 else 'medium'
            }
        except Exception as e:
            logger.error(f"Failed to predict config performance: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def recommend_config_optimization(self, current_config: Dict[str, Any], 
                                    constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """推荐配置优化方案"""
        if not self.is_trained:
            return {
                'success': False,
                'error': 'Model not trained yet'
            }
            
        try:
            # 生成候选配置
            candidate_configs = self._generate_candidate_configs(current_config, constraints)
            
            # 评估候选配置
            evaluations = []
            for config in candidate_configs:
                prediction = self.predict_config_performance(config)
                if prediction['success']:
                    evaluations.append({
                        'config': config,
                        'performance': prediction['predicted_performance'],
                        'score': 1.0 / (1.0 + prediction['predicted_performance'])  # 假设性能越低越好
                    })
                    
            # 选择最佳配置
            if evaluations:
                best_config = min(evaluations, key=lambda x: x['performance'])
                return {
                    'success': True,
                    'recommended_config': best_config['config'],
                    'expected_performance': best_config['performance'],
                    'improvement': best_config['performance'] - self.predict_config_performance(current_config)['predicted_performance']
                }
            else:
                return {
                    'success': False,
                    'error': 'No valid configurations found'
                }
        except Exception as e:
            logger.error(f"Failed to recommend config optimization: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def _generate_candidate_configs(self, base_config: Dict[str, Any], 
                                  constraints: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """生成候选配置"""
        candidates = []
        num_candidates = 20
        
        for _ in range(num_candidates):
            candidate = base_config.copy()
            
            # 随机调整数值型配置参数
            for key, value in candidate.items():
                if isinstance(value, (int, float)) and key.startswith('config_'):
                    # 根据约束调整参数
                    if constraints and key in constraints:
                        min_val = constraints[key].get('min', value * 0.5)
                        max_val = constraints[key].get('max', value * 1.5)
                        candidate[key] = np.random.uniform(min_val, max_val)
                    else:
                        # 无约束时进行小幅调整
                        adjustment = np.random.uniform(0.8, 1.2)
                        candidate[key] = value * adjustment
                        
            candidates.append(candidate)
            
        return candidates

# 使用示例
# analyzer = AIConfigAnalyzer()

# # 配置历史数据示例
# config_history = [
#     {
#         "timestamp": "2025-01-01T10:00:00Z",
#         "config": {
#             "config_thread_pool_size": 10,
#             "config_cache_size": 100,
#             "config_timeout": 30
#         },
#         "metrics": {
#             "cpu_usage": 70,
#             "memory_usage": 60,
#             "response_time": 150,
#             "error_rate": 0.01,
#             "requests_per_second": 1000
#         }
#     },
#     # ... 更多历史数据
# ]

# # 训练模型
# train_result = analyzer.train_performance_model(config_history)

# # 预测配置性能
# current_config = {
#     "config_thread_pool_size": 15,
#     "config_cache_size": 150,
#     "config_timeout": 25
# }
# prediction = analyzer.predict_config_performance(current_config)

# # 推荐配置优化
# constraints = {
#     "config_thread_pool_size": {"min": 5, "max": 50},
#     "config_cache_size": {"min": 50, "max": 500}
# }
# recommendation = analyzer.recommend_config_optimization(current_config, constraints)
```

### 2. 智能配置推荐系统

```yaml
# ai-config-recommendation-system.yaml
---
ai_config_recommendation_system:
  # 系统架构
  architecture:
    data_layer:
      description: "数据收集和存储层"
      components:
        - "配置历史数据库"
        - "性能指标收集器"
        - "日志分析器"
        
    processing_layer:
      description: "AI处理和分析层"
      components:
        - "机器学习模型训练器"
        - "实时推理引擎"
        - "配置优化器"
        
    application_layer:
      description: "应用和服务层"
      components:
        - "配置推荐API"
        - "自动化执行器"
        - "可视化界面"
        
  # 机器学习模型
  ml_models:
    performance_prediction:
      type: "回归模型"
      algorithm: "随机森林/梯度提升"
      features:
        - "配置参数值"
        - "系统资源使用率"
        - "应用性能指标"
      target: "综合性能评分"
      
    anomaly_detection:
      type: "异常检测模型"
      algorithm: "孤立森林/自编码器"
      features:
        - "配置变更历史"
        - "性能指标异常"
        - "系统行为模式"
      target: "异常配置识别"
      
    optimization_recommendation:
      type: "强化学习模型"
      algorithm: "Q学习/策略梯度"
      features:
        - "当前配置状态"
        - "性能目标"
        - "资源约束"
      target: "最优配置推荐"
      
  # 推荐策略
  recommendation_strategies:
    performance_optimization:
      description: "性能优化推荐"
      priority: "高"
      update_frequency: "实时"
      
    cost_optimization:
      description: "成本优化推荐"
      priority: "中"
      update_frequency: "每日"
      
    reliability_improvement:
      description: "可靠性提升推荐"
      priority: "高"
      update_frequency: "实时"
      
    security_enhancement:
      description: "安全增强推荐"
      priority: "高"
      update_frequency: "实时"
```

### 3. AI配置管理平台

```bash
# ai-config-platform.sh

# AI驱动的配置管理平台脚本
ai_config_platform() {
    echo "Initializing AI-driven configuration management platform..."
    
    # 1. 数据收集和处理
    echo "1. Setting up data collection and processing..."
    setup_data_collection
    
    # 2. 机器学习模型部署
    echo "2. Deploying machine learning models..."
    deploy_ml_models
    
    # 3. 推荐系统实现
    echo "3. Implementing recommendation system..."
    implement_recommendation_system
    
    # 4. 自动化执行机制
    echo "4. Setting up automation execution..."
    setup_automation_execution
    
    echo "AI-driven configuration management platform initialized"
}

# 设置数据收集
setup_data_collection() {
    echo "Setting up data collection mechanisms..."
    
    # 创建配置历史收集脚本
    cat > collect-config-history.sh << 'EOF'
#!/bin/bash

# 配置历史收集脚本
OUTPUT_DIR="/data/config-history/$(date +%Y%m%d)"
mkdir -p $OUTPUT_DIR

echo "Collecting configuration history..."

# 收集Kubernetes ConfigMaps和Secrets
kubectl get configmap --all-namespaces -o json > $OUTPUT_DIR/configmaps.json
kubectl get secret --all-namespaces -o json > $OUTPUT_DIR/secrets.json

# 收集应用性能指标
curl -s "http://prometheus:9090/api/v1/query?query=up" > $OUTPUT_DIR/service_status.json
curl -s "http://prometheus:9090/api/v1/query?query=rate(http_requests_total[5m])" > $OUTPUT_DIR/request_rates.json

# 收集系统资源使用情况
kubectl top nodes > $OUTPUT_DIR/node_resources.txt
kubectl top pods > $OUTPUT_DIR/pod_resources.txt

# 记录时间戳
echo "$(date -Iseconds)" > $OUTPUT_DIR/timestamp.txt

echo "Configuration history collected to $OUTPUT_DIR"
EOF
    
    chmod +x collect-config-history.sh
    
    # 设置定时任务
    echo "0 * * * * /path/to/collect-config-history.sh" | crontab -
    
    # 创建数据处理管道
    cat > process-config-data.py << 'EOF'
#!/usr/bin/env python3

import json
import pandas as pd
from datetime import datetime
import os

def process_config_data(data_dir):
    """处理配置数据"""
    print(f"Processing configuration data from {data_dir}")
    
    # 读取配置数据
    configmaps_file = os.path.join(data_dir, "configmaps.json")
    if os.path.exists(configmaps_file):
        with open(configmaps_file, 'r') as f:
            configmaps = json.load(f)
        
        # 提取配置信息
        config_data = []
        for item in configmaps.get('items', []):
            config_data.append({
                'timestamp': datetime.now().isoformat(),
                'namespace': item['metadata']['namespace'],
                'name': item['metadata']['name'],
                'config_type': 'configmap',
                'data_keys': list(item.get('data', {}).keys()),
                'labels': item['metadata'].get('labels', {})
            })
    
    # 保存处理后的数据
    output_file = os.path.join(data_dir, "processed_config_data.json")
    with open(output_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"Processed data saved to {output_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        process_config_data(sys.argv[1])
EOF
    
    echo "Data collection mechanisms set up"
}

# 部署机器学习模型
deploy_ml_models() {
    echo "Deploying machine learning models..."
    
    # 创建模型训练脚本
    cat > train-ml-models.sh << 'EOF'
#!/bin/bash

# 机器学习模型训练脚本
MODEL_DIR="/models/$(date +%Y%m%d)"
mkdir -p $MODEL_DIR

echo "Training machine learning models..."

# 训练性能预测模型
python3 -c "
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

# 加载数据（示例）
# 在实际应用中，这里会加载真实的历史配置数据
data = pd.DataFrame({
    'config_param1': [10, 20, 30, 40, 50],
    'config_param2': [100, 200, 300, 400, 500],
    'performance_metric': [50, 40, 30, 20, 10]
})

X = data[['config_param1', 'config_param2']]
y = data['performance_metric']

# 训练模型
model = RandomForestRegressor(n_estimators=100)
model.fit(X, y)

# 保存模型
joblib.dump(model, '$MODEL_DIR/performance_model.pkl')
print('Performance prediction model trained and saved')
"

# 训练异常检测模型
python3 -c "
from sklearn.ensemble import IsolationForest
import numpy as np
import joblib

# 生成示例数据
np.random.seed(42)
normal_data = np.random.normal(0, 1, (100, 2))
anomalies = np.random.uniform(-5, 5, (10, 2))
data = np.vstack([normal_data, anomalies])

# 训练异常检测模型
anomaly_detector = IsolationForest(contamination=0.1)
anomaly_detector.fit(data)

# 保存模型
joblib.dump(anomaly_detector, '$MODEL_DIR/anomaly_detector.pkl')
print('Anomaly detection model trained and saved')
"

echo "Machine learning models trained and deployed to $MODEL_DIR"
EOF
    
    chmod +x train-ml-models.sh
    
    echo "ML models deployed"
}

# 实现推荐系统
implement_recommendation_system() {
    echo "Implementing recommendation system..."
    
    # 创建推荐API
    cat > config-recommender-api.py << 'EOF'
#!/usr/bin/env python3

from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# 加载模型
try:
    performance_model = joblib.load('/models/latest/performance_model.pkl')
    anomaly_detector = joblib.load('/models/latest/anomaly_detector.pkl')
except Exception as e:
    print(f"Warning: Could not load models: {e}")
    performance_model = None
    anomaly_detector = None

@app.route('/recommend/config', methods=['POST'])
def recommend_config():
    """配置推荐API"""
    try:
        data = request.json
        current_config = data.get('current_config', {})
        
        # 构造特征向量
        features = [
            current_config.get('thread_pool_size', 10),
            current_config.get('cache_size', 100)
        ]
        
        # 预测性能
        if performance_model:
            predicted_performance = performance_model.predict([features])[0]
        else:
            predicted_performance = 50  # 默认值
        
        # 生成推荐
        recommendations = {
            'thread_pool_size': max(1, int(features[0] * 1.2)),
            'cache_size': max(10, int(features[1] * 1.1))
        }
        
        return jsonify({
            'success': True,
            'current_performance': predicted_performance,
            'recommended_config': recommendations,
            'expected_improvement': 10 - predicted_performance
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/detect/anomalies', methods=['POST'])
def detect_anomalies():
    """异常检测API"""
    try:
        data = request.json
        config_features = data.get('config_features', [])
        
        if anomaly_detector:
            is_anomaly = anomaly_detector.predict([config_features])[0] == -1
            anomaly_score = anomaly_detector.decision_function([config_features])[0]
        else:
            is_anomaly = False
            anomaly_score = 0
        
        return jsonify({
            'success': True,
            'is_anomaly': is_anomaly,
            'anomaly_score': float(anomaly_score)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF
    
    echo "Recommendation system implemented"
}

# 设置自动化执行
setup_automation_execution() {
    echo "Setting up automation execution mechanisms..."
    
    # 创建自动化执行器
    cat > config-automation-executor.py << 'EOF'
#!/usr/bin/env python3

import subprocess
import json
import time
from datetime import datetime

class ConfigAutomationExecutor:
    def __init__(self):
        self.execution_log = []
        
    def apply_config_recommendation(self, recommendation, dry_run=False):
        """应用配置推荐"""
        try:
            if dry_run:
                print("DRY RUN: Would apply configuration:")
                print(json.dumps(recommendation, indent=2))
                return {"success": True, "dry_run": True}
            
            # 应用配置（示例：更新Kubernetes ConfigMap）
            config_patch = {
                "data": {
                    "thread.pool.size": str(recommendation.get("thread_pool_size", "10")),
                    "cache.size": str(recommendation.get("cache_size", "100"))
                }
            }
            
            # 这里应该执行实际的配置更新命令
            # kubectl patch configmap myapp-config -p "$(echo $config_patch | jq -c .)"
            
            execution_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "apply_config",
                "recommendation": recommendation,
                "status": "success"
            }
            
            self.execution_log.append(execution_record)
            
            return {"success": True, "execution_record": execution_record}
            
        except Exception as e:
            error_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "apply_config",
                "recommendation": recommendation,
                "status": "failed",
                "error": str(e)
            }
            
            self.execution_log.append(error_record)
            
            return {"success": False, "error": str(e), "execution_record": error_record}
    
    def rollback_config(self, previous_config):
        """回滚配置"""
        try:
            # 执行配置回滚
            print(f"Rolling back to previous configuration: {previous_config}")
            
            rollback_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "rollback_config",
                "previous_config": previous_config,
                "status": "success"
            }
            
            self.execution_log.append(rollback_record)
            
            return {"success": True, "rollback_record": rollback_record}
            
        except Exception as e:
            error_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "rollback_config",
                "previous_config": previous_config,
                "status": "failed",
                "error": str(e)
            }
            
            self.execution_log.append(error_record)
            
            return {"success": False, "error": str(e), "rollback_record": error_record}

# 使用示例
# executor = ConfigAutomationExecutor()
# recommendation = {"thread_pool_size": 20, "cache_size": 200}
# result = executor.apply_config_recommendation(recommendation)
EOF
    
    echo "Automation execution mechanisms set up"
}

# 使用示例
# ai_config_platform
```

## 机器学习驱动的配置优化

机器学习技术为配置优化提供了强大的分析和预测能力，使得配置优化从基于经验和规则的方式转变为基于数据驱动的智能化方式。

### 1. 配置参数优化算法

```java
// MLConfigOptimizer.java
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;
import org.apache.commons.math3.optim.*;
import org.apache.commons.math3.optim.linear.*;
import org.apache.commons.math3.optim.nonlinear.scalar.GoalType;

public class MLConfigOptimizer {
    private final Map<String, ConfigParameter> parameters;
    private final List<PerformanceRecord> history;
    private final ExecutorService executor;
    
    public MLConfigOptimizer() {
        this.parameters = new ConcurrentHashMap<>();
        this.history = new ArrayList<>();
        this.executor = Executors.newFixedThreadPool(4);
    }
    
    public static class ConfigParameter {
        private final String name;
        private final double minValue;
        private final double maxValue;
        private final double defaultValue;
        private final String description;
        
        public ConfigParameter(String name, double minValue, double maxValue, 
                             double defaultValue, String description) {
            this.name = name;
            this.minValue = minValue;
            this.maxValue = maxValue;
            this.defaultValue = defaultValue;
            this.description = description;
        }
        
        // Getters
        public String getName() { return name; }
        public double getMinValue() { return minValue; }
        public double getMaxValue() { return maxValue; }
        public double getDefaultValue() { return defaultValue; }
        public String getDescription() { return description; }
    }
    
    public static class PerformanceRecord {
        private final Map<String, Double> config;
        private final double performanceScore;
        private final long timestamp;
        private final Map<String, Object> metrics;
        
        public PerformanceRecord(Map<String, Double> config, double performanceScore, 
                               Map<String, Object> metrics) {
            this.config = config;
            this.performanceScore = performanceScore;
            this.timestamp = System.currentTimeMillis();
            this.metrics = metrics;
        }
        
        // Getters
        public Map<String, Double> getConfig() { return config; }
        public double getPerformanceScore() { return performanceScore; }
        public long getTimestamp() { return timestamp; }
        public Map<String, Object> getMetrics() { return metrics; }
    }
    
    public void addParameter(String name, double minValue, double maxValue, 
                           double defaultValue, String description) {
        parameters.put(name, new ConfigParameter(name, minValue, maxValue, defaultValue, description));
    }
    
    public void recordPerformance(Map<String, Double> config, double performanceScore, 
                                Map<String, Object> metrics) {
        history.add(new PerformanceRecord(config, performanceScore, metrics));
    }
    
    public OptimizationResult optimizeConfiguration(GoalType goalType, 
                                                  Map<String, Object> constraints) {
        System.out.println("Starting configuration optimization...");
        
        try {
            // 准备优化数据
            List<double[]> featureMatrix = prepareFeatureMatrix();
            double[] targetVector = prepareTargetVector(goalType);
            
            if (featureMatrix.isEmpty() || targetVector.length == 0) {
                return new OptimizationResult(false, null, "Insufficient data for optimization");
            }
            
            // 执行优化
            Map<String, Double> optimalConfig = performOptimization(
                featureMatrix, targetVector, goalType, constraints
            );
            
            return new OptimizationResult(true, optimalConfig, "Optimization completed successfully");
            
        } catch (Exception e) {
            return new OptimizationResult(false, null, "Optimization failed: " + e.getMessage());
        }
    }
    
    private List<double[]> prepareFeatureMatrix() {
        List<double[]> features = new ArrayList<>();
        
        for (PerformanceRecord record : history) {
            double[] row = new double[parameters.size()];
            int i = 0;
            for (ConfigParameter param : parameters.values()) {
                Double value = record.getConfig().get(param.getName());
                row[i++] = value != null ? value : param.getDefaultValue();
            }
            features.add(row);
        }
        
        return features;
    }
    
    private double[] prepareTargetVector(GoalType goalType) {
        return history.stream()
            .mapToDouble(record -> goalType == GoalType.MINIMIZE ? 
                         record.getPerformanceScore() : 
                         -record.getPerformanceScore())
            .toArray();
    }
    
    private Map<String, Double> performOptimization(List<double[]> features, 
                                                  double[] targets, 
                                                  GoalType goalType,
                                                  Map<String, Object> constraints) {
        // 简化的线性回归优化（实际应用中会使用更复杂的算法）
        Map<String, Double> optimalConfig = new HashMap<>();
        
        // 计算每个参数与性能的相关性
        for (int paramIndex = 0; paramIndex < parameters.size(); paramIndex++) {
            ConfigParameter param = new ArrayList<>(parameters.values()).get(paramIndex);
            
            // 计算相关系数
            double correlation = calculateCorrelation(
                features.stream().mapToDouble(row -> row[paramIndex]).toArray(),
                targets
            );
            
            // 基于相关性调整参数值
            double optimalValue;
            if (correlation > 0.5) {
                // 正相关，最大化参数值
                optimalValue = goalType == GoalType.MINIMIZE ? 
                              param.getMinValue() : param.getMaxValue();
            } else if (correlation < -0.5) {
                // 负相关，最小化参数值
                optimalValue = goalType == GoalType.MINIMIZE ? 
                              param.getMaxValue() : param.getMinValue();
            } else {
                // 弱相关，使用默认值
                optimalValue = param.getDefaultValue();
            }
            
            // 应用约束
            if (constraints != null && constraints.containsKey(param.getName())) {
                @SuppressWarnings("unchecked")
                Map<String, Double> paramConstraints = 
                    (Map<String, Double>) constraints.get(param.getName());
                Double minConstraint = paramConstraints.get("min");
                Double maxConstraint = paramConstraints.get("max");
                
                if (minConstraint != null) {
                    optimalValue = Math.max(optimalValue, minConstraint);
                }
                if (maxConstraint != null) {
                    optimalValue = Math.min(optimalValue, maxConstraint);
                }
            }
            
            optimalConfig.put(param.getName(), optimalValue);
        }
        
        return optimalConfig;
    }
    
    private double calculateCorrelation(double[] x, double[] y) {
        if (x.length != y.length || x.length == 0) {
            return 0.0;
        }
        
        double meanX = Arrays.stream(x).average().orElse(0.0);
        double meanY = Arrays.stream(y).average().orElse(0.0);
        
        double numerator = 0.0;
        double denomX = 0.0;
        double denomY = 0.0;
        
        for (int i = 0; i < x.length; i++) {
            double diffX = x[i] - meanX;
            double diffY = y[i] - meanY;
            numerator += diffX * diffY;
            denomX += diffX * diffX;
            denomY += diffY * diffY;
        }
        
        if (denomX == 0.0 || denomY == 0.0) {
            return 0.0;
        }
        
        return numerator / Math.sqrt(denomX * denomY);
    }
    
    public void startContinuousOptimization(long intervalMs) {
        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
        
        scheduler.scheduleAtFixedRate(() -> {
            System.out.println("Performing continuous configuration optimization...");
            
            OptimizationResult result = optimizeConfiguration(
                GoalType.MINIMIZE, 
                new HashMap<>() // 无约束
            );
            
            if (result.isSuccess()) {
                System.out.println("Optimal configuration found: " + result.getOptimalConfig());
            } else {
                System.err.println("Optimization failed: " + result.getErrorMessage());
            }
        }, intervalMs, intervalMs, TimeUnit.MILLISECONDS);
    }
    
    // 结果类
    public static class OptimizationResult {
        private final boolean success;
        private final Map<String, Double> optimalConfig;
        private final String errorMessage;
        
        public OptimizationResult(boolean success, Map<String, Double> optimalConfig, 
                                String errorMessage) {
            this.success = success;
            this.optimalConfig = optimalConfig;
            this.errorMessage = errorMessage;
        }
        
        // Getters
        public boolean isSuccess() { return success; }
        public Map<String, Double> getOptimalConfig() { return optimalConfig; }
        public String getErrorMessage() { return errorMessage; }
    }
    
    // 使用示例
    // public static void main(String[] args) {
    //     MLConfigOptimizer optimizer = new MLConfigOptimizer();
    //     
    //     // 添加配置参数
    //     optimizer.addParameter("threadPoolSize", 1, 100, 10, "线程池大小");
    //     optimizer.addParameter("cacheSize", 10, 1000, 100, "缓存大小");
    //     optimizer.addParameter("timeout", 1, 300, 30, "超时时间");
    //     
    //     // 记录性能数据
    //     Map<String, Double> config1 = Map.of("threadPoolSize", 10.0, "cacheSize", 100.0, "timeout", 30.0);
    //     optimizer.recordPerformance(config1, 50.0, Map.of("cpu", 70, "memory", 60));
    //     
    //     Map<String, Double> config2 = Map.of("threadPoolSize", 20.0, "cacheSize", 200.0, "timeout", 25.0);
    //     optimizer.recordPerformance(config2, 30.0, Map.of("cpu", 80, "memory", 70));
    //     
    //     // 执行优化
    //     OptimizationResult result = optimizer.optimizeConfiguration(GoalType.MINIMIZE, null);
    //     if (result.isSuccess()) {
    //         System.out.println("Optimal configuration: " + result.getOptimalConfig());
    //     }
    // }
}
```

### 2. 强化学习配置优化

```python
# rl-config-optimizer.py
import numpy as np
import random
from collections import deque
import json
from typing import Dict, Any, List, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RLConfigOptimizer:
    def __init__(self, config_space: Dict[str, Dict[str, Any]], 
                 learning_rate: float = 0.1, discount_factor: float = 0.95, 
                 epsilon: float = 0.1):
        self.config_space = config_space
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        # Q表：状态-动作值函数
        self.q_table = {}
        
        # 经验回放缓冲区
        self.replay_buffer = deque(maxlen=10000)
        
        # 配置历史
        self.config_history = []
        
    def get_state(self, metrics: Dict[str, float]) -> str:
        """将性能指标转换为状态"""
        # 简化的状态表示
        cpu_state = self._discretize(metrics.get('cpu_usage', 0), [0, 30, 70, 100])
        memory_state = self._discretize(metrics.get('memory_usage', 0), [0, 50, 80, 100])
        response_state = self._discretize(metrics.get('response_time', 0), [0, 100, 500, 1000])
        
        return f"{cpu_state}_{memory_state}_{response_state}"
    
    def _discretize(self, value: float, thresholds: List[float]) -> int:
        """将连续值离散化"""
        for i, threshold in enumerate(thresholds):
            if value <= threshold:
                return i
        return len(thresholds) - 1
    
    def get_action_space(self, state: str) -> List[str]:
        """获取给定状态下的动作空间"""
        # 动作：增加/减少配置参数
        actions = []
        for param_name in self.config_space.keys():
            actions.append(f"increase_{param_name}")
            actions.append(f"decrease_{param_name}")
        return actions
    
    def select_action(self, state: str) -> str:
        """使用ε-贪婪策略选择动作"""
        if random.random() < self.epsilon:
            # 探索：随机选择动作
            actions = self.get_action_space(state)
            return random.choice(actions)
        else:
            # 利用：选择Q值最大的动作
            if state not in self.q_table:
                self.q_table[state] = {}
                
            actions = self.get_action_space(state)
            q_values = {action: self.q_table[state].get(action, 0) for action in actions}
            return max(q_values, key=q_values.get)
    
    def calculate_reward(self, current_metrics: Dict[str, float], 
                        previous_metrics: Dict[str, float]) -> float:
        """计算奖励"""
        # 奖励函数：性能改善获得正奖励，性能下降获得负奖励
        current_score = self._calculate_performance_score(current_metrics)
        previous_score = self._calculate_performance_score(previous_metrics)
        
        improvement = previous_score - current_score  # 分数越低越好
        
        # 基础奖励
        base_reward = improvement * 10
        
        # 惩罚过度调整
        adjustment_penalty = 0
        if abs(improvement) > 50:  # 过度调整
            adjustment_penalty = -5
        
        # 惩罚资源浪费
        resource_penalty = 0
        if current_metrics.get('cpu_usage', 0) > 90 or current_metrics.get('memory_usage', 0) > 90:
            resource_penalty = -10
            
        return base_reward + adjustment_penalty + resource_penalty
    
    def _calculate_performance_score(self, metrics: Dict[str, float]) -> float:
        """计算综合性能分数"""
        # 加权综合分数
        cpu_weight = 0.3
        memory_weight = 0.2
        response_weight = 0.5
        
        cpu_score = metrics.get('cpu_usage', 0) / 100
        memory_score = metrics.get('memory_usage', 0) / 100
        response_score = min(metrics.get('response_time', 0) / 1000, 1.0)
        
        return (cpu_score * cpu_weight + 
                memory_score * memory_weight + 
                response_score * response_weight) * 100
    
    def update_q_value(self, state: str, action: str, reward: float, 
                      next_state: str, done: bool):
        """更新Q值"""
        if state not in self.q_table:
            self.q_table[state] = {}
        if next_state not in self.q_table:
            self.q_table[next_state] = {}
            
        # 当前Q值
        current_q = self.q_table[state].get(action, 0)
        
        # 下一状态的最大Q值
        if done:
            next_max_q = 0
        else:
            next_actions = self.get_action_space(next_state)
            next_max_q = max([self.q_table[next_state].get(a, 0) for a in next_actions])
        
        # Q学习更新公式
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * next_max_q - current_q
        )
        
        self.q_table[state][action] = new_q
        
        # 存储到经验回放缓冲区
        self.replay_buffer.append((state, action, reward, next_state, done))
    
    def apply_action_to_config(self, config: Dict[str, Any], action: str) -> Dict[str, Any]:
        """将动作应用到配置"""
        new_config = config.copy()
        
        if action.startswith("increase_"):
            param_name = action[9:]  # 去掉"increase_"前缀
            if param_name in self.config_space:
                param_info = self.config_space[param_name]
                current_value = new_config.get(param_name, param_info['default'])
                max_value = param_info['max']
                step = param_info.get('step', 1)
                
                new_config[param_name] = min(current_value + step, max_value)
                
        elif action.startswith("decrease_"):
            param_name = action[9:]  # 去掉"decrease_"前缀
            if param_name in self.config_space:
                param_info = self.config_space[param_name]
                current_value = new_config.get(param_name, param_info['default'])
                min_value = param_info['min']
                step = param_info.get('step', 1)
                
                new_config[param_name] = max(current_value - step, min_value)
                
        return new_config
    
    def train_from_replay_buffer(self, batch_size: int = 32):
        """从经验回放缓冲区训练"""
        if len(self.replay_buffer) < batch_size:
            return
            
        # 随机采样一批经验
        batch = random.sample(self.replay_buffer, batch_size)
        
        for state, action, reward, next_state, done in batch:
            self.update_q_value(state, action, reward, next_state, done)
    
    def optimize_configuration(self, initial_config: Dict[str, Any], 
                             metrics_history: List[Dict[str, float]], 
                             episodes: int = 100) -> Dict[str, Any]:
        """优化配置"""
        current_config = initial_config.copy()
        
        for episode in range(episodes):
            logger.info(f"Episode {episode + 1}/{episodes}")
            
            # 获取当前状态
            if len(metrics_history) > 0:
                current_metrics = metrics_history[-1]
                current_state = self.get_state(current_metrics)
            else:
                current_state = "0_0_0"  # 初始状态
                
            # 选择动作
            action = self.select_action(current_state)
            
            # 应用动作到配置
            new_config = self.apply_action_to_config(current_config, action)
            
            # 模拟执行新配置并获取性能指标（在实际应用中需要真实执行）
            # 这里简化为基于动作的奖励计算
            reward = self._simulate_reward(action, current_config, new_config)
            
            # 获取下一状态
            next_metrics = self._simulate_metrics(new_config)
            next_state = self.get_state(next_metrics)
            
            # 更新Q值
            self.update_q_value(current_state, action, reward, next_state, False)
            
            # 从经验回放训练
            if episode % 10 == 0:
                self.train_from_replay_buffer()
            
            # 更新配置和指标历史
            current_config = new_config
            metrics_history.append(next_metrics)
            
            logger.info(f"Action: {action}, Reward: {reward:.2f}")
        
        return current_config
    
    def _simulate_reward(self, action: str, old_config: Dict[str, Any], 
                        new_config: Dict[str, Any]) -> float:
        """模拟奖励计算"""
        # 简化的奖励模拟
        param_changes = 0
        for key in old_config:
            if old_config[key] != new_config.get(key, old_config[key]):
                param_changes += 1
                
        # 奖励参数调整
        base_reward = param_changes * 2
        
        # 根据动作类型调整奖励
        if "increase" in action:
            base_reward += 1
        else:
            base_reward -= 1
            
        return base_reward
    
    def _simulate_metrics(self, config: Dict[str, Any]) -> Dict[str, float]:
        """模拟性能指标"""
        # 简化的指标模拟
        return {
            'cpu_usage': random.uniform(20, 90),
            'memory_usage': random.uniform(30, 85),
            'response_time': random.uniform(50, 500),
            'error_rate': random.uniform(0, 0.05)
        }
    
    def get_optimal_policy(self) -> Dict[str, str]:
        """获取最优策略"""
        policy = {}
        for state in self.q_table:
            actions = self.get_action_space(state)
            q_values = {action: self.q_table[state].get(action, 0) for action in actions}
            policy[state] = max(q_values, key=q_values.get)
        return policy

# 使用示例
# 定义配置空间
config_space = {
    'thread_pool_size': {
        'min': 1,
        'max': 100,
        'default': 10,
        'step': 5
    },
    'cache_size': {
        'min': 10,
        'max': 1000,
        'default': 100,
        'step': 50
    },
    'timeout': {
        'min': 1,
        'max': 300,
        'default': 30,
        'step': 5
    }
}

# 创建优化器
# optimizer = RLConfigOptimizer(config_space)

# 初始配置
# initial_config = {
#     'thread_pool_size': 10,
#     'cache_size': 100,
#     'timeout': 30
# }

# 性能指标历史
# metrics_history = [
#     {'cpu_usage': 70, 'memory_usage': 60, 'response_time': 150, 'error_rate': 0.01}
# ]

# 执行优化
# optimal_config = optimizer.optimize_configuration(initial_config, metrics_history, episodes=50)
# print("Optimal configuration:", optimal_config)
```

## 智能异常检测和预测性维护

智能化运维的一个重要方面是能够提前检测配置异常并进行预测性维护，防患于未然。

### 1. 异常检测系统

```yaml
# anomaly-detection-system.yaml
---
anomaly_detection_system:
  # 检测器类型
  detectors:
    statistical_detector:
      description: "基于统计的异常检测"
      algorithm: "Z-Score/Modified Z-Score"
      features:
        - "配置参数值变化"
        - "性能指标异常"
        - "资源使用率突变"
        
    ml_detector:
      description: "基于机器学习的异常检测"
      algorithm: "孤立森林/One-Class SVM"
      features:
        - "多维配置特征"
        - "历史行为模式"
        - "上下文相关信息"
        
    rule_based_detector:
      description: "基于规则的异常检测"
      algorithm: "专家规则/阈值检测"
      features:
        - "配置合规性检查"
        - "安全策略验证"
        - "最佳实践匹配"
        
  # 检测流程
  detection_pipeline:
    data_collection:
      sources:
        - "配置变更日志"
        - "性能监控数据"
        - "系统日志"
        - "安全事件日志"
        
    feature_engineering:
      steps:
        - "数据清洗和预处理"
        - "特征提取和转换"
        - "特征选择和降维"
        - "特征标准化"
        
    anomaly_scoring:
      methods:
        - "概率评分"
        - "距离评分"
        - "密度评分"
        - "集成评分"
        
    alert_generation:
      thresholds:
        - "低风险: 0.3-0.6"
        - "中风险: 0.6-0.8"
        - "高风险: 0.8-1.0"
        
  # 响应机制
  response_mechanisms:
    automatic_response:
      actions:
        - "配置回滚"
        - "服务隔离"
        - "资源调整"
        - "通知相关人员"
        
    manual_review:
      workflow:
        - "异常确认"
        - "根本原因分析"
        - "修复方案制定"
        - "变更实施"
```

### 2. 预测性维护系统

```go
// predictive-maintenance.go
package main

import (
    "context"
    "fmt"
    "log"
    "time"
    "math"
    "sort"
    "github.com/gonum/stat"
)

type PredictiveMaintenanceSystem struct {
    configHistory     []ConfigRecord
    performanceData   []PerformanceRecord
    predictionModels  map[string]PredictionModel
    alertThresholds   AlertThresholds
}

type ConfigRecord struct {
    Timestamp    time.Time
    Config       map[string]interface{}
    ChangeType   string  // create, update, delete
    ChangedBy    string
}

type PerformanceRecord struct {
    Timestamp    time.Time
    Metrics      map[string]float64
    ConfigState  map[string]interface{}
    Anomalies    []Anomaly
}

type Anomaly struct {
    Type        string
    Severity    string
    Description string
    Timestamp   time.Time
}

type PredictionModel interface {
    Predict(data []float64) (float64, error)
    Train(data [][]float64, targets []float64) error
}

type AlertThresholds struct {
    Critical float64 `json:"critical"`
    Warning  float64 `json:"warning"`
    Info     float64 `json:"info"`
}

type MaintenancePrediction struct {
    ConfigParam     string
    PredictedIssue  string
    Probability     float64
    TimeToFailure   time.Duration
    RecommendedAction string
}

func NewPredictiveMaintenanceSystem() *PredictiveMaintenanceSystem {
    return &PredictiveMaintenanceSystem{
        configHistory:    make([]ConfigRecord, 0),
        performanceData:  make([]PerformanceRecord, 0),
        predictionModels: make(map[string]PredictionModel),
        alertThresholds:  AlertThresholds{Critical: 0.9, Warning: 0.7, Info: 0.5},
    }
}

func (pms *PredictiveMaintenanceSystem) AddConfigRecord(record ConfigRecord) {
    pms.configHistory = append(pms.configHistory, record)
    
    // 保持历史记录在合理范围内
    if len(pms.configHistory) > 10000 {
        pms.configHistory = pms.configHistory[len(pms.configHistory)-5000:]
    }
}

func (pms *PredictiveMaintenanceSystem) AddPerformanceRecord(record PerformanceRecord) {
    pms.performanceData = append(pms.performanceData, record)
    
    // 保持性能数据在合理范围内
    if len(pms.performanceData) > 10000 {
        pms.performanceData = pms.performanceData[len(pms.performanceData)-5000:]
    }
}

func (pms *PredictiveMaintenanceSystem) DetectAnomalies() []Anomaly {
    var anomalies []Anomaly
    
    if len(pms.performanceData) < 2 {
        return anomalies
    }
    
    // 检测性能指标异常
    latestMetrics := pms.performanceData[len(pms.performanceData)-1].Metrics
    historicalMetrics := pms.getHistoricalMetrics()
    
    for metricName, currentValue := range latestMetrics {
        if historicalValues, exists := historicalMetrics[metricName]; exists && len(historicalValues) > 10 {
            // 计算Z-Score
            mean := stat.Mean(historicalValues, nil)
            stdDev := stat.StdDev(historicalValues, nil)
            
            if stdDev > 0 {
                zScore := math.Abs(currentValue - mean) / stdDev
                
                // 根据Z-Score判断异常
                if zScore > 3.0 {
                    anomalies = append(anomalies, Anomaly{
                        Type:        "Performance Anomaly",
                        Severity:    "Critical",
                        Description: fmt.Sprintf("Metric %s shows abnormal value: %.2f (Z-Score: %.2f)", metricName, currentValue, zScore),
                        Timestamp:   time.Now(),
                    })
                } else if zScore > 2.0 {
                    anomalies = append(anomalies, Anomaly{
                        Type:        "Performance Warning",
                        Severity:    "Warning",
                        Description: fmt.Sprintf("Metric %s shows warning value: %.2f (Z-Score: %.2f)", metricName, currentValue, zScore),
                        Timestamp:   time.Now(),
                    })
                }
            }
        }
    }
    
    return anomalies
}

func (pms *PredictiveMaintenanceSystem) getHistoricalMetrics() map[string][]float64 {
    metrics := make(map[string][]float64)
    
    for _, record := range pms.performanceData {
        for metricName, value := range record.Metrics {
            metrics[metricName] = append(metrics[metricName], value)
        }
    }
    
    return metrics
}

func (pms *PredictiveMaintenanceSystem) PredictMaintenance() []MaintenancePrediction {
    var predictions []MaintenancePrediction
    
    if len(pms.performanceData) < 10 {
        return predictions
    }
    
    // 基于趋势分析预测维护需求
    trendPredictions := pms.analyzeTrends()
    predictions = append(predictions, trendPredictions...)
    
    // 基于机器学习模型预测
    mlPredictions := pms.predictWithML()
    predictions = append(predictions, mlPredictions...)
    
    // 基于配置变更频率预测
    configPredictions := pms.analyzeConfigChanges()
    predictions = append(predictions, configPredictions...)
    
    return predictions
}

func (pms *PredictiveMaintenanceSystem) analyzeTrends() []MaintenancePrediction {
    var predictions []MaintenancePrediction
    
    metrics := pms.getHistoricalMetrics()
    
    for metricName, values := range metrics {
        if len(values) < 10 {
            continue
        }
        
        // 计算线性趋势
        slope := pms.calculateLinearTrend(values)
        
        // 预测未来值
        currentValue := values[len(values)-1]
        predictedValue := currentValue + slope*10 // 预测10个时间点后
        
        // 判断是否需要维护
        if metricName == "error_rate" && predictedValue > 0.05 {
            predictions = append(predictions, MaintenancePrediction{
                ConfigParam:     "error_handling",
                PredictedIssue:  "Error rate will exceed threshold",
                Probability:     math.Min(predictedValue/0.1, 1.0),
                TimeToFailure:   time.Duration(10) * time.Hour, // 简化的时间预测
                RecommendedAction: "Review error handling configuration and increase retry limits",
            })
        } else if metricName == "response_time" && predictedValue > 1000 {
            predictions = append(predictions, MaintenancePrediction{
                ConfigParam:     "performance_tuning",
                PredictedIssue:  "Response time will exceed SLA",
                Probability:     math.Min(predictedValue/2000, 1.0),
                TimeToFailure:   time.Duration(8) * time.Hour,
                RecommendedAction: "Optimize thread pool configuration and cache settings",
            })
        }
    }
    
    return predictions
}

func (pms *PredictiveMaintenanceSystem) calculateLinearTrend(values []float64) float64 {
    n := len(values)
    if n < 2 {
        return 0
    }
    
    var sumX, sumY, sumXY, sumXX float64
    
    for i, value := range values {
        x := float64(i)
        sumX += x
        sumY += value
        sumXY += x * value
        sumXX += x * x
    }
    
    denominator := float64(n)*sumXX - sumX*sumX
    if denominator == 0 {
        return 0
    }
    
    slope := (float64(n)*sumXY - sumX*sumY) / denominator
    return slope
}

func (pms *PredictiveMaintenanceSystem) predictWithML() []MaintenancePrediction {
    // 简化的机器学习预测（实际应用中会使用更复杂的模型）
    var predictions []MaintenancePrediction
    
    // 基于历史数据的简单模式匹配
    if len(pms.performanceData) > 50 {
        recentIssues := pms.countRecentIssues()
        
        if recentIssues["memory_leak"] > 5 {
            predictions = append(predictions, MaintenancePrediction{
                ConfigParam:     "memory_management",
                PredictedIssue:  "Potential memory leak detected",
                Probability:     0.8,
                TimeToFailure:   time.Duration(24) * time.Hour,
                RecommendedAction: "Review garbage collection settings and memory allocation",
            })
        }
        
        if recentIssues["high_cpu"] > 10 {
            predictions = append(predictions, MaintenancePrediction{
                ConfigParam:     "cpu_optimization",
                PredictedIssue:  "CPU usage trending high",
                Probability:     0.7,
                TimeToFailure:   time.Duration(12) * time.Hour,
                RecommendedAction: "Optimize thread pool size and processing algorithms",
            })
        }
    }
    
    return predictions
}

func (pms *PredictiveMaintenanceSystem) countRecentIssues() map[string]int {
    issues := make(map[string]int)
    
    // 统计最近24小时的问题
    cutoffTime := time.Now().Add(-24 * time.Hour)
    
    for _, record := range pms.performanceData {
        if record.Timestamp.After(cutoffTime) {
            for _, anomaly := range record.Anomalies {
                issues[anomaly.Type]++
            }
        }
    }
    
    return issues
}

func (pms *PredictiveMaintenanceSystem) analyzeConfigChanges() []MaintenancePrediction {
    var predictions []MaintenancePrediction
    
    if len(pms.configHistory) < 10 {
        return predictions
    }
    
    // 分析配置变更频率
    changeFrequency := pms.calculateChangeFrequency()
    
    for param, frequency := range changeFrequency {
        if frequency > 5.0 { // 每天变更超过5次
            predictions = append(predictions, MaintenancePrediction{
                ConfigParam:     param,
                PredictedIssue:  "High configuration change frequency",
                Probability:     math.Min(frequency/10.0, 1.0),
                TimeToFailure:   time.Duration(72) * time.Hour,
                RecommendedAction: "Review configuration management process and consider parameter stabilization",
            })
        }
    }
    
    return predictions
}

func (pms *PredictiveMaintenanceSystem) calculateChangeFrequency() map[string]float64 {
    frequency := make(map[string]float64)
    
    if len(pms.configHistory) < 2 {
        return frequency
    }
    
    // 计算每个配置参数的变更频率（次/天）
    timeSpan := pms.configHistory[len(pms.configHistory)-1].Timestamp.Sub(
        pms.configHistory[0].Timestamp).Hours() / 24.0
    
    if timeSpan <= 0 {
        return frequency
    }
    
    // 统计各参数变更次数
    changeCount := make(map[string]int)
    for _, record := range pms.configHistory {
        for param := range record.Config {
            changeCount[param]++
        }
    }
    
    // 计算频率
    for param, count := range changeCount {
        frequency[param] = float64(count) / timeSpan
    }
    
    return frequency
}

func (pms *PredictiveMaintenanceSystem) StartMonitoring(ctx context.Context) {
    ticker := time.NewTicker(5 * time.Minute)
    defer ticker.Stop()
    
    for {
        select {
        case <-ctx.Done():
            log.Println("Predictive maintenance monitoring stopped")
            return
        case <-ticker.C:
            // 执行异常检测
            anomalies := pms.DetectAnomalies()
            if len(anomalies) > 0 {
                log.Printf("Detected %d anomalies", len(anomalies))
                for _, anomaly := range anomalies {
                    log.Printf("Anomaly: %s - %s (%s)", anomaly.Type, anomaly.Description, anomaly.Severity)
                }
            }
            
            // 执行预测性维护分析
            predictions := pms.PredictMaintenance()
            if len(predictions) > 0 {
                log.Printf("Generated %d maintenance predictions", len(predictions))
                for _, prediction := range predictions {
                    log.Printf("Prediction: %s - %s (Probability: %.2f)", 
                        prediction.ConfigParam, prediction.PredictedIssue, prediction.Probability)
                }
            }
        }
    }
}

// 使用示例
// func main() {
//     pms := NewPredictiveMaintenanceSystem()
//     
//     // 添加配置记录
//     pms.AddConfigRecord(ConfigRecord{
//         Timestamp: time.Now(),
//         Config: map[string]interface{}{
//             "thread_pool_size": 10,
//             "cache_size": 100,
//         },
//         ChangeType: "update",
//         ChangedBy: "admin",
//     })
//     
//     // 添加性能记录
//     pms.AddPerformanceRecord(PerformanceRecord{
//         Timestamp: time.Now(),
//         Metrics: map[string]float64{
//             "cpu_usage": 75.5,
//             "memory_usage": 62.3,
//             "response_time": 120.5,
//             "error_rate": 0.001,
//         },
//         ConfigState: map[string]interface{}{
//             "thread_pool_size": 10,
//             "cache_size": 100,
//         },
//     })
//     
//     // 启动监控
//     ctx, cancel := context.WithCancel(context.Background())
//     defer cancel()
//     
//     go pms.StartMonitoring(ctx)
//     
//     // 让程序运行一段时间
//     time.Sleep(10 * time.Minute)
// }
```

## 自主运维和自适应配置

自主运维和自适应配置代表了配置管理的未来发展方向，系统能够根据环境变化自动调整配置以维持最佳性能。

### 1. 自主配置管理系统

```python
# autonomous-config-manager.py
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutonomousConfigManager:
    def __init__(self, config_space: Dict[str, Any]):
        self.config_space = config_space
        self.current_config = {}
        self.config_history = []
        self.performance_metrics = []
        self.autonomous_mode = False
        self.optimization_goals = []
        self.safety_constraints = []
        
    def initialize_config(self, initial_config: Dict[str, Any]):
        """初始化配置"""
        self.current_config = initial_config.copy()
        self.config_history.append({
            'timestamp': datetime.now().isoformat(),
            'config': self.current_config.copy(),
            'change_reason': 'initialization',
            'performance_before': None,
            'performance_after': None
        })
        logger.info("Configuration initialized")
        
    def set_autonomous_mode(self, enabled: bool, goals: List[str] = None, 
                          constraints: List[str] = None):
        """设置自主运维模式"""
        self.autonomous_mode = enabled
        self.optimization_goals = goals or []
        self.safety_constraints = constraints or []
        logger.info(f"Autonomous mode {'enabled' if enabled else 'disabled'}")
        
    def add_performance_metric(self, metric_name: str, value: float, 
                             timestamp: datetime = None):
        """添加性能指标"""
        if timestamp is None:
            timestamp = datetime.now()
            
        self.performance_metrics.append({
            'name': metric_name,
            'value': value,
            'timestamp': timestamp.isoformat()
        })
        
        # 保持历史数据在合理范围内
        if len(self.performance_metrics) > 1000:
            self.performance_metrics = self.performance_metrics[-500:]
            
    def get_recent_performance(self, metric_name: str, 
                             time_window_minutes: int = 60) -> List[float]:
        """获取最近的性能指标"""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_metrics = [
            m['value'] for m in self.performance_metrics
            if m['name'] == metric_name and 
            datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        return recent_metrics
        
    def should_adjust_config(self) -> bool:
        """判断是否需要调整配置"""
        if not self.autonomous_mode:
            return False
            
        # 检查性能指标是否偏离目标
        for goal in self.optimization_goals:
            if goal == 'minimize_response_time':
                recent_response_times = self.get_recent_performance('response_time', 30)
                if len(recent_response_times) > 5:
                    avg_response_time = sum(recent_response_times) / len(recent_response_times)
                    if avg_response_time > 200:  # 响应时间超过200ms
                        return True
                        
            elif goal == 'maximize_throughput':
                recent_throughput = self.get_recent_performance('throughput', 30)
                if len(recent_throughput) > 5:
                    avg_throughput = sum(recent_throughput) / len(recent_throughput)
                    if avg_throughput < 1000:  # 吞吐量低于1000 req/s
                        return True
                        
        return False
        
    def adjust_configuration(self):
        """自动调整配置"""
        if not self.should_adjust_config():
            return
            
        logger.info("Adjusting configuration automatically...")
        
        # 记录调整前的性能
        performance_before = self.capture_current_performance()
        
        # 生成配置调整建议
        recommendations = self.generate_recommendations()
        
        # 应用最佳推荐
        if recommendations:
            best_recommendation = recommendations[0]  # 假设第一个是最好的
            self.apply_recommendation(best_recommendation)
            
            # 记录配置变更
            self.config_history.append({
                'timestamp': datetime.now().isoformat(),
                'config': self.current_config.copy(),
                'change_reason': f"autonomous_adjustment: {best_recommendation['reason']}",
                'performance_before': performance_before,
                'performance_after': None  # 将在后续更新
            })
            
            logger.info(f"Configuration adjusted: {best_recommendation['changes']}")
            
    def capture_current_performance(self) -> Dict[str, Any]:
        """捕获当前性能指标"""
        metrics = {}
        for goal in self.optimization_goals:
            if 'response_time' in goal:
                recent_times = self.get_recent_performance('response_time', 5)
                if recent_times:
                    metrics['response_time'] = sum(recent_times) / len(recent_times)
            elif 'throughput' in goal:
                recent_throughput = self.get_recent_performance('throughput', 5)
                if recent_throughput:
                    metrics['throughput'] = sum(recent_throughput) / len(recent_throughput)
        return metrics
        
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """生成配置调整推荐"""
        recommendations = []
        
        # 基于性能目标生成推荐
        for goal in self.optimization_goals:
            if goal == 'minimize_response_time':
                # 如果响应时间过长，推荐增加线程池大小
                current_thread_pool = self.current_config.get('thread_pool_size', 10)
                if current_thread_pool < self.config_space['thread_pool_size']['max']:
                    recommendations.append({
                        'changes': {'thread_pool_size': min(current_thread_pool + 5, 
                                                          self.config_space['thread_pool_size']['max'])},
                        'reason': 'Increase thread pool size to reduce response time',
                        'expected_improvement': '10-20% response time reduction'
                    })
                    
            elif goal == 'maximize_throughput':
                # 如果吞吐量不足，推荐增加缓存大小
                current_cache = self.current_config.get('cache_size', 100)
                if current_cache < self.config_space['cache_size']['max']:
                    recommendations.append({
                        'changes': {'cache_size': min(current_cache + 50,
                                                    self.config_space['cache_size']['max'])},
                        'reason': 'Increase cache size to improve throughput',
                        'expected_improvement': '15-25% throughput increase'
                    })
                    
        return recommendations
        
    def apply_recommendation(self, recommendation: Dict[str, Any]):
        """应用配置推荐"""
        changes = recommendation['changes']
        for param, value in changes.items():
            if param in self.config_space:
                # 检查安全约束
                if self.is_safe_to_change(param, value):
                    self.current_config[param] = value
                    logger.info(f"Applied configuration change: {param} = {value}")
                else:
                    logger.warning(f"Configuration change rejected due to safety constraints: {param} = {value}")
                    
    def is_safe_to_change(self, param: str, value: Any) -> bool:
        """检查配置变更是否安全"""
        # 检查基本约束
        if param in self.config_space:
            param_info = self.config_space[param]
            if 'min' in param_info and value < param_info['min']:
                return False
            if 'max' in param_info and value > param_info['max']:
                return False
                
        # 检查自定义安全约束
        for constraint in self.safety_constraints:
            if not self.evaluate_constraint(constraint, {param: value}):
                return False
                
        return True
        
    def evaluate_constraint(self, constraint: str, config_changes: Dict[str, Any]) -> bool:
        """评估安全约束"""
        # 简化的约束评估（实际应用中会更复杂）
        try:
            # 这里可以实现更复杂的约束逻辑
            # 例如：资源使用不超过限制、配置参数间的依赖关系等
            return True
        except Exception as e:
            logger.error(f"Error evaluating constraint: {e}")
            return False
            
    async def start_autonomous_loop(self, interval_seconds: int = 300):
        """启动自主运维循环"""
        logger.info("Starting autonomous configuration management loop...")
        
        while True:
            try:
                if self.autonomous_mode:
                    self.adjust_configuration()
                    
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in autonomous loop: {e}")
                await asyncio.sleep(60)  # 出错时等待更长时间
                
    def get_config_status(self) -> Dict[str, Any]:
        """获取配置状态"""
        return {
            'current_config': self.current_config,
            'autonomous_mode': self.autonomous_mode,
            'optimization_goals': self.optimization_goals,
            'safety_constraints': self.safety_constraints,
            'config_history_count': len(self.config_history),
            'performance_metrics_count': len(self.performance_metrics)
        }

# 使用示例
# 配置空间定义
config_space = {
    'thread_pool_size': {
        'min': 1,
        'max': 100,
        'default': 10
    },
    'cache_size': {
        'min': 10,
        'max': 1000,
        'default': 100
    },
    'timeout': {
        'min': 1,
        'max': 300,
        'default': 30
    }
}

# 创建自主配置管理器
# acm = AutonomousConfigManager(config_space)

# 初始化配置
# acm.initialize_config({
#     'thread_pool_size': 10,
#     'cache_size': 100,
#     'timeout': 30
# })

# 设置自主运维模式
# acm.set_autonomous_mode(
#     enabled=True,
#     goals=['minimize_response_time', 'maximize_throughput'],
#     constraints=['total_memory_usage < 80%']
# )

# 添加性能指标
# acm.add_performance_metric('response_time', 250.0)
# acm.add_performance_metric('throughput', 800.0)

# 启动自主运维循环
# asyncio.run(acm.start_autonomous_loop(interval_seconds=60))
```

### 2. 自适应配置控制器

```bash
# adaptive-config-controller.sh

# 自适应配置控制器脚本
adaptive_config_controller() {
    echo "Initializing adaptive configuration controller..."
    
    # 1. 设置监控和检测机制
    echo "1. Setting up monitoring and detection..."
    setup_monitoring_detection
    
    # 2. 实现自适应调整逻辑
    echo "2. Implementing adaptive adjustment logic..."
    implement_adaptive_logic
    
    # 3. 配置安全和回滚机制
    echo "3. Setting up safety and rollback mechanisms..."
    setup_safety_rollback
    
    # 4. 启动控制器
    echo "4. Starting controller..."
    start_controller
    
    echo "Adaptive configuration controller initialized"
}

# 设置监控和检测机制
setup_monitoring_detection() {
    echo "Setting up monitoring and detection mechanisms..."
    
    # 创建性能指标收集脚本
    cat > collect-metrics.sh << 'EOF'
#!/bin/bash

# 性能指标收集脚本
METRICS_DIR="/var/lib/adaptive-config/metrics"
mkdir -p $METRICS_DIR

TIMESTAMP=$(date -Iseconds)

# 收集系统指标
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.2f", $3*100/$2 }')
LOAD_AVERAGE=$(uptime | awk -F'load average:' '{print $2}' | cut -d',' -f1 | tr -d ' ')

# 收集应用指标（示例）
RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:8080/health)
THROUGHPUT=$(curl -s http://localhost:8080/metrics | grep "http_requests_total" | awk '{print $2}')

# 保存指标
cat > $METRICS_DIR/metrics-$TIMESTAMP.json << EOF
{
    "timestamp": "$TIMESTAMP",
    "system": {
        "cpu_usage": $CPU_USAGE,
        "memory_usage": $MEMORY_USAGE,
        "load_average": $LOAD_AVERAGE
    },
    "application": {
        "response_time": $RESPONSE_TIME,
        "throughput": $THROUGHPUT
    }
}
EOF

echo "Metrics collected at $TIMESTAMP"
EOF
    
    chmod +x collect-metrics.sh
    
    # 设置定时收集任务
    echo "*/5 * * * * /path/to/collect-metrics.sh" | crontab -
    
    # 创建异常检测脚本
    cat > detect-anomalies.py << 'EOF'
#!/usr/bin/env python3

import json
import os
import numpy as np
from datetime import datetime, timedelta
import glob

class AnomalyDetector:
    def __init__(self, metrics_dir="/var/lib/adaptive-config/metrics"):
        self.metrics_dir = metrics_dir
        self.thresholds = {
            'cpu_usage': 80,
            'memory_usage': 85,
            'response_time': 2.0,  # 秒
            'load_average': 5.0
        }
        
    def detect_anomalies(self):
        """检测异常"""
        # 获取最近的指标文件
        metrics_files = glob.glob(os.path.join(self.metrics_dir, "metrics-*.json"))
        metrics_files.sort(reverse=True)
        
        if not metrics_files:
            return []
            
        # 分析最近30分钟的数据
        cutoff_time = datetime.now() - timedelta(minutes=30)
        recent_metrics = []
        
        for file_path in metrics_files[:50]:  # 最多分析50个文件
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                timestamp = datetime.fromisoformat(data['timestamp'])
                if timestamp > cutoff_time:
                    recent_metrics.append(data)
                else:
                    break
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                
        if len(recent_metrics) < 5:
            return []
            
        anomalies = []
        
        # 检测CPU使用率异常
        cpu_values = [m['system']['cpu_usage'] for m in recent_metrics]
        if np.mean(cpu_values) > self.thresholds['cpu_usage']:
            anomalies.append({
                'type': 'high_cpu_usage',
                'severity': 'warning',
                'value': np.mean(cpu_values),
                'threshold': self.thresholds['cpu_usage'],
                'timestamp': datetime.now().isoformat()
            })
            
        # 检测内存使用率异常
        memory_values = [m['system']['memory_usage'] for m in recent_metrics]
        if np.mean(memory_values) > self.thresholds['memory_usage']:
            anomalies.append({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'value': np.mean(memory_values),
                'threshold': self.thresholds['memory_usage'],
                'timestamp': datetime.now().isoformat()
            })
            
        # 检测响应时间异常
        response_values = [m['application']['response_time'] for m in recent_metrics if 'response_time' in m['application']]
        if response_values and np.mean(response_values) > self.thresholds['response_time']:
            anomalies.append({
                'type': 'high_response_time',
                'severity': 'critical',
                'value': np.mean(response_values),
                'threshold': self.thresholds['response_time'],
                'timestamp': datetime.now().isoformat()
            })
            
        return anomalies

# 使用示例
# detector = AnomalyDetector()
# anomalies = detector.detect_anomalies()
# if anomalies:
#     print("Detected anomalies:")
#     for anomaly in anomalies:
#         print(f"  {anomaly['type']}: {anomaly['value']} > {anomaly['threshold']}")
EOF
    
    echo "Monitoring and detection mechanisms set up"
}

# 实现自适应调整逻辑
implement_adaptive_logic() {
    echo "Implementing adaptive adjustment logic..."
    
    # 创建配置调整脚本
    cat > adjust-configuration.py << 'EOF'
#!/usr/bin/env python3

import json
import subprocess
import os
from typing import Dict, Any

class AdaptiveAdjuster:
    def __init__(self):
        self.config_file = "/app/config/application.json"
        self.backup_dir = "/var/lib/adaptive-config/backups"
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def adjust_for_high_cpu(self, current_cpu: float):
        """针对高CPU使用率的调整"""
        print(f"Adjusting for high CPU usage: {current_cpu}%")
        
        # 备份当前配置
        self.backup_config()
        
        # 读取当前配置
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            
        # 调整线程池大小
        if 'thread_pool_size' in config:
            current_threads = config['thread_pool_size']
            new_threads = max(1, int(current_threads * 0.8))  # 减少20%
            config['thread_pool_size'] = new_threads
            print(f"Reduced thread pool size from {current_threads} to {new_threads}")
            
        # 保存调整后的配置
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        # 通知应用重新加载配置
        self.reload_application()
        
    def adjust_for_high_memory(self, current_memory: float):
        """针对高内存使用率的调整"""
        print(f"Adjusting for high memory usage: {current_memory}%")
        
        # 备份当前配置
        self.backup_config()
        
        # 读取当前配置
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            
        # 调整缓存大小
        if 'cache_size' in config:
            current_cache = config['cache_size']
            new_cache = max(10, int(current_cache * 0.7))  # 减少30%
            config['cache_size'] = new_cache
            print(f"Reduced cache size from {current_cache} to {new_cache}")
            
        # 保存调整后的配置
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        # 通知应用重新加载配置
        self.reload_application()
        
    def adjust_for_high_response_time(self, current_response: float):
        """针对高响应时间的调整"""
        print(f"Adjusting for high response time: {current_response}s")
        
        # 备份当前配置
        self.backup_config()
        
        # 读取当前配置
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            
        # 增加线程池大小
        if 'thread_pool_size' in config:
            current_threads = config['thread_pool_size']
            new_threads = min(100, int(current_threads * 1.2))  # 增加20%
            config['thread_pool_size'] = new_threads
            print(f"Increased thread pool size from {current_threads} to {new_threads}")
            
        # 优化超时设置
        if 'timeout' in config:
            current_timeout = config['timeout']
            new_timeout = min(300, int(current_timeout * 1.1))  # 增加10%
            config['timeout'] = new_timeout
            print(f"Increased timeout from {current_timeout} to {new_timeout}")
            
        # 保存调整后的配置
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        # 通知应用重新加载配置
        self.reload_application()
        
    def backup_config(self):
        """备份配置文件"""
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"config_backup_{timestamp}.json")
        shutil.copy2(self.config_file, backup_file)
        print(f"Configuration backed up to {backup_file}")
        
    def reload_application(self):
        """重新加载应用配置"""
        try:
            # 发送重载信号给应用
            subprocess.run(["curl", "-X", "POST", "http://localhost:8080/actuator/refresh"], 
                         check=True, capture_output=True)
            print("Application configuration reloaded")
        except subprocess.CalledProcessError as e:
            print(f"Failed to reload application: {e}")
            
    def rollback_config(self):
        """回滚配置"""
        import glob
        
        # 找到最新的备份
        backup_files = glob.glob(os.path.join(self.backup_dir, "config_backup_*.json"))
        if not backup_files:
            print("No backup files found")
            return
            
        backup_files.sort(reverse=True)
        latest_backup = backup_files[0]
        
        # 恢复配置
        import shutil
        shutil.copy2(latest_backup, self.config_file)
        print(f"Configuration rolled back to {latest_backup}")
        
        # 重新加载应用
        self.reload_application()

# 使用示例
# adjuster = AdaptiveAdjuster()
# adjuster.adjust_for_high_cpu(85.5)
EOF
    
    echo "Adaptive adjustment logic implemented"
}

# 设置安全和回滚机制
setup_safety_rollback() {
    echo "Setting up safety and rollback mechanisms..."
    
    # 创建安全检查脚本
    cat > safety-check.sh << 'EOF'
#!/bin/bash

# 安全检查脚本
CONFIG_FILE="/app/config/application.json"
BACKUP_DIR="/var/lib/adaptive-config/backups"

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# 检查配置文件是否为有效的JSON
if ! jq empty "$CONFIG_FILE" 2>/dev/null; then
    echo "ERROR: Configuration file is not valid JSON"
    exit 1
fi

# 检查关键配置参数是否存在
REQUIRED_PARAMS=("thread_pool_size" "cache_size" "timeout")
for param in "${REQUIRED_PARAMS[@]}"; do
    if ! jq -e ".${param}" "$CONFIG_FILE" >/dev/null 2>&1; then
        echo "ERROR: Required parameter $param not found in configuration"
        exit 1
    fi
done

# 检查参数值是否在合理范围内
THREAD_POOL_SIZE=$(jq -r ".thread_pool_size" "$CONFIG_FILE")
if [ "$THREAD_POOL_SIZE" -lt 1 ] || [ "$THREAD_POOL_SIZE" -gt 1000 ]; then
    echo "ERROR: Invalid thread pool size: $THREAD_POOL_SIZE"
    exit 1
fi

CACHE_SIZE=$(jq -r ".cache_size" "$CONFIG_FILE")
if [ "$CACHE_SIZE" -lt 1 ] || [ "$CACHE_SIZE" -gt 10000 ]; then
    echo "ERROR: Invalid cache size: $CACHE_SIZE"
    exit 1
fi

TIMEOUT=$(jq -r ".timeout" "$CONFIG_FILE")
if [ "$TIMEOUT" -lt 1 ] || [ "$TIMEOUT" -gt 3600 ]; then
    echo "ERROR: Invalid timeout: $TIMEOUT"
    exit 1
fi

echo "Configuration safety check passed"
exit 0
EOF
    
    chmod +x safety-check.sh
    
    # 创建自动回滚脚本
    cat > auto-rollback.sh << 'EOF'
#!/bin/bash

# 自动回滚脚本
CONFIG_FILE="/app/config/application.json"
BACKUP_DIR="/var/lib/adaptive-config/backups"
HEALTH_CHECK_URL="http://localhost:8080/health"

# 检查应用健康状态
if ! curl -s -f "$HEALTH_CHECK_URL" >/dev/null; then
    echo "Application is unhealthy, checking recent configuration changes..."
    
    # 检查最近的备份
    LATEST_BACKUP=$(ls -t $BACKUP_DIR/config_backup_*.json 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        echo "Rolling back to latest backup: $LATEST_BACKUP"
        
        # 恢复配置
        cp "$LATEST_BACKUP" "$CONFIG_FILE"
        
        # 重新加载应用
        curl -X POST "http://localhost:8080/actuator/refresh"
        
        echo "Rollback completed"
        
        # 发送告警通知
        echo "Configuration rollback performed due to application health check failure" | \
            mail -s "Configuration Rollback Alert" admin@example.com
    else
        echo "No backup found for rollback"
    fi
else
    echo "Application is healthy"
fi
EOF
    
    chmod +x auto-rollback.sh
    
    # 设置定期健康检查
    echo "*/10 * * * * /path/to/auto-rollback.sh" | crontab -
    
    echo "Safety and rollback mechanisms set up"
}

# 启动控制器
start_controller() {
    echo "Starting adaptive configuration controller..."
    
    # 创建主控制器脚本
    cat > adaptive-controller.py << 'EOF'
#!/usr/bin/env python3

import json
import subprocess
import time
import glob
from datetime import datetime
import os

class AdaptiveController:
    def __init__(self):
        self.metrics_dir = "/var/lib/adaptive-config/metrics"
        self.config_file = "/app/config/application.json"
        self.adjuster_script = "/path/to/adjust-configuration.py"
        self.safety_check_script = "/path/to/safety-check.sh"
        
    def run_controller_loop(self):
        """运行控制器循环"""
        print("Starting adaptive configuration controller loop...")
        
        while True:
            try:
                # 检测异常
                anomalies = self.detect_anomalies()
                
                if anomalies:
                    print(f"Detected {len(anomalies)} anomalies")
                    for anomaly in anomalies:
                        self.handle_anomaly(anomaly)
                        
                # 等待下一次检查
                time.sleep(300)  # 5分钟
                
            except KeyboardInterrupt:
                print("Controller stopped by user")
                break
            except Exception as e:
                print(f"Error in controller loop: {e}")
                time.sleep(60)  # 出错时等待1分钟
                
    def detect_anomalies(self):
        """检测异常"""
        # 获取最新的指标文件
        metrics_files = glob.glob(os.path.join(self.metrics_dir, "metrics-*.json"))
        if not metrics_files:
            return []
            
        metrics_files.sort(reverse=True)
        latest_file = metrics_files[0]
        
        try:
            with open(latest_file, 'r') as f:
                metrics = json.load(f)
                
            anomalies = []
            
            # 检查CPU使用率
            cpu_usage = metrics['system']['cpu_usage']
            if cpu_usage > 80:
                anomalies.append({
                    'type': 'high_cpu',
                    'value': cpu_usage,
                    'threshold': 80
                })
                
            # 检查内存使用率
            memory_usage = metrics['system']['memory_usage']
            if memory_usage > 85:
                anomalies.append({
                    'type': 'high_memory',
                    'value': memory_usage,
                    'threshold': 85
                })
                
            # 检查响应时间
            if 'application' in metrics and 'response_time' in metrics['application']:
                response_time = metrics['application']['response_time']
                if response_time > 2.0:
                    anomalies.append({
                        'type': 'high_response_time',
                        'value': response_time,
                        'threshold': 2.0
                    })
                    
            return anomalies
            
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return []
            
    def handle_anomaly(self, anomaly):
        """处理异常"""
        print(f"Handling anomaly: {anomaly['type']} = {anomaly['value']}")
        
        # 执行安全检查
        safety_result = subprocess.run([self.safety_check_script], capture_output=True)
        if safety_result.returncode != 0:
            print(f"Safety check failed: {safety_result.stderr.decode()}")
            return
            
        # 根据异常类型调整配置
        if anomaly['type'] == 'high_cpu':
            subprocess.run(["python3", self.adjuster_script, "high_cpu", str(anomaly['value'])])
        elif anomaly['type'] == 'high_memory':
            subprocess.run(["python3", self.adjuster_script, "high_memory", str(anomaly['value'])])
        elif anomaly['type'] == 'high_response_time':
            subprocess.run(["python3", self.adjuster_script, "high_response_time", str(anomaly['value'])])
            
        print(f"Configuration adjustment completed for {anomaly['type']}")

# 启动控制器
# controller = AdaptiveController()
# controller.run_controller_loop()
EOF
    
    echo "Controller started"
}

# 使用示例
# adaptive_config_controller
```

## 最佳实践总结

通过以上内容，我们可以总结出配置管理与智能化运维的最佳实践：

### 1. AI驱动的配置分析
- 利用机器学习算法分析配置与性能的关系
- 建立配置优化推荐系统
- 实施智能配置管理平台

### 2. 机器学习驱动的配置优化
- 使用强化学习算法进行配置优化
- 实施多目标优化策略
- 建立配置优化的反馈机制

### 3. 智能异常检测和预测性维护
- 实施多层次的异常检测机制
- 建立预测性维护系统
- 实施自动化的响应和修复机制

### 4. 自主运维和自适应配置
- 实施自主配置管理系统
- 建立自适应调整逻辑
- 实施安全约束和回滚机制

通过实施这些最佳实践，企业可以构建智能化的配置管理体系，实现配置管理的自动化、智能化和自适应化，为未来的IT运维奠定坚实基础。

在下一节中，我们将深入探讨无服务器架构对配置管理的影响，帮助您了解这一新兴架构模式下的配置管理挑战和解决方案。