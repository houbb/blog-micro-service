---
title: Ansible的基本模块与常用操作：构建自动化配置管理的核心组件
date: 2025-08-31
categories: [Configuration Management]
tags: [ansible, modules, operations, automation, devops]
published: true
---

# 5.3 Ansible的基本模块与常用操作

Ansible的强大功能很大程度上源于其丰富的模块生态系统。模块是Ansible执行具体任务的组件，每个模块都专注于特定的功能领域。掌握Ansible的基本模块和常用操作是有效使用Ansible进行自动化配置管理的关键。本节将详细介绍Ansible的核心模块及其使用方法。

## Ansible模块分类

### 1. 系统模块

系统模块用于管理操作系统级别的配置和资源。

#### 包管理模块

```yaml
# 包管理模块示例
tasks:
  # YUM包管理 (RedHat/CentOS)
  - name: Install packages with YUM
    yum:
      name:
        - nginx
        - mysql-server
        - python3
      state: present
  
  # APT包管理 (Debian/Ubuntu)
  - name: Install packages with APT
    apt:
      name:
        - nginx
        - mysql-server
        - python3
      state: present
      update_cache: yes
  
  # DNF包管理 (Fedora)
  - name: Install packages with DNF
    dnf:
      name:
        - nginx
        - mysql-server
      state: present
  
  # 包状态管理
  - name: Ensure package is latest version
    yum:
      name: nginx
      state: latest
  
  - name: Remove package
    yum:
      name: old-package
      state: absent
  
  # 特定版本安装
  - name: Install specific version
    yum:
      name: nginx-1.20.1
      state: present
```

#### 服务管理模块

```yaml
# 服务管理模块示例
tasks:
  # 基本服务管理
  - name: Start and enable service
    service:
      name: nginx
      state: started
      enabled: yes
  
  # 服务重启
  - name: Restart service
    service:
      name: nginx
      state: restarted
  
  # 服务停止
  - name: Stop service
    service:
      name: nginx
      state: stopped
  
  # 服务状态检查
  - name: Check service status
    service:
      name: nginx
      state: status
    register: service_status
  
  - name: Display service status
    debug:
      msg: "Nginx service is {{ 'running' if service_status.status.ActiveState == 'active' else 'stopped' }}"
  
  # 系统特定服务管理
  - name: Manage systemd service
    systemd:
      name: nginx
      state: started
      enabled: yes
      daemon_reload: yes
```

#### 用户和组管理模块

```yaml
# 用户和组管理模块示例
tasks:
  # 创建用户组
  - name: Create user groups
    group:
      name: "{{ item.name }}"
      gid: "{{ item.gid | default(omit) }}"
      state: present
    loop:
      - { name: "webapps", gid: 2000 }
      - { name: "database", gid: 2001 }
      - { name: "backup" }
  
  # 创建用户
  - name: Create system users
    user:
      name: "{{ item.name }}"
      uid: "{{ item.uid | default(omit) }}"
      group: "{{ item.group | default(omit) }}"
      groups: "{{ item.groups | default(omit) }}"
      shell: "{{ item.shell | default('/bin/bash') }}"
      home: "{{ item.home | default('/home/' + item.name) }}"
      create_home: "{{ item.create_home | default(true) }}"
      state: present
    loop:
      - { name: "webuser", uid: 2000, group: "webapps", home: "/var/www" }
      - { name: "dbuser", uid: 2001, group: "database", shell: "/bin/false" }
      - { name: "backupuser", groups: ["backup", "webapps"] }
  
  # 用户权限管理
  - name: Add user to sudoers
    lineinfile:
      path: /etc/sudoers
      line: "{{ item.user }} ALL=(ALL) NOPASSWD: ALL"
      validate: 'visudo -cf %s'
    loop:
      - { user: "webuser" }
      - { user: "dbuser" }
```

#### 文件和目录管理模块

```yaml
# 文件和目录管理模块示例
tasks:
  # 目录管理
  - name: Create application directories
    file:
      path: "{{ item.path }}"
      state: directory
      owner: "{{ item.owner | default('root') }}"
      group: "{{ item.group | default('root') }}"
      mode: "{{ item.mode | default('0755') }}"
    loop:
      - { path: "/var/www/myapp", owner: "webuser", group: "webapps", mode: "0755" }
      - { path: "/var/log/myapp", owner: "webuser", group: "webapps", mode: "0750" }
      - { path: "/etc/myapp", owner: "root", group: "root", mode: "0755" }
  
  # 文件管理
  - name: Manage configuration files
    file:
      path: "{{ item.path }}"
      state: "{{ item.state | default('file') }}"
      owner: "{{ item.owner | default('root') }}"
      group: "{{ item.group | default('root') }}"
      mode: "{{ item.mode | default('0644') }}"
    loop:
      - { path: "/etc/myapp/app.conf", mode: "0644" }
      - { path: "/etc/myapp/ssl.key", mode: "0600", owner: "root", group: "root" }
      - { path: "/var/www/myapp/uploads", state: "absent" }
  
  # 符号链接管理
  - name: Create symbolic links
    file:
      src: "{{ item.src }}"
      dest: "{{ item.dest }}"
      state: link
    loop:
      - { src: "/var/www/myapp/releases/1.2.3", dest: "/var/www/myapp/current" }
      - { src: "/etc/myapp/config.prod.yml", dest: "/etc/myapp/config.yml" }
```

### 2. 文件操作模块

文件操作模块用于处理文件内容、传输和模板化。

#### 模板模块

```yaml
# 模板模块示例
tasks:
  # 基本模板部署
  - name: Deploy Nginx configuration
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
      owner: root
      group: root
      mode: '0644'
    notify: restart nginx
  
  # 条件性模板部署
  - name: Deploy SSL configuration if enabled
    template:
      src: ssl.conf.j2
      dest: /etc/nginx/conf.d/ssl.conf
      owner: root
      group: root
      mode: '0644'
    when: ssl_enabled | default(false)
    notify: reload nginx
  
  # 多环境模板
  - name: Deploy environment-specific configuration
    template:
      src: "app.conf.{{ ansible_env.DEPLOY_ENV | default('development') }}.j2"
      dest: /etc/myapp/app.conf
      owner: root
      group: root
      mode: '0644'
```

```jinja2
{# templates/nginx.conf.j2 #}
# Nginx Configuration
user {{ nginx_user | default('nginx') }};
worker_processes {{ nginx_worker_processes | default('auto') }};

error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections {{ nginx_worker_connections | default(1024) }};
}

http {
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout {{ nginx_keepalive_timeout | default(65) }};
    
    # Server configuration
    server {
        listen {{ http_port | default(80) }};
        server_name {{ server_name | default('_') }};
        
        {% if ssl_enabled | default(false) %}
        listen {{ https_port | default(443) }} ssl;
        ssl_certificate {{ ssl_cert_path | default('/etc/ssl/certs/nginx.crt') }};
        ssl_certificate_key {{ ssl_key_path | default('/etc/ssl/private/nginx.key') }};
        {% endif %}
        
        location / {
            root {{ document_root | default('/usr/share/nginx/html') }};
            index index.html index.htm;
        }
    }
}
```

#### 复制模块

```yaml
# 复制模块示例
tasks:
  # 基本文件复制
  - name: Deploy static files
    copy:
      src: files/index.html
      dest: /var/www/html/index.html
      owner: nginx
      group: nginx
      mode: '0644'
  
  # 目录复制
  - name: Deploy application files
    copy:
      src: files/myapp/
      dest: /var/www/myapp/
      owner: webuser
      group: webapps
      mode: '0644'
  
  # 内容直接写入
  - name: Create configuration file with content
    copy:
      content: |
        # Application Configuration
        app.name={{ app_name }}
        app.version={{ app_version }}
        app.debug={{ debug_mode | default(false) }}
      dest: /etc/myapp/app.conf
      owner: root
      group: root
      mode: '0644'
  
  # 备份和验证
  - name: Copy file with backup
    copy:
      src: files/critical.conf
      dest: /etc/critical.conf
      owner: root
      group: root
      mode: '0600'
      backup: yes
      validate: "/usr/sbin/nginx -t -c %s"
```

#### 行内文件模块

```yaml
# 行内文件模块示例
tasks:
  # 添加或修改行
  - name: Configure SSH security
    lineinfile:
      path: /etc/ssh/sshd_config
      regexp: "{{ item.regexp }}"
      line: "{{ item.line }}"
      backup: yes
    loop:
      - { regexp: '^#?PermitRootLogin', line: 'PermitRootLogin no' }
      - { regexp: '^#?PasswordAuthentication', line: 'PasswordAuthentication no' }
      - { regexp: '^#?PubkeyAuthentication', line: 'PubkeyAuthentication yes' }
    notify: restart sshd
  
  # 删除行
  - name: Remove deprecated configuration
    lineinfile:
      path: /etc/myapp/app.conf
      regexp: "^deprecated_.*"
      state: absent
  
  # 插入块
  - name: Insert configuration block
    blockinfile:
      path: /etc/myapp/app.conf
      marker: "# {mark} ANSIBLE MANAGED BLOCK"
      block: |
        # Database configuration
        database.host={{ db_host }}
        database.port={{ db_port }}
        database.name={{ db_name }}
      insertafter: EOF
```

### 3. 网络模块

网络模块用于管理网络配置和连接。

#### 网络命令模块

```yaml
# 网络命令模块示例
tasks:
  # 基本网络命令
  - name: Check network connectivity
    command: ping -c 4 {{ item }}
    register: ping_result
    ignore_errors: yes
    loop:
      - "8.8.8.8"
      - "1.1.1.1"
  
  - name: Display ping results
    debug:
      msg: "Ping to {{ item.item }}: {{ 'Success' if item.rc == 0 else 'Failed' }}"
    loop: "{{ ping_result.results }}"
  
  # 网络服务管理
  - name: Manage firewall
    firewalld:
      service: "{{ item.service }}"
      permanent: yes
      state: "{{ item.state }}"
      immediate: yes
    loop:
      - { service: "http", state: "enabled" }
      - { service: "https", state: "enabled" }
      - { service: "ssh", state: "enabled" }
  
  # 网络接口配置
  - name: Configure network interface
    nmcli:
      conn_name: eth0
      ifname: eth0
      type: ethernet
      ip4: "{{ item.ip }}/24"
      gw4: "{{ item.gw }}"
      state: present
    loop:
      - { ip: "192.168.1.100", gw: "192.168.1.1" }
      - { ip: "10.0.0.100", gw: "10.0.0.1" }
```

#### URL获取模块

```yaml
# URL获取模块示例
tasks:
  # 下载文件
  - name: Download application package
    get_url:
      url: "https://example.com/myapp-{{ app_version }}.tar.gz"
      dest: "/tmp/myapp-{{ app_version }}.tar.gz"
      mode: '0644'
      checksum: "sha256:{{ app_checksum }}"
      timeout: 300
  
  # 条件性下载
  - name: Download only if file doesn't exist
    get_url:
      url: "https://example.com/config.yml"
      dest: "/etc/myapp/remote-config.yml"
      force: no
    when: not ansible_check_mode
  
  # 带认证的下载
  - name: Download from protected endpoint
    get_url:
      url: "https://api.example.com/v1/config"
      dest: "/etc/myapp/api-config.json"
      headers:
        Authorization: "Bearer {{ api_token }}"
        Accept: "application/json"
      force_basic_auth: yes
```

### 4. 命令和Shell模块

命令和Shell模块用于执行系统命令。

#### 命令模块

```yaml
# 命令模块示例
tasks:
  # 基本命令执行
  - name: Check system uptime
    command: uptime
    register: uptime_result
  
  - name: Display uptime
    debug:
      msg: "System uptime: {{ uptime_result.stdout }}"
  
  # 带参数的命令
  - name: Create directory with specific permissions
    command: mkdir -p /var/www/myapp/{{ item }}
    args:
      chdir: /var/www/myapp
    loop:
      - "logs"
      - "cache"
      - "tmp"
  
  # 命令执行条件
  - name: Run database migration only if needed
    command: /usr/local/bin/check-migration-needed.sh
    register: migration_check
    changed_when: migration_check.stdout == "migration_needed"
    check_mode: no
  
  - name: Execute database migration
    command: /usr/local/bin/run-migration.sh
    when: migration_check.stdout == "migration_needed"
```

#### Shell模块

```yaml
# Shell模块示例
tasks:
  # 基本Shell执行
  - name: Check disk usage
    shell: df -h | grep -E '(/$|/var)' | awk '{print $5}' | sed 's/%//'
    register: disk_usage
  
  - name: Display disk usage
    debug:
      msg: "Disk usage: {{ disk_usage.stdout_lines }}"
  
  # 复杂Shell脚本
  - name: Execute complex deployment script
    shell: |
      #!/bin/bash
      set -e
      
      # Backup current version
      if [ -d "/var/www/myapp/current" ]; then
        cp -r /var/www/myapp/current /var/www/myapp/backup-$(date +%Y%m%d-%H%M%S)
      fi
      
      # Extract new version
      tar -xzf /tmp/myapp-{{ app_version }}.tar.gz -C /var/www/myapp/
      
      # Update symlink
      ln -sfn /var/www/myapp/myapp-{{ app_version }} /var/www/myapp/current
      
      # Run post-deployment scripts
      /var/www/myapp/current/scripts/post-deploy.sh
    args:
      executable: /bin/bash
    register: deployment_result
    changed_when: deployment_result.rc == 0
```

### 5. 云和虚拟化模块

云和虚拟化模块用于管理云资源和虚拟机。

#### AWS模块

```yaml
# AWS模块示例
tasks:
  # EC2实例管理
  - name: Launch EC2 instances
    ec2:
      key_name: "{{ aws_key_name }}"
      group: "{{ aws_security_group }}"
      instance_type: "{{ aws_instance_type | default('t3.micro') }}"
      image: "{{ aws_ami_id }}"
      wait: yes
      count: "{{ instance_count | default(1) }}"
      vpc_subnet_id: "{{ aws_subnet_id }}"
      assign_public_ip: yes
      instance_tags:
        Name: "{{ item.name }}"
        Environment: "{{ deploy_environment }}"
      region: "{{ aws_region }}"
    loop:
      - { name: "web01" }
      - { name: "web02" }
      - { name: "db01" }
    register: ec2_instances
  
  # S3存储桶管理
  - name: Create S3 bucket
    s3_bucket:
      name: "{{ s3_bucket_name }}"
      state: present
      region: "{{ aws_region }}"
      versioning: yes
      encryption: AES256
  
  # RDS数据库管理
  - name: Create RDS instance
    rds:
      command: create
      instance_name: "{{ db_instance_name }}"
      db_engine: mysql
      db_engine_version: "{{ mysql_version | default('8.0') }}"
      instance_type: "{{ db_instance_type | default('db.t3.micro') }}"
      username: "{{ db_username }}"
      password: "{{ db_password }}"
      db_name: "{{ db_name }}"
      region: "{{ aws_region }}"
      wait: yes
```

#### Docker模块

```yaml
# Docker模块示例
tasks:
  # Docker镜像管理
  - name: Pull Docker images
    docker_image:
      name: "{{ item.image }}"
      source: pull
      force_source: "{{ item.force | default(false) }}"
    loop:
      - { image: "nginx:1.21", force: true }
      - { image: "mysql:8.0" }
      - { image: "redis:6.2" }
  
  # Docker容器管理
  - name: Run application containers
    docker_container:
      name: "{{ item.name }}"
      image: "{{ item.image }}"
      state: started
      restart: yes
      ports: "{{ item.ports | default(omit) }}"
      volumes: "{{ item.volumes | default(omit) }}"
      env: "{{ item.env | default(omit) }}"
      networks: "{{ item.networks | default(omit) }}"
    loop:
      - { 
          name: "web-server",
          image: "nginx:1.21",
          ports: ["80:80", "443:443"],
          volumes: ["/var/www:/usr/share/nginx/html"]
        }
      - {
          name: "database",
          image: "mysql:8.0",
          env: {
            MYSQL_ROOT_PASSWORD: "{{ db_root_password }}",
            MYSQL_DATABASE: "{{ db_name }}"
          },
          volumes: ["/var/lib/mysql:/var/lib/mysql"]
        }
  
  # Docker网络管理
  - name: Create Docker network
    docker_network:
      name: "{{ app_network_name }}"
      driver: bridge
      ipam_config:
        - subnet: "{{ docker_subnet | default('172.20.0.0/16') }}"
          gateway: "{{ docker_gateway | default('172.20.0.1') }}"
```

## 模块使用最佳实践

### 1. 模块选择原则

```yaml
# 模块选择最佳实践示例
tasks:
  # 优先使用专用模块而非通用命令
  # 好的做法
  - name: Install package (good)
    yum:
      name: nginx
      state: present
  
  # 避免的做法
  - name: Install package (avoid)
    command: yum install -y nginx
    changed_when: true  # 需要手动指定变更条件
  
  # 使用幂等性模块
  - name: Ensure user exists (idempotent)
    user:
      name: myuser
      state: present
  
  # 避免非幂等操作
  - name: Create user (non-idempotent - avoid)
    command: useradd myuser
    changed_when: true
```

### 2. 错误处理和验证

```yaml
# 模块错误处理示例
tasks:
  # 使用模块内置验证
  - name: Deploy configuration with validation
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
      validate: "/usr/sbin/nginx -t -c %s"
    notify: restart nginx
  
  # 自定义变更检测
  - name: Update configuration file
    copy:
      src: app.conf
      dest: /etc/myapp/app.conf
      mode: '0644'
    register: config_result
    notify: reload service
  
  # 条件性执行
  - name: Restart service only if configuration changed
    service:
      name: myapp
      state: restarted
    when: config_result.changed
```

### 3. 性能优化

```yaml
# 模块性能优化示例
tasks:
  # 批量操作优于单个操作
  # 好的做法
  - name: Install multiple packages (efficient)
    yum:
      name:
        - nginx
        - mysql-server
        - python3
        - git
      state: present
  
  # 避免的做法
  - name: Install packages individually (inefficient)
    yum:
      name: "{{ item }}"
      state: present
    loop:
      - nginx
      - mysql-server
      - python3
      - git
  
  # 使用异步执行长时间任务
  - name: Execute long-running task asynchronously
    command: /usr/local/bin/long-running-task.sh
    async: 3600
    poll: 0
    register: long_task
  
  - name: Check task status
    async_status:
      jid: "{{ long_task.ansible_job_id }}"
    register: job_result
    until: job_result.finished
    retries: 30
    delay: 10
```

## 自定义模块开发

### 1. 基本自定义模块

```python
# 自定义模块示例: health_check.py
#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import requests
import json

def main():
    module = AnsibleModule(
        argument_spec=dict(
            url=dict(required=True, type='str'),
            expected_status=dict(default=200, type='int'),
            timeout=dict(default=30, type='int'),
            headers=dict(type='dict', default={}),
            validate_ssl=dict(default=True, type='bool')
        ),
        supports_check_mode=True
    )
    
    url = module.params['url']
    expected_status = module.params['expected_status']
    timeout = module.params['timeout']
    headers = module.params['headers']
    validate_ssl = module.params['validate_ssl']
    
    if module.check_mode:
        module.exit_json(changed=False, msg="Check mode enabled")
    
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            verify=validate_ssl
        )
        
        result = {
            'url': url,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'content_length': len(response.content)
        }
        
        if response.status_code == expected_status:
            module.exit_json(
                changed=False,
                msg=f"Health check passed for {url}",
                result=result
            )
        else:
            module.fail_json(
                msg=f"Health check failed for {url}. Expected {expected_status}, got {response.status_code}",
                result=result
            )
    
    except requests.exceptions.RequestException as e:
        module.fail_json(
            msg=f"Health check failed for {url}: {str(e)}",
            exception=str(e)
        )

if __name__ == '__main__':
    main()
```

使用自定义模块：

```yaml
# 使用自定义健康检查模块
tasks:
  - name: Check application health
    health_check:
      url: "https://{{ inventory_hostname }}/health"
      expected_status: 200
      timeout: 10
      headers:
        User-Agent: "Ansible/HealthCheck"
    register: health_result
  
  - name: Display health check results
    debug:
      msg: |
        Health check for {{ health_result.result.url }}:
        Status: {{ health_result.result.status_code }}
        Response time: {{ health_result.result.response_time }}s
        Content length: {{ health_result.result.content_length }} bytes
```

### 2. 模块文档

```python
# 模块文档示例
DOCUMENTATION = '''
---
module: health_check
short_description: Check HTTP endpoint health
description:
  - Check the health of HTTP endpoints by making requests and validating responses
version_added: "2.9"
author:
  - "Your Name (@yourgithub)"
options:
  url:
    description:
      - The URL to check
    required: true
    type: str
  expected_status:
    description:
      - The expected HTTP status code
    default: 200
    type: int
  timeout:
    description:
      - Request timeout in seconds
    default: 30
    type: int
  headers:
    description:
      - HTTP headers to send with the request
    type: dict
  validate_ssl:
    description:
      - Whether to validate SSL certificates
    default: true
    type: bool
'''

EXAMPLES = '''
- name: Check website health
  health_check:
    url: https://example.com
    expected_status: 200
    timeout: 10

- name: Check API endpoint with custom headers
  health_check:
    url: https://api.example.com/health
    expected_status: 200
    headers:
      Authorization: "Bearer {{ api_token }}"
      Accept: "application/json"
'''

RETURN = '''
result:
  description: Health check results
  returned: always
  type: dict
  contains:
    url:
      description: The checked URL
      type: str
      sample: "https://example.com"
    status_code:
      description: HTTP status code received
      type: int
      sample: 200
    response_time:
      description: Response time in seconds
      type: float
      sample: 0.5
    content_length:
      description: Content length in bytes
      type: int
      sample: 1024
'''
```

## 模块调试技巧

### 1. 模块调试命令

```bash
# 模块调试命令
# 查看模块文档
ansible-doc yum
ansible-doc service
ansible-doc template

# 查看模块源码位置
ansible-doc -s yum

# 列出所有可用模块
ansible-doc -l

# 搜索模块
ansible-doc -l | grep docker
ansible-doc -l | grep aws

# 查看模块返回值
ansible-doc -r yum
```

### 2. 模块执行调试

```yaml
# 模块调试示例
tasks:
  # 详细输出调试
  - name: Debug module execution
    yum:
      name: nginx
      state: present
    register: yum_result
    verbosity: 2
  
  - name: Display module result
    debug:
      var: yum_result
      verbosity: 2
  
  # 检查模式调试
  - name: Test in check mode
    template:
      src: config.j2
      dest: /etc/myapp/config.conf
    check_mode: yes
    register: check_result
  
  - name: Display check mode result
    debug:
      msg: "Would have changed: {{ check_result.changed }}"
```

## 总结

Ansible的基本模块与常用操作构成了自动化配置管理的核心组件。通过掌握系统模块、文件操作模块、网络模块、命令模块以及云和虚拟化模块，我们可以构建强大而灵活的自动化解决方案。

关键要点包括：
1. 理解不同类别模块的功能和使用场景
2. 掌握模块的最佳实践和性能优化技巧
3. 学会开发自定义模块以满足特定需求
4. 熟悉模块调试和故障排除方法

在下一节中，我们将深入探讨Ansible实战：自动化运维与配置管理，学习如何将这些模块和操作应用到实际的运维场景中。