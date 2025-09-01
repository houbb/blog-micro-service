---
title: Playbook的编写与执行：掌握Ansible自动化的核心技能
date: 2025-08-31
categories: [Configuration Management]
tags: [ansible, playbook, automation, devops, configuration]
published: true
---

# 5.2 Playbook的编写与执行

Playbook是Ansible的核心组件，它使用YAML格式定义配置管理任务，是实现基础设施即代码（Infrastructure as Code）的重要工具。掌握Playbook的编写与执行是使用Ansible进行自动化配置管理的关键技能。本节将详细介绍Playbook的结构、语法、编写技巧以及执行方法。

## Playbook基础结构

### 1. Playbook的基本组成

Playbook由一个或多个Play组成，每个Play定义了一组要在特定主机上执行的任务：

```yaml
# Playbook基本结构示例
---
# 第一个Play
- name: Configure web servers
  hosts: webservers
  become: yes
  tasks:
    - name: Install Nginx
      yum:
        name: nginx
        state: present
    
    - name: Start Nginx service
      service:
        name: nginx
        state: started
        enabled: yes

# 第二个Play
- name: Configure database servers
  hosts: databases
  become: yes
  tasks:
    - name: Install MySQL
      yum:
        name: mysql-server
        state: present
    
    - name: Start MySQL service
      service:
        name: mysqld
        state: started
        enabled: yes
```

### 2. Play的关键属性

每个Play都有多个关键属性，用于控制Play的行为：

```yaml
# Play的完整属性示例
---
- name: Comprehensive Play Example
  # 主机选择
  hosts: webservers
  
  # 权限提升
  become: yes
  become_method: sudo
  become_user: root
  
  # 连接设置
  gather_facts: yes
  serial: 2
  max_fail_percentage: 10
  
  # 变量定义
  vars:
    app_name: myapp
    app_version: 1.2.3
    http_port: 80
  
  # 变量文件
  vars_files:
    - vars/common.yml
    - vars/{{ ansible_os_family }}.yml
  
  # 环境变量
  environment:
    DEBIAN_FRONTEND: noninteractive
    PATH: "/usr/local/bin:{{ ansible_env.PATH }}"
  
  # 预处理任务
  pre_tasks:
    - name: Update package cache
      yum:
        name: "*"
        state: latest
      when: ansible_os_family == "RedHat"
  
  # Roles引用
  roles:
    - common
    - webserver
    - application
  
  # 主要任务
  tasks:
    - name: Ensure application is running
      service:
        name: "{{ app_name }}"
        state: started
        enabled: yes
  
  # 后处理任务
  post_tasks:
    - name: Send notification
      mail:
        host: localhost
        port: 25
        to: admin@example.com
        subject: "Deployment completed"
        body: "Application {{ app_name }} deployed successfully"
```

## Playbook编写技巧

### 1. 任务定义与组织

#### 基本任务结构

```yaml
# 任务的基本结构
- name: Task description
  module_name:
    parameter1: value1
    parameter2: value2
  when: condition
  notify: handler_name
  register: variable_name
  ignore_errors: yes
  tags: [tag1, tag2]
```

#### 任务命名规范

```yaml
# 良好的任务命名示例
tasks:
  # 使用动词开头，描述具体操作
  - name: Install Nginx web server
    yum:
      name: nginx
      state: present
  
  - name: Configure Nginx main configuration
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: restart nginx
  
  - name: Deploy default web page
    copy:
      src: index.html
      dest: /usr/share/nginx/html/index.html
      owner: nginx
      group: nginx
      mode: '0644'
  
  - name: Enable and start Nginx service
    service:
      name: nginx
      state: started
      enabled: yes
```

#### 任务条件执行

```yaml
# 条件执行示例
tasks:
  # 基于操作系统执行不同任务
  - name: Install packages on RedHat systems
    yum:
      name: "{{ item }}"
      state: present
    loop:
      - nginx
      - python3
    when: ansible_os_family == "RedHat"
  
  - name: Install packages on Debian systems
    apt:
      name: "{{ item }}"
      state: present
    loop:
      - nginx
      - python3
    when: ansible_os_family == "Debian"
  
  # 基于变量值执行任务
  - name: Configure SSL if enabled
    template:
      src: ssl.conf.j2
      dest: /etc/nginx/conf.d/ssl.conf
    when: ssl_enabled | default(false)
  
  # 复杂条件判断
  - name: Perform maintenance only on weekends
    command: /usr/local/bin/maintenance.sh
    when: >
      ansible_date_time.weekday_number in ['6', '0'] and
      maintenance_mode | default(false)
```

### 2. 变量使用与管理

#### 变量定义方式

```yaml
# 多种变量定义方式
---
- name: Variable usage examples
  hosts: all
  # Play级别变量
  vars:
    app_name: myapp
    app_port: 8080
    debug_mode: false
  
  # 从文件加载变量
  vars_files:
    - vars/common.yml
    - vars/{{ ansible_os_family }}.yml
  
  # 交互式变量输入
  vars_prompt:
    - name: "db_password"
      prompt: "Enter database password"
      private: yes
      confirm: yes
  
  tasks:
    - name: Use variables in task
      template:
        src: app.conf.j2
        dest: "/etc/{{ app_name }}/app.conf"
      # 任务级别变量
      vars:
        config_file: "/etc/{{ app_name }}/app.conf"
        log_level: "{{ 'DEBUG' if debug_mode else 'INFO' }}"
```

#### 变量文件管理

```yaml
# vars/common.yml
---
# 通用变量
common_packages:
  - vim
  - curl
  - wget
  - git

common_users:
  - name: deploy
    uid: 2000
    groups: [wheel]
  - name: backup
    uid: 2001
    groups: []

# vars/RedHat.yml
---
# RedHat特定变量
package_manager: yum
service_manager: systemd
web_server_package: httpd
web_server_service: httpd

# vars/Debian.yml
---
# Debian特定变量
package_manager: apt
service_manager: systemd
web_server_package: nginx
web_server_service: nginx
```

#### 变量过滤器

```yaml
# 变量过滤器使用示例
tasks:
  - name: Demonstrate variable filters
    debug:
      msg: |
        Original string: {{ "hello world" }}
        Uppercase: {{ "hello world" | upper }}
        Capitalized: {{ "hello world" | capitalize }}
        Length: {{ "hello world" | length }}
        
        Number formatting: {{ 1234.567 | round(2) }}
        File size: {{ 1024 | filesizeformat }}
        
        Default value: {{ undefined_var | default('default_value') }}
        Mandatory value: {{ required_var | mandatory }}
        
        List operations:
        Join list: {{ ['a', 'b', 'c'] | join(',') }}
        Unique items: {{ [1, 2, 2, 3, 3, 4] | unique }}
        Shuffle list: {{ [1, 2, 3, 4, 5] | shuffle }}
        
        Dictionary operations:
        Combine dicts: {{ {'a': 1} | combine({'b': 2}) }}
        Dict to items: {{ {'a': 1, 'b': 2} | dict2items }}
```

### 3. 循环与迭代

#### 基本循环

```yaml
# 基本循环示例
tasks:
  # 简单循环
  - name: Install multiple packages
    yum:
      name: "{{ item }}"
      state: present
    loop:
      - nginx
      - mysql-server
      - python3
      - git
  
  # 字典循环
  - name: Create multiple users
    user:
      name: "{{ item.name }}"
      uid: "{{ item.uid }}"
      groups: "{{ item.groups }}"
      state: present
    loop:
      - { name: "webuser", uid: 2000, groups: "nginx" }
      - { name: "dbuser", uid: 2001, groups: "mysql" }
      - { name: "appuser", uid: 2002, groups: "webuser" }
  
  # 嵌套循环
  - name: Configure multiple services on multiple ports
    template:
      src: service.conf.j2
      dest: "/etc/{{ item.service }}-{{ item.port }}.conf"
    loop: "{{ services | product(ports) | list }}"
    vars:
      services: ["web", "api", "admin"]
      ports: [80, 443, 8080]
```

#### 高级循环控制

```yaml
# 高级循环控制示例
tasks:
  # 带索引的循环
  - name: Process items with index
    debug:
      msg: "Processing item {{ item.0 }}: {{ item.1 }}"
    loop: "{{ ['first', 'second', 'third'] | enumerate }}"
  
  # 条件循环
  - name: Install packages with conditions
    yum:
      name: "{{ item.name }}"
      state: present
    loop:
      - { name: "nginx", when: "web_server_required" }
      - { name: "mysql-server", when: "database_required" }
      - { name: "redis", when: "cache_required" }
    when: item.when | default(true) | bool
  
  # 循环控制
  - name: Process items with break/continue logic
    block:
      - name: Check item validity
        set_fact:
          item_valid: "{{ item.value > 0 }}"
      
      - name: Process valid item
        command: "/usr/local/bin/process.sh {{ item.name }}"
        when: item_valid
    loop:
      - { name: "item1", value: 10 }
      - { name: "item2", value: -5 }
      - { name: "item3", value: 20 }
```

### 4. 错误处理与异常管理

#### 错误处理机制

```yaml
# 错误处理示例
tasks:
  # 忽略错误
  - name: Attempt to install optional package
    yum:
      name: optional-package
      state: present
    ignore_errors: yes
  
  # 条件性失败
  - name: Check disk space
    command: df / | awk 'NR==2 {print $5}' | sed 's/%//'
    register: disk_usage
    failed_when: disk_usage.stdout | int > 90
  
  # 自定义错误消息
  - name: Validate configuration
    command: /usr/local/bin/validate-config.sh
    register: validation_result
    failed_when: validation_result.rc != 0
    fail:
      msg: "Configuration validation failed: {{ validation_result.stdout }}"
    when: validation_result.rc != 0
  
  # 块级错误处理
  - name: Complex operation with error handling
    block:
      - name: Step 1 - Backup configuration
        copy:
          src: /etc/app.conf
          dest: /etc/app.conf.backup
          remote_src: yes
      
      - name: Step 2 - Update configuration
        template:
          src: app.conf.j2
          dest: /etc/app.conf
      
      - name: Step 3 - Restart service
        service:
          name: app
          state: restarted
    
    rescue:
      - name: Rollback configuration
        copy:
          src: /etc/app.conf.backup
          dest: /etc/app.conf
          remote_src: yes
      
      - name: Restart service with old configuration
        service:
          name: app
          state: restarted
      
      - name: Notify administrators
        mail:
          host: localhost
          to: admin@example.com
          subject: "Configuration update failed"
          body: "Rollback completed successfully"
    
    always:
      - name: Clean up backup file
        file:
          path: /etc/app.conf.backup
          state: absent
```

## Playbook执行方法

### 1. 基本执行命令

```bash
# 基本Playbook执行
ansible-playbook site.yml

# 指定Inventory文件
ansible-playbook -i inventory/production site.yml

# 限制执行主机
ansible-playbook -i inventory/production site.yml --limit webservers

# 指定标签执行
ansible-playbook site.yml --tags "configuration,deployment"

# 跳过标签执行
ansible-playbook site.yml --skip-tags "testing"

# 检查模式（Dry run）
ansible-playbook site.yml --check

# 详细输出
ansible-playbook site.yml -v
ansible-playbook site.yml -vv
ansible-playbook site.yml -vvv
ansible-playbook site.yml -vvvv

# 设置额外变量
ansible-playbook site.yml -e "app_version=1.2.4"
ansible-playbook site.yml -e "@vars/override.yml"

# 并行执行控制
ansible-playbook site.yml -f 10  # 10个并发
```

### 2. 高级执行选项

#### 执行控制选项

```bash
# 串行执行
ansible-playbook site.yml --serial 1

# 分批执行
ansible-playbook site.yml --serial 20%

# 最大失败百分比
ansible-playbook site.yml --max-fail-percentage 10

# 开始执行位置
ansible-playbook site.yml --start-at-task "Configure Nginx"

# 从任务文件开始
ansible-playbook site.yml --start-at-task "@start_from.yml"

# 步骤执行
ansible-playbook site.yml --step

# 语法检查
ansible-playbook site.yml --syntax-check

# 列出主机
ansible-playbook site.yml --list-hosts

# 列出任务
ansible-playbook site.yml --list-tasks

# 列出标签
ansible-playbook site.yml --list-tags
```

#### 调试与诊断

```bash
# 调试模式
ansible-playbook site.yml -vvv --diff

# 显示变量
ansible-playbook site.yml -v --extra-vars "debug=true"

# 模块调试
ANSIBLE_DEBUG=1 ansible-playbook site.yml

# 性能分析
ANSIBLE_PROFILE_TASKS=1 ansible-playbook site.yml

# 连接调试
ANSIBLE_SSH_ARGS="-vvv" ansible-playbook site.yml
```

### 3. Playbook执行优化

#### 性能优化技巧

```yaml
# 性能优化的Playbook示例
---
- name: Optimized playbook
  hosts: all
  # 减少facts收集
  gather_facts: no
  
  # 预加载facts（如果需要）
  pre_tasks:
    - name: Gather minimum facts
      setup:
        gather_subset: 
          - network
          - virtual
      when: gather_minimal_facts | default(false)
  
  tasks:
    # 批量操作
    - name: Install multiple packages efficiently
      yum:
        name:
          - nginx
          - mysql-server
          - python3
          - git
        state: present
      # 避免循环单个包安装
    
    # 条件性执行
    - name: Skip unnecessary tasks
      debug:
        msg: "This task only runs in debug mode"
      when: debug_mode | default(false)
    
    # 并行友好的任务
    - name: Independent tasks can run in parallel
      file:
        path: "/tmp/task_{{ item }}"
        state: touch
      loop: "{{ range(1, 11) | list }}"
```

#### 连接优化

```ini
# ansible.cfg中的连接优化
[ssh_connection]
# SSH连接复用
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
# 管道传输（减少临时文件）
pipelining = True
# SCP替代SFTP
scp_if_ssh = True

[defaults]
# 增加并发数
forks = 50
# 减少超时时间
timeout = 30
# 优化模块传输
module_compression = 'ZIP_DEFLATED'
```

## Playbook最佳实践

### 1. 结构化组织

```bash
# 推荐的Playbook项目结构
ansible-project/
├── ansible.cfg
├── inventory/
│   ├── production
│   ├── staging
│   └── development
├── group_vars/
│   ├── all.yml
│   ├── webservers.yml
│   └── databases.yml
├── host_vars/
│   └── web01.example.com.yml
├── roles/
│   ├── common/
│   ├── webserver/
│   └── database/
├── playbooks/
│   ├── site.yml
│   ├── webservers.yml
│   └── databases.yml
├── files/
├── templates/
├── vars/
├── handlers/
└── README.md
```

### 2. 安全实践

```yaml
# 安全的Playbook示例
---
- name: Secure configuration management
  hosts: all
  become: yes
  vars:
    # 使用Vault加密敏感数据
    db_password: !vault |
      $ANSIBLE_VAULT;1.1;AES256
      66386439653...
  
  tasks:
    - name: Configure database with encrypted password
      template:
        src: database.conf.j2
        dest: /etc/myapp/database.conf
        mode: '0600'
        owner: root
        group: root
    
    - name: Ensure secure file permissions
      file:
        path: "{{ item.path }}"
        mode: "{{ item.mode }}"
        owner: "{{ item.owner | default('root') }}"
        group: "{{ item.group | default('root') }}"
      loop:
        - { path: "/etc/ssh/sshd_config", mode: "0600" }
        - { path: "/etc/ssl/private", mode: "0700", owner: "root", group: "root" }
        - { path: "/var/log/myapp", mode: "0750", owner: "myapp", group: "myapp" }
```

### 3. 可维护性实践

```yaml
# 可维护的Playbook示例
---
- name: Maintainable web server configuration
  hosts: webservers
  become: yes
  
  # 清晰的变量组织
  vars:
    # 应用配置
    app:
      name: myapp
      version: 1.2.3
      port: 8080
    
    # 系统配置
    system:
      user: www-data
      group: www-data
      home: /var/www
  
  # 模块化任务组织
  tasks:
    # 安装阶段
    - name: Install required packages
      include_tasks: tasks/install.yml
    
    # 配置阶段
    - name: Configure application
      include_tasks: tasks/configure.yml
    
    # 服务阶段
    - name: Manage service
      include_tasks: tasks/service.yml
    
    # 验证阶段
    - name: Verify installation
      include_tasks: tasks/verify.yml
```

## Playbook调试技巧

### 1. 调试模块使用

```yaml
# 调试技巧示例
tasks:
  # 显示变量值
  - name: Debug variables
    debug:
      var: ansible_facts
      verbosity: 2
  
  # 显示消息
  - name: Display custom message
    debug:
      msg: "Current app version: {{ app_version }}"
  
  # 显示注册变量
  - name: Check command output
    command: uptime
    register: uptime_result
  
  - name: Display command output
    debug:
      msg: |
        Command output: {{ uptime_result.stdout }}
        Return code: {{ uptime_result.rc }}
  
  # 条件性调试
  - name: Debug only in verbose mode
    debug:
      msg: "Detailed configuration: {{ app_config }}"
    when: debug_mode | default(false)
    verbosity: 2
```

### 2. 故障排除

```bash
# 故障排除命令
# 语法检查
ansible-playbook site.yml --syntax-check

# 列出任务
ansible-playbook site.yml --list-tasks

# 检查模式
ansible-playbook site.yml --check --diff

# 详细输出
ansible-playbook site.yml -vvv

# 特定主机执行
ansible-playbook site.yml --limit web01.example.com

# 从特定任务开始
ansible-playbook site.yml --start-at-task "Configure Nginx"
```

## 总结

Playbook的编写与执行是Ansible自动化配置管理的核心技能。通过掌握Playbook的基本结构、编写技巧、执行方法和最佳实践，我们可以构建高效、可靠、安全的自动化配置管理解决方案。

关键要点包括：
1. 理解Playbook的基本组成和属性
2. 掌握变量使用、循环控制和错误处理
3. 熟悉Playbook的执行方法和优化技巧
4. 遵循最佳实践确保Playbook的可维护性和安全性

在下一节中，我们将深入探讨Ansible的基本模块与常用操作，学习如何使用Ansible的丰富模块生态系统来实现各种配置管理任务。