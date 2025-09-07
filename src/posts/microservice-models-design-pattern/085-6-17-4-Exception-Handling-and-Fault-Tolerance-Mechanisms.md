---
title: 异常处理与容错机制：构建高可用的微服务系统
date: 2025-08-31
categories: [ModelsDesignPattern]
tags: [microservice-models-design-pattern]
published: true
---

# 异常处理与容错机制

微服务系统的分布式特性使得异常处理变得更加复杂。网络故障、服务不可用、超时等问题都需要有完善的处理机制。设计合理的异常处理和容错机制是确保系统稳定性的关键。本章将深入探讨微服务系统中的异常处理策略、容错模式和高可用性设计。

## 异常处理策略

### 分层异常处理

在微服务架构中，异常处理应该分层进行，每一层都有明确的职责。

```java
// 领域层异常 - 业务规则违反
public class BusinessRuleViolationException extends RuntimeException {
    private final String errorCode;
    private final Object[] parameters;
    
    public BusinessRuleViolationException(String message, String errorCode, Object... parameters) {
        super(message);
        this.errorCode = errorCode;
        this.parameters = parameters;
    }
    
    // 预定义的业务异常
    public static class InsufficientInventoryException extends BusinessRuleViolationException {
        public InsufficientInventoryException(String productId, int requested, int available) {
            super("Insufficient inventory for product " + productId + 
                  ". Requested: " + requested + ", Available: " + available,
                  "INSUFFICIENT_INVENTORY", productId, requested, available);
        }
    }
    
    public static class OrderAlreadyExistsException extends BusinessRuleViolationException {
        public OrderAlreadyExistsException(String orderId) {
            super("Order already exists: " + orderId,
                  "ORDER_ALREADY_EXISTS", orderId);
        }
    }
}

// 应用层异常 - 服务调用失败
public class ServiceException extends RuntimeException {
    private final String service;
    private final int httpStatus;
    
    public ServiceException(String message, String service, int httpStatus) {
        super(message);
        this.service = service;
        this.httpStatus = httpStatus;
    }
    
    public static class ServiceUnavailableException extends ServiceException {
        public ServiceUnavailableException(String service) {
            super("Service unavailable: " + service, service, 503);
        }
    }
    
    public static class ServiceTimeoutException extends ServiceException {
        public ServiceTimeoutException(String service, long timeoutMs) {
            super("Service timeout: " + service + " after " + timeoutMs + "ms", service, 408);
        }
    }
}

// 基础设施层异常 - 技术故障
public class InfrastructureException extends RuntimeException {
    private final String component;
    
    public InfrastructureException(String message, String component, Throwable cause) {
        super(message, cause);
        this.component = component;
    }
    
    public static class DatabaseConnectionException extends InfrastructureException {
        public DatabaseConnectionException(String message, Throwable cause) {
            super("Database connection failed: " + message, "DATABASE", cause);
        }
    }
    
    public static class MessagingException extends InfrastructureException {
        public MessagingException(String message, Throwable cause) {
            super("Messaging system error: " + message, "MESSAGING", cause);
        }
    }
}
```

### 全局异常处理

使用全局异常处理器统一处理各种异常。

```java
// REST控制器全局异常处理
@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);
    
    // 处理业务规则异常
    @ExceptionHandler(BusinessRuleViolationException.class)
    public ResponseEntity<ErrorResponse> handleBusinessRuleViolation(
            BusinessRuleViolationException ex) {
        logger.warn("Business rule violation: {}", ex.getMessage());
        
        ErrorResponse error = ErrorResponse.builder()
            .timestamp(Instant.now())
            .status(HttpStatus.BAD_REQUEST.value())
            .error("Bad Request")
            .message(ex.getMessage())
            .errorCode(ex.getErrorCode())
            .parameters(ex.getParameters())
            .build();
            
        return ResponseEntity.badRequest().body(error);
    }
    
    // 处理服务不可用异常
    @ExceptionHandler(ServiceUnavailableException.class)
    public ResponseEntity<ErrorResponse> handleServiceUnavailable(
            ServiceUnavailableException ex) {
        logger.error("Service unavailable: {}", ex.getService());
        
        ErrorResponse error = ErrorResponse.builder()
            .timestamp(Instant.now())
            .status(HttpStatus.SERVICE_UNAVAILABLE.value())
            .error("Service Unavailable")
            .message("Service temporarily unavailable: " + ex.getService())
            .retryAfter(30) // 建议30秒后重试
            .build();
            
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(error);
    }
    
    // 处理服务超时异常
    @ExceptionHandler(ServiceTimeoutException.class)
    public ResponseEntity<ErrorResponse> handleServiceTimeout(
            ServiceTimeoutException ex) {
        logger.warn("Service timeout: {}", ex.getService());
        
        ErrorResponse error = ErrorResponse.builder()
            .timestamp(Instant.now())
            .status(HttpStatus.REQUEST_TIMEOUT.value())
            .error("Request Timeout")
            .message("Service timeout: " + ex.getService())
            .build();
            
        return ResponseEntity.status(HttpStatus.REQUEST_TIMEOUT).body(error);
    }
    
    // 处理基础设施异常
    @ExceptionHandler(InfrastructureException.class)
    public ResponseEntity<ErrorResponse> handleInfrastructureException(
            InfrastructureException ex) {
        logger.error("Infrastructure error in component {}: {}", 
                    ex.getComponent(), ex.getMessage(), ex);
        
        ErrorResponse error = ErrorResponse.builder()
            .timestamp(Instant.now())
            .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
            .error("Internal Server Error")
            .message("Internal system error")
            .build();
            
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
    
    // 处理未预期的异常
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleUnexpectedException(Exception ex) {
        logger.error("Unexpected error occurred", ex);
        
        ErrorResponse error = ErrorResponse.builder()
            .timestamp(Instant.now())
            .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
            .error("Internal Server Error")
            .message("An unexpected error occurred")
            .build();
            
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}

// 统一错误响应格式
@Data
@Builder
public class ErrorResponse {
    private Instant timestamp;
    private int status;
    private String error;
    private String message;
    private String errorCode;
    private Object[] parameters;
    private Integer retryAfter;
    private String path;
}
```

## 容错设计模式

### 熔断器模式

熔断器模式可以防止故障级联，提高系统的稳定性。

```java
// 使用Resilience4j实现熔断器
@Service
public class OrderServiceClient {
    private final CircuitBreaker circuitBreaker;
    private final Retry retry;
    private final RestTemplate restTemplate;
    
    public OrderServiceClient() {
        // 配置熔断器
        this.circuitBreaker = CircuitBreaker.ofDefaults("orderService");
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50) // 失败率阈值50%
            .waitDurationInOpenState(Duration.ofSeconds(30)) // 熔断器打开后等待30秒
            .slidingWindowType(CircuitBreakerConfig.SlidingWindowType.TIME_BASED)
            .slidingWindowSize(10) // 滑动窗口大小
            .minimumNumberOfCalls(5) // 最小调用次数
            .build();
        this.circuitBreaker = CircuitBreaker.of("orderService", config);
        
        // 配置重试
        this.retry = Retry.ofDefaults("orderService");
        
        // 注册事件监听器
        circuitBreaker.getEventPublisher()
            .onStateTransition(event -> logCircuitBreakerStateChange(event));
    }
    
    @CircuitBreaker(name = "orderService", fallbackMethod = "getDefaultOrders")
    @Retry(name = "orderService")
    public List<Order> getOrders(String userId) {
        String url = "http://order-service/orders?userId=" + userId;
        return restTemplate.exchange(url, HttpMethod.GET, null,
            new ParameterizedTypeReference<List<Order>>() {}).getBody();
    }
    
    // 熔断器打开时的降级方法
    public List<Order> getDefaultOrders(String userId, Exception ex) {
        logger.warn("Circuit breaker is open, returning default orders for user: {}", userId);
        
        // 记录熔断事件
        circuitBreakerMetrics.recordCircuitBreakerTriggered();
        
        // 返回缓存数据或默认值
        return orderCache.getOrDefault(userId, Collections.emptyList());
    }
    
    private void logCircuitBreakerStateChange(
            CircuitBreakerOnStateTransitionEvent event) {
        logger.info("Circuit breaker state changed from {} to {} for {}",
                   event.getStateTransition().getFromState(),
                   event.getStateTransition().getToState(),
                   event.getCircuitBreakerName());
        
        // 发送告警（如果熔断器打开）
        if (event.getStateTransition().getToState() == CircuitBreaker.State.OPEN) {
            alertService.sendAlert("Circuit Breaker Opened",
                                 "Service: " + event.getCircuitBreakerName());
        }
    }
}
```

### 限流模式

限流模式可以防止系统过载，保护系统稳定性。

```java
// 使用Resilience4j实现限流
@RestController
public class PaymentController {
    private final RateLimiter rateLimiter;
    
    public PaymentController() {
        // 配置限流器
        RateLimiterConfig config = RateLimiterConfig.custom()
            .limitRefreshPeriod(Duration.ofSeconds(1)) // 限流周期
            .limitForPeriod(100) // 每周期允许的请求数
            .timeoutDuration(Duration.ofMillis(500)) // 等待超时时间
            .build();
        this.rateLimiter = RateLimiter.of("paymentService", config);
        
        // 注册事件监听器
        rateLimiter.getEventPublisher()
            .onFailure(event -> logRateLimitExceeded(event));
    }
    
    @RateLimiter(name = "paymentService")
    @PostMapping("/payments")
    public ResponseEntity<PaymentResult> processPayment(@RequestBody PaymentRequest request) {
        try {
            PaymentResult result = paymentService.process(request);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(PaymentResult.failure(e.getMessage()));
        }
    }
    
    private void logRateLimitExceeded(RateLimiterOnFailureEvent event) {
        logger.warn("Rate limit exceeded for {}", event.getRateLimiterName());
        
        // 记录限流指标
        rateLimitMetrics.recordRateLimitExceeded();
        
        // 发送告警
        alertService.sendAlert("Rate Limit Exceeded",
                             "Service: " + event.getRateLimiterName());
    }
}

// 基于令牌桶算法的自定义限流器
@Component
public class TokenBucketRateLimiter {
    private final long capacity; // 桶容量
    private final long refillTokens; // 每次补充的令牌数
    private final Duration refillInterval; // 补充间隔
    private final AtomicLong tokens; // 当前令牌数
    private final AtomicLong lastRefillTime; // 上次补充时间
    
    public TokenBucketRateLimiter(long capacity, long refillTokens, Duration refillInterval) {
        this.capacity = capacity;
        this.refillTokens = refillTokens;
        this.refillInterval = refillInterval;
        this.tokens = new AtomicLong(capacity);
        this.lastRefillTime = new AtomicLong(System.nanoTime());
    }
    
    public boolean tryAcquire() {
        return tryAcquire(1);
    }
    
    public boolean tryAcquire(int permits) {
        refillTokens(); // 先补充令牌
        
        long currentTokens = tokens.get();
        if (currentTokens >= permits) {
            return tokens.compareAndSet(currentTokens, currentTokens - permits);
        }
        return false;
    }
    
    private void refillTokens() {
        long now = System.nanoTime();
        long lastRefill = lastRefillTime.get();
        long timePassed = now - lastRefill;
        
        if (timePassed >= refillInterval.toNanos()) {
            long newTokens = Math.min(capacity, tokens.get() + refillTokens);
            tokens.set(newTokens);
            lastRefillTime.set(now);
        }
    }
}
```

### 超时模式

超时模式可以防止请求无限等待，提高系统响应性。

```java
// HTTP客户端超时配置
@Configuration
public class HttpClientConfig {
    @Bean
    public RestTemplate restTemplate() {
        HttpComponentsClientHttpRequestFactory factory = 
            new HttpComponentsClientHttpRequestFactory();
        
        // 连接超时
        factory.setConnectTimeout(5000); // 5秒
        
        // 读取超时
        factory.setReadTimeout(10000); // 10秒
        
        // 连接池超时
        factory.setConnectionRequestTimeout(2000); // 2秒
        
        return new RestTemplate(factory);
    }
}

// 使用WebClient的响应式超时配置
@Service
public class ReactiveOrderServiceClient {
    private final WebClient webClient;
    
    public ReactiveOrderServiceClient() {
        this.webClient = WebClient.builder()
            .baseUrl("http://order-service")
            .clientConnector(new ReactorClientHttpConnector(
                HttpClient.create()
                    .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 5000)
                    .responseTimeout(Duration.ofSeconds(10))
                    .doOnConnected(conn -> 
                        conn.addHandlerLast(new ReadTimeoutHandler(10, TimeUnit.SECONDS))
                            .addHandlerLast(new WriteTimeoutHandler(10, TimeUnit.SECONDS))
                    )
            ))
            .build();
    }
    
    public Mono<Order> getOrder(String orderId) {
        return webClient.get()
            .uri("/orders/{orderId}", orderId)
            .retrieve()
            .bodyToMono(Order.class)
            .timeout(Duration.ofSeconds(15)) // 总体超时
            .onErrorResume(TimeoutException.class, 
                ex -> {
                    logger.warn("Order service timeout for order: {}", orderId);
                    return Mono.error(new ServiceTimeoutException("order-service", 15000));
                });
    }
}
```

## 重试机制

### 指数退避重试

```java
// 指数退避重试策略
@Component
public class ExponentialBackoffRetryStrategy {
    private final int maxAttempts;
    private final long initialDelayMs;
    private final double multiplier;
    private final long maxDelayMs;
    
    public ExponentialBackoffRetryStrategy() {
        this.maxAttempts = 3;
        this.initialDelayMs = 1000; // 1秒
        this.multiplier = 2.0;
        this.maxDelayMs = 30000; // 30秒
    }
    
    public <T> T executeWithRetry(Supplier<T> operation, 
                                 Predicate<Exception> retryableException) {
        Exception lastException = null;
        
        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                return operation.get();
            } catch (Exception e) {
                lastException = e;
                
                // 检查是否应该重试
                if (!retryableException.test(e) || attempt == maxAttempts) {
                    throw new RetryExhaustedException("Operation failed after " + 
                                                     maxAttempts + " attempts", e);
                }
                
                // 计算延迟时间
                long delayMs = Math.min(
                    (long) (initialDelayMs * Math.pow(multiplier, attempt - 1)),
                    maxDelayMs
                );
                
                logger.warn("Attempt {} failed, retrying in {}ms: {}", 
                           attempt, delayMs, e.getMessage());
                
                // 等待后重试
                try {
                    Thread.sleep(delayMs);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("Retry interrupted", ie);
                }
            }
        }
        
        throw new RetryExhaustedException("Operation failed after " + 
                                         maxAttempts + " attempts", lastException);
    }
}

// 使用示例
@Service
public class ReliablePaymentService {
    @Autowired
    private ExponentialBackoffRetryStrategy retryStrategy;
    
    public Payment processPayment(PaymentRequest request) {
        return retryStrategy.executeWithRetry(
            () -> paymentGateway.process(request),
            this::isRetryableException
        );
    }
    
    private boolean isRetryableException(Exception e) {
        return e instanceof TimeoutException || 
               e instanceof ServiceUnavailableException ||
               e instanceof NetworkException;
    }
}
```

### 幂等性保证

```java
// 幂等性处理
@Service
public class IdempotentPaymentService {
    @Autowired
    private PaymentRepository paymentRepository;
    
    @Autowired
    private IdempotencyKeyRepository idempotencyKeyRepository;
    
    public Payment processPayment(PaymentRequest request) {
        // 检查幂等性键
        String idempotencyKey = request.getIdempotencyKey();
        if (idempotencyKey == null || idempotencyKey.isEmpty()) {
            throw new IllegalArgumentException("Idempotency key is required");
        }
        
        // 检查是否已处理过
        IdempotencyRecord record = idempotencyKeyRepository
            .findByIdempotencyKey(idempotencyKey);
            
        if (record != null) {
            // 已处理过，返回之前的结果
            logger.info("Payment already processed with idempotency key: {}", idempotencyKey);
            return paymentRepository.findById(record.getPaymentId())
                .orElseThrow(() -> new PaymentNotFoundException(record.getPaymentId()));
        }
        
        try {
            // 处理支付
            Payment payment = paymentGateway.process(request);
            
            // 保存幂等性记录
            IdempotencyRecord newRecord = new IdempotencyRecord();
            newRecord.setIdempotencyKey(idempotencyKey);
            newRecord.setPaymentId(payment.getId());
            newRecord.setProcessedAt(Instant.now());
            newRecord.setRequestHash(calculateRequestHash(request));
            idempotencyKeyRepository.save(newRecord);
            
            return payment;
        } catch (Exception e) {
            // 记录失败的幂等性记录
            IdempotencyRecord failedRecord = new IdempotencyRecord();
            failedRecord.setIdempotencyKey(idempotencyKey);
            failedRecord.setProcessedAt(Instant.now());
            failedRecord.setRequestHash(calculateRequestHash(request));
            failedRecord.setFailed(true);
            failedRecord.setErrorMessage(e.getMessage());
            idempotencyKeyRepository.save(failedRecord);
            
            throw e;
        }
    }
    
    private String calculateRequestHash(PaymentRequest request) {
        try {
            String json = objectMapper.writeValueAsString(request);
            return DigestUtils.sha256Hex(json);
        } catch (Exception e) {
            throw new RuntimeException("Failed to calculate request hash", e);
        }
    }
}
```

## 监控与告警

### 健康检查

```java
// 综合健康检查
@Component
public class ComprehensiveHealthIndicator implements HealthIndicator {
    @Autowired
    private DatabaseHealthIndicator databaseHealth;
    
    @Autowired
    private CacheHealthIndicator cacheHealth;
    
    @Autowired
    private ExternalServiceHealthIndicator externalServiceHealth;
    
    @Override
    public Health health() {
        Map<String, Health> healths = new HashMap<>();
        
        // 检查数据库
        Health dbHealth = databaseHealth.health();
        healths.put("database", dbHealth);
        
        // 检查缓存
        Health cacheHealth = cacheHealth.health();
        healths.put("cache", cacheHealth);
        
        // 检查外部服务
        Health externalHealth = externalServiceHealth.health();
        healths.put("external-services", externalHealth);
        
        // 检查业务指标
        Health businessHealth = checkBusinessMetrics();
        healths.put("business-metrics", businessHealth);
        
        // 综合判断
        boolean allUp = healths.values().stream()
            .allMatch(health -> health.getStatus() == Status.UP);
            
        if (allUp) {
            return Health.up()
                .withDetails(healths)
                .build();
        } else {
            return Health.down()
                .withDetails(healths)
                .build();
        }
    }
    
    private Health checkBusinessMetrics() {
        try {
            // 检查关键业务指标
            long pendingOrders = orderService.getPendingOrderCount();
            long errorRate = metricsService.getErrorRate();
            
            if (pendingOrders > 10000) {
                return Health.down()
                    .withDetail("pendingOrders", pendingOrders)
                    .withDetail("message", "Too many pending orders")
                    .build();
            }
            
            if (errorRate > 0.05) { // 错误率超过5%
                return Health.down()
                    .withDetail("errorRate", errorRate)
                    .withDetail("message", "High error rate")
                    .build();
            }
            
            return Health.up()
                .withDetail("pendingOrders", pendingOrders)
                .withDetail("errorRate", errorRate)
                .build();
        } catch (Exception e) {
            return Health.down()
                .withDetail("message", "Failed to check business metrics")
                .withException(e)
                .build();
        }
    }
}
```

### 故障指标监控

```java
// 故障指标收集
@Component
public class FaultMetricsCollector {
    private final MeterRegistry meterRegistry;
    private final Counter serviceCallFailures;
    private final Counter circuitBreakerTriggers;
    private final Counter rateLimitExceeded;
    private final Timer serviceCallLatency;
    
    public FaultMetricsCollector(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        this.serviceCallFailures = Counter.builder("service.call.failures")
            .description("Number of service call failures")
            .register(meterRegistry);
            
        this.circuitBreakerTriggers = Counter.builder("circuit.breaker.triggers")
            .description("Number of circuit breaker triggers")
            .register(meterRegistry);
            
        this.rateLimitExceeded = Counter.builder("rate.limit.exceeded")
            .description("Number of rate limit exceeded events")
            .register(meterRegistry);
            
        this.serviceCallLatency = Timer.builder("service.call.latency")
            .description("Service call latency")
            .register(meterRegistry);
    }
    
    public void recordServiceCallFailure(String service, String errorType) {
        serviceCallFailures.increment(
            Tags.of(
                Tag.of("service", service),
                Tag.of("error_type", errorType)
            )
        );
    }
    
    public void recordCircuitBreakerTriggered() {
        circuitBreakerTriggers.increment();
    }
    
    public void recordRateLimitExceeded() {
        rateLimitExceeded.increment();
    }
    
    public Timer.Sample startServiceCallTimer(String service) {
        return Timer.start(meterRegistry);
    }
    
    public void stopServiceCallTimer(Timer.Sample sample, String service, boolean success) {
        sample.stop(Timer.builder("service.call.latency")
            .tag("service", service)
            .tag("success", String.valueOf(success))
            .register(meterRegistry));
    }
}
```

## 故障恢复机制

### 自动故障转移

```java
// 多实例故障转移
@Service
public class FailoverServiceClient {
    private final List<ServiceInstance> serviceInstances;
    private final AtomicInteger currentInstanceIndex;
    
    public FailoverServiceClient(List<ServiceInstance> serviceInstances) {
        this.serviceInstances = new ArrayList<>(serviceInstances);
        this.currentInstanceIndex = new AtomicInteger(0);
    }
    
    public <T> T executeWithFailover(Function<ServiceInstance, T> operation) {
        Exception lastException = null;
        int startIndex = currentInstanceIndex.get();
        
        // 尝试所有实例
        for (int i = 0; i < serviceInstances.size(); i++) {
            int instanceIndex = (startIndex + i) % serviceInstances.size();
            ServiceInstance instance = serviceInstances.get(instanceIndex);
            
            try {
                T result = operation.apply(instance);
                
                // 更新当前实例索引（成功时使用该实例）
                currentInstanceIndex.set(instanceIndex);
                
                return result;
            } catch (Exception e) {
                lastException = e;
                logger.warn("Failed to execute on instance {}: {}", 
                           instance.getId(), e.getMessage());
                
                // 标记实例为不可用
                markInstanceAsUnhealthy(instance);
            }
        }
        
        throw new ServiceUnavailableException("All service instances unavailable", lastException);
    }
    
    private void markInstanceAsUnhealthy(ServiceInstance instance) {
        instance.setHealthy(false);
        instance.setLastFailureTime(Instant.now());
        
        // 启动健康检查任务
        healthCheckScheduler.schedule(
            () -> checkInstanceHealth(instance),
            Duration.ofMinutes(1)
        );
    }
    
    private void checkInstanceHealth(ServiceInstance instance) {
        try {
            // 执行健康检查
            boolean isHealthy = healthCheckService.check(instance);
            instance.setHealthy(isHealthy);
            
            if (isHealthy) {
                logger.info("Instance {} is now healthy", instance.getId());
            }
        } catch (Exception e) {
            logger.warn("Health check failed for instance {}: {}", 
                       instance.getId(), e.getMessage());
        }
    }
}
```

### 数据恢复机制

```java
// 数据恢复服务
@Service
public class DataRecoveryService {
    @Autowired
    private BackupService backupService;
    
    @Autowired
    private EventSourcingService eventSourcingService;
    
    @Autowired
    private DeadLetterQueueService dlqService;
    
    // 从备份恢复数据
    public void recoverFromBackup(String serviceName, Instant recoveryPoint) {
        try {
            logger.info("Starting data recovery for service {} at {}", 
                       serviceName, recoveryPoint);
            
            // 停止服务写入
            pauseServiceWrites(serviceName);
            
            // 从备份恢复
            backupService.restore(serviceName, recoveryPoint);
            
            // 重放事件（从备份时间点到当前）
            eventSourcingService.replayEvents(serviceName, recoveryPoint, Instant.now());
            
            // 恢复死信队列中的消息
            dlqService.reprocessMessages(serviceName);
            
            // 恢复服务写入
            resumeServiceWrites(serviceName);
            
            logger.info("Data recovery completed for service {}", serviceName);
            
        } catch (Exception e) {
            logger.error("Data recovery failed for service {}", serviceName, e);
            throw new DataRecoveryException("Failed to recover data for " + serviceName, e);
        }
    }
    
    // 补偿事务恢复
    public void recoverCompensatingTransactions(List<FailedTransaction> failedTransactions) {
        for (FailedTransaction transaction : failedTransactions) {
            try {
                // 执行补偿事务
                compensationService.executeCompensation(transaction);
                
                // 标记为已恢复
                transaction.markAsRecovered();
                transactionRepository.save(transaction);
                
                logger.info("Successfully recovered transaction {}", transaction.getId());
                
            } catch (Exception e) {
                logger.error("Failed to recover transaction {}", transaction.getId(), e);
                // 记录恢复失败，可能需要人工干预
                transaction.markAsRecoveryFailed(e.getMessage());
                transactionRepository.save(transaction);
            }
        }
    }
}
```

通过合理设计和实现这些异常处理与容错机制，可以显著提高微服务系统的稳定性和可用性。关键是要根据具体的业务场景和系统要求，选择合适的容错模式，并建立完善的监控和恢复机制。