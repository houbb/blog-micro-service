---
title: 加密存储与加密传输：构建端到端数据安全防护体系
date: 2025-08-31
categories: [Write]
tags: [write]
published: true
---

在现代数据管理环境中，数据安全不再仅仅是静态保护的问题，而是需要从数据产生到销毁的全生命周期进行保护。加密存储和加密传输作为数据安全防护体系的两个核心环节，共同构建了端到端的数据安全解决方案。加密存储确保数据在静止状态下的安全性，而加密传输则保护数据在流动过程中的机密性。本文将深入探讨这两种技术的实现原理、应用场景以及最佳实践，帮助读者构建完整的数据安全防护体系。

## 加密存储技术详解

### 静态数据加密（Data at Rest Encryption）

静态数据加密是指对存储在各种介质上的数据进行加密保护，包括硬盘、数据库、文件系统等存储设备中的数据。

#### 存储加密层次

##### 1. 应用层加密
应用层加密是在应用程序层面实现的数据加密，提供了最高的安全性和灵活性。

```python
# 应用层加密示例
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class ApplicationLevelEncryption:
    def __init__(self, password):
        # 使用密码派生密钥
        self.key = self._derive_key(password)
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password):
        """从密码派生密钥"""
        salt = b'static_salt_for_demo'  # 实际应用中应使用随机盐值
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_file(self, file_path):
        """加密文件"""
        # 读取文件内容
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        # 加密数据
        encrypted_data = self.cipher.encrypt(file_data)
        
        # 写入加密文件
        encrypted_file_path = file_path + '.encrypted'
        with open(encrypted_file_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)
        
        print(f"文件 {file_path} 已加密为 {encrypted_file_path}")
        return encrypted_file_path
    
    def decrypt_file(self, encrypted_file_path):
        """解密文件"""
        # 读取加密文件
        with open(encrypted_file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        
        # 解密数据
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        # 写入解密文件
        decrypted_file_path = encrypted_file_path.replace('.encrypted', '.decrypted')
        with open(decrypted_file_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)
        
        print(f"文件 {encrypted_file_path} 已解密为 {decrypted_file_path}")
        return decrypted_file_path

# 使用示例
app_encryption = ApplicationLevelEncryption("StrongPassword123!")
# app_encryption.encrypt_file("sensitive_data.txt")
# app_encryption.decrypt_file("sensitive_data.txt.encrypted")
```

##### 2. 数据库层加密
数据库层加密是在数据库管理系统内部实现的数据加密，包括透明数据加密（TDE）和列级加密等。

```sql
-- MySQL数据库加密示例
-- 启用表空间加密
CREATE TABLESPACE encrypted_ts
    ADD DATAFILE 'encrypted_ts.ibd'
    ENCRYPTION = 'Y';

-- 创建加密表
CREATE TABLE sensitive_data (
    id INT PRIMARY KEY,
    user_id VARCHAR(50),
    encrypted_personal_info VARBINARY(1000)
) ENCRYPTION='Y';

-- 插入加密数据
INSERT INTO sensitive_data (id, user_id, encrypted_personal_info)
VALUES (1, 'user001', AES_ENCRYPT('敏感个人信息', 'encryption_key'));
```

##### 3. 文件系统层加密
文件系统层加密是在操作系统文件系统层面实现的数据加密，如Windows BitLocker、Linux dm-crypt等。

```python
# 文件系统加密概念示例
class FileSystemEncryption:
    def __init__(self, encryption_key):
        self.key = encryption_key
        self.cipher = Fernet(encryption_key)
    
    def encrypt_directory(self, directory_path):
        """加密目录中的所有文件"""
        import glob
        
        # 获取目录中所有文件
        files = glob.glob(os.path.join(directory_path, "*"))
        
        for file_path in files:
            if os.path.isfile(file_path):
                self._encrypt_single_file(file_path)
    
    def _encrypt_single_file(self, file_path):
        """加密单个文件"""
        try:
            # 读取文件
            with open(file_path, 'rb') as file:
                data = file.read()
            
            # 加密数据
            encrypted_data = self.cipher.encrypt(data)
            
            # 写入加密文件
            with open(file_path + '.encrypted', 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)
            
            # 删除原文件（实际应用中应谨慎处理）
            # os.remove(file_path)
            
            print(f"文件 {file_path} 加密完成")
        except Exception as e:
            print(f"加密文件 {file_path} 失败: {e}")
    
    def decrypt_directory(self, directory_path):
        """解密目录中的所有加密文件"""
        import glob
        
        # 获取目录中所有加密文件
        encrypted_files = glob.glob(os.path.join(directory_path, "*.encrypted"))
        
        for file_path in encrypted_files:
            self._decrypt_single_file(file_path)
    
    def _decrypt_single_file(self, encrypted_file_path):
        """解密单个文件"""
        try:
            # 读取加密文件
            with open(encrypted_file_path, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()
            
            # 解密数据
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # 写入解密文件
            decrypted_file_path = encrypted_file_path.replace('.encrypted', '.decrypted')
            with open(decrypted_file_path, 'wb') as decrypted_file:
                decrypted_file.write(decrypted_data)
            
            print(f"文件 {encrypted_file_path} 解密完成")
        except Exception as e:
            print(f"解密文件 {encrypted_file_path} 失败: {e}")

# 使用示例
fs_key = Fernet.generate_key()
fs_encryption = FileSystemEncryption(fs_key)
# fs_encryption.encrypt_directory("/path/to/sensitive/data")
# fs_encryption.decrypt_directory("/path/to/sensitive/data")
```

### 存储加密最佳实践

#### 密钥管理策略
```python
# 存储加密密钥管理示例
import json
from datetime import datetime, timedelta

class StorageKeyManager:
    def __init__(self):
        self.master_key = Fernet.generate_key()
        self.master_cipher = Fernet(self.master_key)
        self.data_encryption_keys = {}
        self.key_rotation_interval = timedelta(days=90)
    
    def generate_data_key(self, data_id):
        """为特定数据生成专用加密密钥"""
        data_key = Fernet.generate_key()
        
        # 使用主密钥加密数据密钥
        encrypted_data_key = self.master_cipher.encrypt(data_key)
        
        self.data_encryption_keys[data_id] = {
            'encrypted_key': encrypted_data_key,
            'created_time': datetime.now(),
            'last_rotated': datetime.now()
        }
        
        return data_key
    
    def get_data_key(self, data_id):
        """获取特定数据的解密密钥"""
        if data_id not in self.data_encryption_keys:
            raise ValueError(f"数据ID {data_id} 不存在")
        
        # 使用主密钥解密数据密钥
        encrypted_key = self.data_encryption_keys[data_id]['encrypted_key']
        data_key = self.master_cipher.decrypt(encrypted_key)
        
        return data_key
    
    def rotate_data_key(self, data_id):
        """轮换特定数据的加密密钥"""
        if data_id not in self.data_encryption_keys:
            raise ValueError(f"数据ID {data_id} 不存在")
        
        # 生成新密钥
        new_data_key = self.generate_data_key(data_id)
        
        # 更新轮换时间
        self.data_encryption_keys[data_id]['last_rotated'] = datetime.now()
        
        print(f"数据 {data_id} 的密钥已轮换")
        return new_data_key
    
    def should_rotate_key(self, data_id):
        """检查是否需要轮换密钥"""
        if data_id not in self.data_encryption_keys:
            return False
        
        last_rotated = self.data_encryption_keys[data_id]['last_rotated']
        return datetime.now() - last_rotated > self.key_rotation_interval
    
    def backup_master_key(self, backup_path):
        """备份主密钥"""
        backup_data = {
            'master_key': self.master_key.decode('utf-8') if isinstance(self.master_key, bytes) else self.master_key,
            'backup_time': datetime.now().isoformat(),
            'key_count': len(self.data_encryption_keys)
        }
        
        with open(backup_path, 'w') as backup_file:
            json.dump(backup_data, backup_file)
        
        print(f"主密钥已备份到 {backup_path}")

# 使用示例
key_manager = StorageKeyManager()
user_data_key = key_manager.generate_data_key("user_sensitive_data_001")
print(f"为用户数据生成的密钥: {user_data_key}")

# 检查是否需要轮换密钥
if key_manager.should_rotate_key("user_sensitive_data_001"):
    key_manager.rotate_data_key("user_sensitive_data_001")

# 备份主密钥
key_manager.backup_master_key("master_key_backup.json")
```

#### 加密策略实施
```python
# 存储加密策略实施示例
class StorageEncryptionPolicy:
    def __init__(self, key_manager):
        self.key_manager = key_manager
        self.encryption_rules = {}
    
    def add_encryption_rule(self, data_type, algorithm="AES", key_rotation_days=90):
        """添加加密规则"""
        self.encryption_rules[data_type] = {
            'algorithm': algorithm,
            'key_rotation_days': key_rotation_days,
            'encryption_required': True
        }
    
    def should_encrypt(self, data_type):
        """检查数据类型是否需要加密"""
        return (data_type in self.encryption_rules and 
                self.encryption_rules[data_type]['encryption_required'])
    
    def get_encryption_algorithm(self, data_type):
        """获取数据类型的加密算法"""
        if data_type in self.encryption_rules:
            return self.encryption_rules[data_type]['algorithm']
        return "AES"  # 默认算法
    
    def encrypt_data_by_type(self, data, data_type, data_id):
        """根据数据类型加密数据"""
        if not self.should_encrypt(data_type):
            print(f"数据类型 {data_type} 不需要加密")
            return data
        
        # 获取或生成数据密钥
        try:
            data_key = self.key_manager.get_data_key(data_id)
        except ValueError:
            data_key = self.key_manager.generate_data_key(data_id)
        
        # 执行加密
        cipher = Fernet(data_key)
        if isinstance(data, str):
            encrypted_data = cipher.encrypt(data.encode('utf-8'))
        else:
            encrypted_data = cipher.encrypt(data)
        
        print(f"数据类型 {data_type} 的数据已加密")
        return encrypted_data
    
    def decrypt_data_by_type(self, encrypted_data, data_type, data_id):
        """根据数据类型解密数据"""
        if not self.should_encrypt(data_type):
            print(f"数据类型 {data_type} 不需要解密")
            return encrypted_data
        
        # 获取数据密钥
        data_key = self.key_manager.get_data_key(data_id)
        
        # 执行解密
        cipher = Fernet(data_key)
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # 如果原数据是字符串，转换回来
        try:
            return decrypted_data.decode('utf-8')
        except UnicodeDecodeError:
            return decrypted_data

# 使用示例
policy = StorageEncryptionPolicy(key_manager)
policy.add_encryption_rule("personal_info", "AES", 90)
policy.add_encryption_rule("financial_data", "AES", 30)
policy.add_encryption_rule("public_info", "AES", 365)  # 公共信息也加密但轮换周期长

# 加密不同类型的数据
personal_info = "用户的身份证号码、住址等敏感信息"
encrypted_personal = policy.encrypt_data_by_type(
    personal_info, "personal_info", "user_data_001")

financial_data = "用户的银行账户、交易记录等财务信息"
encrypted_financial = policy.encrypt_data_by_type(
    financial_data, "financial_data", "user_data_002")

public_info = "用户的公开信息，如昵称、头像等"
encrypted_public = policy.encrypt_data_by_type(
    public_info, "public_info", "user_data_003")

# 解密数据
decrypted_personal = policy.decrypt_data_by_type(
    encrypted_personal, "personal_info", "user_data_001")
print(f"解密的个人信息: {decrypted_personal}")
```

## 加密传输技术详解

### 传输中数据加密（Data in Transit Encryption）

传输中数据加密是指对在网络中传输的数据进行加密保护，防止数据在传输过程中被窃取或篡改。

#### TLS/SSL协议

TLS（Transport Layer Security）是目前最广泛使用的传输层加密协议，其前身是SSL（Secure Sockets Layer）。

##### TLS握手过程
```python
# TLS握手过程概念示例
class TLSHandshake:
    def __init__(self):
        self.client_hello = None
        self.server_hello = None
        self.master_secret = None
    
    def client_hello(self, client_random, supported_ciphers):
        """客户端Hello消息"""
        self.client_hello = {
            'protocol_version': 'TLS 1.3',
            'client_random': client_random,
            'supported_ciphers': supported_ciphers,
            'compression_methods': ['none']
        }
        print("客户端发送Hello消息")
        return self.client_hello
    
    def server_hello(self, server_random, selected_cipher):
        """服务器Hello消息"""
        self.server_hello = {
            'protocol_version': 'TLS 1.3',
            'server_random': server_random,
            'selected_cipher': selected_cipher
        }
        print("服务器发送Hello消息")
        return self.server_hello
    
    def exchange_keys(self, client_public_key, server_public_key):
        """密钥交换"""
        # 在实际TLS中，这里会使用Diffie-Hellman密钥交换算法
        print("客户端和服务器交换密钥")
        # 简化处理，实际实现会更复杂
        return "shared_secret"
    
    def generate_master_secret(self, shared_secret, client_random, server_random):
        """生成主密钥"""
        # 在实际TLS中，这里会使用PRF（伪随机函数）
        self.master_secret = f"{shared_secret}_{client_random}_{server_random}"
        print("生成主密钥")
        return self.master_secret
    
    def establish_secure_connection(self):
        """建立安全连接"""
        print("TLS握手完成，建立安全连接")
        return {
            'encryption_algorithm': 'AES-256-GCM',
            'master_secret': self.master_secret,
            'connection_status': 'secure'
        }

# 使用示例
tls_handshake = TLSHandshake()
client_hello = tls_handshake.client_hello("client_random_123", ["TLS_AES_256_GCM_SHA384"])
server_hello = tls_handshake.server_hello("server_random_456", "TLS_AES_256_GCM_SHA384")
shared_secret = tls_handshake.exchange_keys("client_pub_key", "server_pub_key")
master_secret = tls_handshake.generate_master_secret(shared_secret, "client_random_123", "server_random_456")
secure_connection = tls_handshake.establish_secure_connection()
```

#### HTTPS实现
```python
# HTTPS服务器示例（使用Flask）
from flask import Flask, request, jsonify
import ssl

app = Flask(__name__)

@app.route('/api/secure-data', methods=['POST'])
def secure_data_endpoint():
    """安全数据端点"""
    # 从请求中获取数据
    data = request.json
    
    # 在实际应用中，这里会处理加密数据
    # 由于TLS层已经处理了传输加密，应用层可以处理业务逻辑
    
    response = {
        'status': 'success',
        'message': '数据已安全接收',
        'received_data': data
    }
    
    return jsonify(response)

# 配置SSL上下文
def create_ssl_context():
    """创建SSL上下文"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('server.crt', 'server.key')
    return context

# 注意：在实际部署中，需要真实的证书文件
# context = create_ssl_context()
# app.run(host='0.0.0.0', port=443, ssl_context=context)
```

### 端到端加密（End-to-End Encryption）

端到端加密确保数据在发送方和接收方之间始终保持加密状态，即使经过中间服务器也无法被解密。

#### 实现示例
```python
# 端到端加密示例
class EndToEndEncryption:
    def __init__(self):
        self.user_keys = {}  # 存储用户公钥
    
    def generate_user_keypair(self, user_id):
        """为用户生成密钥对"""
        private_key = Fernet.generate_key()
        public_key = hashlib.sha256(private_key).digest()
        
        self.user_keys[user_id] = {
            'private_key': private_key,
            'public_key': public_key
        }
        
        return public_key
    
    def get_user_public_key(self, user_id):
        """获取用户公钥"""
        if user_id in self.user_keys:
            return self.user_keys[user_id]['public_key']
        return None
    
    def encrypt_message(self, message, recipient_id):
        """为接收者加密消息"""
        recipient_public_key = self.get_user_public_key(recipient_id)
        if not recipient_public_key:
            raise ValueError(f"用户 {recipient_id} 的公钥不存在")
        
        # 使用接收者的公钥加密消息
        # 这里简化处理，实际应用中会使用更复杂的非对称加密
        key = recipient_public_key[:32]  # 取前32字节作为对称密钥
        cipher = Fernet(base64.urlsafe_b64encode(key))
        encrypted_message = cipher.encrypt(message.encode('utf-8'))
        
        return encrypted_message
    
    def decrypt_message(self, encrypted_message, recipient_id):
        """接收者解密消息"""
        if recipient_id not in self.user_keys:
            raise ValueError(f"用户 {recipient_id} 的密钥不存在")
        
        private_key = self.user_keys[recipient_id]['private_key']
        key = private_key[:32]  # 取前32字节作为对称密钥
        cipher = Fernet(base64.urlsafe_b64encode(key))
        decrypted_message = cipher.decrypt(encrypted_message)
        
        return decrypted_message.decode('utf-8')

# 使用示例
e2e = EndToEndEncryption()
# 为发送者和接收者生成密钥对
sender_pub_key = e2e.generate_user_keypair("sender_001")
recipient_pub_key = e2e.generate_user_keypair("recipient_001")

# 发送者加密消息
message = "这是一条端到端加密的消息"
encrypted_message = e2e.encrypt_message(message, "recipient_001")
print(f"加密后的消息: {encrypted_message}")

# 接收者解密消息
decrypted_message = e2e.decrypt_message(encrypted_message, "recipient_001")
print(f"解密后的消息: {decrypted_message}")
```

### 传输加密最佳实践

#### 证书管理
```python
# 证书管理示例
class CertificateManager:
    def __init__(self):
        self.certificates = {}
        self.certificate_authority = None
    
    def generate_self_signed_cert(self, common_name, validity_days=365):
        """生成自签名证书"""
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        
        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # 创建证书
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=validity_days)
        ).sign(private_key, hashes.SHA256())
        
        cert_data = {
            'certificate': cert,
            'private_key': private_key,
            'common_name': common_name,
            'valid_from': cert.not_valid_before,
            'valid_to': cert.not_valid_after
        }
        
        self.certificates[common_name] = cert_data
        return cert_data
    
    def validate_certificate(self, cert_data):
        """验证证书有效性"""
        current_time = datetime.utcnow()
        valid_from = cert_data['valid_from']
        valid_to = cert_data['valid_to']
        
        if current_time < valid_from:
            return False, "证书尚未生效"
        if current_time > valid_to:
            return False, "证书已过期"
        
        return True, "证书有效"
    
    def renew_certificate(self, common_name, validity_days=365):
        """续订证书"""
        if common_name not in self.certificates:
            raise ValueError(f"证书 {common_name} 不存在")
        
        # 生成新证书
        new_cert = self.generate_self_signed_cert(common_name, validity_days)
        self.certificates[common_name] = new_cert
        
        print(f"证书 {common_name} 已续订")
        return new_cert

# 使用示例
cert_manager = CertificateManager()
server_cert = cert_manager.generate_self_signed_cert("api.example.com", 365)
is_valid, message = cert_manager.validate_certificate(server_cert)
print(f"证书验证结果: {message}")
```

#### 安全传输策略
```python
# 安全传输策略示例
class SecureTransportPolicy:
    def __init__(self):
        self.allowed_protocols = ['TLSv1.3', 'TLSv1.2']
        self.required_ciphers = [
            'TLS_AES_256_GCM_SHA384',
            'TLS_CHACHA20_POLY1305_SHA256',
            'TLS_AES_128_GCM_SHA256'
        ]
        self.min_key_size = 2048
    
    def validate_connection_security(self, protocol, cipher_suite, key_size):
        """验证连接安全性"""
        issues = []
        
        # 检查协议版本
        if protocol not in self.allowed_protocols:
            issues.append(f"不支持的协议版本: {protocol}")
        
        # 检查加密套件
        if cipher_suite not in self.required_ciphers:
            issues.append(f"不安全的加密套件: {cipher_suite}")
        
        # 检查密钥长度
        if key_size < self.min_key_size:
            issues.append(f"密钥长度不足: {key_size} < {self.min_key_size}")
        
        return len(issues) == 0, issues
    
    def enforce_security_policy(self, connection_info):
        """强制执行安全策略"""
        is_secure, issues = self.validate_connection_security(
            connection_info.get('protocol', ''),
            connection_info.get('cipher_suite', ''),
            connection_info.get('key_size', 0)
        )
        
        if not is_secure:
            print("安全策略违规:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        print("连接符合安全策略")
        return True

# 使用示例
transport_policy = SecureTransportPolicy()
connection_info = {
    'protocol': 'TLSv1.3',
    'cipher_suite': 'TLS_AES_256_GCM_SHA384',
    'key_size': 2048
}

is_compliant = transport_policy.enforce_security_policy(connection_info)
print(f"连接是否符合安全策略: {is_compliant}")
```

## 加密存储与传输的集成方案

### 统一数据保护平台
```python
# 统一数据保护平台示例
class UnifiedDataProtectionPlatform:
    def __init__(self):
        self.storage_encryption = StorageEncryptionPolicy(StorageKeyManager())
        self.transport_security = SecureTransportPolicy()
        self.encryption_algorithms = {
            'AES-256-GCM': self._aes_gcm_encrypt,
            'ChaCha20-Poly1305': self._chacha20_encrypt
        }
    
    def _aes_gcm_encrypt(self, data, key):
        """AES-GCM加密"""
        # 实现AES-GCM加密
        cipher = Fernet(key)
        return cipher.encrypt(data.encode() if isinstance(data, str) else data)
    
    def _chacha20_encrypt(self, data, key):
        """ChaCha20加密"""
        # 实现ChaCha20加密
        cipher = Fernet(key)
        return cipher.encrypt(data.encode() if isinstance(data, str) else data)
    
    def protect_data_at_rest(self, data, data_type, data_id):
        """保护静态数据"""
        return self.storage_encryption.encrypt_data_by_type(data, data_type, data_id)
    
    def protect_data_in_transit(self, data, transport_config):
        """保护传输中数据"""
        # 首先验证传输安全性
        is_secure = self.transport_security.enforce_security_policy(transport_config)
        if not is_secure:
            raise ValueError("传输配置不符合安全策略")
        
        # 选择合适的加密算法
        algorithm = transport_config.get('algorithm', 'AES-256-GCM')
        if algorithm in self.encryption_algorithms:
            # 在实际应用中，这里会使用TLS等标准协议
            # 这里简化处理，仅作示例
            key = Fernet.generate_key()
            encrypted_data = self.encryption_algorithms[algorithm](data, key)
            return encrypted_data
        else:
            raise ValueError(f"不支持的加密算法: {algorithm}")
    
    def comprehensive_data_protection(self, data, data_type, data_id, transport_config):
        """全面数据保护"""
        # 静态数据加密
        encrypted_storage_data = self.protect_data_at_rest(data, data_type, data_id)
        
        # 传输数据加密
        encrypted_transport_data = self.protect_data_in_transit(data, transport_config)
        
        return {
            'storage_encrypted': encrypted_storage_data,
            'transport_encrypted': encrypted_transport_data,
            'protection_status': 'complete'
        }

# 使用示例
platform = UnifiedDataProtectionPlatform()
platform.storage_encryption.add_encryption_rule("sensitive_data", "AES", 90)

sensitive_data = "这是需要全面保护的敏感数据"
transport_config = {
    'protocol': 'TLSv1.3',
    'cipher_suite': 'TLS_AES_256_GCM_SHA384',
    'key_size': 2048,
    'algorithm': 'AES-256-GCM'
}

protection_result = platform.comprehensive_data_protection(
    sensitive_data, "sensitive_data", "data_001", transport_config)

print("数据已获得全面保护:")
print(f"  - 静态数据加密完成: {bool(protection_result['storage_encrypted'])}")
print(f"  - 传输数据加密完成: {bool(protection_result['transport_encrypted'])}")
```

### 监控与审计
```python
# 加密监控与审计示例
class EncryptionMonitoring:
    def __init__(self):
        self.encryption_events = []
        self.security_alerts = []
    
    def log_encryption_event(self, event_type, data_id, algorithm, status, details=""):
        """记录加密事件"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,  # encrypt, decrypt, key_rotation, etc.
            'data_id': data_id,
            'algorithm': algorithm,
            'status': status,  # success, failed
            'details': details
        }
        
        self.encryption_events.append(event)
        print(f"记录加密事件: {event_type} - {status}")
    
    def log_security_alert(self, alert_type, severity, message, data_id=None):
        """记录安全警报"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_type,
            'severity': severity,  # low, medium, high, critical
            'message': message,
            'data_id': data_id
        }
        
        self.security_alerts.append(alert)
        print(f"安全警报 [{severity}]: {message}")
    
    def generate_encryption_report(self, time_range_hours=24):
        """生成加密报告"""
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        
        # 过滤时间范围内的事件
        recent_events = [
            event for event in self.encryption_events
            if datetime.fromisoformat(event['timestamp']) > cutoff_time
        ]
        
        # 统计信息
        total_events = len(recent_events)
        successful_encryptions = len([
            event for event in recent_events
            if event['event_type'] == 'encrypt' and event['status'] == 'success'
        ])
        failed_operations = len([
            event for event in recent_events
            if event['status'] == 'failed'
        ])
        
        report = {
            'time_range_hours': time_range_hours,
            'total_events': total_events,
            'successful_encryptions': successful_encryptions,
            'failed_operations': failed_operations,
            'recent_events': recent_events[-10:],  # 最近10个事件
            'security_alerts': self.security_alerts[-5:]  # 最近5个警报
        }
        
        return report
    
    def check_for_anomalies(self):
        """检查异常行为"""
        # 检查失败率是否过高
        recent_events = self.encryption_events[-100:]  # 最近100个事件
        if len(recent_events) > 10:
            failed_events = [
                event for event in recent_events
                if event['status'] == 'failed'
            ]
            failure_rate = len(failed_events) / len(recent_events)
            
            if failure_rate > 0.1:  # 失败率超过10%
                self.log_security_alert(
                    'high_failure_rate',
                    'high',
                    f'加密操作失败率过高: {failure_rate:.2%}',
                    None
                )

# 使用示例
monitor = EncryptionMonitoring()

# 模拟一些加密事件
monitor.log_encryption_event('encrypt', 'user_data_001', 'AES-256', 'success')
monitor.log_encryption_event('decrypt', 'user_data_001', 'AES-256', 'success')
monitor.log_encryption_event('key_rotation', 'master_key', 'N/A', 'success')
monitor.log_encryption_event('encrypt', 'user_data_002', 'AES-256', 'failed', '密钥错误')

# 记录安全警报
monitor.log_security_alert('unauthorized_access', 'medium', '检测到未授权访问尝试', 'user_data_003')

# 生成报告
report = monitor.generate_encryption_report(24)
print("24小时加密报告:")
print(f"  总事件数: {report['total_events']}")
print(f"  成功加密数: {report['successful_encryptions']}")
print(f"  失败操作数: {report['failed_operations']}")

# 检查异常
monitor.check_for_anomalies()
```

加密存储与加密传输作为数据安全防护体系的两个核心环节，共同构建了端到端的数据安全解决方案。通过合理选择和实施静态数据加密、传输中数据加密技术，结合完善的密钥管理、证书管理和安全策略，可以有效保护数据在整个生命周期中的安全性。

在实际应用中，需要根据具体的业务需求、安全要求和合规性标准来选择合适的加密技术和实施方案。同时，建立完善的监控和审计机制，能够及时发现和响应安全事件，确保数据保护措施的有效性。

随着技术的不断发展，新的加密技术和标准不断涌现，如后量子加密、同态加密等，将为数据安全带来新的解决方案。持续关注和采用这些新技术，将有助于构建更加安全可靠的数据保护体系。