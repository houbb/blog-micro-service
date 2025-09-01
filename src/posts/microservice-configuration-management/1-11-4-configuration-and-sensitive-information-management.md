---
title: 配置与敏感信息管理：环境隔离与密钥管理的最佳实践
date: 2025-08-31
categories: [Configuration Management]
tags: [microservice-configuration-management]
published: true
---

# 11.4 配置与敏感信息管理

在现代应用程序开发和部署中，敏感信息的安全管理是配置管理的核心挑战之一。密码、API密钥、证书等敏感信息如果处理不当，可能导致严重的安全漏洞和数据泄露。本节将深入探讨敏感信息的识别与分类、环境隔离策略、加密存储与传输技术，以及访问控制与审计机制，帮助您建立安全可靠的敏感信息管理体系。

## 敏感信息识别与分类

有效管理敏感信息的第一步是准确识别和分类这些信息。

### 敏感信息类型

1. **认证凭证**
   - 用户名和密码
   - API密钥和访问令牌
   - SSH密钥和证书
   - 数据库连接字符串

2. **个人身份信息(PII)**
   - 用户名、姓名、地址
   - 身份证号、社保号
   - 电话号码、邮箱地址
   - 生物识别数据

3. **财务信息**
   - 信用卡号、银行账户
   - 交易记录、支付信息
   - 税务信息

4. **商业机密**
   - 源代码、算法
   - 商业计划、客户名单
   - 价格策略、合同条款

### 敏感信息分类标准

```javascript
// sensitive-data-classifier.js
class SensitiveDataClassifier {
  constructor() {
    this.classificationRules = {
      // 高敏感度信息
      HIGH: [
        { pattern: /\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/, type: 'credit_card' },
        { pattern: /\b\d{3}-\d{2}-\d{4}\b/, type: 'ssn' },
        { pattern: /\b[A-Z0-9]{12,}\b/, type: 'api_key' },
        { pattern: /-----BEGIN.*PRIVATE.*KEY-----/, type: 'private_key' }
      ],
      
      // 中敏感度信息
      MEDIUM: [
        { pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/, type: 'email' },
        { pattern: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/, type: 'phone' },
        { pattern: /password\s*[:=]\s*['"][^'"]+['"]/, type: 'password' }
      ],
      
      // 低敏感度信息
      LOW: [
        { pattern: /username\s*[:=]\s*['"][^'"]+['"]/, type: 'username' },
        { pattern: /connection\s*string/i, type: 'connection_string' }
      ]
    };
  }

  classify(text) {
    const results = {
      HIGH: [],
      MEDIUM: [],
      LOW: []
    };

    for (const [level, rules] of Object.entries(this.classificationRules)) {
      for (const rule of rules) {
        const matches = text.match(rule.pattern);
        if (matches) {
          results[level].push({
            type: rule.type,
            matches: matches,
            level: level
          });
        }
      }
    }

    return results;
  }

  scanFile(filePath) {
    const fs = require('fs');
    const content = fs.readFileSync(filePath, 'utf8');
    return this.classify(content);
  }

  scanDirectory(dirPath) {
    const fs = require('fs');
    const path = require('path');
    const results = [];

    const files = fs.readdirSync(dirPath);
    for (const file of files) {
      const fullPath = path.join(dirPath, file);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory()) {
        results.push(...this.scanDirectory(fullPath));
      } else if (file.endsWith('.yaml') || file.endsWith('.json') || file.endsWith('.env')) {
        const classification = this.scanFile(fullPath);
        if (this.hasSensitiveData(classification)) {
          results.push({
            file: fullPath,
            classification: classification
          });
        }
      }
    }

    return results;
  }

  hasSensitiveData(classification) {
    return Object.values(classification).some(level => level.length > 0);
  }
}

// 使用示例
const classifier = new SensitiveDataClassifier();
const results = classifier.scanDirectory('./config');

for (const result of results) {
  console.log(`File: ${result.file}`);
  for (const [level, items] of Object.entries(result.classification)) {
    if (items.length > 0) {
      console.log(`  ${level} sensitivity:`);
      for (const item of items) {
        console.log(`    - ${item.type}: ${item.matches.length} matches`);
      }
    }
  }
}
```

### 敏感信息清单

```yaml
# sensitive-data-inventory.yaml
version: "1.0"

inventory:
  - name: "Database Credentials"
    type: "database"
    sensitivity: "HIGH"
    locations:
      - "config/production/database.yaml"
      - "environment variables"
    rotation_schedule: "90 days"
    owner: "db-admin-team"
    access_control:
      - "application-service-account"
      - "db-admins"

  - name: "API Keys"
    type: "api_key"
    sensitivity: "HIGH"
    locations:
      - "config/secrets/api-keys.yaml"
      - "vault/secrets/api-keys"
    rotation_schedule: "30 days"
    owner: "platform-team"
    access_control:
      - "microservice-accounts"
      - "platform-engineers"

  - name: "TLS Certificates"
    type: "certificate"
    sensitivity: "MEDIUM"
    locations:
      - "/etc/ssl/certs/"
      - "vault/pki"
    rotation_schedule: "365 days"
    owner: "security-team"
    access_control:
      - "web-servers"
      - "load-balancers"
      - "security-engineers"

  - name: "User Emails"
    type: "pii"
    sensitivity: "MEDIUM"
    locations:
      - "database/users"
      - "logs"
    rotation_schedule: "N/A"
    owner: "data-protection-officer"
    access_control:
      - "user-service"
      - "support-team"
      - "data-analysts"
```

## 环境隔离策略

环境隔离是确保敏感信息在不同环境中得到适当保护的重要策略。

### 环境分类

```yaml
# environment-classification.yaml
environments:
  development:
    description: "Local development environments"
    sensitivity: "LOW"
    isolation_level: "basic"
    access_control: "developers"
    data_classification: "synthetic"
    
  testing:
    description: "QA and integration testing environments"
    sensitivity: "LOW"
    isolation_level: "standard"
    access_control: "qa-engineers, developers"
    data_classification: "anonymized"
    
  staging:
    description: "Pre-production environment"
    sensitivity: "MEDIUM"
    isolation_level: "enhanced"
    access_control: "operations, qa-engineers"
    data_classification: "production-like"
    
  production:
    description: "Live production environment"
    sensitivity: "HIGH"
    isolation_level: "strict"
    access_control: "operations, security"
    data_classification: "real"
```

### 环境隔离实现

```bash
# 网络隔离
# 使用不同的VPC/子网
# development: 10.10.0.0/16
# testing: 10.20.0.0/16
# staging: 10.30.0.0/16
# production: 10.40.0.0/16

# 防火墙规则示例
# iptables -A INPUT -s 10.10.0.0/16 -p tcp --dport 5432 -j ACCEPT  # 开发环境数据库访问
# iptables -A INPUT -s 10.20.0.0/16 -p tcp --dport 5432 -j ACCEPT  # 测试环境数据库访问
# iptables -A INPUT -s 10.40.0.0/16 -p tcp --dport 5432 -j ACCEPT  # 生产环境数据库访问

# Kubernetes网络策略
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-access-policy
spec:
  podSelector:
    matchLabels:
      app: database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          environment: production
    ports:
    - protocol: TCP
      port: 5432
```

### 环境特定配置

```yaml
# config/environments/development.yaml
app:
  environment: development
  debug: true

database:
  host: localhost
  port: 5432
  name: myapp_dev
  # 使用开发环境凭证
  username: dev_user
  password: dev_password123  # 开发环境可以使用明文（但仍需谨慎）

# config/environments/production.yaml
app:
  environment: production
  debug: false

database:
  host: db.production.internal
  port: 5432
  name: myapp_prod
  # 生产环境凭证从安全存储获取
  username: ${DB_USER}
  password: ${DB_PASSWORD}  # 必须从环境变量或密钥管理器获取
```

## 加密存储与传输

加密是保护敏感信息的核心技术手段。

### 静态数据加密

```bash
# 使用AES-256加密敏感配置文件
# 1. 生成密钥
openssl rand -base64 32 > config/master.key

# 2. 加密配置文件
openssl enc -aes-256-cbc -salt -in config/secrets.yaml -out config/secrets.yaml.enc -pass file:config/master.key

# 3. 解密配置文件
openssl enc -aes-256-cbc -d -in config/secrets.yaml.enc -out config/secrets.yaml -pass file:config/master.key

# 4. 在应用程序中自动解密
#!/bin/bash
# start-app.sh
set -e

# 解密敏感配置
openssl enc -aes-256-cbc -d -in config/secrets.yaml.enc -out config/secrets.yaml -pass file:config/master.key

# 启动应用
node app.js

# 清理明文配置
trap "rm -f config/secrets.yaml" EXIT
```

### 使用专业加密工具

```bash
# 使用git-crypt进行文件级加密
# 1. 初始化git-crypt
git crypt init

# 2. 配置加密规则
cat > .gitattributes << EOF
config/secrets/*.yaml filter=git-crypt diff=git-crypt
config/production/*.yaml filter=git-crypt diff=git-crypt
EOF

# 3. 添加团队成员的GPG密钥
git crypt add-gpg-user user1@example.com
git crypt add-gpg-user user2@example.com

# 4. 创建加密配置文件
cat > config/secrets/database.yaml << EOF
database:
  password: actual_production_password
redis:
  password: actual_redis_password
EOF

# 5. 提交加密文件
git add .
git commit -m "Add encrypted database credentials"
```

### 密钥管理服务集成

```javascript
// vault-integration.js
const Vault = require('node-vault');

class SecretsManager {
  constructor() {
    this.vault = Vault({
      apiVersion: 'v1',
      endpoint: process.env.VAULT_ADDR || 'http://127.0.0.1:8200',
      token: process.env.VAULT_TOKEN
    });
  }

  async getSecret(path) {
    try {
      const result = await this.vault.read(path);
      return result.data;
    } catch (error) {
      console.error(`Failed to retrieve secret from ${path}:`, error.message);
      throw error;
    }
  }

  async setSecret(path, data) {
    try {
      await this.vault.write(path, data);
      console.log(`Secret stored at ${path}`);
    } catch (error) {
      console.error(`Failed to store secret at ${path}:`, error.message);
      throw error;
    }
  }

  async rotateDatabasePassword() {
    // 生成新密码
    const newPassword = this.generatePassword(32);
    
    // 更新Vault中的密码
    await this.setSecret('secret/myapp/database', {
      password: newPassword
    });
    
    // 通知应用程序重新加载配置
    await this.notifyApplication('database-password-rotated');
    
    return newPassword;
  }

  generatePassword(length) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()';
    let password = '';
    for (let i = 0; i < length; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
  }

  async notifyApplication(event) {
    // 实现通知机制，如发送HTTP请求、消息队列等
    console.log(`Notifying application of event: ${event}`);
  }
}

// 使用示例
const secretsManager = new SecretsManager();

// 获取数据库密码
secretsManager.getSecret('secret/myapp/database').then(secret => {
  console.log('Database password:', secret.password);
});

// 轮换密码
secretsManager.rotateDatabasePassword().then(newPassword => {
  console.log('New password generated:', newPassword);
});
```

### 传输层加密

```bash
# HTTPS配置示例
# nginx.conf
server {
    listen 443 ssl http2;
    server_name myapp.example.com;
    
    # SSL证书配置
    ssl_certificate /etc/ssl/certs/myapp.crt;
    ssl_certificate_key /etc/ssl/private/myapp.key;
    
    # 安全的SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# 数据库连接加密
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/postgresql.crt'
ssl_key_file = '/etc/ssl/private/postgresql.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'

# 应用程序中的加密连接
# database-config.js
const config = {
  client: 'postgresql',
  connection: {
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    ssl: {
      rejectUnauthorized: true,
      ca: fs.readFileSync('/etc/ssl/certs/ca.crt').toString(),
      key: fs.readFileSync('/etc/ssl/private/client.key').toString(),
      cert: fs.readFileSync('/etc/ssl/certs/client.crt').toString()
    }
  }
};
```

## 访问控制与审计

严格的访问控制和全面的审计机制是保护敏感信息的重要保障。

### 基于角色的访问控制(RBAC)

```yaml
# rbac-policy.yaml
roles:
  developer:
    permissions:
      - read:config/development/*
      - write:config/development/*
      - read:secrets/development/*
    restrictions:
      - cannot_access:production_secrets
      - cannot_modify:base_config

  qa_engineer:
    permissions:
      - read:config/testing/*
      - write:config/testing/*
      - read:secrets/testing/*
      - read:config/staging/*
    restrictions:
      - cannot_access:production_secrets
      - cannot_modify:base_config

  operations:
    permissions:
      - read:config/*
      - write:config/staging/*
      - write:config/production/*
      - read:secrets/*
      - write:secrets/staging/*
      - write:secrets/production/*
    restrictions:
      - approval_required:production_changes

  security_admin:
    permissions:
      - read:secrets/*
      - write:secrets/*
      - manage:access_control
      - audit:all_activities
    restrictions:
      - none
```

### 细粒度访问控制

```javascript
// access-control.js
class AccessController {
  constructor() {
    this.policies = this.loadPolicies();
    this.permissions = new Map();
  }

  loadPolicies() {
    // 从配置文件加载策略
    const fs = require('fs');
    const yaml = require('js-yaml');
    return yaml.load(fs.readFileSync('./config/rbac-policy.yaml', 'utf8'));
  }

  async checkPermission(user, action, resource) {
    // 获取用户角色
    const userRoles = await this.getUserRoles(user);
    
    // 检查每个角色的权限
    for (const role of userRoles) {
      const rolePolicy = this.policies.roles[role];
      
      // 检查权限
      if (this.hasPermission(rolePolicy.permissions, action, resource)) {
        // 检查限制
        if (this.hasRestriction(rolePolicy.restrictions, action, resource)) {
          return false;
        }
        return true;
      }
    }
    
    return false;
  }

  hasPermission(permissions, action, resource) {
    for (const permission of permissions) {
      const [permAction, permResource] = permission.split(':');
      
      if (permAction === '*' || permAction === action) {
        if (this.matchesResource(permResource, resource)) {
          return true;
        }
      }
    }
    return false;
  }

  hasRestriction(restrictions, action, resource) {
    for (const restriction of restrictions) {
      if (restriction === 'none') return false;
      
      const [restrictType, restrictResource] = restriction.split(':');
      
      if (restrictType === 'cannot_access' && this.matchesResource(restrictResource, resource)) {
        return true;
      }
      
      if (restrictType === 'approval_required' && this.matchesResource(restrictResource, resource)) {
        return !this.hasApproval(action, resource);
      }
    }
    return false;
  }

  matchesResource(pattern, resource) {
    // 简单的通配符匹配
    const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
    return regex.test(resource);
  }

  async getUserRoles(user) {
    // 从用户管理系统获取用户角色
    // 这里简化处理
    const userRoles = {
      'dev-user': ['developer'],
      'qa-user': ['qa_engineer'],
      'ops-user': ['operations'],
      'sec-admin': ['security_admin', 'operations']
    };
    
    return userRoles[user] || [];
  }

  hasApproval(action, resource) {
    // 检查是否已获得审批
    // 这里简化处理
    return false;
  }
}

// 使用示例
const accessController = new AccessController();

// 检查开发者是否可以读取开发环境配置
accessController.checkPermission('dev-user', 'read', 'config/development/app.yaml')
  .then(allowed => {
    console.log('Developer can read dev config:', allowed);
  });

// 检查开发者是否可以写入生产环境配置
accessController.checkPermission('dev-user', 'write', 'config/production/app.yaml')
  .then(allowed => {
    console.log('Developer can write prod config:', allowed);
  });
```

### 全面审计机制

```javascript
// audit-logger.js
class AuditLogger {
  constructor() {
    this.auditTrail = [];
  }

  logEvent(eventType, user, resource, details = {}) {
    const auditEvent = {
      timestamp: new Date().toISOString(),
      eventType: eventType,
      user: user,
      resource: resource,
      details: details,
      ipAddress: this.getClientIP(),
      userAgent: this.getUserAgent(),
      sessionId: this.getSessionId()
    };

    this.auditTrail.push(auditEvent);
    
    // 持久化到数据库或日志系统
    this.persistEvent(auditEvent);
    
    // 实时监控和告警
    this.monitorEvent(auditEvent);
  }

  persistEvent(event) {
    // 写入审计日志数据库
    const fs = require('fs');
    const logEntry = JSON.stringify(event) + '\n';
    fs.appendFileSync('/var/log/audit-trail.log', logEntry);
  }

  monitorEvent(event) {
    // 敏感操作实时告警
    const sensitiveEvents = [
      'secrets.access',
      'secrets.modify',
      'config.production.modify',
      'access_control.change'
    ];

    if (sensitiveEvents.includes(event.eventType)) {
      this.sendAlert(event);
    }

    // 异常行为检测
    this.detectAnomalies(event);
  }

  sendAlert(event) {
    console.log(`SECURITY ALERT: ${event.eventType} by ${event.user} on ${event.resource}`);
    
    // 发送告警通知
    // this.sendSlackAlert(event);
    // this.sendEmailAlert(event);
  }

  detectAnomalies(event) {
    // 检测异常访问模式
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    
    const recentEvents = this.auditTrail.filter(e => 
      e.user === event.user && 
      new Date(e.timestamp) > oneHourAgo
    );
    
    if (recentEvents.length > 100) {
      console.log(`ANOMALY DETECTED: High frequency access by ${event.user}`);
    }
  }

  getClientIP() {
    return process.env.REMOTE_ADDR || '127.0.0.1';
  }

  getUserAgent() {
    return process.env.HTTP_USER_AGENT || 'unknown';
  }

  getSessionId() {
    return process.env.SESSION_ID || 'unknown';
  }

  getAuditTrail(filter = {}) {
    return this.auditTrail.filter(event => {
      for (const [key, value] of Object.entries(filter)) {
        if (event[key] !== value) {
          return false;
        }
      }
      return true;
    });
  }

  generateReport(startDate, endDate) {
    const filteredEvents = this.auditTrail.filter(event => {
      const eventDate = new Date(event.timestamp);
      return eventDate >= startDate && eventDate <= endDate;
    });

    const report = {
      period: { start: startDate, end: endDate },
      totalEvents: filteredEvents.length,
      eventTypes: this.countBy(filteredEvents, 'eventType'),
      users: this.countBy(filteredEvents, 'user'),
      resources: this.countBy(filteredEvents, 'resource'),
      sensitiveEvents: filteredEvents.filter(e => 
        e.eventType.includes('secrets') || e.eventType.includes('production')
      )
    };

    return report;
  }

  countBy(events, field) {
    const counts = {};
    for (const event of events) {
      const value = event[field];
      counts[value] = (counts[value] || 0) + 1;
    }
    return counts;
  }
}

// 使用示例
const auditLogger = new AuditLogger();

// 记录敏感信息访问
auditLogger.logEvent('secrets.access', 'ops-user', 'secret/myapp/database', {
  action: 'read',
  reason: 'application deployment'
});

// 记录配置变更
auditLogger.logEvent('config.production.modify', 'ops-user', 'config/production/app.yaml', {
  action: 'update',
  changes: { 'server.port': 443 },
  approval: 'APPROVAL-12345'
});

// 生成审计报告
const report = auditLogger.generateReport(
  new Date('2023-01-01'),
  new Date('2023-01-31')
);

console.log('Audit Report:', JSON.stringify(report, null, 2));
```

## 敏感信息轮换策略

定期轮换敏感信息是安全最佳实践的重要组成部分。

### 自动化轮换机制

```python
#!/usr/bin/env python3
# secret-rotator.py

import os
import time
import subprocess
import boto3
import requests
from datetime import datetime, timedelta

class SecretRotator:
    def __init__(self):
        self.vault_addr = os.environ.get('VAULT_ADDR', 'http://127.0.0.1:8200')
        self.vault_token = os.environ.get('VAULT_TOKEN')
        self.rotation_schedule = {
            'database_password': 90,  # 90天
            'api_key': 30,            # 30天
            'tls_certificate': 365    # 365天
        }
        
    def rotate_database_password(self):
        """轮换数据库密码"""
        print(f"{datetime.now()}: Rotating database password...")
        
        # 生成新密码
        new_password = self.generate_password(32)
        
        # 更新Vault中的密码
        self.update_vault_secret('secret/myapp/database', {
            'password': new_password
        })
        
        # 更新数据库用户密码
        self.update_database_user_password(new_password)
        
        # 通知应用程序重新加载配置
        self.notify_applications('database_password_rotated')
        
        # 记录轮换事件
        self.log_rotation_event('database_password', new_password)
        
        print(f"{datetime.now()}: Database password rotated successfully")
        
    def rotate_api_key(self):
        """轮换API密钥"""
        print(f"{datetime.now()}: Rotating API key...")
        
        # 生成新API密钥
        new_api_key = self.generate_api_key(64)
        
        # 更新Vault中的API密钥
        self.update_vault_secret('secret/myapp/api', {
            'key': new_api_key
        })
        
        # 更新第三方服务的API密钥
        self.update_third_party_api_key(new_api_key)
        
        # 通知应用程序重新加载配置
        self.notify_applications('api_key_rotated')
        
        # 记录轮换事件
        self.log_rotation_event('api_key', new_api_key)
        
        print(f"{datetime.now()}: API key rotated successfully")
        
    def generate_password(self, length):
        """生成安全密码"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
        
    def generate_api_key(self, length):
        """生成API密钥"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
        
    def update_vault_secret(self, path, data):
        """更新Vault中的密钥"""
        import hvac
        
        client = hvac.Client(url=self.vault_addr, token=self.vault_token)
        client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=data
        )
        
    def update_database_user_password(self, new_password):
        """更新数据库用户密码"""
        # 这里需要根据实际数据库类型实现
        # 示例：PostgreSQL
        conn_string = f"postgresql://admin:{os.environ.get('ADMIN_PASSWORD')}@{os.environ.get('DB_HOST')}/postgres"
        
        # 使用psql命令更新密码
        cmd = f"psql {conn_string} -c \"ALTER USER myapp_user WITH PASSWORD '{new_password}';\""
        subprocess.run(cmd, shell=True, check=True)
        
    def update_third_party_api_key(self, new_api_key):
        """更新第三方服务的API密钥"""
        # 这里需要根据具体第三方服务实现
        # 示例：更新AWS访问密钥
        iam = boto3.client('iam')
        # iam.update_access_key(...)
        
    def notify_applications(self, event):
        """通知应用程序"""
        # 可以通过HTTP webhook、消息队列等方式通知
        try:
            requests.post('http://localhost:3000/internal/secret-rotated', 
                         json={'event': event})
        except Exception as e:
            print(f"Failed to notify applications: {e}")
            
    def log_rotation_event(self, secret_type, new_value):
        """记录轮换事件"""
        with open('/var/log/secret-rotation.log', 'a') as f:
            f.write(f"{datetime.now()}: {secret_type} rotated\n")
            
    def check_rotation_due(self):
        """检查哪些密钥需要轮换"""
        due_rotations = []
        
        # 检查上次轮换时间
        try:
            with open('/var/log/secret-rotation.log', 'r') as f:
                lines = f.readlines()
                
            for secret_type, days in self.rotation_schedule.items():
                # 查找该密钥的最后轮换时间
                last_rotation = None
                for line in reversed(lines):
                    if secret_type in line:
                        last_rotation = datetime.fromisoformat(line.split(':')[0])
                        break
                        
                if last_rotation is None or \
                   datetime.now() - last_rotation > timedelta(days=days):
                    due_rotations.append(secret_type)
                    
        except FileNotFoundError:
            # 如果日志文件不存在，所有密钥都需要轮换
            due_rotations = list(self.rotation_schedule.keys())
            
        return due_rotations
        
    def run_rotation_cycle(self):
        """运行轮换周期"""
        due_rotations = self.check_rotation_due()
        
        for secret_type in due_rotations:
            try:
                if secret_type == 'database_password':
                    self.rotate_database_password()
                elif secret_type == 'api_key':
                    self.rotate_api_key()
                elif secret_type == 'tls_certificate':
                    self.rotate_tls_certificate()
            except Exception as e:
                print(f"Failed to rotate {secret_type}: {e}")
                # 发送告警
                self.send_alert(f"Secret rotation failed for {secret_type}: {e}")
                
    def send_alert(self, message):
        """发送告警"""
        print(f"ALERT: {message}")
        # 可以集成Slack、Email等告警系统

if __name__ == "__main__":
    rotator = SecretRotator()
    
    # 定期检查并轮换密钥
    while True:
        rotator.run_rotation_cycle()
        time.sleep(3600)  # 每小时检查一次
```

### 证书管理与轮换

```bash
# tls-certificate-manager.sh

# 使用Let's Encrypt自动获取和续期证书
#!/bin/bash

DOMAIN="myapp.example.com"
EMAIL="admin@example.com"
WEBROOT="/var/www/html"

# 获取证书
get_certificate() {
    certbot certonly \
        --webroot \
        --webroot-path $WEBROOT \
        --domain $DOMAIN \
        --email $EMAIL \
        --agree-tos \
        --non-interactive
}

# 续期证书
renew_certificate() {
    certbot renew --quiet
    
    # 如果续期成功，重启相关服务
    if [ $? -eq 0 ]; then
        systemctl reload nginx
        systemctl reload haproxy
    fi
}

# 转换证书格式
convert_certificate() {
    # 转换为PKCS#12格式
    openssl pkcs12 -export \
        -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem \
        -inkey /etc/letsencrypt/live/$DOMAIN/privkey.pem \
        -out /etc/ssl/certs/myapp.p12 \
        -passout pass:
        
    # 转换为Java keystore格式
    keytool -importkeystore \
        -deststorepass changeit \
        -destkeypass changeit \
        -destkeystore /etc/ssl/certs/myapp.jks \
        -srckeystore /etc/ssl/certs/myapp.p12 \
        -srcstoretype PKCS12 \
        -srcstorepass "" \
        -alias $DOMAIN
}

# 监控证书有效期
monitor_certificate() {
    CERT_FILE="/etc/letsencrypt/live/$DOMAIN/cert.pem"
    
    if [ -f "$CERT_FILE" ]; then
        EXPIRY_DATE=$(openssl x509 -in "$CERT_FILE" -noout -enddate | cut -d= -f2)
        EXPIRY_SECONDS=$(date -d "$EXPIRY_DATE" +%s)
        CURRENT_SECONDS=$(date +%s)
        DAYS_LEFT=$(( (EXPIRY_SECONDS - CURRENT_SECONDS) / 86400 ))
        
        if [ $DAYS_LEFT -lt 30 ]; then
            echo "Certificate for $DOMAIN expires in $DAYS_LEFT days"
            # 发送告警
        fi
    fi
}

# 根据命令行参数执行操作
case "$1" in
    get)
        get_certificate
        ;;
    renew)
        renew_certificate
        ;;
    convert)
        convert_certificate
        ;;
    monitor)
        monitor_certificate
        ;;
    *)
        echo "Usage: $0 {get|renew|convert|monitor}"
        exit 1
        ;;
esac
```

## 最佳实践总结

通过以上内容，我们可以总结出配置与敏感信息管理的最佳实践：

### 1. 敏感信息识别与分类
- 建立完整的敏感信息分类标准
- 定期扫描和识别敏感信息
- 维护敏感信息清单和责任人

### 2. 环境隔离策略
- 明确不同环境的安全级别
- 实施网络和访问控制隔离
- 使用环境特定的配置和凭证

### 3. 加密存储与传输
- 静态数据加密存储敏感信息
- 传输过程中使用TLS加密
- 集成专业的密钥管理系统

### 4. 访问控制与审计
- 实施基于角色的访问控制
- 记录完整的审计日志
- 实时监控和异常检测

### 5. 定期轮换机制
- 建立自动化的密钥轮换流程
- 定期更新证书和凭证
- 确保轮换过程不影响业务

敏感信息管理是配置管理中最具挑战性的领域之一，需要技术手段与管理流程相结合。通过实施这些最佳实践，可以显著提高应用程序的安全性，降低数据泄露风险。

第11章完整地覆盖了环境变量与配置文件管理的各个方面，从基础概念到高级实践，为读者提供了全面的指导。这些知识和技能对于构建安全、可靠的现代应用程序配置管理体系至关重要。