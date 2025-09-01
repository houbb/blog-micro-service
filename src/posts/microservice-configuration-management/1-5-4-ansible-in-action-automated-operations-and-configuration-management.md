---
title: Ansible实战：自动化运维与配置管理
date: 2025-08-31
categories: [Configuration Management]
tags: [ansible,实战, automation, devops, configuration]
published: true
---

# 5.4 Ansible实战：自动化运维与配置管理

在前几节中，我们学习了Ansible的基本概念、Playbook编写和模块使用。现在，让我们通过实际的案例来深入了解如何在真实的运维场景中应用Ansible进行自动化配置管理。本节将通过具体的实战案例，展示Ansible在Web服务器部署、数据库配置、安全加固、应用部署等方面的强大能力。

## Web服务器自动化部署

### 1. Nginx Web服务器部署

```yaml
# roles/webserver/tasks/main.yml
---
- name: Install Nginx
  package:
    name: nginx
    state: present

- name: Configure Nginx
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
  notify: restart nginx

- name: Deploy default web page
  template:
    src: index.html.j2
    dest: /var/www/html/index.html
    owner: nginx
    group: nginx
    mode: '0644'

- name: Configure firewall for HTTP/HTTPS
  firewalld:
    service: "{{ item }}"
    permanent: yes
    state: enabled
    immediate: yes
  loop:
    - http
    - https

- name: Enable and start Nginx service
  service:
    name: nginx
    state: started
    enabled: yes
```

```jinja2
{# roles/webserver/templates/nginx.conf.j2 #}
user nginx;
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
    types_hash_max_size 2048;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    include /etc/nginx/conf.d/*.conf;

    server {
        listen {{ http_port | default(80) }};
        listen {{ https_port | default(443) }} ssl http2;
        server_name {{ server_name | default('_') }};

        ssl_certificate {{ ssl_cert_path | default('/etc/ssl/certs/nginx.crt') }};
        ssl_certificate_key {{ ssl_key_path | default('/etc/ssl/private/nginx.key') }};

        root {{ document_root | default('/usr/share/nginx/html') }};
        index index.html index.htm;

        location / {
            try_files $uri $uri/ =404;
        }

        error_page 404 /404.html;
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }
}
```

```jinja2
{# roles/webserver/templates/index.html.j2 #}
<!DOCTYPE html>
<html>
<head>
    <title>{{ site_title | default('Welcome to Nginx') }}</title>
    <style>
        body {
            width: 35em;
            margin: 0 auto;
            font-family: Tahoma, Verdana, Arial, sans-serif;
        }
    </style>
</head>
<body>
    <h1>{{ site_title | default('Welcome to Nginx!') }}</h1>
    <p>{{ site_description | default('If you see this page, the nginx web server is successfully installed and working.') }}</p>
    
    <p><em>Thank you for using nginx.</em></p>
    
    <div style="margin-top: 2em; padding: 1em; background-color: #f0f0f0;">
        <h3>Server Information</h3>
        <ul>
            <li>Hostname: {{ ansible_hostname }}</li>
            <li>IP Address: {{ ansible_default_ipv4.address }}</li>
            <li>OS: {{ ansible_distribution }} {{ ansible_distribution_version }}</li>
            <li>Deployment Time: {{ ansible_date_time.iso8601 }}</li>
        </ul>
    </div>
</body>
</html>
```

### 2. Apache Web服务器部署

```yaml
# roles/apache/tasks/main.yml
---
- name: Install Apache HTTP Server
  package:
    name: httpd
    state: present

- name: Configure Apache
  template:
    src: httpd.conf.j2
    dest: /etc/httpd/conf/httpd.conf
    owner: root
    group: root
    mode: '0644'
  notify: restart apache

- name: Deploy virtual host configuration
  template:
    src: vhost.conf.j2
    dest: /etc/httpd/conf.d/{{ vhost_name | default('default') }}.conf
    owner: root
    group: root
    mode: '0644'
  notify: restart apache

- name: Create document root directory
  file:
    path: "{{ document_root | default('/var/www/html') }}"
    state: directory
    owner: apache
    group: apache
    mode: '0755'

- name: Deploy default web page
  template:
    src: index.html.j2
    dest: "{{ document_root | default('/var/www/html') }}/index.html"
    owner: apache
    group: apache
    mode: '0644'

- name: Configure SELinux for Apache
  seboolean:
    name: httpd_can_network_connect
    state: yes
    persistent: yes
  when: ansible_selinux.status == "enabled"

- name: Enable and start Apache service
  service:
    name: httpd
    state: started
    enabled: yes
```

## 数据库自动化配置

### 1. MySQL数据库配置

```yaml
# roles/mysql/tasks/main.yml
---
- name: Install MySQL server
  package:
    name: mysql-server
    state: present

- name: Start MySQL service
  service:
    name: mysqld
    state: started
    enabled: yes

- name: Secure MySQL installation
  mysql_user:
    name: root
    password: "{{ mysql_root_password }}"
    login_unix_socket: /var/lib/mysql/mysql.sock
    state: present

- name: Remove anonymous users
  mysql_user:
    name: ""
    host_all: yes
    state: absent
    login_user: root
    login_password: "{{ mysql_root_password }}"

- name: Remove test database
  mysql_db:
    name: test
    state: absent
    login_user: root
    login_password: "{{ mysql_root_password }}"

- name: Create application database
  mysql_db:
    name: "{{ app_database_name }}"
    state: present
    login_user: root
    login_password: "{{ mysql_root_password }}"

- name: Create application database user
  mysql_user:
    name: "{{ app_database_user }}"
    password: "{{ app_database_password }}"
    priv: "{{ app_database_name }}.*:ALL"
    host: "{{ item }}"
    state: present
    login_user: root
    login_password: "{{ mysql_root_password }}"
  loop:
    - localhost
    - "{{ ansible_default_ipv4.address }}"
    - "%"

- name: Configure MySQL
  template:
    src: my.cnf.j2
    dest: /etc/my.cnf
    owner: root
    group: root
    mode: '0644'
  notify: restart mysql

- name: Configure firewall for MySQL
  firewalld:
    port: "{{ mysql_port | default(3306) }}/tcp"
    permanent: yes
    state: enabled
    immediate: yes
```

```jinja2
{# roles/mysql/templates/my.cnf.j2 #}
[mysqld]
datadir=/var/lib/mysql
socket=/var/lib/mysql/mysql.sock
log-error=/var/log/mysqld.log
pid-file=/var/run/mysqld/mysqld.pid

# Connection settings
port = {{ mysql_port | default(3306) }}
bind-address = {{ mysql_bind_address | default('127.0.0.1') }}

# Performance settings
innodb_buffer_pool_size = {{ innodb_buffer_pool_size | default('128M') }}
max_connections = {{ max_connections | default(151) }}
thread_cache_size = {{ thread_cache_size | default(8) }}

# Security settings
local-infile = 0
skip-symbolic-links = 1

# Logging
log-error = /var/log/mysqld.log
slow_query_log = 1
slow_query_log_file = /var/log/mysql-slow.log
long_query_time = 2

{% if mysql_performance_schema | default(true) %}
performance_schema = ON
{% endif %}
```

### 2. PostgreSQL数据库配置

```yaml
# roles/postgresql/tasks/main.yml
---
- name: Install PostgreSQL
  package:
    name: postgresql-server
    state: present

- name: Initialize PostgreSQL database
  command: postgresql-setup initdb
  args:
    creates: /var/lib/pgsql/data/postgresql.conf

- name: Configure PostgreSQL
  template:
    src: postgresql.conf.j2
    dest: /var/lib/pgsql/data/postgresql.conf
    owner: postgres
    group: postgres
    mode: '0600'
  notify: restart postgresql

- name: Configure PostgreSQL authentication
  template:
    src: pg_hba.conf.j2
    dest: /var/lib/pgsql/data/pg_hba.conf
    owner: postgres
    group: postgres
    mode: '0600'
  notify: restart postgresql

- name: Start PostgreSQL service
  service:
    name: postgresql
    state: started
    enabled: yes

- name: Create application database
  postgresql_db:
    name: "{{ app_database_name }}"
    state: present
    login_user: postgres

- name: Create application database user
  postgresql_user:
    name: "{{ app_database_user }}"
    password: "{{ app_database_password }}"
    priv: ALL
    db: "{{ app_database_name }}"
    state: present
    login_user: postgres

- name: Configure firewall for PostgreSQL
  firewalld:
    port: "{{ postgresql_port | default(5432) }}/tcp"
    permanent: yes
    state: enabled
    immediate: yes
```

## 安全加固与合规性配置

### 1. 系统安全加固

```yaml
# roles/security/tasks/main.yml
---
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
    - { regexp: '^#?Port', line: 'Port {{ ssh_port | default(22) }}' }
    - { regexp: '^#?MaxAuthTries', line: 'MaxAuthTries 3' }
    - { regexp: '^#?ClientAliveInterval', line: 'ClientAliveInterval 300' }
    - { regexp: '^#?ClientAliveCountMax', line: 'ClientAliveCountMax 2' }
  notify: restart sshd

- name: Configure firewall rules
  firewalld:
    service: "{{ item.service }}"
    port: "{{ item.port | default(omit) }}"
    permanent: yes
    state: "{{ item.state }}"
    immediate: yes
  loop:
    - { service: "ssh", port: "{{ ssh_port | default(22) }}/tcp", state: "enabled" }
    - { service: "http", state: "enabled" }
    - { service: "https", state: "enabled" }
    - { service: "dhcpv6-client", state: "disabled" }
    - { service: "cockpit", state: "disabled" }

- name: Install and configure fail2ban
  package:
    name: fail2ban
    state: present

- name: Configure fail2ban
  template:
    src: jail.local.j2
    dest: /etc/fail2ban/jail.local
    owner: root
    group: root
    mode: '0644'
  notify: restart fail2ban

- name: Enable and start fail2ban service
  service:
    name: fail2ban
    state: started
    enabled: yes

- name: Configure system auditing
  lineinfile:
    path: /etc/audit/rules.d/audit.rules
    line: "{{ item }}"
    create: yes
  loop:
    - "-w /etc/passwd -p wa -k identity"
    - "-w /etc/shadow -p wa -k identity"
    - "-w /etc/group -p wa -k identity"
    - "-w /etc/sudoers -p wa -k priv_actions"
    - "-w /etc/ssh/sshd_config -p wa -k ssh"
  notify: restart auditd

- name: Set up automatic security updates
  yum:
    name: yum-cron
    state: present
  when: ansible_os_family == "RedHat"

- name: Configure automatic security updates
  lineinfile:
    path: /etc/yum/yum-cron.conf
    regexp: "{{ item.regexp }}"
    line: "{{ item.line }}"
  loop:
    - { regexp: '^#?apply_updates', line: 'apply_updates = yes' }
    - { regexp: '^#?update_cmd', line: 'update_cmd = security' }
  when: ansible_os_family == "RedHat"
  notify: restart yum-cron
```

### 2. 合规性检查

```yaml
# roles/compliance/tasks/main.yml
---
- name: Check for unauthorized users
  command: awk -F: '$3 >= 1000 && $3 < 65534 {print $1}' /etc/passwd
  register: authorized_users
  changed_when: false

- name: Verify authorized users
  assert:
    that:
      - "item in authorized_users_list | default([])"
    fail_msg: "Unauthorized user found: {{ item }}"
  loop: "{{ authorized_users.stdout_lines }}"

- name: Check for unauthorized services
  service_facts:

- name: Verify authorized services
  assert:
    that:
      - "item not in unauthorized_services | default([])"
    fail_msg: "Unauthorized service running: {{ item }}"
  loop: "{{ ansible_facts.services.keys() }}"
  when: ansible_facts.services[item].state == "running"

- name: Check file permissions
  stat:
    path: "{{ item.path }}"
  register: file_stats
  loop:
    - { path: "/etc/passwd", mode: "0644" }
    - { path: "/etc/shadow", mode: "0640" }
    - { path: "/etc/group", mode: "0644" }
    - { path: "/etc/ssh/sshd_config", mode: "0600" }

- name: Verify file permissions
  assert:
    that:
      - "item.stat.mode == item.mode"
    fail_msg: "Incorrect permissions for {{ item.item.path }}: expected {{ item.item.mode }}, got {{ item.stat.mode }}"
  loop: "{{ file_stats.results }}"

- name: Check for world-writable files
  command: find / -xdev -type f -perm -0002 -not -path "/proc/*" -not -path "/sys/*" 2>/dev/null
  register: world_writable_files
  changed_when: false

- name: Report world-writable files
  debug:
    msg: "World-writable file found: {{ item }}"
  loop: "{{ world_writable_files.stdout_lines }}"
  when: world_writable_files.stdout_lines | length > 0
```

## 应用部署与管理

### 1. Java应用部署

```yaml
# roles/java-app/tasks/main.yml
---
- name: Install Java
  package:
    name: java-11-openjdk-devel
    state: present

- name: Create application user
  user:
    name: "{{ app_user }}"
    system: yes
    shell: /bin/false
    home: "{{ app_home }}"
    state: present

- name: Create application directories
  file:
    path: "{{ item }}"
    state: directory
    owner: "{{ app_user }}"
    group: "{{ app_user }}"
    mode: '0755'
  loop:
    - "{{ app_home }}"
    - "{{ app_home }}/logs"
    - "{{ app_home }}/config"
    - "{{ app_home }}/lib"

- name: Download application package
  get_url:
    url: "{{ app_download_url }}"
    dest: "{{ app_home }}/app.tar.gz"
    mode: '0644'
    checksum: "{{ app_checksum | default(omit) }}"

- name: Extract application
  unarchive:
    src: "{{ app_home }}/app.tar.gz"
    dest: "{{ app_home }}"
    owner: "{{ app_user }}"
    group: "{{ app_user }}"
    remote_src: yes

- name: Deploy application configuration
  template:
    src: application.properties.j2
    dest: "{{ app_home }}/config/application.properties"
    owner: "{{ app_user }}"
    group: "{{ app_user }}"
    mode: '0644'

- name: Create systemd service file
  template:
    src: app.service.j2
    dest: "/etc/systemd/system/{{ app_name }}.service"
    owner: root
    group: root
    mode: '0644'
  notify: reload systemd

- name: Enable and start application service
  service:
    name: "{{ app_name }}"
    state: started
    enabled: yes

- name: Wait for application to start
  wait_for:
    port: "{{ app_port }}"
    delay: 10
    timeout: 300
```

```jinja2
{# roles/java-app/templates/application.properties.j2 #}
# Application Configuration
server.port={{ app_port | default(8080) }}
server.servlet.context-path={{ context_path | default('/') }}

# Database Configuration
spring.datasource.url={{ db_url | default('jdbc:mysql://localhost:3306/myapp') }}
spring.datasource.username={{ db_username | default('myapp') }}
spring.datasource.password={{ db_password }}
spring.datasource.driver-class-name={{ db_driver | default('com.mysql.cj.jdbc.Driver') }}

# Logging Configuration
logging.level.{{ app_package | default('com.example') }}={{ log_level | default('INFO') }}
logging.file.name={{ app_home }}/logs/application.log
logging.pattern.console=%d{yyyy-MM-dd HH:mm:ss} - %msg%n
logging.pattern.file=%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n

# Security Configuration
spring.security.user.name={{ admin_username | default('admin') }}
spring.security.user.password={{ admin_password }}
spring.security.user.roles=ADMIN

# Performance Configuration
spring.datasource.hikari.maximum-pool-size={{ db_pool_size | default(10) }}
spring.datasource.hikari.minimum-idle={{ db_min_idle | default(5) }}
spring.datasource.hikari.connection-timeout={{ db_connection_timeout | default(30000) }}
```

```jinja2
{# roles/java-app/templates/app.service.j2 #}
[Unit]
Description={{ app_name | title }} Application
After=network.target

[Service]
Type=simple
User={{ app_user }}
Group={{ app_user }}
WorkingDirectory={{ app_home }}
ExecStart={{ java_home | default('/usr/bin/java') }} \
  -jar {{ app_home }}/app.jar \
  --spring.config.location={{ app_home }}/config/
Environment=JAVA_OPTS="-Xmx{{ heap_size | default('512m') }} -Xms{{ initial_heap_size | default('256m') }}"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Docker化应用部署

```yaml
# roles/docker-app/tasks/main.yml
---
- name: Install Docker
  package:
    name: docker
    state: present

- name: Start and enable Docker service
  service:
    name: docker
    state: started
    enabled: yes

- name: Install Docker Compose
  get_url:
    url: https://github.com/docker/compose/releases/download/{{ docker_compose_version | default('1.29.2') }}/docker-compose-Linux-x86_64
    dest: /usr/local/bin/docker-compose
    mode: '0755'

- name: Create application directory
  file:
    path: "{{ app_directory }}"
    state: directory
    owner: root
    group: root
    mode: '0755'

- name: Deploy Docker Compose file
  template:
    src: docker-compose.yml.j2
    dest: "{{ app_directory }}/docker-compose.yml"
    owner: root
    group: root
    mode: '0644'

- name: Deploy application configuration
  template:
    src: app.conf.j2
    dest: "{{ app_directory }}/config/app.conf"
    owner: root
    group: root
    mode: '0644'

- name: Pull Docker images
  docker_compose:
    project_src: "{{ app_directory }}"
    pull: yes

- name: Start application stack
  docker_compose:
    project_src: "{{ app_directory }}"
    state: present
    recreate: smart

- name: Wait for application to be ready
  uri:
    url: "http://{{ app_host | default('localhost') }}:{{ app_port }}/health"
    method: GET
    status_code: 200
    timeout: 30
  retries: 10
  delay: 5
```

```jinja2
{# roles/docker-app/templates/docker-compose.yml.j2 #}
version: '3.8'

services:
  web:
    image: {{ web_image | default('nginx:1.21') }}
    ports:
      - "{{ external_port | default(80) }}:{{ internal_port | default(80) }}"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./data:/usr/share/nginx/html:ro
    depends_on:
      - app
    networks:
      - app-network

  app:
    image: {{ app_image | default('myapp:latest') }}
    environment:
      - DATABASE_URL={{ db_url | default('postgresql://user:pass@db:5432/myapp') }}
      - REDIS_URL={{ redis_url | default('redis://redis:6379') }}
      - LOG_LEVEL={{ log_level | default('INFO') }}
    volumes:
      - ./config:/app/config:ro
      - app-logs:/app/logs
    networks:
      - app-network
    depends_on:
      - db
      - redis

  db:
    image: {{ db_image | default('postgres:13') }}
    environment:
      - POSTGRES_DB={{ db_name | default('myapp') }}
      - POSTGRES_USER={{ db_user | default('myapp') }}
      - POSTGRES_PASSWORD={{ db_password }}
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: {{ redis_image | default('redis:6.2') }}
    networks:
      - app-network

  nginx-proxy:
    image: {{ proxy_image | default('nginx:1.21') }}
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx-proxy.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    networks:
      - app-network

volumes:
  db-data:
  app-logs:

networks:
  app-network:
    driver: bridge
```

## 监控与日志管理

### 1. Prometheus监控部署

```yaml
# roles/prometheus/tasks/main.yml
---
- name: Create Prometheus user
  user:
    name: prometheus
    system: yes
    shell: /bin/false
    home: /var/lib/prometheus
    state: present

- name: Create Prometheus directories
  file:
    path: "{{ item }}"
    state: directory
    owner: prometheus
    group: prometheus
    mode: '0755'
  loop:
    - /var/lib/prometheus
    - /etc/prometheus
    - /etc/prometheus/rules
    - /etc/prometheus/files

- name: Download Prometheus
  get_url:
    url: "https://github.com/prometheus/prometheus/releases/download/v{{ prometheus_version | default('2.30.3') }}/prometheus-{{ prometheus_version | default('2.30.3') }}.linux-amd64.tar.gz"
    dest: "/tmp/prometheus-{{ prometheus_version | default('2.30.3') }}.tar.gz"
    mode: '0644'

- name: Extract Prometheus
  unarchive:
    src: "/tmp/prometheus-{{ prometheus_version | default('2.30.3') }}.tar.gz"
    dest: /tmp
    remote_src: yes

- name: Install Prometheus binary
  copy:
    src: "/tmp/prometheus-{{ prometheus_version | default('2.30.3') }}.linux-amd64/prometheus"
    dest: /usr/local/bin/prometheus
    owner: prometheus
    group: prometheus
    mode: '0755'
    remote_src: yes

- name: Install Prometheus configuration
  template:
    src: prometheus.yml.j2
    dest: /etc/prometheus/prometheus.yml
    owner: prometheus
    group: prometheus
    mode: '0644'

- name: Create Prometheus systemd service
  template:
    src: prometheus.service.j2
    dest: /etc/systemd/system/prometheus.service
    owner: root
    group: root
    mode: '0644'

- name: Reload systemd and start Prometheus
  systemd:
    daemon_reload: yes
    name: prometheus
    state: started
    enabled: yes

- name: Configure firewall for Prometheus
  firewalld:
    port: "{{ prometheus_port | default(9090) }}/tcp"
    permanent: yes
    state: enabled
    immediate: yes
```

### 2. ELK日志堆栈部署

```yaml
# roles/elk-stack/tasks/main.yml
---
- name: Install Java for Elasticsearch
  package:
    name: java-11-openjdk
    state: present

- name: Add Elasticsearch repository
  yum_repository:
    name: elasticsearch
    description: Elasticsearch repository for 7.x packages
    baseurl: https://artifacts.elastic.co/packages/7.x/yum
    gpgkey: https://artifacts.elastic.co/GPG-KEY-elasticsearch
    gpgcheck: yes
    enabled: yes
  when: ansible_os_family == "RedHat"

- name: Install ELK components
  package:
    name: "{{ item }}"
    state: present
  loop:
    - elasticsearch
    - logstash
    - kibana

- name: Configure Elasticsearch
  template:
    src: elasticsearch.yml.j2
    dest: /etc/elasticsearch/elasticsearch.yml
    owner: elasticsearch
    group: elasticsearch
    mode: '0644'
  notify: restart elasticsearch

- name: Configure Logstash
  template:
    src: logstash.conf.j2
    dest: /etc/logstash/conf.d/logstash.conf
    owner: root
    group: root
    mode: '0644'
  notify: restart logstash

- name: Configure Kibana
  template:
    src: kibana.yml.j2
    dest: /etc/kibana/kibana.yml
    owner: kibana
    group: kibana
    mode: '0644'
  notify: restart kibana

- name: Start and enable ELK services
  service:
    name: "{{ item }}"
    state: started
    enabled: yes
  loop:
    - elasticsearch
    - logstash
    - kibana

- name: Configure firewall for ELK
  firewalld:
    port: "{{ item.port }}/tcp"
    permanent: yes
    state: enabled
    immediate: yes
  loop:
    - { port: "{{ elasticsearch_port | default(9200) }}" }
    - { port: "{{ kibana_port | default(5601) }}" }
    - { port: "{{ logstash_port | default(5044) }}" }
```

## 备份与灾难恢复

### 1. 系统备份策略

```yaml
# roles/backup/tasks/main.yml
---
- name: Install backup tools
  package:
    name:
      - rsync
      - bzip2
      - tar
    state: present

- name: Create backup directories
  file:
    path: "{{ item }}"
    state: directory
    owner: root
    group: root
    mode: '0755'
  loop:
    - /var/backups
    - /var/backups/system
    - /var/backups/database
    - /var/backups/application

- name: Deploy backup script
  template:
    src: backup.sh.j2
    dest: /usr/local/bin/system-backup.sh
    owner: root
    group: root
    mode: '0755'

- name: Deploy database backup script
  template:
    src: db-backup.sh.j2
    dest: /usr/local/bin/database-backup.sh
    owner: root
    group: root
    mode: '0755'

- name: Create backup cron jobs
  cron:
    name: "{{ item.name }}"
    minute: "{{ item.minute }}"
    hour: "{{ item.hour }}"
    job: "{{ item.job }}"
    user: root
  loop:
    - { name: "Daily system backup", minute: "0", hour: "2", job: "/usr/local/bin/system-backup.sh" }
    - { name: "Daily database backup", minute: "30", hour: "2", job: "/usr/local/bin/database-backup.sh" }
    - { name: "Weekly full backup", minute: "0", hour: "3", job: "/usr/local/bin/full-backup.sh" }

- name: Configure backup retention
  template:
    src: backup-cleanup.sh.j2
    dest: /usr/local/bin/backup-cleanup.sh
    owner: root
    group: root
    mode: '0755'

- name: Schedule backup cleanup
  cron:
    name: "Backup cleanup"
    minute: "0"
    hour: "4"
    job: "/usr/local/bin/backup-cleanup.sh"
    user: root
```

```jinja2
{# roles/backup/templates/backup.sh.j2 #}
#!/bin/bash

# System backup script
BACKUP_DIR="/var/backups/system"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="system-backup-$DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup important system files
tar -czf "$BACKUP_DIR/$BACKUP_NAME/etc.tar.gz" /etc
tar -czf "$BACKUP_DIR/$BACKUP_NAME/home.tar.gz" /home
tar -czf "$BACKUP_DIR/$BACKUP_NAME/var-www.tar.gz" /var/www

# Backup package list
if [ -f /etc/redhat-release ]; then
    rpm -qa > "$BACKUP_DIR/$BACKUP_NAME/packages.txt"
elif [ -f /etc/debian_version ]; then
    dpkg -l > "$BACKUP_DIR/$BACKUP_NAME/packages.txt"
fi

# Create backup archive
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"

# Remove temporary directory
rm -rf "$BACKUP_DIR/$BACKUP_NAME"

# Log backup completion
echo "System backup completed: $BACKUP_NAME.tar.gz" >> /var/log/backup.log
```

## 性能优化与调优

### 1. 系统性能优化

```yaml
# roles/performance/tasks/main.yml
---
- name: Configure kernel parameters
  sysctl:
    name: "{{ item.name }}"
    value: "{{ item.value }}"
    sysctl_set: yes
    state: present
    reload: yes
  loop:
    - { name: "vm.swappiness", value: "1" }
    - { name: "vm.dirty_ratio", value: "15" }
    - { name: "vm.dirty_background_ratio", value: "5" }
    - { name: "net.core.somaxconn", value: "65535" }
    - { name: "net.ipv4.tcp_max_syn_backlog", value: "65535" }

- name: Configure systemd limits
  lineinfile:
    path: /etc/security/limits.conf
    line: "{{ item }}"
    create: yes
  loop:
    - "* soft nofile 65536"
    - "* hard nofile 65536"
    - "* soft nproc 65536"
    - "* hard nproc 65536"

- name: Configure tuned profile
  package:
    name: tuned
    state: present

- name: Start and enable tuned
  service:
    name: tuned
    state: started
    enabled: yes

- name: Apply tuned profile
  command: tuned-adm profile "{{ tuned_profile | default('throughput-performance') }}"

- name: Optimize filesystem mount options
  mount:
    path: "{{ item.path }}"
    src: "{{ item.src }}"
    fstype: "{{ item.fstype }}"
    opts: "{{ item.opts }}"
    state: mounted
  loop:
    - { path: "/var/log", src: "/dev/sdb1", fstype: "ext4", opts: "defaults,noatime" }
    - { path: "/tmp", src: "tmpfs", fstype: "tmpfs", opts: "defaults,size=2G" }
```

## 完整的部署Playbook

```yaml
# site.yml
---
- name: Deploy complete web application stack
  hosts: all
  become: yes
  vars:
    app_name: "mywebapp"
    app_version: "1.2.3"
    deploy_environment: "production"
  
  pre_tasks:
    - name: Update package cache
      yum:
        name: "*"
        state: latest
      when: ansible_os_family == "RedHat"
  
  roles:
    - common
    - security
    - webserver
    - database
    - java-app
    - monitoring
    - backup
  
  post_tasks:
    - name: Run health checks
      uri:
        url: "http://{{ inventory_hostname }}/health"
        method: GET
        status_code: 200
        timeout: 30
      retries: 5
      delay: 10
    
    - name: Send deployment notification
      mail:
        host: localhost
        port: 25
        to: "ops-team@example.com"
        subject: "Deployment completed - {{ app_name }} {{ app_version }}"
        body: |
          Deployment of {{ app_name }} version {{ app_version }} completed successfully.
          
          Hosts: {{ ansible_play_hosts_all | join(', ') }}
          Environment: {{ deploy_environment }}
          Timestamp: {{ ansible_date_time.iso8601 }}
```

## 总结

通过本节的实战案例，我们深入了解了Ansible在各种运维场景中的应用：

1. **Web服务器部署**：展示了Nginx和Apache的自动化配置
2. **数据库管理**：涵盖了MySQL和PostgreSQL的自动化部署
3. **安全加固**：提供了系统安全和合规性配置方案
4. **应用部署**：演示了Java应用和Docker化应用的部署
5. **监控日志**：实现了Prometheus和ELK堆栈的部署
6. **备份恢复**：建立了完整的备份策略
7. **性能优化**：提供了系统性能调优方案

这些实战案例展示了Ansible在现代IT运维中的强大能力，通过声明式配置、幂等性操作和丰富的模块生态系统，Ansible能够有效解决复杂的配置管理挑战，提高运维效率和系统可靠性。

在实际应用中，建议根据具体需求调整和优化这些示例，建立标准化的Role库和Playbook模板，形成组织的自动化运维最佳实践。