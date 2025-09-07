---
title: 日志加密与访问控制：构建安全可靠的日志管理系统
date: 2025-08-31
categories: [Microservices, Logging, Security]
tags: [log-monitor]
published: true
---

在前两篇文章中，我们探讨了日志中敏感信息的识别、分类和保护策略。本文将深入研究日志加密与访问控制的具体实现方法，包括传输加密、存储加密以及细粒度的访问控制策略，帮助您构建安全可靠的日志管理系统。

## 日志数据加密策略

### 传输加密（TLS/SSL）

传输加密确保日志数据在网络传输过程中的安全性，防止数据被窃听或篡改。

#### TLS配置实现

```java
@Configuration
public class SecureLogTransmissionConfig {
    
    @Bean
    public SSLContext sslContext() throws Exception {
        // 加载密钥库
        KeyStore keyStore = KeyStore.getInstance("JKS");
        try (InputStream keyStoreStream = 
             getClass().getResourceAsStream("/keystore.jks")) {
            keyStore.load(keyStoreStream, "keystorePassword".toCharArray());
        }
        
        // 初始化密钥管理器
        KeyManagerFactory keyManagerFactory = 
            KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
        keyManagerFactory.init(keyStore, "keyPassword".toCharArray());
        
        // 加载信任库
        KeyStore trustStore = KeyStore.getInstance("JKS");
        try (InputStream trustStoreStream = 
             getClass().getResourceAsStream("/truststore.jks")) {
            trustStore.load(trustStoreStream, "truststorePassword".toCharArray());
        }
        
        // 初始化信任管理器
        TrustManagerFactory trustManagerFactory = 
            TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        trustManagerFactory.init(trustStore);
        
        // 创建SSL上下文
        SSLContext sslContext = SSLContext.getInstance("TLSv1.3");
        sslContext.init(
            keyManagerFactory.getKeyManagers(),
            trustManagerFactory.getTrustManagers(),
            null
        );
        
        return sslContext;
    }
    
    @Bean
    public HttpClient secureHttpClient(SSLContext sslContext) {
        return HttpClient.newBuilder()
            .sslContext(sslContext)
            .connectTimeout(Duration.ofSeconds(30))
            .build();
    }
}
```

#### Logstash TLS配置

```ruby
# logstash.conf
output {
  elasticsearch {
    hosts => ["https://elasticsearch:9200"]
    ssl => true
    ssl_certificate_verification => true
    ssl_truststore_path => "/etc/logstash/truststore.jks"
    ssl_truststore_password => "truststorePassword"
    ssl_keystore_path => "/etc/logstash/keystore.jks"
    ssl_keystore_password => "keystorePassword"
    user => "logstash_user"
    password => "secure_password"
  }
}
```

#### 客户端TLS配置

```java
@Component
public class SecureLogClient {
    
    private final HttpClient httpClient;
    
    public SecureLogClient(HttpClient httpClient) {
        this.httpClient = httpClient;
    }
    
    public void sendLogSecurely(LogEntry logEntry) throws Exception {
        String logJson = objectMapper.writeValueAsString(logEntry);
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://log-server:9200/logs"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(logJson))
            .build();
        
        HttpResponse<String> response = httpClient.send(request, 
            HttpResponse.BodyHandlers.ofString());
        
        if (response.statusCode() != 200) {
            throw new RuntimeException("Failed to send log: " + response.body());
        }
    }
}
```

### 存储加密

存储加密保护日志数据在存储介质上的安全性，防止物理访问导致的数据泄露。

#### 数据库级别加密

```java
@Entity
@Table(name = "encrypted_logs")
public class EncryptedLogEntry {
    @Id
    private String id;
    
    @Column(name = "timestamp_encrypted")
    @Convert(converter = EncryptedStringConverter.class)
    private String timestamp;
    
    @Column(name = "level_encrypted")
    @Convert(converter = EncryptedStringConverter.class)
    private String level;
    
    @Column(name = "service_encrypted")
    @Convert(converter = EncryptedStringConverter.class)
    private String service;
    
    @Column(name = "message_encrypted", length = 10000)
    @Convert(converter = EncryptedStringConverter.class)
    private String message;
    
    @Column(name = "user_id_encrypted")
    @Convert(converter = EncryptedStringConverter.class)
    private String userId;
    
    @Column(name = "ip_address_encrypted")
    @Convert(converter = EncryptedStringConverter.class)
    private String ipAddress;
    
    // getters and setters
}

@Converter
public class EncryptedStringConverter implements AttributeConverter<String, String> {
    
    @Autowired
    private EncryptionService encryptionService;
    
    @Override
    public String convertToDatabaseColumn(String attribute) {
        if (attribute == null) {
            return null;
        }
        return encryptionService.encrypt(attribute);
    }
    
    @Override
    public String convertToEntityAttribute(String dbData) {
        if (dbData == null) {
            return null;
        }
        return encryptionService.decrypt(dbData);
    }
}
```

#### 文件系统级别加密

```java
@Component
public class EncryptedFileLogStorage {
    
    private final EncryptionService encryptionService;
    private final Path logDirectory;
    
    public EncryptedFileLogStorage(EncryptionService encryptionService, 
                                  @Value("${log.storage.path}") String logPath) {
        this.encryptionService = encryptionService;
        this.logDirectory = Paths.get(logPath);
    }
    
    public void storeEncryptedLog(String serviceName, LogEntry logEntry) throws IOException {
        // 创建服务特定的日志文件
        Path logFile = logDirectory.resolve(serviceName + ".log.encrypted");
        
        // 序列化并加密日志条目
        String logJson = objectMapper.writeValueAsString(logEntry);
        String encryptedLog = encryptionService.encrypt(logJson);
        
        // 追加到文件
        Files.write(logFile, (encryptedLog + "\n").getBytes(), 
                   StandardOpenOption.CREATE, StandardOpenOption.APPEND);
    }
    
    public List<LogEntry> retrieveDecryptedLogs(String serviceName, 
                                               Instant startTime, 
                                               Instant endTime) throws IOException {
        Path logFile = logDirectory.resolve(serviceName + ".log.encrypted");
        
        if (!Files.exists(logFile)) {
            return Collections.emptyList();
        }
        
        List<LogEntry> decryptedLogs = new ArrayList<>();
        
        try (Stream<String> lines = Files.lines(logFile)) {
            lines.forEach(line -> {
                try {
                    // 解密日志行
                    String decryptedLine = encryptionService.decrypt(line.trim());
                    
                    // 反序列化日志条目
                    LogEntry logEntry = objectMapper.readValue(decryptedLine, LogEntry.class);
                    
                    // 过滤时间范围
                    Instant logTime = Instant.parse(logEntry.getTimestamp());
                    if (!logTime.isBefore(startTime) && !logTime.isAfter(endTime)) {
                        decryptedLogs.add(logEntry);
                    }
                } catch (Exception e) {
                    log.warn("Failed to decrypt log line", e);
                }
            });
        }
        
        return decryptedLogs;
    }
}
```

#### Elasticsearch加密配置

```yaml
# elasticsearch.yml
# 启用传输层安全
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: certificate
xpack.security.transport.ssl.key: certs/elastic-certificates.key
xpack.security.transport.ssl.certificate: certs/elastic-certificates.crt
xpack.security.transport.ssl.certificate_authorities: certs/elastic-stack-ca.crt

# 启用HTTP层安全
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.verification_mode: certificate
xpack.security.http.ssl.key: certs/elastic-certificates.key
xpack.security.http.ssl.certificate: certs/elastic-certificates.crt
xpack.security.http.ssl.certificate_authorities: certs/elastic-stack-ca.crt

# 启用加密密钥存储
xpack.security.encryption.algorithm: AES/CTR/NoPadding
```

### 字段级加密

对特定敏感字段进行加密，提供更精细的保护：

```java
@Component
public class FieldLevelEncryptionService {
    
    private final Map<String, EncryptionPolicy> fieldPolicies = new HashMap<>();
    
    public FieldLevelEncryptionService() {
        // 为不同字段定义加密策略
        fieldPolicies.put("userId", new EncryptionPolicy()
            .setAlgorithm(EncryptionAlgorithm.AES_256_GCM)
            .setRequired(true));
        
        fieldPolicies.put("email", new EncryptionPolicy()
            .setAlgorithm(EncryptionAlgorithm.AES_256_GCM)
            .setRequired(true));
        
        fieldPolicies.put("phoneNumber", new EncryptionPolicy()
            .setAlgorithm(EncryptionAlgorithm.AES_256_GCM)
            .setRequired(true));
        
        fieldPolicies.put("creditCard", new EncryptionPolicy()
            .setAlgorithm(EncryptionAlgorithm.AES_256_GCM)
            .setRequired(true));
    }
    
    public LogEntry encryptSensitiveFields(LogEntry logEntry) {
        LogEntry encryptedEntry = new LogEntry();
        encryptedEntry.setId(logEntry.getId());
        encryptedEntry.setTimestamp(logEntry.getTimestamp());
        encryptedEntry.setLevel(logEntry.getLevel());
        encryptedEntry.setService(logEntry.getService());
        encryptedEntry.setMessage(logEntry.getMessage());
        
        // 加密敏感字段
        if (logEntry.getUserId() != null) {
            encryptedEntry.setUserId(encryptField("userId", logEntry.getUserId()));
        }
        
        if (logEntry.getEmail() != null) {
            encryptedEntry.setEmail(encryptField("email", logEntry.getEmail()));
        }
        
        if (logEntry.getPhoneNumber() != null) {
            encryptedEntry.setPhoneNumber(encryptField("phoneNumber", logEntry.getPhoneNumber()));
        }
        
        if (logEntry.getCreditCard() != null) {
            encryptedEntry.setCreditCard(encryptField("creditCard", logEntry.getCreditCard()));
        }
        
        return encryptedEntry;
    }
    
    private String encryptField(String fieldName, String fieldValue) {
        EncryptionPolicy policy = fieldPolicies.get(fieldName);
        if (policy == null || !policy.isRequired()) {
            return fieldValue;
        }
        
        return encryptionService.encrypt(fieldValue, policy.getAlgorithm());
    }
    
    public LogEntry decryptSensitiveFields(LogEntry encryptedEntry) {
        LogEntry decryptedEntry = new LogEntry();
        decryptedEntry.setId(encryptedEntry.getId());
        decryptedEntry.setTimestamp(encryptedEntry.getTimestamp());
        decryptedEntry.setLevel(encryptedEntry.getLevel());
        decryptedEntry.setService(encryptedEntry.getService());
        decryptedEntry.setMessage(encryptedEntry.getMessage());
        
        // 解密敏感字段
        if (encryptedEntry.getUserId() != null) {
            decryptedEntry.setUserId(decryptField("userId", encryptedEntry.getUserId()));
        }
        
        if (encryptedEntry.getEmail() != null) {
            decryptedEntry.setEmail(decryptField("email", encryptedEntry.getEmail()));
        }
        
        if (encryptedEntry.getPhoneNumber() != null) {
            decryptedEntry.setPhoneNumber(decryptField("phoneNumber", encryptedEntry.getPhoneNumber()));
        }
        
        if (encryptedEntry.getCreditCard() != null) {
            decryptedEntry.setCreditCard(decryptField("creditCard", encryptedEntry.getCreditCard()));
        }
        
        return decryptedEntry;
    }
    
    private String decryptField(String fieldName, String encryptedValue) {
        EncryptionPolicy policy = fieldPolicies.get(fieldName);
        if (policy == null) {
            return encryptedValue;
        }
        
        return encryptionService.decrypt(encryptedValue, policy.getAlgorithm());
    }
}
```

## 访问控制机制

### 基于角色的访问控制（RBAC）

RBAC通过角色定义用户权限，简化权限管理：

```java
@Entity
@Table(name = "roles")
public class Role {
    @Id
    private String id;
    
    @Enumerated(EnumType.STRING)
    private RoleType roleType;
    
    @ElementCollection
    @CollectionTable(name = "role_permissions", joinColumns = @JoinColumn(name = "role_id"))
    @Column(name = "permission")
    private Set<String> permissions;
    
    // getters and setters
}

public enum RoleType {
    ADMIN("系统管理员"),
    SECURITY("安全管理员"),
    OPERATIONS("运维人员"),
    DEVELOPER("开发人员"),
    AUDITOR("审计员"),
    GUEST("访客");
    
    private final String description;
    
    RoleType(String description) {
        this.description = description;
    }
    
    // getter
}

@Entity
@Table(name = "users")
public class User {
    @Id
    private String id;
    
    private String username;
    
    private String email;
    
    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles;
    
    // getters and setters
}
```

#### 权限配置

```java
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .authorizeRequests()
                // 公共接口
                .antMatchers("/api/health").permitAll()
                .antMatchers("/api/metrics").permitAll()
                
                // 管理员接口
                .antMatchers("/api/admin/**").hasRole("ADMIN")
                
                // 安全相关接口
                .antMatchers("/api/security/**").hasAnyRole("ADMIN", "SECURITY")
                
                // 运维接口
                .antMatchers("/api/operations/**").hasAnyRole("ADMIN", "OPERATIONS")
                
                // 开发接口
                .antMatchers("/api/development/**").hasAnyRole("ADMIN", "DEVELOPER")
                
                // 审计接口
                .antMatchers("/api/audit/**").hasAnyRole("ADMIN", "AUDITOR")
                
                // 日志查询接口
                .antMatchers("/api/logs/query").hasAnyRole("ADMIN", "OPERATIONS", "SECURITY")
                
                // 日志导出接口
                .antMatchers("/api/logs/export").hasAnyRole("ADMIN", "AUDITOR")
                
                .anyRequest().authenticated()
            .and()
            .httpBasic()
            .and()
            .csrf().disable();
    }
}
```

#### 方法级权限控制

```java
@Service
public class LogAccessService {
    
    @PreAuthorize("hasRole('ADMIN') or hasRole('SECURITY')")
    public List<LogEntry> getSecurityLogs(Instant startTime, Instant endTime) {
        return logRepository.findSecurityLogs(startTime, endTime);
    }
    
    @PreAuthorize("hasRole('ADMIN') or hasRole('OPERATIONS')")
    public List<LogEntry> getOperationalLogs(String service, Instant startTime, Instant endTime) {
        return logRepository.findOperationalLogs(service, startTime, endTime);
    }
    
    @PreAuthorize("hasRole('ADMIN') or hasRole('AUDITOR')")
    public void exportLogs(ExportRequest request) {
        // 导出日志逻辑
        logExportService.exportLogs(request);
    }
    
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteLogs(Instant beforeTime) {
        logRepository.deleteLogsBefore(beforeTime);
    }
}
```

### 基于属性的访问控制（ABAC）

ABAC提供更灵活的权限控制，基于用户、资源和环境属性：

```java
@Component
public class AttributeBasedAccessControl {
    
    public boolean canAccessLog(User user, LogEntry logEntry, AccessContext context) {
        // 检查用户角色
        if (user.hasRole("ADMIN")) {
            return true; // 管理员可以访问所有日志
        }
        
        // 检查用户部门
        if (!user.getDepartment().equals(logEntry.getServiceDepartment())) {
            return false; // 用户部门与服务部门不匹配
        }
        
        // 检查敏感级别
        if (logEntry.getSensitivityLevel() == SensitivityLevel.HIGH && 
            !user.hasRole("SECURITY")) {
            return false; // 高敏感度日志需要安全角色
        }
        
        // 检查时间约束
        if (context.getCurrentTime().isAfter(context.getAccessWindowEnd()) ||
            context.getCurrentTime().isBefore(context.getAccessWindowStart())) {
            return false; // 不在访问时间窗口内
        }
        
        // 检查IP地址限制
        if (!isAllowedIpAddress(context.getClientIpAddress(), user.getAllowedIpRanges())) {
            return false; // IP地址不在允许范围内
        }
        
        return true;
    }
    
    private boolean isAllowedIpAddress(String clientIp, Set<String> allowedIpRanges) {
        try {
            InetAddress clientAddress = InetAddress.getByName(clientIp);
            
            for (String ipRange : allowedIpRanges) {
                if (isInRange(clientAddress, ipRange)) {
                    return true;
                }
            }
        } catch (UnknownHostException e) {
            log.warn("Invalid IP address: {}", clientIp, e);
        }
        
        return false;
    }
    
    private boolean isInRange(InetAddress address, String range) {
        // 实现IP范围检查逻辑
        // 这里简化处理，实际应用中需要实现完整的IP范围匹配
        return range.contains(address.getHostAddress());
    }
}
```

### 细粒度访问控制

实现基于日志内容和用户权限的细粒度访问控制：

```java
@Component
public class FineGrainedLogAccessControl {
    
    private final AttributeBasedAccessControl abac;
    private final SensitiveDataClassifier classifier;
    
    public boolean canViewLogField(User user, LogEntry logEntry, String fieldName) {
        // 检查字段敏感性
        SensitivityLevel fieldSensitivity = classifier.classifyField(fieldName);
        
        // 管理员可以查看所有字段
        if (user.hasRole("ADMIN")) {
            return true;
        }
        
        // 根据字段敏感性和用户角色决定访问权限
        switch (fieldSensitivity) {
            case HIGH:
                return user.hasRole("SECURITY") || user.hasRole("ADMIN");
            case MEDIUM:
                return user.hasRole("SECURITY") || 
                       user.hasRole("ADMIN") || 
                       user.hasRole("AUDITOR");
            case LOW:
                return user.hasRole("SECURITY") || 
                       user.hasRole("ADMIN") || 
                       user.hasRole("OPERATIONS") || 
                       user.hasRole("DEVELOPER");
            default:
                return true;
        }
    }
    
    public LogEntry filterLogEntry(User user, LogEntry logEntry) {
        LogEntry filteredEntry = new LogEntry();
        filteredEntry.setId(logEntry.getId());
        filteredEntry.setTimestamp(logEntry.getTimestamp());
        filteredEntry.setLevel(logEntry.getLevel());
        filteredEntry.setService(logEntry.getService());
        
        // 根据用户权限过滤字段
        if (canViewLogField(user, logEntry, "message")) {
            filteredEntry.setMessage(logEntry.getMessage());
        } else {
            filteredEntry.setMessage("*** REDACTED ***");
        }
        
        if (canViewLogField(user, logEntry, "userId")) {
            filteredEntry.setUserId(logEntry.getUserId());
        } else {
            filteredEntry.setUserId("*** REDACTED ***");
        }
        
        if (canViewLogField(user, logEntry, "ipAddress")) {
            filteredEntry.setIpAddress(logEntry.getIpAddress());
        } else {
            filteredEntry.setIpAddress("*** REDACTED ***");
        }
        
        // 继续过滤其他字段...
        
        return filteredEntry;
    }
}
```

## 审计日志与监控

### 访问审计

记录所有日志访问操作，确保可追溯性：

```java
@Entity
@Table(name = "access_audit_logs")
public class AccessAuditLog {
    @Id
    private String id;
    
    private String userId;
    
    private String userName;
    
    private String userRole;
    
    private String resourceType; // LOG, DASHBOARD, CONFIG, etc.
    
    private String resourceId; // 具体资源ID
    
    private String action; // READ, WRITE, DELETE, EXPORT, etc.
    
    private String clientIpAddress;
    
    private Instant timestamp;
    
    @Column(length = 2000)
    private String details;
    
    private String userAgent;
    
    private String sessionId;
    
    private AccessResult accessResult; // GRANTED, DENIED, FAILED
    
    private String failureReason;
    
    // getters and setters
}

@Aspect
@Component
public class LogAccessAuditAspect {
    
    private static final Logger auditLogger = LoggerFactory.getLogger("ACCESS_AUDIT");
    
    @Around("@annotation(LogAccessAudited)")
    public Object auditLogAccess(ProceedingJoinPoint joinPoint) throws Throwable {
        String userId = getCurrentUserId();
        String userName = getCurrentUserName();
        String userRole = getCurrentUserRole();
        String methodName = joinPoint.getSignature().getName();
        String clientIp = getClientIpAddress();
        Instant startTime = Instant.now();
        
        AccessAuditLog auditLog = new AccessAuditLog();
        auditLog.setId(UUID.randomUUID().toString());
        auditLog.setUserId(userId);
        auditLog.setUserName(userName);
        auditLog.setUserRole(userRole);
        auditLog.setResourceType("LOG");
        auditLog.setAction(extractActionFromMethod(methodName));
        auditLog.setClientIpAddress(clientIp);
        auditLog.setTimestamp(startTime);
        auditLog.setUserAgent(getUserAgent());
        auditLog.setSessionId(getCurrentSessionId());
        
        try {
            Object result = joinPoint.proceed();
            
            auditLog.setAccessResult(AccessResult.GRANTED);
            auditLog.setDetails("Access granted for method: " + methodName + 
                              ", duration: " + (System.currentTimeMillis() - startTime.toEpochMilli()) + "ms");
            
            auditLogger.info("Log access granted - User: {}, Method: {}, Duration: {}ms",
                userName, methodName, System.currentTimeMillis() - startTime.toEpochMilli());
            
            return result;
        } catch (AccessDeniedException e) {
            auditLog.setAccessResult(AccessResult.DENIED);
            auditLog.setFailureReason(e.getMessage());
            
            auditLogger.warn("Log access denied - User: {}, Method: {}, Reason: {}",
                userName, methodName, e.getMessage());
            
            throw e;
        } catch (Exception e) {
            auditLog.setAccessResult(AccessResult.FAILED);
            auditLog.setFailureReason(e.getMessage());
            
            auditLogger.error("Log access failed - User: {}, Method: {}, Error: {}",
                userName, methodName, e.getMessage(), e);
            
            throw e;
        } finally {
            // 异步保存审计日志
            auditLogService.saveAsync(auditLog);
        }
    }
    
    private String extractActionFromMethod(String methodName) {
        if (methodName.startsWith("get") || methodName.startsWith("find")) {
            return "READ";
        } else if (methodName.startsWith("save") || methodName.startsWith("update")) {
            return "WRITE";
        } else if (methodName.startsWith("delete")) {
            return "DELETE";
        } else if (methodName.contains("export")) {
            return "EXPORT";
        } else {
            return "UNKNOWN";
        }
    }
}
```

### 实时监控与告警

监控访问模式并及时发现异常行为：

```java
@Component
public class RealTimeAccessMonitor {
    
    private final MeterRegistry meterRegistry;
    private final Counter accessGrantedCounter;
    private final Counter accessDeniedCounter;
    private final Counter accessFailedCounter;
    private final Timer accessResponseTimer;
    
    private final Map<String, AtomicInteger> userAccessCount = new ConcurrentHashMap<>();
    private final Map<String, AtomicInteger> ipAccessCount = new ConcurrentHashMap<>();
    
    public RealTimeAccessMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.accessGrantedCounter = Counter.builder("log.access.granted")
            .description("Number of granted log access requests")
            .register(meterRegistry);
        this.accessDeniedCounter = Counter.builder("log.access.denied")
            .description("Number of denied log access requests")
            .register(meterRegistry);
        this.accessFailedCounter = Counter.builder("log.access.failed")
            .description("Number of failed log access requests")
            .register(meterRegistry);
        this.accessResponseTimer = Timer.builder("log.access.response.time")
            .description("Response time for log access requests")
            .register(meterRegistry);
    }
    
    @EventListener
    public void handleAccessAuditEvent(AccessAuditLog auditLog) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            // 更新计数器
            switch (auditLog.getAccessResult()) {
                case GRANTED:
                    accessGrantedCounter.increment();
                    break;
                case DENIED:
                    accessDeniedCounter.increment();
                    break;
                case FAILED:
                    accessFailedCounter.increment();
                    break;
            }
            
            // 统计用户访问频率
            userAccessCount.computeIfAbsent(auditLog.getUserId(), 
                k -> new AtomicInteger(0)).incrementAndGet();
            
            // 统计IP访问频率
            ipAccessCount.computeIfAbsent(auditLog.getClientIpAddress(), 
                k -> new AtomicInteger(0)).incrementAndGet();
            
            // 检查异常访问模式
            checkAnomalousAccessPatterns(auditLog);
            
        } finally {
            sample.stop(accessResponseTimer);
        }
    }
    
    private void checkAnomalousAccessPatterns(AccessAuditLog auditLog) {
        // 检查用户访问频率异常
        int userAccessCount = this.userAccessCount.get(auditLog.getUserId()).get();
        if (userAccessCount > 1000) { // 单用户1小时内访问超过1000次
            triggerSecurityAlert("HIGH_USER_ACCESS_FREQUENCY", auditLog);
        }
        
        // 检查IP访问频率异常
        int ipAccessCount = this.ipAccessCount.get(auditLog.getClientIpAddress()).get();
        if (ipAccessCount > 5000) { // 单IP 1小时内访问超过5000次
            triggerSecurityAlert("HIGH_IP_ACCESS_FREQUENCY", auditLog);
        }
        
        // 检查非工作时间访问
        LocalTime accessTime = auditLog.getTimestamp().atZone(ZoneId.systemDefault()).toLocalTime();
        if (accessTime.isBefore(LocalTime.of(8, 0)) || accessTime.isAfter(LocalTime.of(18, 0))) {
            // 工作时间外访问需要额外关注
            if (auditLog.getResourceType().equals("LOG") && 
                auditLog.getAction().equals("EXPORT")) {
                triggerSecurityAlert("OFF_HOUR_LOG_EXPORT", auditLog);
            }
        }
    }
    
    private void triggerSecurityAlert(String alertType, AccessAuditLog auditLog) {
        SecurityAlert alert = new SecurityAlert();
        alert.setType(alertType);
        alert.setTimestamp(Instant.now());
        alert.setSeverity(AlertSeverity.HIGH);
        alert.setSource("ACCESS_MONITOR");
        alert.setDetails("Anomalous access pattern detected: " + alertType);
        alert.setRelatedData(objectMapper.writeValueAsString(auditLog));
        
        // 发送告警
        alertService.sendAlert(alert);
        
        // 记录告警日志
        log.warn("Security alert triggered: {} for user {} from IP {}", 
                alertType, auditLog.getUserName(), auditLog.getClientIpAddress());
    }
}
```

## 最佳实践

### 1. 零信任安全模型

实施零信任安全模型，确保每个访问请求都经过验证：

```java
@Component
public class ZeroTrustSecurityManager {
    
    public boolean validateAccessRequest(AccessRequest request) {
        // 多因素验证
        if (!validateIdentity(request.getUserId())) {
            log.warn("Identity validation failed for user: {}", request.getUserId());
            return false;
        }
        
        // 设备验证
        if (!validateDevice(request.getDeviceId())) {
            log.warn("Device validation failed for device: {}", request.getDeviceId());
            return false;
        }
        
        // 位置验证
        if (!validateLocation(request.getIpAddress())) {
            log.warn("Location validation failed for IP: {}", request.getIpAddress());
            return false;
        }
        
        // 权限验证
        if (!validatePermissions(request.getUserId(), request.getResource())) {
            log.warn("Permission validation failed for user: {} on resource: {}", 
                    request.getUserId(), request.getResource());
            return false;
        }
        
        // 行为分析
        if (!analyzeBehavior(request)) {
            log.warn("Behavior analysis failed for user: {}", request.getUserId());
            return false;
        }
        
        // 记录访问日志
        logAccessAttempt(request);
        
        return true;
    }
    
    private boolean analyzeBehavior(AccessRequest request) {
        // 获取用户历史访问模式
        List<AccessAuditLog> history = auditLogService.getUserAccessHistory(
            request.getUserId(), Instant.now().minus(Duration.ofDays(30)));
        
        // 分析访问模式
        BehaviorAnalysisResult result = behaviorAnalyzer.analyze(history);
        
        // 如果行为异常，需要额外验证
        if (result.isAnomalous()) {
            log.warn("Anomalous behavior detected for user: {}", request.getUserId());
            return performAdditionalVerification(request);
        }
        
        return true;
    }
}
```

### 2. 密钥管理

实施安全的密钥管理策略：

```java
@Component
public class SecureKeyManagementService {
    
    private final KeyStore keyStore;
    private final SecretKey encryptionKey;
    private final ScheduledExecutorService keyRotationScheduler;
    
    public SecureKeyManagementService() throws Exception {
        // 初始化密钥库
        this.keyStore = KeyStore.getInstance("JCEKS");
        this.keyStore.load(null, null);
        
        // 生成主加密密钥
        this.encryptionKey = generateEncryptionKey();
        storeKey("master-encryption-key", encryptionKey);
        
        // 启动密钥轮换任务
        this.keyRotationScheduler = Executors.newScheduledThreadPool(1);
        this.keyRotationScheduler.scheduleAtFixedRate(
            this::rotateKeys, 
            30, // 30天后开始
            30, // 每30天轮换一次
            TimeUnit.DAYS
        );
    }
    
    private SecretKey generateEncryptionKey() {
        try {
            KeyGenerator keyGenerator = KeyGenerator.getInstance("AES");
            keyGenerator.init(256);
            return keyGenerator.generateKey();
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate encryption key", e);
        }
    }
    
    public SecretKey getCurrentEncryptionKey() {
        try {
            return (SecretKey) keyStore.getKey("master-encryption-key", null);
        } catch (Exception e) {
            throw new RuntimeException("Failed to get encryption key", e);
        }
    }
    
    private void rotateKeys() {
        try {
            log.info("Starting key rotation process");
            
            // 生成新密钥
            SecretKey newKey = generateEncryptionKey();
            
            // 更新密钥库
            storeKey("master-encryption-key", newKey);
            
            // 重新加密现有数据（如果需要）
            reencryptDataWithNewKey();
            
            log.info("Key rotation completed successfully");
        } catch (Exception e) {
            log.error("Key rotation failed", e);
            // 发送告警
            alertService.sendAlert(new SecurityAlert()
                .setType("KEY_ROTATION_FAILED")
                .setSeverity(AlertSeverity.CRITICAL)
                .setDetails("Key rotation process failed: " + e.getMessage()));
        }
    }
    
    private void reencryptDataWithNewKey() {
        // 实现数据重新加密逻辑
        // 注意：这可能是一个耗时操作，需要考虑性能影响
    }
}
```

### 3. 安全配置管理

集中管理安全配置并定期审查：

```java
@ConfigurationProperties(prefix = "log.security")
@Component
public class LogSecurityConfiguration {
    
    private EncryptionConfig encryption = new EncryptionConfig();
    private AccessControlConfig accessControl = new AccessControlConfig();
    private AuditConfig audit = new AuditConfig();
    
    // getters and setters
    
    public static class EncryptionConfig {
        private boolean enabled = true;
        private String algorithm = "AES/GCM/NoPadding";
        private int keySize = 256;
        private boolean fieldLevelEncryption = true;
        
        // getters and setters
    }
    
    public static class AccessControlConfig {
        private boolean rbacEnabled = true;
        private boolean abacEnabled = true;
        private List<String> allowedIpRanges = new ArrayList<>();
        private Map<String, List<String>> rolePermissions = new HashMap<>();
        
        // getters and setters
    }
    
    public static class AuditConfig {
        private boolean enabled = true;
        private boolean detailedLogging = true;
        private int retentionDays = 365;
        
        // getters and setters
    }
}

@Component
public class SecurityConfigurationValidator {
    
    @EventListener
    public void validateConfiguration(LogSecurityConfiguration config) {
        List<String> issues = new ArrayList<>();
        
        // 验证加密配置
        if (config.getEncryption().isEnabled()) {
            if (config.getEncryption().getKeySize() < 256) {
                issues.add("Encryption key size should be at least 256 bits");
            }
            
            if (!config.getEncryption().getAlgorithm().contains("GCM")) {
                issues.add("GCM mode should be used for authenticated encryption");
            }
        }
        
        // 验证访问控制配置
        if (config.getAccessControl().isRbacEnabled() && 
            config.getAccessControl().getRolePermissions().isEmpty()) {
            issues.add("RBAC is enabled but no role permissions are configured");
        }
        
        // 验证审计配置
        if (config.getAudit().isEnabled() && 
            config.getAudit().getRetentionDays() < 90) {
            issues.add("Audit log retention should be at least 90 days");
        }
        
        if (!issues.isEmpty()) {
            log.warn("Security configuration issues detected: {}", issues);
            // 发送配置告警
            sendConfigurationAlert(issues);
        }
    }
}
```

## 总结

日志加密与访问控制是构建安全可靠日志管理系统的核心要素。通过实施传输加密、存储加密和字段级加密，我们可以保护日志数据在各个阶段的安全性。结合基于角色和属性的访问控制机制，以及完善的审计和监控体系，我们可以确保只有授权用户能够访问相应的日志数据，并且所有访问行为都可追溯。

在实际应用中，需要根据具体的业务需求和安全要求，选择合适的加密算法、访问控制策略和监控机制，并定期审查和更新安全配置，以应对不断变化的安全威胁。

在下一章中，我们将探讨监控的基本概念与重要性，包括监控的主要目标、度量指标分类以及健康检查与监控的结合等内容。