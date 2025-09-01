---
title: 附录B：常见配置管理脚本示例与模板
date: 2025-08-31
categories: [Configuration Management]
tags: [configuration-management, scripts, templates, automation, best-practices]
published: true
---

# 附录B：常见配置管理脚本示例与模板

在配置管理实践中，脚本和模板是实现自动化的重要工具。本附录提供了常见配置管理任务的脚本示例和模板，涵盖Ansible、Chef、Puppet、SaltStack等主流工具，以及通用的Shell和Python脚本，帮助读者快速上手配置管理自动化。

## 1. Ansible脚本示例与模板

### 1.1 基础Playbook模板

```yaml
# ansible-playbook-template.yml
---
- name: 基础配置管理Playbook模板
  hosts: all
  become: yes
  vars:
    # 定义变量
    app_name: "myapp"
    app_version: "1.0.0"
    config_dir: "/etc/{{ app_name }}"
    
  tasks:
    - name: 确保配置目录存在
      file:
        path: "{{ config_dir }}"
        state: directory
        owner: root
        group: root
        mode: '0755'
        
    - name: 部署应用配置文件
      template:
        src: app.conf.j2
        dest: "{{ config_dir }}/app.conf"
        owner: root
        group: root
        mode: '0644'
      notify: 重启应用服务
      
    - name: 部署环境特定配置
      template:
        src: "env/{{ env }}.conf.j2"
        dest: "{{ config_dir }}/env.conf"
        owner: root
        group: root
        mode: '0644'
      when: env is defined
      
    - name: 验证配置文件语法
      command: "app --validate-config {{ config_dir }}/app.conf"
      changed_when: false
      ignore_errors: yes
      
  handlers:
    - name: 重启应用服务
      service:
        name: "{{ app_name }}"
        state: restarted
```

### 1.2 配置文件模板 (Jinja2)

```jinja2
# app.conf.j2
# 应用配置文件模板
# 生成时间: {{ ansible_date_time.iso8601 }}

[application]
name = {{ app_name }}
version = {{ app_version }}
environment = {{ env | default('production') }}

[database]
host = {{ db_host | default('localhost') }}
port = {{ db_port | default(5432) }}
name = {{ db_name | default(app_name) }}
username = {{ db_username | default('appuser') }}
password = {{ db_password | default('apppassword') }}

[cache]
host = {{ cache_host | default('localhost') }}
port = {{ cache_port | default(6379) }}
ttl = {{ cache_ttl | default(3600) }}

[logging]
level = {{ log_level | default('INFO') }}
format = {{ log_format | default('json') }}
file = {{ log_file | default('/var/log/' + app_name + '.log') }}

[security]
ssl_enabled = {{ ssl_enabled | default(true) }}
cert_file = {{ cert_file | default('/etc/ssl/certs/' + app_name + '.crt') }}
key_file = {{ key_file | default('/etc/ssl/private/' + app_name + '.key') }}
```

### 1.3 环境特定配置模板

```jinja2
# env/production.conf.j2
# 生产环境配置

[performance]
worker_threads = 16
connection_pool_size = 100
request_timeout = 30

[monitoring]
enabled = true
endpoint = https://monitoring.example.com
api_key = {{ monitoring_api_key }}

[backup]
enabled = true
schedule = "0 2 * * *"
retention_days = 30
```

```jinja2
# env/staging.conf.j2
# 预发布环境配置

[performance]
worker_threads = 8
connection_pool_size = 50
request_timeout = 15

[monitoring]
enabled = true
endpoint = https://staging-monitoring.example.com
api_key = {{ monitoring_api_key }}

[backup]
enabled = true
schedule = "0 3 * * *"
retention_days = 7
```

### 1.4 高级Playbook示例

```yaml
# advanced-configuration-playbook.yml
---
- name: 高级配置管理Playbook
  hosts: webservers
  become: yes
  vars:
    nginx_config:
      worker_processes: "{{ ansible_processor_cores }}"
      worker_connections: 1024
      keepalive_timeout: 65
      
  pre_tasks:
    - name: 检查系统状态
      debug:
        msg: "开始配置{{ inventory_hostname }}"
        
  tasks:
    - name: 安装Nginx
      package:
        name: nginx
        state: present
        
    - name: 配置Nginx主配置文件
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        owner: root
        group: root
        mode: '0644'
      notify: 重载Nginx
        
    - name: 部署站点配置
      template:
        src: site.conf.j2
        dest: "/etc/nginx/sites-available/{{ item.name }}"
        owner: root
        group: root
        mode: '0644'
      loop: "{{ sites }}"
      notify: 重载Nginx
      register: site_config
      
    - name: 启用站点
      file:
        src: "/etc/nginx/sites-available/{{ item.item.name }}"
        dest: "/etc/nginx/sites-enabled/{{ item.item.name }}"
        state: link
      loop: "{{ site_config.results }}"
      when: item.changed
      notify: 重载Nginx
      
    - name: 验证Nginx配置
      command: nginx -t
      changed_when: false
      register: nginx_test
      failed_when: nginx_test.rc != 0
      
  handlers:
    - name: 重载Nginx
      service:
        name: nginx
        state: reloaded
        
  post_tasks:
    - name: 验证服务状态
      uri:
        url: "http://{{ ansible_default_ipv4.address }}"
        method: GET
        status_code: 200
      retries: 5
      delay: 10
```

## 2. Chef脚本示例与模板

### 2.1 Cookbook基础结构

```ruby
# metadata.rb
name 'myapp'
maintainer 'Your Company'
maintainer_email 'you@example.com'
license 'Apache-2.0'
description 'Installs/Configures myapp'
version '1.0.0'
chef_version '>= 14.0'

depends 'nginx'
depends 'database'
```

### 2.2 Recipe示例

```ruby
# recipes/default.rb
# 基础应用配置Recipe

# 安装应用包
package 'myapp' do
  action :install
end

# 创建配置目录
directory '/etc/myapp' do
  owner 'root'
  group 'root'
  mode '0755'
  action :create
end

# 部署主配置文件
template '/etc/myapp/app.conf' do
  source 'app.conf.erb'
  owner 'root'
  group 'root'
  mode '0644'
  variables(
    app_name: node['myapp']['name'],
    app_version: node['myapp']['version'],
    db_host: node['myapp']['database']['host'],
    db_port: node['myapp']['database']['port']
  )
  notifies :restart, 'service[myapp]', :delayed
end

# 配置应用服务
service 'myapp' do
  action [:enable, :start]
end

# 验证配置
execute 'validate-app-config' do
  command '/usr/bin/myapp --validate-config /etc/myapp/app.conf'
  action :run
  only_if { ::File.exist?('/etc/myapp/app.conf') }
end
```

### 2.3 模板文件 (ERB)

```erb
# templates/app.conf.erb
# 应用配置文件
# 生成时间: <%= Time.now.utc.iso8601 %>

[application]
name = <%= @app_name %>
version = <%= @app_version %>
environment = <%= node.chef_environment %>

[database]
host = <%= @db_host %>
port = <%= @db_port %>
name = <%= node['myapp']['database']['name'] %>
username = <%= node['myapp']['database']['username'] %>
password = <%= node['myapp']['database']['password'] %>

[cache]
host = <%= node['myapp']['cache']['host'] %>
port = <%= node['myapp']['cache']['port'] %>
ttl = <%= node['myapp']['cache']['ttl'] %>

[logging]
level = <%= node['myapp']['logging']['level'] %>
format = <%= node['myapp']['logging']['format'] %>
file = <%= node['myapp']['logging']['file'] %>

[security]
ssl_enabled = <%= node['myapp']['security']['ssl_enabled'] %>
cert_file = <%= node['myapp']['security']['cert_file'] %>
key_file = <%= node['myapp']['security']['key_file'] %>
```

### 2.4 Attributes文件

```ruby
# attributes/default.rb
# 默认属性配置

# 应用基本信息
default['myapp']['name'] = 'myapp'
default['myapp']['version'] = '1.0.0'

# 数据库配置
default['myapp']['database']['host'] = 'localhost'
default['myapp']['database']['port'] = 5432
default['myapp']['database']['name'] = 'myapp_db'
default['myapp']['database']['username'] = 'myapp_user'
default['myapp']['database']['password'] = 'myapp_password'

# 缓存配置
default['myapp']['cache']['host'] = 'localhost'
default['myapp']['cache']['port'] = 6379
default['myapp']['cache']['ttl'] = 3600

# 日志配置
default['myapp']['logging']['level'] = 'INFO'
default['myapp']['logging']['format'] = 'json'
default['myapp']['logging']['file'] = '/var/log/myapp.log'

# 安全配置
default['myapp']['security']['ssl_enabled'] = true
default['myapp']['security']['cert_file'] = '/etc/ssl/certs/myapp.crt'
default['myapp']['security']['key_file'] = '/etc/ssl/private/myapp.key'
```

## 3. Puppet脚本示例与模板

### 3.1 Manifest基础示例

```puppet
# manifests/init.pp
# 基础应用配置Manifest

class myapp (
  String $name = 'myapp',
  String $version = '1.0.0',
  Hash $database = {
    'host' => 'localhost',
    'port' => 5432,
  },
  Hash $cache = {
    'host' => 'localhost',
    'port' => 6379,
  }
) {
  # 安装应用包
  package { $name:
    ensure => installed,
  }
  
  # 创建配置目录
  file { "/etc/${name}":
    ensure => directory,
    owner  => 'root',
    group  => 'root',
    mode   => '0755',
  }
  
  # 部署配置文件
  file { "/etc/${name}/app.conf":
    ensure  => file,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    content => template('myapp/app.conf.erb'),
    require => File["/etc/${name}"],
    notify  => Service[$name],
  }
  
  # 配置服务
  service { $name:
    ensure => running,
    enable => true,
    require => Package[$name],
  }
  
  # 验证配置
  exec { "validate-${name}-config":
    command     => "/usr/bin/${name} --validate-config /etc/${name}/app.conf",
    refreshonly => true,
    subscribe   => File["/etc/${name}/app.conf"],
  }
}
```

### 3.2 模板文件 (ERB)

```erb
# templates/app.conf.erb
# 应用配置文件
# 生成时间: <%= Time.now.utc.iso8601 %>

[application]
name = <%= @name %>
version = <%= @version %>
environment = <%= @environment %>

[database]
host = <%= @database['host'] %>
port = <%= @database['port'] %>
name = <%= @database['name'] %>
username = <%= @database['username'] %>
password = <%= @database['password'] %>

[cache]
host = <%= @cache['host'] %>
port = <%= @cache['port'] %>
ttl = <%= @cache['ttl'] %>

[logging]
level = <%= @logging['level'] %>
format = <%= @logging['format'] %>
file = <%= @logging['file'] %>

[security]
ssl_enabled = <%= @security['ssl_enabled'] %>
cert_file = <%= @security['cert_file'] %>
key_file = <%= @security['key_file'] %>
```

### 3.3 Hiera配置示例

```yaml
# hieradata/common.yaml
---
myapp::name: 'myapp'
myapp::version: '1.0.0'

myapp::database:
  host: 'localhost'
  port: 5432
  name: 'myapp_db'
  username: 'myapp_user'
  password: 'myapp_password'

myapp::cache:
  host: 'localhost'
  port: 6379
  ttl: 3600

myapp::logging:
  level: 'INFO'
  format: 'json'
  file: '/var/log/myapp.log'

myapp::security:
  ssl_enabled: true
  cert_file: '/etc/ssl/certs/myapp.crt'
  key_file: '/etc/ssl/private/myapp.key'
```

```yaml
# hieradata/production.yaml
---
myapp::database:
  host: 'prod-db.example.com'
  port: 5432
  name: 'myapp_prod'
  username: 'myapp_prod_user'
  password: 'myapp_prod_password'

myapp::cache:
  host: 'prod-cache.example.com'
  port: 6379
  ttl: 7200

myapp::logging:
  level: 'WARN'
  file: '/var/log/myapp/prod.log'
```

## 4. SaltStack脚本示例与模板

### 4.1 State文件基础示例

```yaml
# states/myapp/init.sls
# 基础应用配置State

# 安装应用包
myapp-package:
  pkg.installed:
    - name: myapp

# 创建配置目录
myapp-config-dir:
  file.directory:
    - name: /etc/myapp
    - user: root
    - group: root
    - mode: 755
    - makedirs: True

# 部署配置文件
myapp-config-file:
  file.managed:
    - name: /etc/myapp/app.conf
    - source: salt://myapp/templates/app.conf.jinja
    - template: jinja
    - user: root
    - group: root
    - mode: 644
    - context:
        app_name: {{ pillar['myapp']['name'] }}
        app_version: {{ pillar['myapp']['version'] }}
        database: {{ pillar['myapp']['database'] }}
    - require:
      - file: myapp-config-dir
    - watch_in:
      - service: myapp-service

# 配置服务
myapp-service:
  service.running:
    - name: myapp
    - enable: True
    - require:
      - pkg: myapp-package

# 验证配置
validate-myapp-config:
  cmd.run:
    - name: /usr/bin/myapp --validate-config /etc/myapp/app.conf
    - onchanges:
      - file: myapp-config-file
```

### 4.2 Jinja2模板文件

```jinja2
# templates/app.conf.jinja
# 应用配置文件
# 生成时间: {{ salt['cmd.run']('date -Iseconds') }}

[application]
name = {{ app_name }}
version = {{ app_version }}
environment = {{ grains['environment'] | default('production') }}

[database]
host = {{ database.host }}
port = {{ database.port }}
name = {{ database.name }}
username = {{ database.username }}
password = {{ database.password }}

[cache]
host = {{ cache.host }}
port = {{ cache.port }}
ttl = {{ cache.ttl }}

[logging]
level = {{ logging.level }}
format = {{ logging.format }}
file = {{ logging.file }}

[security]
ssl_enabled = {{ security.ssl_enabled }}
cert_file = {{ security.cert_file }}
key_file = {{ security.key_file }}
```

### 4.3 Pillar数据示例

```yaml
# pillar/myapp.sls
# 应用Pillar数据

myapp:
  name: 'myapp'
  version: '1.0.0'
  
  database:
    host: 'localhost'
    port: 5432
    name: 'myapp_db'
    username: 'myapp_user'
    password: 'myapp_password'
    
  cache:
    host: 'localhost'
    port: 6379
    ttl: 3600
    
  logging:
    level: 'INFO'
    format: 'json'
    file: '/var/log/myapp.log'
    
  security:
    ssl_enabled: true
    cert_file: '/etc/ssl/certs/myapp.crt'
    key_file: '/etc/ssl/private/myapp.key'
```

```yaml
# pillar/myapp/production.sls
# 生产环境Pillar数据

myapp:
  database:
    host: 'prod-db.example.com'
    port: 5432
    name: 'myapp_prod'
    username: 'myapp_prod_user'
    password: 'myapp_prod_password'
    
  cache:
    host: 'prod-cache.example.com'
    port: 6379
    ttl: 7200
    
  logging:
    level: 'WARN'
    file: '/var/log/myapp/prod.log'
```

## 5. 通用Shell脚本示例

### 5.1 配置部署脚本

```bash
#!/bin/bash
# config-deploy.sh
# 通用配置部署脚本

set -e  # 遇到错误时退出

# 配置变量
APP_NAME="myapp"
CONFIG_DIR="/etc/${APP_NAME}"
TEMPLATE_DIR="./templates"
ENVIRONMENT="${1:-production}"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 错误处理函数
error_exit() {
    log "ERROR: $1"
    exit 1
}

# 检查依赖
check_dependencies() {
    log "检查依赖..."
    
    command -v jq >/dev/null 2>&1 || error_exit "jq未安装"
    command -v envsubst >/dev/null 2>&1 || error_exit "envsubst未安装"
    
    log "依赖检查通过"
}

# 加载环境变量
load_environment() {
    log "加载环境变量..."
    
    if [[ -f ".env.${ENVIRONMENT}" ]]; then
        export $(cat ".env.${ENVIRONMENT}" | xargs)
        log "已加载${ENVIRONMENT}环境变量"
    else
        log "警告: 未找到.env.${ENVIRONMENT}文件"
    fi
}

# 创建配置目录
create_config_dir() {
    log "创建配置目录..."
    
    mkdir -p "${CONFIG_DIR}" || error_exit "创建配置目录失败"
    chown root:root "${CONFIG_DIR}"
    chmod 755 "${CONFIG_DIR}"
}

# 部署配置文件
deploy_config_files() {
    log "部署配置文件..."
    
    # 部署主配置文件
    if [[ -f "${TEMPLATE_DIR}/app.conf.template" ]]; then
        envsubst < "${TEMPLATE_DIR}/app.conf.template" > "${CONFIG_DIR}/app.conf"
        chown root:root "${CONFIG_DIR}/app.conf"
        chmod 644 "${CONFIG_DIR}/app.conf"
        log "主配置文件部署完成"
    else
        error_exit "未找到主配置文件模板"
    fi
    
    # 部署环境特定配置
    if [[ -f "${TEMPLATE_DIR}/env/${ENVIRONMENT}.conf.template" ]]; then
        envsubst < "${TEMPLATE_DIR}/env/${ENVIRONMENT}.conf.template" > "${CONFIG_DIR}/env.conf"
        chown root:root "${CONFIG_DIR}/env.conf"
        chmod 644 "${CONFIG_DIR}/env.conf"
        log "环境配置文件部署完成"
    fi
}

# 验证配置
validate_config() {
    log "验证配置文件..."
    
    if command -v "${APP_NAME}" >/dev/null 2>&1; then
        if "${APP_NAME}" --validate-config "${CONFIG_DIR}/app.conf"; then
            log "配置验证通过"
        else
            error_exit "配置验证失败"
        fi
    else
        log "警告: 未找到${APP_NAME}命令，跳过配置验证"
    fi
}

# 重启服务
restart_service() {
    log "重启服务..."
    
    if systemctl is-active --quiet "${APP_NAME}"; then
        systemctl restart "${APP_NAME}" || error_exit "重启服务失败"
        log "服务重启完成"
    else
        systemctl start "${APP_NAME}" || error_exit "启动服务失败"
        log "服务启动完成"
    fi
}

# 备份现有配置
backup_config() {
    log "备份现有配置..."
    
    if [[ -f "${CONFIG_DIR}/app.conf" ]]; then
        cp "${CONFIG_DIR}/app.conf" "${CONFIG_DIR}/app.conf.backup.$(date +%Y%m%d%H%M%S)"
        log "配置备份完成"
    fi
}

# 主函数
main() {
    log "开始部署${APP_NAME}配置 (${ENVIRONMENT})"
    
    check_dependencies
    load_environment
    backup_config
    create_config_dir
    deploy_config_files
    validate_config
    
    # 询问是否重启服务
    read -p "是否重启服务? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        restart_service
    fi
    
    log "${APP_NAME}配置部署完成"
}

# 执行主函数
main "$@"
```

### 5.2 环境变量文件模板

```bash
# .env.template
# 环境变量模板文件

# 应用配置
APP_NAME=myapp
APP_VERSION=1.0.0

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp_db
DB_USERNAME=myapp_user
DB_PASSWORD=myapp_password

# 缓存配置
CACHE_HOST=localhost
CACHE_PORT=6379
CACHE_TTL=3600

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/myapp.log

# 安全配置
SSL_ENABLED=true
CERT_FILE=/etc/ssl/certs/myapp.crt
KEY_FILE=/etc/ssl/private/myapp.key
```

```bash
# .env.production
# 生产环境变量文件

# 应用配置
APP_NAME=myapp
APP_VERSION=1.0.0

# 数据库配置
DB_HOST=prod-db.example.com
DB_PORT=5432
DB_NAME=myapp_prod
DB_USERNAME=myapp_prod_user
DB_PASSWORD=supersecretpassword

# 缓存配置
CACHE_HOST=prod-cache.example.com
CACHE_PORT=6379
CACHE_TTL=7200

# 日志配置
LOG_LEVEL=WARN
LOG_FORMAT=json
LOG_FILE=/var/log/myapp/prod.log

# 安全配置
SSL_ENABLED=true
CERT_FILE=/etc/ssl/certs/myapp.crt
KEY_FILE=/etc/ssl/private/myapp.key
```

## 6. Python脚本示例

### 6.1 配置管理工具类

```python
#!/usr/bin/env python3
# config-manager.py
# Python配置管理工具

import os
import json
import yaml
import argparse
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import shutil
import subprocess
from datetime import datetime

class ConfigManager:
    def __init__(self, config_dir: str = "/etc/myapp", template_dir: str = "./templates"):
        self.config_dir = Path(config_dir)
        self.template_dir = Path(template_dir)
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_path = self.config_dir / config_file
        
        if not config_path.exists():
            self.logger.warning(f"配置文件不存在: {config_path}")
            return {}
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    # 假设是INI格式或其他文本格式
                    return f.read()
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return {}
    
    def save_config(self, config_file: str, config_data: Dict[str, Any]) -> bool:
        """保存配置文件"""
        config_path = self.config_dir / config_file
        
        try:
            # 创建目录
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                elif config_path.suffix.lower() == '.json':
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                else:
                    f.write(str(config_data))
                    
            self.logger.info(f"配置文件保存成功: {config_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
            return False
    
    def deploy_template(self, template_file: str, output_file: str, 
                       context: Optional[Dict[str, Any]] = None) -> bool:
        """部署模板文件"""
        template_path = self.template_dir / template_file
        output_path = self.config_dir / output_file
        
        if not template_path.exists():
            self.logger.error(f"模板文件不存在: {template_path}")
            return False
            
        try:
            # 创建输出目录
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取模板
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 替换变量
            if context:
                for key, value in context.items():
                    template_content = template_content.replace(f"{{{{{key}}}}}", str(value))
            
            # 写入输出文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
                
            self.logger.info(f"模板部署成功: {template_path} -> {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"模板部署失败: {e}")
            return False
    
    def backup_config(self, config_file: str) -> bool:
        """备份配置文件"""
        config_path = self.config_dir / config_file
        backup_path = self.config_dir / f"{config_file}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if not config_path.exists():
            self.logger.warning(f"配置文件不存在，无需备份: {config_path}")
            return True
            
        try:
            shutil.copy2(config_path, backup_path)
            self.logger.info(f"配置文件备份成功: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"配置文件备份失败: {e}")
            return False
    
    def validate_config(self, config_file: str, validator_cmd: str) -> bool:
        """验证配置文件"""
        config_path = self.config_dir / config_file
        
        if not config_path.exists():
            self.logger.warning(f"配置文件不存在: {config_path}")
            return False
            
        try:
            cmd = validator_cmd.format(config_file=str(config_path))
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"配置文件验证通过: {config_path}")
                return True
            else:
                self.logger.error(f"配置文件验证失败: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"配置文件验证出错: {e}")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """重启服务"""
        try:
            # 检查服务状态
            result = subprocess.run(
                ["systemctl", "is-active", service_name], 
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # 重启服务
                subprocess.run(["systemctl", "restart", service_name], check=True)
                self.logger.info(f"服务重启成功: {service_name}")
            else:
                # 启动服务
                subprocess.run(["systemctl", "start", service_name], check=True)
                self.logger.info(f"服务启动成功: {service_name}")
                
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"服务操作失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"服务操作出错: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='配置管理工具')
    parser.add_argument('--config-dir', default='/etc/myapp', help='配置目录')
    parser.add_argument('--template-dir', default='./templates', help='模板目录')
    parser.add_argument('--action', required=True, 
                       choices=['deploy', 'backup', 'validate', 'restart'],
                       help='操作类型')
    parser.add_argument('--config-file', help='配置文件名')
    parser.add_argument('--template-file', help='模板文件名')
    parser.add_argument('--service-name', help='服务名称')
    parser.add_argument('--validator-cmd', help='验证命令')
    parser.add_argument('--context', help='模板上下文 (JSON格式)')
    
    args = parser.parse_args()
    
    # 创建配置管理器
    config_manager = ConfigManager(args.config_dir, args.template_dir)
    
    # 执行操作
    if args.action == 'deploy':
        context = json.loads(args.context) if args.context else {}
        success = config_manager.deploy_template(
            args.template_file, args.config_file, context
        )
    elif args.action == 'backup':
        success = config_manager.backup_config(args.config_file)
    elif args.action == 'validate':
        success = config_manager.validate_config(args.config_file, args.validator_cmd)
    elif args.action == 'restart':
        success = config_manager.restart_service(args.service_name)
    else:
        success = False
    
    exit(0 if success else 1)

if __name__ == '__main__':
    main()
```

### 6.2 配置文件模板

```yaml
# templates/app-config.yaml.j2
# YAML配置文件模板

# 应用配置
application:
  name: {{ app_name }}
  version: {{ app_version }}
  environment: {{ environment | default('production') }}

# 数据库配置
database:
  host: {{ db_host }}
  port: {{ db_port }}
  name: {{ db_name }}
  username: {{ db_username }}
  password: {{ db_password }}

# 缓存配置
cache:
  host: {{ cache_host }}
  port: {{ cache_port }}
  ttl: {{ cache_ttl }}

# 日志配置
logging:
  level: {{ log_level }}
  format: {{ log_format }}
  file: {{ log_file }}

# 安全配置
security:
  ssl_enabled: {{ ssl_enabled }}
  cert_file: {{ cert_file }}
  key_file: {{ key_file }}

# 生成时间
generated_at: {{ generated_at }}
```

## 7. 最佳实践建议

### 7.1 脚本编写规范

```markdown
# 脚本编写最佳实践

## 1. 错误处理
- 使用set -e确保脚本在出错时退出
- 实现适当的错误处理和日志记录
- 提供有意义的错误消息

## 2. 可配置性
- 使用环境变量或配置文件
- 支持命令行参数
- 提供默认值

## 3. 安全性
- 验证输入参数
- 使用适当的文件权限
- 避免硬编码敏感信息

## 4. 可维护性
- 添加详细的注释
- 使用函数组织代码
- 遵循一致的命名约定

## 5. 可测试性
- 支持dry-run模式
- 提供验证机制
- 记录操作日志
```

### 7.2 模板设计原则

```markdown
# 模板设计原则

## 1. 清晰性
- 使用描述性的变量名
- 添加必要的注释
- 保持结构清晰

## 2. 灵活性
- 提供合理的默认值
- 支持条件渲染
- 允许覆盖配置

## 3. 安全性
- 避免暴露敏感信息
- 使用适当的转义
- 验证输入数据

## 4. 可维护性
- 使用版本控制
- 文档化模板变量
- 定期审查和更新
```

## 总结

本附录提供了配置管理中常用的脚本示例和模板，涵盖了主流的配置管理工具以及通用的Shell和Python脚本。这些示例和模板可以作为实际项目中的参考，帮助读者快速实现配置管理自动化。

在使用这些脚本和模板时，需要注意：

1. **安全性**: 避免在代码中硬编码敏感信息，使用安全的变量传递方式
2. **可配置性**: 提供足够的配置选项以适应不同的环境和需求
3. **错误处理**: 实现完善的错误处理机制，确保脚本的健壮性
4. **日志记录**: 添加详细的日志记录，便于问题排查和审计
5. **测试验证**: 在生产环境使用前进行充分的测试和验证

通过合理使用这些脚本和模板，可以大大提高配置管理的效率和可靠性，实现基础设施和应用配置的自动化管理。