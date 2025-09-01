---
title: 使用云原生工具管理配置：充分利用云平台原生服务
date: 2025-08-31
categories: [Configuration Management]
tags: [microservice-configuration-management]
published: true
---

# 17.3 使用云原生工具管理配置

云原生工具为配置管理提供了强大而灵活的解决方案，充分利用这些工具可以帮助企业实现更安全、更高效的配置管理。本节将深入探讨AWS Systems Manager、Azure App Configuration、Google Cloud Secret Manager等云原生工具的使用方法，并提供实际的操作示例和最佳实践。

## AWS Systems Manager配置管理

AWS Systems Manager是AWS提供的统一界面，用于查看和控制AWS基础设施，其中包括强大的配置管理功能。

### 1. Parameter Store使用详解

Parameter Store是Systems Manager的一个功能，用于分层存储配置数据和密文。

#### 基本操作

```python
# aws-parameter-store-manager.py
import boto3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSParameterStoreManager:
    def __init__(self, region_name: str = 'us-east-1'):
        self.region_name = region_name
        self.ssm_client = boto3.client('ssm', region_name=region_name)
        self.secrets_client = boto3.client('secretsmanager', region_name=region_name)
        
    def create_parameter(self, name: str, value: str, description: str = "", 
                        type: str = "String", tier: str = "Standard",
                        tags: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """创建参数"""
        try:
            params = {
                'Name': name,
                'Value': value,
                'Description': description,
                'Type': type,
                'Tier': tier,
                'Overwrite': True
            }
            
            # 添加标签（如果提供）
            if tags:
                params['Tags'] = tags
                
            response = self.ssm_client.put_parameter(**params)
            
            logger.info(f"Parameter {name} created successfully")
            return {
                'success': True,
                'parameter_name': name,
                'version': response['Version'],
                'tier': tier
            }
        except Exception as e:
            logger.error(f"Failed to create parameter {name}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def get_parameter(self, name: str, decrypt: bool = True) -> Dict[str, Any]:
        """获取参数"""
        try:
            response = self.ssm_client.get_parameter(
                Name=name,
                WithDecryption=decrypt
            )
            
            parameter = response['Parameter']
            return {
                'success': True,
                'name': parameter['Name'],
                'value': parameter['Value'],
                'type': parameter['Type'],
                'version': parameter['Version'],
                'last_modified': parameter['LastModifiedDate'].isoformat() if 'LastModifiedDate' in parameter else None
            }
        except Exception as e:
            logger.error(f"Failed to get parameter {name}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def get_parameters_by_path(self, path: str, recursive: bool = True, 
                              decrypt: bool = True) -> Dict[str, Any]:
        """根据路径获取参数"""
        try:
            parameters = []
            paginator = self.ssm_client.get_paginator('get_parameters_by_path')
            
            for page in paginator.paginate(
                Path=path,
                Recursive=recursive,
                WithDecryption=decrypt
            ):
                for param in page['Parameters']:
                    parameters.append({
                        'name': param['Name'],
                        'value': param['Value'],
                        'type': param['Type'],
                        'version': param['Version'],
                        'last_modified': param['LastModifiedDate'].isoformat() if 'LastModifiedDate' in param else None
                    })
                    
            return {
                'success': True,
                'parameters': parameters,
                'count': len(parameters)
            }
        except Exception as e:
            logger.error(f"Failed to get parameters by path {path}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def delete_parameter(self, name: str) -> Dict[str, Any]:
        """删除参数"""
        try:
            self.ssm_client.delete_parameter(Name=name)
            logger.info(f"Parameter {name} deleted successfully")
            return {
                'success': True,
                'parameter_name': name
            }
        except Exception as e:
            logger.error(f"Failed to delete parameter {name}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def create_secret_parameter(self, name: str, secret_value: str, 
                               description: str = "") -> Dict[str, Any]:
        """创建密文参数（使用Secrets Manager）"""
        try:
            # 首先在Secrets Manager中创建密钥
            secret_response = self.secrets_client.create_secret(
                Name=name.replace('/', '-').lstrip('-'),
                Description=description,
                SecretString=secret_value
            )
            
            # 然后在Parameter Store中创建引用
            param_response = self.ssm_client.put_parameter(
                Name=name,
                Value=f"{{resolve:secretsmanager:{secret_response['Name']}}}",
                Description=description,
                Type="String",
                Overwrite=True
            )
            
            return {
                'success': True,
                'secret_arn': secret_response['ARN'],
                'parameter_name': name,
                'parameter_version': param_response['Version']
            }
        except Exception as e:
            logger.error(f"Failed to create secret parameter {name}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# 使用示例
# param_manager = AWSParameterStoreManager()

# # 创建普通参数
# result = param_manager.create_parameter(
#     name="/myapp/prod/database/host",
#     value="prod-db.example.com",
#     description="Production database host",
#     type="String",
#     tags=[{'Key': 'Environment', 'Value': 'Production'}]
# )

# # 创建密文参数
# secret_result = param_manager.create_secret_parameter(
#     name="/myapp/prod/database/password",
#     secret_value="supersecretpassword",
#     description="Production database password"
# )

# # 获取参数
# param = param_manager.get_parameter("/myapp/prod/database/host")

# # 根据路径获取参数
# params = param_manager.get_parameters_by_path("/myapp/prod/")
```

### 2. 高级配置管理策略

```yaml
# aws-advanced-config-strategy.yaml
---
aws_advanced_config_strategy:
  # 参数命名规范
  parameter_naming:
    structure: "/{application}/{environment}/{component}/{parameter}"
    examples:
      - "/ecommerce/prod/database/host"
      - "/ecommerce/prod/database/port"
      - "/ecommerce/dev/cache/redis-host"
    best_practices:
      - "使用分层结构组织参数"
      - "避免在参数名中包含敏感信息"
      - "为不同环境使用不同的路径"
      
  # 参数类型选择
  parameter_types:
    string:
      description: "普通字符串参数"
      use_cases:
        - "数据库主机名"
        - "API端点"
        - "应用配置"
        
    string_list:
      description: "字符串列表参数"
      use_cases:
        - "允许的IP地址列表"
        - "功能开关列表"
        - "服务依赖列表"
        
    secure_string:
      description: "加密字符串参数"
      use_cases:
        - "数据库密码"
        - "API密钥"
        - "证书内容"
        
  # 参数层级管理
  parameter_hierarchy:
    tiers:
      standard:
        description: "标准层级"
        max_size: "4KB"
        cost: "低成本"
        use_cases: "大多数常规参数"
        
      advanced:
        description: "高级层级"
        max_size: "8KB"
        cost: "较高成本"
        use_cases: "大型配置文件、证书等"
        
      intelligent_tiering:
        description: "智能分层"
        max_size: "8KB"
        cost: "自动优化"
        use_cases: "不确定使用模式的参数"
```

### 3. AWS配置管理最佳实践脚本

```bash
# aws-config-best-practices.sh

# AWS配置管理最佳实践实施脚本
aws_config_best_practices() {
    echo "Implementing AWS configuration management best practices..."
    
    # 1. 参数命名规范实施
    echo "1. Implementing parameter naming conventions..."
    implement_aws_parameter_naming
    
    # 2. 访问控制策略设置
    echo "2. Setting up access control policies..."
    setup_aws_access_control
    
    # 3. 配置备份和恢复机制
    echo "3. Setting up configuration backup and recovery..."
    setup_aws_config_backup
    
    # 4. 监控和告警配置
    echo "4. Setting up monitoring and alerting..."
    setup_aws_config_monitoring
    
    echo "AWS configuration management best practices implemented"
}

# 实施参数命名规范
implement_aws_parameter_naming() {
    echo "Implementing AWS parameter naming conventions..."
    
    # 创建组织级参数
    aws ssm put-parameter --name "/organization/name" --value "MyCompany" --type "String"
    aws ssm put-parameter --name "/organization/department" --value "Engineering" --type "String"
    
    # 创建应用级参数模板
    cat > aws-parameter-template.json << EOF
{
    "parameters": [
        {
            "name": "/{app}/{env}/database/host",
            "type": "String",
            "description": "Database host for {app} in {env}"
        },
        {
            "name": "/{app}/{env}/database/port",
            "type": "String",
            "description": "Database port for {app} in {env}"
        },
        {
            "name": "/{app}/{env}/cache/host",
            "type": "String",
            "description": "Cache host for {app} in {env}"
        }
    ]
}
EOF
    
    echo "Parameter naming conventions implemented"
}

# 设置访问控制策略
setup_aws_access_control() {
    echo "Setting up AWS access control policies..."
    
    # 创建Parameter Store访问策略
    cat > parameter-store-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameter",
                "ssm:GetParameters",
                "ssm:GetParametersByPath"
            ],
            "Resource": [
                "arn:aws:ssm:*:*:parameter/myapp/*",
                "arn:aws:ssm:*:*:parameter/shared/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:PutParameter",
                "ssm:DeleteParameter",
                "ssm:AddTagsToResource"
            ],
            "Resource": "arn:aws:ssm:*:*:parameter/myapp/prod/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret"
            ],
            "Resource": "arn:aws:secretsmanager:*:*:secret:myapp/*"
        }
    ]
}
EOF
    
    # 创建角色并附加策略
    aws iam create-role --role-name ConfigManagerRole --assume-role-policy-document file://trust-policy.json
    aws iam put-role-policy --role-name ConfigManagerRole --policy-name ParameterStorePolicy --policy-document file://parameter-store-policy.json
    
    echo "Access control policies set up"
}

# 设置配置备份机制
setup_aws_config_backup() {
    echo "Setting up AWS configuration backup mechanisms..."
    
    # 启用AWS Config进行资源配置跟踪
    aws configservice put-configuration-recorder \
        --configuration-recorder name=default,roleARN=arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/aws-service-role/config.amazonaws.com/AWSServiceRoleForConfig
    
    # 创建配置备份脚本
    cat > backup-aws-config.sh << 'EOF'
#!/bin/bash

# AWS配置备份脚本
BACKUP_DIR="/backup/aws-config/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

echo "Backing up Parameter Store parameters..."
aws ssm get-parameters-by-path \
    --path "/" \
    --recursive \
    --with-decryption \
    --output json > $BACKUP_DIR/parameters.json

echo "Backing up Secrets Manager metadata..."
aws secretsmanager list-secrets \
    --output json > $BACKUP_DIR/secrets-metadata.json

echo "Creating backup archive..."
tar -czf $BACKUP_DIR.tar.gz -C /backup/aws-config $(date +%Y%m%d)

echo "AWS configuration backup completed: $BACKUP_DIR.tar.gz"
EOF
    
    chmod +x backup-aws-config.sh
    
    # 设置定时备份任务
    echo "0 2 * * * /path/to/backup-aws-config.sh" | crontab -
    
    echo "Configuration backup mechanisms set up"
}

# 设置监控和告警
setup_aws_config_monitoring() {
    echo "Setting up AWS configuration monitoring and alerting..."
    
    # 创建CloudWatch告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "ParameterStoreChanges" \
        --alarm-description "Alert on Parameter Store changes" \
        --metric-name "ParametersChanged" \
        --namespace "AWS/SSM" \
        --statistic "Sum" \
        --period 300 \
        --threshold 1 \
        --comparison-operator "GreaterThanOrEqualToThreshold" \
        --alarm-actions "arn:aws:sns:us-east-1:123456789012:ConfigAlerts"
    
    # 创建配置变更事件规则
    aws events put-rule \
        --name "ParameterStoreChangeRule" \
        --event-pattern '{"source":["aws.ssm"],"detail-type":["Parameter Store Change"]}'
    
    echo "Monitoring and alerting set up"
}

# 使用示例
# aws_config_best_practices
```

## Azure App Configuration使用

Azure App Configuration是Azure提供的托管服务，用于集中管理应用程序配置。

### 1. App Configuration核心功能

```csharp
// AzureAppConfigManager.cs
using Azure;
using Azure.Data.AppConfiguration;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Text.Json;

public class AzureAppConfigManager
{
    private readonly ConfigurationClient _client;
    
    public AzureAppConfigManager(string connectionString)
    {
        _client = new ConfigurationClient(connectionString);
    }
    
    public async Task<bool> SetConfiguration(string key, string value, string label = null, string contentType = null)
    {
        try
        {
            var setting = new ConfigurationSetting(key, value, label)
            {
                ContentType = contentType
            };
            
            await _client.SetConfigurationSettingAsync(setting);
            Console.WriteLine($"Configuration setting '{key}' set successfully");
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error setting configuration '{key}': {ex.Message}");
            return false;
        }
    }
    
    public async Task<string> GetConfiguration(string key, string label = null)
    {
        try
        {
            var setting = await _client.GetConfigurationSettingAsync(key, label);
            return setting.Value.Value;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error getting configuration '{key}': {ex.Message}");
            return null;
        }
    }
    
    public async Task<bool> SetFeatureFlag(string featureName, bool enabled, string label = null)
    {
        try
        {
            var featureKey = $".appconfig.featureflag/{featureName}";
            var featureFlag = new
            {
                id = featureName,
                description = $"Feature flag for {featureName}",
                enabled = enabled,
                conditions = new
                {
                    client_filters = new object[0]
                }
            };
            
            var json = JsonSerializer.Serialize(featureFlag);
            await SetConfiguration(featureKey, json, label, "application/vnd.microsoft.appconfig.ff+json;charset=utf-8");
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error setting feature flag '{featureName}': {ex.Message}");
            return false;
        }
    }
    
    public async Task<List<ConfigurationSetting>> GetSettingsByLabel(string label)
    {
        try
        {
            var settings = new List<ConfigurationSetting>();
            var selector = new SettingSelector
            {
                LabelFilter = label
            };
            
            await foreach (var setting in _client.GetConfigurationSettingsAsync(selector))
            {
                settings.Add(setting);
            }
            
            return settings;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error getting settings by label '{label}': {ex.Message}");
            return new List<ConfigurationSetting>();
        }
    }
    
    public async Task<bool> DeleteConfiguration(string key, string label = null)
    {
        try
        {
            await _client.DeleteConfigurationSettingAsync(key, label);
            Console.WriteLine($"Configuration setting '{key}' deleted successfully");
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error deleting configuration '{key}': {ex.Message}");
            return false;
        }
    }
}

// 使用示例
// var appConfigManager = new AzureAppConfigManager("Endpoint=https://myappconfig.azconfig.io;Id=xxx;Secret=yyy");
// 
// // 设置配置
// await appConfigManager.SetConfiguration("Database:Host", "db.example.com", "Production");
// 
// // 获取配置
// var dbHost = await appConfigManager.GetConfiguration("Database:Host", "Production");
// 
// // 设置功能开关
// await appConfigManager.SetFeatureFlag("NewFeature", true, "Production");
// 
// // 获取标签下的所有配置
// var prodSettings = await appConfigManager.GetSettingsByLabel("Production");
```

### 2. Azure配置管理最佳实践

```yaml
# azure-config-best-practices.yaml
---
azure_config_best_practices:
  # 配置组织结构
  configuration_structure:
    key_naming:
      convention: "{application}:{component}:{setting}"
      examples:
        - "MyApp:Database:ConnectionString"
        - "MyApp:Cache:RedisEndpoint"
        - "MyApp:FeatureFlags:NewUI"
        
    label_usage:
      environments:
        - "Development"
        - "Staging"
        - "Production"
      versions:
        - "v1.0"
        - "v2.0"
        
  # 功能管理
  feature_management:
    feature_flag_structure:
      key_prefix: ".appconfig.featureflag/"
      properties:
        - "id: 功能标识符"
        - "description: 功能描述"
        - "enabled: 是否启用"
        - "conditions: 启用条件"
        
    common_patterns:
      - "环境特定功能开关"
      - "渐进式功能发布"
      - "A/B测试功能"
      
  # 安全配置
  security_practices:
    access_control:
      role_based_access:
        - "App Configuration Data Reader"
        - "App Configuration Data Owner"
      managed_identities:
        - "使用系统分配的托管身份"
        - "使用用户分配的托管身份"
        
    encryption:
      - "静态数据加密（默认）"
      - "传输中加密（HTTPS）"
      - "客户管理的密钥（可选）"
```

## Google Cloud Secret Manager使用

Google Cloud Secret Manager是Google Cloud提供的安全存储和管理敏感数据的服务。

### 1. Secret Manager核心操作

```python
# gcp-secret-manager.py
from google.cloud import secretmanager
import json
from typing import Dict, Any, List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GCPSecretManager:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = secretmanager.SecretManagerServiceClient()
        
    def create_secret(self, secret_id: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """创建密钥"""
        try:
            parent = f"projects/{self.project_id}"
            
            secret = {
                "replication": {
                    "automatic": {}
                }
            }
            
            # 添加标签（如果提供）
            if labels:
                secret["labels"] = labels
                
            response = self.client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": secret,
                }
            )
            
            logger.info(f"Secret {secret_id} created successfully")
            return {
                'success': True,
                'secret_name': response.name
            }
        except Exception as e:
            logger.error(f"Failed to create secret {secret_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def add_secret_version(self, secret_id: str, payload: str) -> Dict[str, Any]:
        """添加密钥版本"""
        try:
            parent = f"projects/{self.project_id}/secrets/{secret_id}"
            
            response = self.client.add_secret_version(
                request={
                    "parent": parent,
                    "payload": {"data": payload.encode("UTF-8")},
                }
            )
            
            logger.info(f"Secret version added to {secret_id}")
            return {
                'success': True,
                'version_name': response.name
            }
        except Exception as e:
            logger.error(f"Failed to add secret version to {secret_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def access_secret_version(self, secret_id: str, version_id: str = "latest") -> Dict[str, Any]:
        """访问密钥版本"""
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
            
            response = self.client.access_secret_version(request={"name": name})
            
            payload = response.payload.data.decode("UTF-8")
            
            return {
                'success': True,
                'secret_id': secret_id,
                'version_id': version_id,
                'payload': payload
            }
        except Exception as e:
            logger.error(f"Failed to access secret {secret_id} version {version_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def list_secrets(self) -> Dict[str, Any]:
        """列出所有密钥"""
        try:
            parent = f"projects/{self.project_id}"
            secrets = []
            
            for secret in self.client.list_secrets(request={"parent": parent}):
                secrets.append({
                    'name': secret.name,
                    'create_time': secret.create_time.isoformat(),
                    'labels': dict(secret.labels) if secret.labels else {}
                })
                
            return {
                'success': True,
                'secrets': secrets,
                'count': len(secrets)
            }
        except Exception as e:
            logger.error(f"Failed to list secrets: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def destroy_secret_version(self, secret_id: str, version_id: str) -> Dict[str, Any]:
        """销毁密钥版本"""
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
            
            response = self.client.destroy_secret_version(request={"name": name})
            
            logger.info(f"Secret version {version_id} of {secret_id} destroyed")
            return {
                'success': True,
                'version_name': response.name
            }
        except Exception as e:
            logger.error(f"Failed to destroy secret version {secret_id}/{version_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def delete_secret(self, secret_id: str) -> Dict[str, Any]:
        """删除密钥"""
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}"
            
            self.client.delete_secret(request={"name": name})
            
            logger.info(f"Secret {secret_id} deleted")
            return {
                'success': True,
                'secret_id': secret_id
            }
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# 使用示例
# secret_manager = GCPSecretManager("my-gcp-project")

# # 创建密钥
# result = secret_manager.create_secret(
#     "database-password",
#     {"environment": "production", "application": "myapp"}
# )

# # 添加密钥版本
# if result['success']:
#     version_result = secret_manager.add_secret_version(
#         "database-password",
#         "supersecretpassword"
#     )

# # 访问密钥
# secret = secret_manager.access_secret_version("database-password")

# # 列出所有密钥
# secrets = secret_manager.list_secrets()
```

### 2. GCP配置管理策略

```yaml
# gcp-config-management-strategy.yaml
---
gcp_config_management_strategy:
  # 密钥命名规范
  secret_naming:
    convention: "{application}-{component}-{purpose}"
    examples:
      - "myapp-database-password"
      - "myapp-api-key"
      - "myapp-tls-certificate"
    best_practices:
      - "使用小写字母和连字符"
      - "避免在名称中包含敏感信息"
      - "保持名称简洁且具有描述性"
      
  # 标签策略
  labeling_strategy:
    required_labels:
      - "environment: {dev|staging|prod}"
      - "application: {app-name}"
      - "team: {team-name}"
      - "cost-center: {cost-center-id}"
      
    optional_labels:
      - "version: {version-number}"
      - "compliance: {level}"
      - "criticality: {high|medium|low}"
      
  # 版本管理
  version_management:
    automatic_rotation:
      schedule: "每90天自动轮换"
      notification: "轮换前7天发送通知"
      
    manual_rotation:
      process: "通过CI/CD管道进行轮换"
      validation: "轮换后验证应用连接性"
      
    version_retention:
      policy: "保留最近10个版本"
      cleanup: "自动清理超过保留期的版本"
```

## 跨平台配置管理工具

为了在多云环境中实现一致的配置管理，可以使用跨平台的配置管理工具。

### 1. HashiCorp Vault集成

```python
# vault-config-manager.py
import hvac
import json
from typing import Dict, Any, List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VaultConfigManager:
    def __init__(self, vault_url: str, token: str = None, cert_file: str = None):
        self.client = hvac.Client(url=vault_url)
        
        if token:
            self.client.token = token
        elif cert_file:
            self.client = hvac.Client(
                url=vault_url,
                cert=(cert_file, cert_file),
                verify=cert_file
            )
            
    def write_secret(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """写入密钥"""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data
            )
            
            logger.info(f"Secret written to {path}")
            return {
                'success': True,
                'path': path
            }
        except Exception as e:
            logger.error(f"Failed to write secret to {path}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def read_secret(self, path: str) -> Dict[str, Any]:
        """读取密钥"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            
            return {
                'success': True,
                'path': path,
                'data': response['data']['data'],
                'metadata': response['data']['metadata']
            }
        except Exception as e:
            logger.error(f"Failed to read secret from {path}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def list_secrets(self, path: str) -> Dict[str, Any]:
        """列出密钥"""
        try:
            response = self.client.secrets.kv.v2.list_secrets(path=path)
            
            return {
                'success': True,
                'path': path,
                'keys': response['data']['keys']
            }
        except Exception as e:
            logger.error(f"Failed to list secrets at {path}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def delete_secret(self, path: str) -> Dict[str, Any]:
        """删除密钥"""
        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(path=path)
            
            logger.info(f"Secret deleted from {path}")
            return {
                'success': True,
                'path': path
            }
        except Exception as e:
            logger.error(f"Failed to delete secret from {path}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def enable_audit_device(self, device_type: str, path: str, options: Dict[str, str] = None) -> Dict[str, Any]:
        """启用审计设备"""
        try:
            self.client.sys.enable_audit_device(
                device_type=device_type,
                path=path,
                options=options
            )
            
            logger.info(f"Audit device {device_type} enabled at {path}")
            return {
                'success': True,
                'device_type': device_type,
                'path': path
            }
        except Exception as e:
            logger.error(f"Failed to enable audit device {device_type}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# 使用示例
# vault_manager = VaultConfigManager("https://vault.example.com", token="s.xxxxxxxx")

# # 写入密钥
# result = vault_manager.write_secret(
#     "myapp/prod/database",
#     {
#         "host": "db.example.com",
#         "port": "5432",
#         "password": "supersecretpassword"
#         "username": "dbuser"
#     }
# )

# # 读取密钥
# secret = vault_manager.read_secret("myapp/prod/database")

# # 列出密钥
# secrets = vault_manager.list_secrets("myapp/prod/")
```

### 2. Consul配置管理

```go
// consul-config-manager.go
package main

import (
    "context"
    "fmt"
    "log"
    "time"

    "github.com/hashicorp/consul/api"
)

type ConsulConfigManager struct {
    client *api.Client
}

func NewConsulConfigManager(address string) (*ConsulConfigManager, error) {
    config := api.DefaultConfig()
    config.Address = address
    
    client, err := api.NewClient(config)
    if err != nil {
        return nil, err
    }
    
    return &ConsulConfigManager{
        client: client,
    }, nil
}

func (c *ConsulConfigManager) PutConfig(key string, value string, tags []string) error {
    kv := c.client.KV()
    
    pair := &api.KVPair{
        Key:   key,
        Value: []byte(value),
        Flags: 0,
    }
    
    _, err := kv.Put(pair, nil)
    if err != nil {
        return fmt.Errorf("failed to put config: %v", err)
    }
    
    // 如果有标签，也存储标签信息
    if len(tags) > 0 {
        tagKey := fmt.Sprintf("%s.tags", key)
        tagPair := &api.KVPair{
            Key:   tagKey,
            Value: []byte(fmt.Sprintf("%v", tags)),
            Flags: 0,
        }
        _, err = kv.Put(tagPair, nil)
        if err != nil {
            return fmt.Errorf("failed to put tags: %v", err)
        }
    }
    
    log.Printf("Config stored successfully: %s", key)
    return nil
}

func (c *ConsulConfigManager) GetConfig(key string) (string, error) {
    kv := c.client.KV()
    
    pair, _, err := kv.Get(key, nil)
    if err != nil {
        return "", fmt.Errorf("failed to get config: %v", err)
    }
    
    if pair == nil {
        return "", fmt.Errorf("config not found: %s", key)
    }
    
    return string(pair.Value), nil
}

func (c *ConsulConfigManager) WatchConfig(key string, onChange func(string)) error {
    kv := c.client.KV()
    
    // 创建查询选项，启用阻塞查询
    opts := &api.QueryOptions{
        WaitIndex: 0,
        WaitTime:  10 * time.Second,
    }
    
    go func() {
        for {
            pair, meta, err := kv.Get(key, opts)
            if err != nil {
                log.Printf("Error watching config: %v", err)
                time.Sleep(5 * time.Second)
                continue
            }
            
            // 更新等待索引
            opts.WaitIndex = meta.LastIndex
            
            if pair != nil {
                onChange(string(pair.Value))
            }
        }
    }()
    
    return nil
}

func (c *ConsulConfigManager) ListConfigs(prefix string) ([]string, error) {
    kv := c.client.KV()
    
    pairs, _, err := kv.List(prefix, nil)
    if err != nil {
        return nil, fmt.Errorf("failed to list configs: %v", err)
    }
    
    keys := make([]string, len(pairs))
    for i, pair := range pairs {
        keys[i] = pair.Key
    }
    
    return keys, nil
}

func (c *ConsulConfigManager) DeleteConfig(key string) error {
    kv := c.client.KV()
    
    _, err := kv.Delete(key, nil)
    if err != nil {
        return fmt.Errorf("failed to delete config: %v", err)
    }
    
    log.Printf("Config deleted successfully: %s", key)
    return nil
}

// 使用示例
// func main() {
//     manager, err := NewConsulConfigManager("localhost:8500")
//     if err != nil {
//         log.Fatal(err)
//     }
//     
//     // 存储配置
//     err = manager.PutConfig("myapp/prod/database/host", "db.example.com", []string{"production", "database"})
//     if err != nil {
//         log.Fatal(err)
//     }
//     
//     // 获取配置
//     host, err := manager.GetConfig("myapp/prod/database/host")
//     if err != nil {
//         log.Fatal(err)
//     }
//     fmt.Printf("Database host: %s\n", host)
//     
//     // 监听配置变化
//     err = manager.WatchConfig("myapp/prod/database/host", func(value string) {
//         fmt.Printf("Config changed: %s\n", value)
//     })
//     if err != nil {
//         log.Fatal(err)
//     }
//     
//     // 保持程序运行
//     select {}
// }
```

## 最佳实践总结

通过以上内容，我们可以总结出使用云原生工具管理配置的最佳实践：

### 1. AWS Systems Manager最佳实践
- 使用分层命名规范组织参数
- 合理选择参数类型和层级
- 实施细粒度的访问控制策略
- 建立配置备份和恢复机制

### 2. Azure App Configuration最佳实践
- 使用标签区分不同环境和版本
- 充分利用功能管理功能
- 实施基于角色的访问控制
- 集成监控和告警机制

### 3. Google Cloud Secret Manager最佳实践
- 遵循密钥命名规范
- 使用标签进行分类管理
- 实施密钥版本管理和轮换策略
- 启用审计日志记录

### 4. 跨平台工具使用最佳实践
- 选择适合组织需求的工具
- 实现统一的配置管理接口
- 建立配置同步机制
- 实施安全的访问控制

通过实施这些最佳实践，企业可以充分利用云原生工具的强大功能，实现安全、高效、可靠的配置管理。

在下一节中，我们将深入探讨配置管理与容器化平台的结合，帮助您更好地理解如何在Kubernetes等容器化环境中管理配置。