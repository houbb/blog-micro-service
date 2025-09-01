---
title: 云厂商的弹性负载均衡（ELB/ALB/NLB）：公有云环境下的负载均衡解决方案
date: 2025-08-31
categories: [LoadBalance]
tags: [load-balance]
published: true
---

在公有云环境中，负载均衡是构建高可用、可扩展应用架构的核心组件。各大云厂商都提供了丰富的负载均衡服务，包括AWS的Elastic Load Balancer (ELB)、Application Load Balancer (ALB)、Network Load Balancer (NLB)，Azure的Load Balancer和Application Gateway，以及Google Cloud的Cloud Load Balancing等。这些服务不仅提供了强大的负载均衡能力，还集成了云平台的其他服务，为用户提供了完整的解决方案。本文将深入探讨主流云厂商的弹性负载均衡服务、技术特点以及在实际应用中的最佳实践。

## AWS弹性负载均衡服务

AWS提供了三种主要的负载均衡服务，分别针对不同的应用场景和需求。

### Classic Load Balancer (ELB)

Classic Load Balancer是AWS最早的负载均衡服务，提供基本的负载均衡功能。

#### 架构特点
```yaml
# Classic Load Balancer配置示例
Resources:
  ClassicLoadBalancer:
    Type: AWS::ElasticLoadBalancing::LoadBalancer
    Properties:
      AvailabilityZones:
        - us-west-2a
        - us-west-2b
      Listeners:
        - LoadBalancerPort: '80'
          InstancePort: '80'
          Protocol: HTTP
        - LoadBalancerPort: '443'
          InstancePort: '443'
          Protocol: HTTPS
          SSLCertificateId: arn:aws:acm:us-west-2:123456789012:certificate/12345678-1234-1234-1234-123456789012
      HealthCheck:
        Target: HTTP:80/health
        HealthyThreshold: '2'
        UnhealthyThreshold: '3'
        Interval: '10'
        Timeout: '5'
      Instances:
        - !Ref WebServer1
        - !Ref WebServer2
```

#### 适用场景
- 传统的三层架构应用
- 简单的负载均衡需求
- 向后兼容现有应用

### Application Load Balancer (ALB)

Application Load Balancer是面向应用层的负载均衡器，支持基于内容的路由和更高级的功能。

#### 核心特性
```yaml
# Application Load Balancer配置示例
Resources:
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: my-alb
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      SecurityGroups:
        - !Ref ALBSecurityGroup

  ALBListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP

  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: my-targets
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VPC
      HealthCheckPath: /health
      HealthCheckProtocol: HTTP
      HealthCheckIntervalSeconds: 30
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3
```

#### 高级路由功能
```yaml
# 基于路径的路由规则
Resources:
  PathBasedRule:
    Type: AWS::ElasticLoadBalancingV2::ListenerRule
    Properties:
      Actions:
        - Type: forward
          TargetGroupArn: !Ref APITargetGroup
      Conditions:
        - Field: path-pattern
          Values:
            - /api/*
      ListenerArn: !Ref ALBListener
      Priority: 100

  HostBasedRule:
    Type: AWS::ElasticLoadBalancingV2::ListenerRule
    Properties:
      Actions:
        - Type: forward
          TargetGroupArn: !Ref WebTargetGroup
      Conditions:
        - Field: host-header
          Values:
            - example.com
      ListenerArn: !Ref ALBListener
      Priority: 200
```

#### 容器集成
```yaml
# ECS服务与ALB集成
Resources:
  ECSService:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !Ref ECSCluster
      DesiredCount: 2
      TaskDefinition: !Ref TaskDefinition
      LoadBalancers:
        - ContainerName: web
          ContainerPort: 80
          TargetGroupArn: !Ref TargetGroup
```

### Network Load Balancer (NLB)

Network Load Balancer是面向网络层的负载均衡器，提供超高性能和低延迟。

#### 配置示例
```yaml
# Network Load Balancer配置
Resources:
  NetworkLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: my-nlb
      Scheme: internet-facing
      Type: network
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2

  NLBListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref NLBTargetGroup
      LoadBalancerArn: !Ref NetworkLoadBalancer
      Port: 80
      Protocol: TCP

  NLBTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: nlb-targets
      Port: 80
      Protocol: TCP
      VpcId: !Ref VPC
      TargetType: instance
```

#### 性能特性
```bash
# NLB性能指标
# - 延迟: <100ms
# - 吞吐量: 数百万请求/秒
# - 连接数: 数百万并发连接
```

## Azure负载均衡服务

Azure提供了多种负载均衡服务，包括Load Balancer和Application Gateway。

### Azure Load Balancer

Azure Load Balancer提供四层负载均衡功能。

#### 基本配置
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.Network/loadBalancers",
      "apiVersion": "2020-06-01",
      "name": "myLoadBalancer",
      "location": "[resourceGroup().location]",
      "properties": {
        "frontendIPConfigurations": [
          {
            "name": "LoadBalancerFrontEnd",
            "properties": {
              "publicIPAddress": {
                "id": "[resourceId('Microsoft.Network/publicIPAddresses', 'myPublicIP')]"
              }
            }
          }
        ],
        "backendAddressPools": [
          {
            "name": "BackendPool"
          }
        ],
        "loadBalancingRules": [
          {
            "name": "HTTPRule",
            "properties": {
              "frontendIPConfiguration": {
                "id": "[resourceId('Microsoft.Network/loadBalancers/frontendIPConfigurations', 'myLoadBalancer', 'LoadBalancerFrontEnd')]"
              },
              "backendAddressPool": {
                "id": "[resourceId('Microsoft.Network/loadBalancers/backendAddressPools', 'myLoadBalancer', 'BackendPool')]"
              },
              "protocol": "Tcp",
              "frontendPort": 80,
              "backendPort": 80,
              "enableFloatingIP": false,
              "idleTimeoutInMinutes": 5,
              "probe": {
                "id": "[resourceId('Microsoft.Network/loadBalancers/probes', 'myLoadBalancer', 'tcpProbe')]"
              }
            }
          }
        ],
        "probes": [
          {
            "name": "tcpProbe",
            "properties": {
              "protocol": "Tcp",
              "port": 80,
              "intervalInSeconds": 5,
              "numberOfProbes": 2
            }
          }
        ]
      }
    }
  ]
}
```

### Application Gateway

Application Gateway提供七层负载均衡和Web应用防火墙功能。

#### 高级配置
```json
{
  "type": "Microsoft.Network/applicationGateways",
  "apiVersion": "2020-06-01",
  "name": "myAppGateway",
  "properties": {
    "sku": {
      "name": "Standard_v2",
      "tier": "Standard_v2"
    },
    "gatewayIPConfigurations": [
      {
        "name": "appGatewayIpConfig",
        "properties": {
          "subnet": {
            "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', 'myVNet', 'myAppGatewaySubnet')]"
          }
        }
      }
    ],
    "frontendIPConfigurations": [
      {
        "name": "appGatewayFrontendIP",
        "properties": {
          "publicIPAddress": {
            "id": "[resourceId('Microsoft.Network/publicIPAddresses', 'myPublicIP')]"
          }
        }
      }
    ],
    "frontendPorts": [
      {
        "name": "port_80",
        "properties": {
          "port": 80
        }
      }
    ],
    "backendAddressPools": [
      {
        "name": "appGatewayBackendPool",
        "properties": {
          "backendAddresses": [
            {
              "ipAddress": "10.0.1.10"
            },
            {
              "ipAddress": "10.0.1.11"
            }
          ]
        }
      }
    ],
    "backendHttpSettingsCollection": [
      {
        "name": "appGatewayBackendHttpSettings",
        "properties": {
          "port": 80,
          "protocol": "Http",
          "cookieBasedAffinity": "Disabled",
          "requestTimeout": 30
        }
      }
    ],
    "httpListeners": [
      {
        "name": "appGatewayHttpListener",
        "properties": {
          "frontendIPConfiguration": {
            "id": "[resourceId('Microsoft.Network/applicationGateways/frontendIPConfigurations', 'myAppGateway', 'appGatewayFrontendIP')]"
          },
          "frontendPort": {
            "id": "[resourceId('Microsoft.Network/applicationGateways/frontendPorts', 'myAppGateway', 'port_80')]"
          },
          "protocol": "Http"
        }
      }
    ],
    "requestRoutingRules": [
      {
        "name": "rule1",
        "properties": {
          "ruleType": "Basic",
          "httpListener": {
            "id": "[resourceId('Microsoft.Network/applicationGateways/httpListeners', 'myAppGateway', 'appGatewayHttpListener')]"
          },
          "backendAddressPool": {
            "id": "[resourceId('Microsoft.Network/applicationGateways/backendAddressPools', 'myAppGateway', 'appGatewayBackendPool')]"
          },
          "backendHttpSettings": {
            "id": "[resourceId('Microsoft.Network/applicationGateways/backendHttpSettingsCollection', 'myAppGateway', 'appGatewayBackendHttpSettings')]"
          }
        }
      }
    ]
  }
}
```

## Google Cloud Load Balancing

Google Cloud提供了多种负载均衡服务，包括外部负载均衡和内部负载均衡。

### 外部HTTP(S)负载均衡
```yaml
# Google Cloud External HTTP(S) Load Balancer
resources:
- name: lb-http
  type: compute.v1.globalForwardingRule
  properties:
    IPProtocol: TCP
    portRange: 80
    target: $(ref.lb-http-target-proxy.selfLink)

- name: lb-http-target-proxy
  type: compute.v1.targetHttpProxy
  properties:
    urlMap: $(ref.lb-http-url-map.selfLink)

- name: lb-http-url-map
  type: compute.v1.urlMap
  properties:
    defaultService: $(ref.lb-http-backend-service.selfLink)

- name: lb-http-backend-service
  type: compute.v1.backendService
  properties:
    backends:
    - group: $(ref.instance-group-1.instanceGroup)
    - group: $(ref.instance-group-2.instanceGroup)
    healthChecks:
    - $(ref.http-health-check.selfLink)
    portName: http
    protocol: HTTP
    timeoutSec: 30
```

### 网络负载均衡
```yaml
# Google Cloud Network Load Balancer
resources:
- name: network-lb
  type: compute.v1.forwardingRule
  properties:
    region: us-central1
    IPProtocol: TCP
    portRange: 80
    target: $(ref.network-lb-target-pool.selfLink)

- name: network-lb-target-pool
  type: compute.v1.targetPool
  properties:
    region: us-central1
    healthChecks:
    - $(ref.network-lb-health-check.selfLink)
    instances:
    - $(ref.instance-1.selfLink)
    - $(ref.instance-2.selfLink)
```

## 跨云厂商负载均衡比较

### 功能对比

| 特性 | AWS ELB | AWS ALB | AWS NLB | Azure LB | Azure AppGW | GCP LB |
|------|---------|---------|---------|----------|-------------|--------|
| 层级 | L4/L7 | L7 | L4 | L4 | L7 | L4/L7 |
| 性能 | 中等 | 中等 | 高 | 中等 | 中等 | 高 |
| 路由 | 基础 | 高级 | 基础 | 基础 | 高级 | 高级 |
| SSL终止 | 支持 | 支持 | 不支持 | 支持 | 支持 | 支持 |
| WAF集成 | 不支持 | 支持 | 不支持 | 不支持 | 支持 | 支持 |
| 容器集成 | 支持 | 优秀 | 支持 | 支持 | 支持 | 优秀 |

### 定价模型

#### AWS定价示例
```bash
# AWS ELB定价（us-east-1）
# - 每小时: $0.025
# - 每GB数据处理: $0.008

# AWS ALB定价
# - 每小时: $0.0225
# - 每LCU小时: $0.008

# AWS NLB定价
# - 每小时: $0.0225
# - 每GB数据处理: $0.008
```

## 最佳实践

### 1. 负载均衡器选择
```yaml
# 根据需求选择合适的负载均衡器
# Web应用 -> ALB
# 高性能TCP服务 -> NLB
# 传统应用 -> Classic ELB
# 内部服务 -> Internal Load Balancer
```

### 2. 健康检查优化
```yaml
# AWS ALB健康检查配置
Resources:
  TargetGroup:
    Properties:
      HealthCheckPath: /health
      HealthCheckProtocol: HTTP
      HealthCheckIntervalSeconds: 30
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3
      HealthCheckTimeoutSeconds: 5
      Matcher:
        HttpCode: 200-299
```

### 3. 安全配置
```yaml
# 安全组配置
Resources:
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for ALB
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
```

### 4. 监控告警
```yaml
# CloudWatch告警配置
Resources:
  HighLatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: HighLatencyAlarm
      AlarmDescription: Alarm when ALB latency exceeds 1 second
      MetricName: TargetResponseTime
      Namespace: AWS/ApplicationELB
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 1
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref NotificationTopic
```

## 故障排除

### 常见问题诊断

#### 1. 502错误
```bash
# 检查目标组健康状态
aws elbv2 describe-target-health --target-group-arn <target-group-arn>

# 检查安全组配置
aws ec2 describe-security-groups --group-ids <security-group-id>

# 检查实例状态
aws ec2 describe-instances --instance-ids <instance-id>
```

#### 2. 503错误
```bash
# 检查目标组注册状态
aws elbv2 describe-target-groups --target-group-arns <target-group-arn>

# 检查实例注册数量
aws elbv2 describe-target-health --target-group-arn <target-group-arn> \
  --query 'TargetHealthDescriptions[*].Target.Id' --output text
```

#### 3. 性能问题
```bash
# 监控负载均衡器指标
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name RequestCount \
  --dimensions Name=LoadBalancer,Value=<load-balancer-name> \
  --start-time 2023-01-01T00:00:00Z \
  --end-time 2023-01-01T01:00:00Z \
  --period 300 \
  --statistics Sum
```

## 总结

云厂商的弹性负载均衡服务为现代应用架构提供了强大而灵活的负载均衡能力。AWS的ELB、ALB、NLB系列提供了从基础到高级的完整解决方案；Azure的Load Balancer和Application Gateway满足了不同层次的需求；Google Cloud的负载均衡服务则以其高性能和全球分布能力著称。

在选择负载均衡服务时，需要根据具体的应用场景、性能要求、安全需求和成本考虑来做出决策。通过合理的配置和优化，云厂商的负载均衡服务能够为应用提供高可用性、高性能和良好的用户体验。

随着云原生技术的发展，负载均衡服务也在不断演进，未来将提供更加智能化、自动化的负载均衡能力，为构建复杂的分布式系统提供更好的支撑。企业在采用这些服务时，应该建立完善的监控和告警机制，确保负载均衡系统的稳定运行。