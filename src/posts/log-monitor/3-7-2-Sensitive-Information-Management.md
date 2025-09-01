---
title: 日志中的敏感信息管理：识别、保护与合规处理
date: 2025-08-31
categories: [Microservices, Logging, Security]
tags: [microservices, logging, sensitive-data, data-protection, pii, compliance]
published: true
---

在前一篇文章中，我们概述了日志安全与合规性的基本概念。本文将深入探讨日志中敏感信息的管理策略，包括敏感信息的识别、分类、保护以及合规处理方法，帮助您构建安全可靠的日志管理系统。

## 敏感信息识别与分类体系

### 敏感信息类型分类

在微服务架构中，日志可能包含多种类型的敏感信息，建立清晰的分类体系是有效管理的基础：

#### 个人身份信息（PII）

个人身份信息是最常见的敏感数据类型，包括：

```java
public enum PersonalIdentifiableInformation {
    FULL_NAME("Full Name", "姓名、全名"),
    ADDRESS("Address", "地址信息"),
    PHONE_NUMBER("Phone Number", "电话号码"),
    EMAIL_ADDRESS("Email Address", "邮箱地址"),
    SOCIAL_SECURITY_NUMBER("SSN", "社会保障号码"),
    PASSPORT_NUMBER("Passport Number", "护照号码"),
    DRIVER_LICENSE("Driver License", "驾照号码"),
    DATE_OF_BIRTH("Date of Birth", "出生日期"),
    NATIONAL_ID("National ID", "身份证号码"),
    BIOMETRIC_DATA("Biometric Data", "生物识别数据");
    
    private final String englishName;
    private final String chineseName;
    
    PersonalIdentifiableInformation(String englishName, String chineseName) {
        this.englishName = englishName;
        this.chineseName = chineseName;
    }
    
    // getters
}
```

#### 财务相关信息

财务信息涉及资金和交易，需要特别保护：

```java
public enum FinancialInformation {
    CREDIT_CARD_NUMBER("Credit Card Number", "信用卡号码"),
    BANK_ACCOUNT_NUMBER("Bank Account Number", "银行账号"),
    TRANSACTION_RECORD("Transaction Record", "交易记录"),
    PAYMENT_INFORMATION("Payment Information", "支付信息"),
    TAX_INFORMATION("Tax Information", "税务信息"),
    SALARY_DATA("Salary Data", "薪资数据"),
    INVESTMENT_PORTFOLIO("Investment Portfolio", "投资组合");
    
    private final String englishName;
    private final String chineseName;
    
    FinancialInformation(String englishName, String chineseName) {
        this.englishName = englishName;
        this.chineseName = chineseName;
    }
    
    // getters
}
```

#### 健康医疗信息

健康医疗信息受HIPAA等法规严格保护：

```java
public enum HealthInformation {
    MEDICAL_RECORD_NUMBER("Medical Record Number", "病历号"),
    DIAGNOSIS("Diagnosis", "诊断信息"),
    TREATMENT_HISTORY("Treatment History", "治疗历史"),
    PRESCRIPTION("Prescription", "处方信息"),
    INSURANCE_ID("Insurance ID", "保险ID"),
    LAB_RESULTS("Lab Results", "化验结果"),
    MEDICAL_IMAGES("Medical Images", "医学影像");
    
    private final String englishName;
    private final String chineseName;
    
    HealthInformation(String englishName, String chineseName) {
        this.englishName = englishName;
        this.chineseName = chineseName;
    }
    
    // getters
}
```

#### 商业机密信息

商业机密信息对企业竞争力至关重要：

```java
public enum BusinessConfidentialInformation {
    CUSTOMER_LIST("Customer List", "客户名单"),
    SUPPLIER_INFORMATION("Supplier Information", "供应商信息"),
    PRODUCT_FORMULA("Product Formula", "产品配方"),
    TECHNICAL_SPECIFICATIONS("Technical Specifications", "技术规格"),
    BUSINESS_STRATEGY("Business Strategy", "商业策略"),
    MARKET_PLAN("Market Plan", "市场计划"),
    TRADE_SECRETS("Trade Secrets", "商业秘密");
    
    private final String englishName;
    private final String chineseName;
    
    BusinessConfidentialInformation(String englishName, String chineseName) {
        this.englishName = englishName;
        this.chineseName = chineseName;
    }
    
    // getters
}
```

### 敏感信息识别技术

#### 基于规则的识别

使用预定义规则识别敏感信息：

```java
@Component
public class RuleBasedSensitiveDataDetector {
    
    private final Map<SensitiveDataType, Pattern> patterns = new HashMap<>();
    
    public RuleBasedSensitiveDataDetector() {
        // 电子邮件模式
        patterns.put(SensitiveDataType.EMAIL, 
            Pattern.compile("\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"));
        
        // 电话号码模式
        patterns.put(SensitiveDataType.PHONE, 
            Pattern.compile("\\b(?:\\+?1[-.\\s]?)?\\(?[0-9]{3}\\)?[-.\\s]?[0-9]{3}[-.\\s]?[0-9]{4}\\b"));
        
        // 社会保障号码模式
        patterns.put(SensitiveDataType.SSN, 
            Pattern.compile("\\b\\d{3}-\\d{2}-\\d{4}\\b"));
        
        // 信用卡号码模式
        patterns.put(SensitiveDataType.CREDIT_CARD, 
            Pattern.compile("\\b(?:\\d{4}[ -]?){3}\\d{4}\\b"));
        
        // IP地址模式
        patterns.put(SensitiveDataType.IP_ADDRESS, 
            Pattern.compile("\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b"));
    }
    
    public Set<SensitiveDataType> detectSensitiveData(String text) {
        Set<SensitiveDataType> detectedTypes = new HashSet<>();
        
        for (Map.Entry<SensitiveDataType, Pattern> entry : patterns.entrySet()) {
            if (entry.getValue().matcher(text).find()) {
                detectedTypes.add(entry.getKey());
            }
        }
        
        return detectedTypes;
    }
    
    public List<SensitiveDataMatch> findSensitiveDataMatches(String text) {
        List<SensitiveDataMatch> matches = new ArrayList<>();
        
        for (Map.Entry<SensitiveDataType, Pattern> entry : patterns.entrySet()) {
            Matcher matcher = entry.getValue().matcher(text);
            while (matcher.find()) {
                matches.add(new SensitiveDataMatch(
                    entry.getKey(),
                    matcher.group(),
                    matcher.start(),
                    matcher.end()
                ));
            }
        }
        
        return matches;
    }
}
```

#### 基于机器学习的识别

使用机器学习模型提高识别准确性：

```python
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

class MLSensitiveDataDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 3))
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        
    def prepare_training_data(self):
        # 准备训练数据
        data = [
            ("User john.doe@example.com logged in", "EMAIL"),
            ("Customer phone: 555-123-4567", "PHONE"),
            ("SSN: 123-45-6789", "SSN"),
            ("Credit card: 4111 1111 1111 1111", "CREDIT_CARD"),
            ("System started successfully", "NONE"),
            ("Processing order ORD-20250831-001", "NONE")
        ]
        
        df = pd.DataFrame(data, columns=['text', 'label'])
        return df['text'], df['label']
    
    def train(self):
        texts, labels = self.prepare_training_data()
        
        # 特征提取
        X = self.vectorizer.fit_transform(texts)
        
        # 训练模型
        self.classifier.fit(X, labels)
        self.is_trained = True
    
    def detect_sensitive_data(self, text):
        if not self.is_trained:
            self.train()
        
        # 特征提取
        X = self.vectorizer.transform([text])
        
        # 预测
        prediction = self.classifier.predict(X)[0]
        probability = max(self.classifier.predict_proba(X)[0])
        
        return {
            'type': prediction if prediction != 'NONE' else None,
            'confidence': probability,
            'details': self.extract_details(text, prediction)
        }
    
    def extract_details(self, text, prediction):
        patterns = {
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'PHONE': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
            'CREDIT_CARD': r'\b(?:\d{4}[ -]?){3}\d{4}\b'
        }
        
        if prediction in patterns:
            matches = re.findall(patterns[prediction], text)
            return matches
        return []
```

### 敏感信息上下文分析

识别敏感信息的上下文环境：

```java
@Component
public class ContextualSensitiveDataAnalyzer {
    
    private final Set<String> sensitiveContextKeywords = Set.of(
        "password", "passwd", "pwd", "secret", "token", "key",
        "credit", "card", "ssn", "social", "security",
        "medical", "health", "patient", "diagnosis",
        "customer", "client", "user", "account"
    );
    
    public SensitivityAnalysisResult analyzeContext(String logMessage) {
        SensitivityAnalysisResult result = new SensitivityAnalysisResult();
        
        // 检查上下文关键词
        String lowerMessage = logMessage.toLowerCase();
        for (String keyword : sensitiveContextKeywords) {
            if (lowerMessage.contains(keyword)) {
                result.addContextKeyword(keyword);
                result.increaseSensitivityScore(10);
            }
        }
        
        // 检查数据模式
        RuleBasedSensitiveDataDetector detector = new RuleBasedSensitiveDataDetector();
        Set<SensitiveDataType> detectedTypes = detector.detectSensitiveData(logMessage);
        result.setDetectedTypes(detectedTypes);
        result.increaseSensitivityScore(detectedTypes.size() * 20);
        
        // 检查日志级别
        if (logMessage.contains("ERROR") || logMessage.contains("FATAL")) {
            result.increaseSensitivityScore(15);
        }
        
        // 确定敏感级别
        if (result.getSensitivityScore() >= 50) {
            result.setSensitivityLevel(SensitivityLevel.HIGH);
        } else if (result.getSensitivityScore() >= 25) {
            result.setSensitivityLevel(SensitivityLevel.MEDIUM);
        } else {
            result.setSensitivityLevel(SensitivityLevel.LOW);
        }
        
        return result;
    }
}
```

## 敏感信息保护策略

### 数据脱敏技术

#### 静态脱敏

对已知的敏感信息进行预处理脱敏：

```java
@Component
public class StaticDataMasker {
    
    public String maskEmail(String email) {
        if (email == null || !email.contains("@")) {
            return email;
        }
        
        String[] parts = email.split("@");
        String username = parts[0];
        String domain = parts[1];
        
        if (username.length() <= 2) {
            return "***@" + domain;
        }
        
        return username.charAt(0) + "***" + 
               username.charAt(username.length() - 1) + "@" + domain;
    }
    
    public String maskPhoneNumber(String phone) {
        if (phone == null || phone.length() < 10) {
            return phone;
        }
        
        // 保留最后4位数字
        return "***-***-" + phone.replaceAll("\\D", "").substring(Math.max(0, phone.replaceAll("\\D", "").length() - 4));
    }
    
    public String maskCreditCard(String cardNumber) {
        if (cardNumber == null || cardNumber.length() < 4) {
            return cardNumber;
        }
        
        // 保留最后4位数字
        String cleanedNumber = cardNumber.replaceAll("[^0-9]", "");
        if (cleanedNumber.length() >= 4) {
            return "****-****-****-" + cleanedNumber.substring(cleanedNumber.length() - 4);
        }
        return "****-****-****-****";
    }
    
    public String maskSSN(String ssn) {
        if (ssn == null || ssn.length() < 9) {
            return ssn;
        }
        
        // 保留最后4位数字
        String cleanedSSN = ssn.replaceAll("[^0-9]", "");
        if (cleanedSSN.length() >= 4) {
            return "***-**-" + cleanedSSN.substring(cleanedSSN.length() - 4);
        }
        return "***-**-****";
    }
}
```

#### 动态脱敏

在日志记录时实时进行脱敏处理：

```java
@Component
public class DynamicDataMasker {
    
    private final RuleBasedSensitiveDataDetector detector;
    private final StaticDataMasker staticMasker;
    
    public DynamicDataMasker(RuleBasedSensitiveDataDetector detector, StaticDataMasker staticMasker) {
        this.detector = detector;
        this.staticMasker = staticMasker;
    }
    
    public String maskSensitiveData(String logMessage) {
        if (logMessage == null) {
            return null;
        }
        
        // 查找所有敏感数据匹配
        List<SensitiveDataMatch> matches = detector.findSensitiveDataMatches(logMessage);
        
        // 按位置倒序排列，避免替换时位置偏移
        matches.sort((a, b) -> Integer.compare(b.getStartIndex(), a.getStartIndex()));
        
        StringBuilder maskedMessage = new StringBuilder(logMessage);
        
        for (SensitiveDataMatch match : matches) {
            String maskedValue = maskValue(match.getType(), match.getMatchedText());
            maskedMessage.replace(match.getStartIndex(), match.getEndIndex(), maskedValue);
        }
        
        return maskedMessage.toString();
    }
    
    private String maskValue(SensitiveDataType type, String value) {
        switch (type) {
            case EMAIL:
                return staticMasker.maskEmail(value);
            case PHONE:
                return staticMasker.maskPhoneNumber(value);
            case SSN:
                return staticMasker.maskSSN(value);
            case CREDIT_CARD:
                return staticMasker.maskCreditCard(value);
            case IP_ADDRESS:
                return "***.***.***.***";
            default:
                return "***";
        }
    }
}
```

### 加密保护

#### 字段级加密

对特定敏感字段进行加密存储：

```java
@Entity
@Table(name = "logs")
public class EncryptedLogEntry {
    @Id
    private String id;
    
    private String timestamp;
    
    private String level;
    
    private String service;
    
    @Column(length = 10000)
    private String message;
    
    @Convert(converter = EncryptedStringConverter.class)
    @Column(name = "user_id")
    private String userId;
    
    @Convert(converter = EncryptedStringConverter.class)
    @Column(name = "ip_address")
    private String ipAddress;
    
    @Convert(converter = EncryptedStringConverter.class)
    @Column(name = "sensitive_data")
    private String sensitiveData;
    
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

#### 传输加密

确保日志数据在传输过程中的安全性：

```java
@Configuration
public class SecureLogTransmissionConfig {
    
    @Bean
    public SSLContext sslContext() throws Exception {
        // 配置SSL上下文
        KeyStore keyStore = KeyStore.getInstance("JKS");
        try (InputStream keyStoreStream = 
             getClass().getResourceAsStream("/keystore.jks")) {
            keyStore.load(keyStoreStream, "password".toCharArray());
        }
        
        KeyManagerFactory keyManagerFactory = 
            KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
        keyManagerFactory.init(keyStore, "password".toCharArray());
        
        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(keyManagerFactory.getKeyManagers(), null, null);
        
        return sslContext;
    }
    
    @Bean
    public HttpClient secureHttpClient(SSLContext sslContext) {
        return HttpClient.newBuilder()
            .sslContext(sslContext)
            .connectTimeout(Duration.ofSeconds(10))
            .build();
    }
}
```

## 合规处理机制

### GDPR合规处理

#### 数据主体权利实现

```java
@Service
public class GDPRComplianceService {
    
    @Autowired
    private LogRepository logRepository;
    
    @Autowired
    private AuditService auditService;
    
    public void handleDataSubjectRequest(String userId, DataSubjectRequest request) {
        switch (request.getRequestType()) {
            case RIGHT_TO_ACCESS:
                provideDataAccess(userId, request);
                break;
            case RIGHT_TO_RECTIFICATION:
                correctUserData(userId, request);
                break;
            case RIGHT_TO_ERASURE:
                deleteUserData(userId, request);
                break;
            case RIGHT_TO_RESTRICT_PROCESSING:
                restrictDataProcessing(userId, request);
                break;
            case RIGHT_TO_DATA_PORTABILITY:
                provideDataPortability(userId, request);
                break;
            case RIGHT_TO_OBJECT:
                handleObjection(userId, request);
                break;
        }
    }
    
    public void deleteUserData(String userId, DataSubjectRequest request) {
        // 记录删除操作
        auditService.logAuditEvent("GDPR_DATA_ERASURE", 
            "Deleting user data for user: " + userId, 
            request.getRequestId());
        
        // 删除用户的所有日志记录
        logRepository.deleteByUserId(userId);
        
        // 通知相关系统
        notificationService.notifyDataErasure(userId);
        
        // 确认删除完成
        request.setStatus(RequestStatus.COMPLETED);
        request.setCompletionTime(Instant.now());
    }
    
    public DataPortabilityResponse exportUserData(String userId) {
        // 导出用户数据
        List<LogEntry> userLogs = logRepository.findByUserId(userId);
        
        // 创建数据导出包
        DataPortabilityResponse response = new DataPortabilityResponse();
        response.setUserId(userId);
        response.setLogs(userLogs);
        response.setExportTime(Instant.now());
        response.setFormat("JSON");
        
        // 加密导出数据
        String encryptedData = encryptionService.encrypt(
            objectMapper.writeValueAsString(response));
        
        response.setEncryptedData(encryptedData);
        
        return response;
    }
}
```

#### 数据保护影响评估（DPIA）

```java
@Component
public class DPIAAssessment {
    
    public DPIAResult conductDPIA(LoggingSystemConfig config) {
        DPIAResult result = new DPIAResult();
        
        // 评估数据处理性质
        result.setProcessingNature(assessProcessingNature(config));
        
        // 评估数据处理规模
        result.setProcessingScale(assessProcessingScale());
        
        // 评估数据处理风险
        result.setRiskLevel(assessRiskLevel(config));
        
        // 评估合规措施
        result.setComplianceMeasures(assessComplianceMeasures(config));
        
        // 评估技术保障
        result.setTechnicalSafeguards(assessTechnicalSafeguards(config));
        
        return result;
    }
    
    private RiskLevel assessRiskLevel(LoggingSystemConfig config) {
        int riskScore = 0;
        
        // 评估敏感数据处理
        if (config.isProcessingSensitiveData()) {
            riskScore += 40;
        }
        
        // 评估数据量
        long dailyVolume = config.getEstimatedDailyLogVolume();
        if (dailyVolume > 1000000) {
            riskScore += 30;
        } else if (dailyVolume > 100000) {
            riskScore += 20;
        }
        
        // 评估访问控制
        if (!config.hasProperAccessControls()) {
            riskScore += 25;
        }
        
        // 评估加密措施
        if (!config.hasEncryption()) {
            riskScore += 25;
        }
        
        // 评估数据保留期
        if (config.getDataRetentionPeriod() > 365) {
            riskScore += 15;
        }
        
        if (riskScore >= 90) {
            return RiskLevel.HIGH;
        } else if (riskScore >= 60) {
            return RiskLevel.MEDIUM;
        } else {
            return RiskLevel.LOW;
        }
    }
}
```

### HIPAA合规处理

#### 电子受保护健康信息（ePHI）保护

```java
@Service
public class HIPAAComplianceService {
    
    private static final Set<String> PHI_INDICATORS = Set.of(
        "patient", "medical", "diagnosis", "treatment", 
        "prescription", "insurance", "health", "clinical"
    );
    
    public void processHealthcareLog(LogEntry logEntry) {
        // 检查是否包含PHI
        if (containsPHI(logEntry)) {
            // 应用HIPAA合规措施
            applyHIPAACompliance(logEntry);
        }
        
        // 存储日志
        logRepository.save(logEntry);
    }
    
    private boolean containsPHI(LogEntry logEntry) {
        String message = logEntry.getMessage().toLowerCase();
        return PHI_INDICATORS.stream().anyMatch(message::contains);
    }
    
    private void applyHIPAACompliance(LogEntry logEntry) {
        // 加密PHI数据
        logEntry.setMessage(encryptPHI(logEntry.getMessage()));
        
        // 限制访问权限
        logEntry.setAccessLevel("HIPAA_RESTRICTED");
        
        // 添加审计标记
        logEntry.addTag("HIPAA_COMPLIANT");
        
        // 设置数据保留策略
        logEntry.setDataRetentionPeriod(365); // HIPAA要求至少保留6年
        
        // 启用详细审计
        logEntry.setAuditTrailEnabled(true);
    }
    
    private String encryptPHI(String message) {
        // 使用HIPAA合规的加密算法
        return encryptionService.encrypt(message, EncryptionAlgorithm.AES_256_GCM);
    }
}
```

## 最佳实践

### 1. 敏感信息分类管理

建立清晰的敏感信息分类和处理策略：

```java
@Component
public class SensitiveDataClassificationManager {
    
    private final Map<SensitivityLevel, SensitiveDataPolicy> policies = new HashMap<>();
    
    public SensitiveDataClassificationManager() {
        // 高敏感度数据策略
        policies.put(SensitivityLevel.HIGH, new SensitiveDataPolicy()
            .setEncryptionRequired(true)
            .setAccessControlLevel(AccessControlLevel.ADMIN_ONLY)
            .setRetentionPeriod(3650) // 10年
            .setMaskingRequired(true)
            .setAuditTrailRequired(true));
        
        // 中敏感度数据策略
        policies.put(SensitivityLevel.MEDIUM, new SensitiveDataPolicy()
            .setEncryptionRequired(true)
            .setAccessControlLevel(AccessControlLevel.AUTHORIZED_ONLY)
            .setRetentionPeriod(1825) // 5年
            .setMaskingRequired(true)
            .setAuditTrailRequired(true));
        
        // 低敏感度数据策略
        policies.put(SensitivityLevel.LOW, new SensitiveDataPolicy()
            .setEncryptionRequired(false)
            .setAccessControlLevel(AccessControlLevel.OPERATIONS)
            .setRetentionPeriod(365) // 1年
            .setMaskingRequired(false)
            .setAuditTrailRequired(false));
    }
    
    public void applyClassificationPolicy(LogEntry logEntry) {
        SensitivityLevel level = classifyLogEntry(logEntry);
        SensitiveDataPolicy policy = policies.get(level);
        
        if (policy.isEncryptionRequired()) {
            logEntry.setEncrypted(true);
        }
        
        if (policy.isMaskingRequired()) {
            logEntry.setMessage(maskSensitiveData(logEntry.getMessage()));
        }
        
        logEntry.setAccessLevel(policy.getAccessControlLevel().toString());
        logEntry.setDataRetentionPeriod(policy.getRetentionPeriod());
        logEntry.setAuditTrailEnabled(policy.isAuditTrailRequired());
    }
}
```

### 2. 自动化检测与处理

实现敏感信息的自动化检测和处理：

```java
@Component
public class AutomatedSensitiveDataHandler {
    
    private final RuleBasedSensitiveDataDetector detector;
    private final DynamicDataMasker masker;
    private final SensitiveDataClassificationManager classifier;
    
    @Scheduled(fixedRate = 60000) // 每分钟检查一次
    public void processPendingLogs() {
        // 获取待处理的日志
        List<LogEntry> pendingLogs = logRepository.findPendingLogs();
        
        for (LogEntry logEntry : pendingLogs) {
            try {
                // 检测敏感信息
                Set<SensitiveDataType> sensitiveTypes = detector.detectSensitiveData(logEntry.getMessage());
                
                if (!sensitiveTypes.isEmpty()) {
                    // 分类处理
                    classifier.applyClassificationPolicy(logEntry);
                    
                    // 脱敏处理
                    logEntry.setMessage(masker.maskSensitiveData(logEntry.getMessage()));
                    
                    // 记录处理日志
                    auditService.logSensitiveDataHandling(logEntry.getId(), sensitiveTypes);
                }
                
                // 标记为已处理
                logEntry.setStatus(LogStatus.PROCESSED);
                logRepository.save(logEntry);
                
            } catch (Exception e) {
                log.error("Failed to process log entry: {}", logEntry.getId(), e);
                logEntry.setStatus(LogStatus.FAILED);
                logEntry.setErrorMessage(e.getMessage());
                logRepository.save(logEntry);
            }
        }
    }
}
```

### 3. 持续监控与改进

建立持续监控和改进机制：

```java
@Component
public class SensitiveDataMonitoringService {
    
    private final MeterRegistry meterRegistry;
    private final Counter sensitiveDataDetectedCounter;
    private final Counter sensitiveDataMaskedCounter;
    private final Timer sensitiveDataProcessingTimer;
    
    public SensitiveDataMonitoringService(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.sensitiveDataDetectedCounter = Counter.builder("sensitive.data.detected")
            .description("Number of sensitive data items detected")
            .register(meterRegistry);
        this.sensitiveDataMaskedCounter = Counter.builder("sensitive.data.masked")
            .description("Number of sensitive data items masked")
            .register(meterRegistry);
        this.sensitiveDataProcessingTimer = Timer.builder("sensitive.data.processing.time")
            .description("Time taken to process sensitive data")
            .register(meterRegistry);
    }
    
    @EventListener
    public void handleSensitiveDataEvent(SensitiveDataEvent event) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            // 处理敏感数据事件
            processSensitiveDataEvent(event);
            
            // 更新指标
            sensitiveDataDetectedCounter.increment(event.getDetectedCount());
            sensitiveDataMaskedCounter.increment(event.getMaskedCount());
            
        } finally {
            sample.stop(sensitiveDataProcessingTimer);
        }
    }
    
    public void generateComplianceReport() {
        // 生成合规性报告
        ComplianceReport report = new ComplianceReport();
        report.setReportDate(Instant.now());
        report.setTotalLogsProcessed(logRepository.count());
        report.setSensitiveDataDetected((long) sensitiveDataDetectedCounter.count());
        report.setSensitiveDataMasked((long) sensitiveDataMaskedCounter.count());
        report.setAverageProcessingTime(sensitiveDataProcessingTimer.mean(TimeUnit.MILLISECONDS));
        
        // 发送报告
        reportService.sendComplianceReport(report);
    }
}
```

## 总结

敏感信息管理是日志安全与合规性的核心环节。通过建立完善的识别、保护和合规处理机制，我们可以有效降低数据泄露风险，满足各种法规要求。关键是要结合基于规则和机器学习的识别技术，实施多层次的保护策略，并建立持续监控和改进机制。

在下一节中，我们将探讨日志加密与访问控制的具体实现方法，包括传输加密、存储加密以及细粒度的访问控制策略。