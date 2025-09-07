---
title: 微服务健康检查与监控集成：构建可靠的系统观测体系
date: 2025-08-31
categories: [Microservices, Monitoring]
tags: [log-monitor]
published: true
---

在前两篇文章中，我们探讨了监控的基础概念和关键指标。本文将深入研究微服务健康检查与监控的集成方法，包括健康检查的设计、实现以及如何与监控系统紧密结合，构建可靠的系统观测体系。

## 健康检查的核心概念

### 什么是健康检查

健康检查是微服务架构中用于确定服务实例运行状态的机制。它通过定期执行检查来验证服务是否能够正常处理请求，是实现高可用性和自动故障恢复的基础。

### 健康检查的类型

#### 存活检查（Liveness Probe）

存活检查用于确定应用进程是否在运行。如果存活检查失败，Kubernetes等容器编排系统会重启容器。

```java
@RestController
public class LivenessController {
    
    private final AtomicBoolean applicationHealthy = new AtomicBoolean(true);
    
    @GetMapping("/health/live")
    public ResponseEntity<HealthStatus> livenessProbe() {
        if (applicationHealthy.get()) {
            return ResponseEntity.ok(new HealthStatus("UP"));
        } else {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(new HealthStatus("DOWN"));
        }
    }
    
    // 模拟应用故障
    @PostMapping("/admin/fail")
    public ResponseEntity<String> simulateFailure() {
        applicationHealthy.set(false);
        return ResponseEntity.ok("Application marked as unhealthy");
    }
    
    // 模拟应用恢复
    @PostMapping("/admin/recover")
    public ResponseEntity<String> simulateRecovery() {
        applicationHealthy.set(true);
        return ResponseEntity.ok("Application marked as healthy");
    }
}
```

#### 就绪检查（Readiness Probe）

就绪检查用于确定应用是否准备好接收流量。如果就绪检查失败，服务实例将从负载均衡器中移除。

```java
@RestController
public class ReadinessController {
    
    @Autowired
    private DatabaseService databaseService;
    
    @Autowired
    private ExternalService externalService;
    
    @Autowired
    private CacheService cacheService;
    
    @GetMapping("/health/ready")
    public ResponseEntity<ReadinessStatus> readinessProbe() {
        List<ReadinessCheck> checks = performReadinessChecks();
        
        boolean isReady = checks.stream().allMatch(ReadinessCheck::isHealthy);
        
        ReadinessStatus status = new ReadinessStatus()
            .setReady(isReady)
            .setChecks(checks);
            
        HttpStatus httpStatus = isReady ? HttpStatus.OK : HttpStatus.SERVICE_UNAVAILABLE;
        return ResponseEntity.status(httpStatus).body(status);
    }
    
    private List<ReadinessCheck> performReadinessChecks() {
        List<ReadinessCheck> checks = new ArrayList<>();
        
        // 数据库连接检查
        try {
            boolean dbHealthy = databaseService.isHealthy();
            checks.add(new ReadinessCheck("database", dbHealthy)
                .setDetails("Database connection status"));
        } catch (Exception e) {
            checks.add(new ReadinessCheck("database", false)
                .setDetails("Database check failed: " + e.getMessage()));
        }
        
        // 外部服务依赖检查
        try {
            boolean externalHealthy = externalService.isHealthy();
            checks.add(new ReadinessCheck("external-service", externalHealthy)
                .setDetails("External service connectivity"));
        } catch (Exception e) {
            checks.add(new ReadinessCheck("external-service", false)
                .setDetails("External service check failed: " + e.getMessage()));
        }
        
        // 缓存服务检查
        try {
            boolean cacheHealthy = cacheService.isHealthy();
            checks.add(new ReadinessCheck("cache", cacheHealthy)
                .setDetails("Cache service status"));
        } catch (Exception e) {
            checks.add(new ReadinessCheck("cache", false)
                .setDetails("Cache service check failed: " + e.getMessage()));
        }
        
        return checks;
    }
}
```

#### 启动检查（Startup Probe）

启动检查用于确定应用是否已经启动完成。在应用启动期间，启动检查会持续执行直到成功或超时。

```java
@RestController
public class StartupController {
    
    private final AtomicBoolean applicationStarted = new AtomicBoolean(false);
    
    @PostConstruct
    public void initializeApplication() {
        // 模拟应用启动过程
        CompletableFuture.runAsync(() -> {
            try {
                // 执行初始化任务
                performInitialization();
                applicationStarted.set(true);
            } catch (Exception e) {
                log.error("Application initialization failed", e);
            }
        });
    }
    
    @GetMapping("/health/startup")
    public ResponseEntity<HealthStatus> startupProbe() {
        if (applicationStarted.get()) {
            return ResponseEntity.ok(new HealthStatus("UP"));
        } else {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(new HealthStatus("STARTING"));
        }
    }
    
    private void performInitialization() throws InterruptedException {
        // 模拟耗时的初始化过程
        Thread.sleep(30000); // 30秒初始化时间
        
        // 初始化数据库连接池
        databaseService.initializeConnectionPool();
        
        // 预热缓存
        cacheService.warmUp();
        
        // 加载配置
        configurationService.loadConfiguration();
        
        log.info("Application initialization completed");
    }
}
```

## 健康检查的实现策略

### 分层健康检查

实现分层的健康检查策略，从基础到高级逐步验证：

```java
@Component
public class HierarchicalHealthChecker {
    
    @Autowired
    private List<HealthIndicator> healthIndicators;
    
    public HealthReport performComprehensiveHealthCheck() {
        HealthReport report = new HealthReport();
        report.setTimestamp(Instant.now());
        
        // 第一层：基础健康检查
        HealthCheckResult basicCheck = performBasicHealthCheck();
        report.addCheck("basic", basicCheck);
        
        if (!basicCheck.isHealthy()) {
            report.setStatus(HealthStatus.DOWN);
            return report;
        }
        
        // 第二层：依赖服务检查
        HealthCheckResult dependencyCheck = performDependencyHealthCheck();
        report.addCheck("dependencies", dependencyCheck);
        
        if (!dependencyCheck.isHealthy()) {
            report.setStatus(HealthStatus.DOWN);
            return report;
        }
        
        // 第三层：业务功能检查
        HealthCheckResult businessCheck = performBusinessHealthCheck();
        report.addCheck("business", businessCheck);
        
        report.setStatus(businessCheck.isHealthy() ? HealthStatus.UP : HealthStatus.DOWN);
        return report;
    }
    
    private HealthCheckResult performBasicHealthCheck() {
        try {
            // 检查JVM状态
            MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
            long heapUsed = memoryBean.getHeapMemoryUsage().getUsed();
            long heapMax = memoryBean.getHeapMemoryUsage().getMax();
            
            if ((double) heapUsed / heapMax > 0.95) {
                return new HealthCheckResult(false, "High memory usage: " + (heapUsed * 100 / heapMax) + "%");
            }
            
            // 检查线程状态
            ThreadMXBean threadBean = ManagementFactory.getThreadMXBean();
            if (threadBean.getThreadCount() > 1000) {
                return new HealthCheckResult(false, "Too many threads: " + threadBean.getThreadCount());
            }
            
            return new HealthCheckResult(true, "Basic health check passed");
        } catch (Exception e) {
            return new HealthCheckResult(false, "Basic health check failed: " + e.getMessage());
        }
    }
    
    private HealthCheckResult performDependencyHealthCheck() {
        List<DependencyHealth> dependencies = new ArrayList<>();
        boolean allHealthy = true;
        
        for (HealthIndicator indicator : healthIndicators) {
            try {
                HealthDetail detail = indicator.checkHealth();
                dependencies.add(new DependencyHealth(indicator.getName(), detail));
                
                if (detail.getStatus() != HealthStatus.UP) {
                    allHealthy = false;
                }
            } catch (Exception e) {
                dependencies.add(new DependencyHealth(indicator.getName(), 
                    new HealthDetail(HealthStatus.DOWN, e.getMessage())));
                allHealthy = false;
            }
        }
        
        return new HealthCheckResult(allHealthy, "Dependency check completed")
            .setDetails(objectMapper.writeValueAsString(dependencies));
    }
    
    private HealthCheckResult performBusinessHealthCheck() {
        try {
            // 执行关键业务功能测试
            boolean businessLogicHealthy = testBusinessLogic();
            
            if (businessLogicHealthy) {
                return new HealthCheckResult(true, "Business logic check passed");
            } else {
                return new HealthCheckResult(false, "Business logic check failed");
            }
        } catch (Exception e) {
            return new HealthCheckResult(false, "Business logic check failed: " + e.getMessage());
        }
    }
    
    private boolean testBusinessLogic() {
        try {
            // 测试核心业务功能
            userService.testFunctionality();
            orderService.testFunctionality();
            return true;
        } catch (Exception e) {
            log.warn("Business logic test failed", e);
            return false;
        }
    }
}
```

### 自适应健康检查

根据系统负载和状态动态调整健康检查策略：

```java
@Component
public class AdaptiveHealthChecker {
    
    private final MeterRegistry meterRegistry;
    private final CircuitBreaker circuitBreaker;
    
    public AdaptiveHealthChecker(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.circuitBreaker = CircuitBreaker.ofDefaults("health-check");
    }
    
    public HealthStatus performAdaptiveHealthCheck() {
        // 获取当前系统负载
        double cpuLoad = getSystemCpuLoad();
        double memoryUsage = getMemoryUsageRatio();
        
        // 根据负载调整检查策略
        if (cpuLoad > 0.8 || memoryUsage > 0.85) {
            // 高负载时执行轻量级检查
            return performLightweightHealthCheck();
        } else if (circuitBreaker.getState() == CircuitBreaker.State.OPEN) {
            // 熔断器开启时执行快速检查
            return performFastHealthCheck();
        } else {
            // 正常情况下执行完整检查
            return performFullHealthCheck();
        }
    }
    
    private HealthStatus performLightweightHealthCheck() {
        // 只检查最基本的状态
        if (isApplicationRunning()) {
            return HealthStatus.UP;
        } else {
            return HealthStatus.DOWN;
        }
    }
    
    private HealthStatus performFastHealthCheck() {
        // 快速检查，跳过耗时的依赖检查
        try {
            // 检查核心组件
            if (databaseService.isConnectionHealthy() && 
                cacheService.isConnectionHealthy()) {
                return HealthStatus.UP;
            } else {
                return HealthStatus.DOWN;
            }
        } catch (Exception e) {
            return HealthStatus.DOWN;
        }
    }
    
    private HealthStatus performFullHealthCheck() {
        // 执行完整的健康检查
        HealthReport report = hierarchicalHealthChecker.performComprehensiveHealthCheck();
        return report.getStatus();
    }
    
    private double getSystemCpuLoad() {
        OperatingSystemMXBean osBean = ManagementFactory.getPlatformMXBean(OperatingSystemMXBean.class);
        return osBean.getSystemCpuLoad();
    }
    
    private double getMemoryUsageRatio() {
        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        MemoryUsage heapUsage = memoryBean.getHeapMemoryUsage();
        return (double) heapUsage.getUsed() / heapUsage.getMax();
    }
}
```

## 监控与健康检查的集成

### 健康检查指标化

将健康检查结果转化为监控指标：

```java
@Component
public class HealthCheckMetrics {
    
    private final MeterRegistry meterRegistry;
    private final Gauge healthStatusGauge;
    private final Timer healthCheckTimer;
    private final Counter healthCheckSuccessCounter;
    private final Counter healthCheckFailureCounter;
    
    public HealthCheckMetrics(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        this.healthStatusGauge = Gauge.builder("service.health.status")
            .description("Overall health status of the service (1=UP, 0=DOWN)")
            .tags("service", "user-service")
            .register(meterRegistry);
            
        this.healthCheckTimer = Timer.builder("health.check.duration")
            .description("Duration of health check execution")
            .tags("service", "user-service")
            .register(meterRegistry);
            
        this.healthCheckSuccessCounter = Counter.builder("health.check.success")
            .description("Number of successful health checks")
            .tags("service", "user-service")
            .register(meterRegistry);
            
        this.healthCheckFailureCounter = Counter.builder("health.check.failure")
            .description("Number of failed health checks")
            .tags("service", "user-service")
            .register(meterRegistry);
    }
    
    @Scheduled(fixedRate = 30000) // 每30秒执行一次健康检查
    public void performAndRecordHealthCheck() {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            HealthStatus status = healthChecker.performHealthCheck();
            
            // 更新健康状态指标
            healthStatusGauge.set(status == HealthStatus.UP ? 1.0 : 0.0);
            
            // 记录成功或失败
            if (status == HealthStatus.UP) {
                healthCheckSuccessCounter.increment();
            } else {
                healthCheckFailureCounter.increment();
            }
            
            sample.stop(healthCheckTimer);
        } catch (Exception e) {
            healthCheckFailureCounter.increment();
            sample.stop(healthCheckTimer);
            log.error("Health check failed", e);
        }
    }
}
```

### 健康检查告警集成

基于健康检查结果触发告警：

```java
@Component
public class HealthCheckAlerting {
    
    private final AlertService alertService;
    private final Map<String, Instant> lastAlertTimes = new ConcurrentHashMap<>();
    private final Map<String, Integer> failureCounts = new ConcurrentHashMap<>();
    
    @EventListener
    public void handleHealthCheckEvent(HealthCheckEvent event) {
        if (event.getStatus() == HealthStatus.DOWN) {
            handleHealthCheckFailure(event);
        } else {
            handleHealthCheckRecovery(event);
        }
    }
    
    private void handleHealthCheckFailure(HealthCheckEvent event) {
        String serviceKey = event.getServiceName();
        int failureCount = failureCounts.compute(serviceKey, (k, v) -> v == null ? 1 : v + 1);
        
        // 如果连续失败3次，触发告警
        if (failureCount >= 3) {
            if (shouldSendAlert(serviceKey)) {
                Alert alert = new Alert()
                    .setType("SERVICE_UNHEALTHY")
                    .setSeverity(AlertSeverity.CRITICAL)
                    .setTitle("Service Unhealthy: " + event.getServiceName())
                    .setMessage("Service health check failed: " + event.getDetails())
                    .setTimestamp(Instant.now())
                    .setService(event.getServiceName());
                
                alertService.sendAlert(alert);
                lastAlertTimes.put(serviceKey, Instant.now());
                
                // 重置失败计数
                failureCounts.put(serviceKey, 0);
            }
        }
    }
    
    private void handleHealthCheckRecovery(HealthCheckEvent event) {
        String serviceKey = event.getServiceName();
        
        // 如果之前有告警，发送恢复通知
        if (failureCounts.getOrDefault(serviceKey, 0) > 0) {
            Alert alert = new Alert()
                .setType("SERVICE_RECOVERED")
                .setSeverity(AlertSeverity.INFO)
                .setTitle("Service Recovered: " + event.getServiceName())
                .setMessage("Service health check recovered")
                .setTimestamp(Instant.now())
                .setService(event.getServiceName());
                
            alertService.sendAlert(alert);
        }
        
        // 重置失败计数
        failureCounts.put(serviceKey, 0);
    }
    
    private boolean shouldSendAlert(String serviceKey) {
        Instant lastAlertTime = lastAlertTimes.get(serviceKey);
        if (lastAlertTime == null) {
            return true;
        }
        
        // 至少间隔5分钟才发送下一次告警
        return Instant.now().isAfter(lastAlertTime.plus(Duration.ofMinutes(5)));
    }
}
```

### 健康检查可视化

通过监控面板展示健康检查状态：

```java
@RestController
public class HealthDashboardController {
    
    @Autowired
    private HealthCheckService healthCheckService;
    
    @GetMapping("/dashboard/health")
    public ResponseEntity<HealthDashboard> getHealthDashboard() {
        HealthDashboard dashboard = new HealthDashboard();
        
        // 获取所有服务的健康状态
        List<ServiceHealth> serviceHealths = healthCheckService.getAllServiceHealth();
        dashboard.setServiceHealths(serviceHealths);
        
        // 计算整体健康度
        double overallHealth = calculateOverallHealth(serviceHealths);
        dashboard.setOverallHealth(overallHealth);
        
        // 获取最近的健康检查历史
        List<HealthCheckHistory> recentHistory = healthCheckService.getRecentHistory();
        dashboard.setRecentHistory(recentHistory);
        
        return ResponseEntity.ok(dashboard);
    }
    
    @GetMapping("/dashboard/health/trends")
    public ResponseEntity<HealthTrends> getHealthTrends(
            @RequestParam(defaultValue = "24h") String timeRange) {
        
        HealthTrends trends = healthCheckService.getHealthTrends(timeRange);
        return ResponseEntity.ok(trends);
    }
    
    private double calculateOverallHealth(List<ServiceHealth> serviceHealths) {
        if (serviceHealths.isEmpty()) {
            return 100.0;
        }
        
        long healthyServices = serviceHealths.stream()
            .filter(sh -> sh.getStatus() == HealthStatus.UP)
            .count();
            
        return (double) healthyServices / serviceHealths.size() * 100;
    }
}
```

## Kubernetes集成

### Probe配置

在Kubernetes中配置健康检查探针：

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:1.2.3
        ports:
        - containerPort: 8080
        env:
        - name: SERVER_PORT
          value: "8080"
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 5
        startupProbe:
          httpGet:
            path: /health/startup
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30
```

### 健康检查最佳实践

```java
@Component
public class KubernetesHealthCheckBestPractices {
    
    // 1. 避免在存活检查中执行耗时操作
    @GetMapping("/health/live")
    public ResponseEntity<HealthStatus> livenessProbe() {
        // 只检查应用进程是否在运行
        // 避免数据库查询、外部服务调用等耗时操作
        return ResponseEntity.ok(new HealthStatus("UP"));
    }
    
    // 2. 就绪检查应该包含必要的依赖检查
    @GetMapping("/health/ready")
    public ResponseEntity<ReadinessStatus> readinessProbe() {
        // 检查数据库、缓存等必要依赖
        // 但不要检查所有依赖（避免单点故障影响整个服务）
        List<ReadinessCheck> checks = new ArrayList<>();
        
        // 核心依赖检查
        checks.add(checkDatabase());
        checks.add(checkCache());
        
        boolean isReady = checks.stream()
            .filter(check -> "database".equals(check.getName()) || "cache".equals(check.getName()))
            .allMatch(ReadinessCheck::isHealthy);
        
        ReadinessStatus status = new ReadinessStatus()
            .setReady(isReady)
            .setChecks(checks);
            
        HttpStatus httpStatus = isReady ? HttpStatus.OK : HttpStatus.SERVICE_UNAVAILABLE;
        return ResponseEntity.status(httpStatus).body(status);
    }
    
    // 3. 实现超时控制
    @GetMapping("/health/ready")
    public ResponseEntity<ReadinessStatus> readinessProbeWithTimeout() {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        
        try {
            Future<ReadinessStatus> future = executor.submit(() -> performReadinessChecks());
            
            // 5秒超时
            ReadinessStatus status = future.get(5, TimeUnit.SECONDS);
            
            HttpStatus httpStatus = status.isReady() ? HttpStatus.OK : HttpStatus.SERVICE_UNAVAILABLE;
            return ResponseEntity.status(httpStatus).body(status);
        } catch (TimeoutException e) {
            log.warn("Readiness check timed out");
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(new ReadinessStatus().setReady(false).setDetails("Check timed out"));
        } catch (Exception e) {
            log.error("Readiness check failed", e);
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(new ReadinessStatus().setReady(false).setDetails("Check failed: " + e.getMessage()));
        } finally {
            executor.shutdown();
        }
    }
}
```

## 监控驱动的健康检查

### 基于监控数据的健康评估

```java
@Component
public class MonitoringDrivenHealthCheck {
    
    private final MeterRegistry meterRegistry;
    
    public HealthStatus assessHealthBasedOnMetrics() {
        // 基于错误率评估健康状态
        double errorRate = getErrorRate();
        if (errorRate > 0.05) { // 错误率超过5%
            return HealthStatus.DOWN;
        }
        
        // 基于响应时间评估健康状态
        double p95ResponseTime = getResponseTimeP95();
        if (p95ResponseTime > 5000) { // 95%分位响应时间超过5秒
            return HealthStatus.DOWN;
        }
        
        // 基于资源使用率评估健康状态
        double cpuUsage = getCpuUsage();
        double memoryUsage = getMemoryUsage();
        if (cpuUsage > 0.9 || memoryUsage > 0.9) { // 资源使用率超过90%
            return HealthStatus.DOWN;
        }
        
        return HealthStatus.UP;
    }
    
    private double getErrorRate() {
        Counter totalRequests = meterRegistry.find("http.requests.total").counter();
        Counter failedRequests = meterRegistry.find("http.requests.failed").counter();
        
        if (totalRequests == null || failedRequests == null) {
            return 0.0;
        }
        
        long total = (long) totalRequests.count();
        long failed = (long) failedRequests.count();
        
        return total > 0 ? (double) failed / total : 0.0;
    }
    
    private double getResponseTimeP95() {
        Timer responseTimer = meterRegistry.find("http.server.requests").timer();
        if (responseTimer == null) {
            return 0.0;
        }
        
        return responseTimer.percentile(Percentile.of(95), TimeUnit.MILLISECONDS);
    }
    
    private double getCpuUsage() {
        Gauge cpuGauge = meterRegistry.find("system.cpu.usage").gauge();
        return cpuGauge != null ? cpuGauge.value() : 0.0;
    }
    
    private double getMemoryUsage() {
        Gauge memoryGauge = meterRegistry.find("jvm.memory.heap.used").gauge();
        Gauge maxMemoryGauge = meterRegistry.find("jvm.memory.heap.max").gauge();
        
        if (memoryGauge == null || maxMemoryGauge == null) {
            return 0.0;
        }
        
        return memoryGauge.value() / maxMemoryGauge.value();
    }
}
```

### 健康检查与自动扩缩容集成

```java
@Component
public class HealthCheckAutoscalingIntegration {
    
    @EventListener
    public void handleHealthCheckEvent(HealthCheckEvent event) {
        if (event.getStatus() == HealthStatus.DOWN) {
            // 如果服务不健康，可能需要调整副本数
            adjustReplicaCountBasedOnHealth(event);
        }
    }
    
    private void adjustReplicaCountBasedOnHealth(HealthCheckEvent event) {
        String serviceName = event.getServiceName();
        HealthStatus status = event.getStatus();
        
        // 获取当前副本数
        int currentReplicas = getCurrentReplicaCount(serviceName);
        
        if (status == HealthStatus.DOWN) {
            // 如果服务不健康，减少副本数以减轻负载
            if (currentReplicas > 1) {
                scaleService(serviceName, currentReplicas - 1);
                log.info("Scaled down service {} due to unhealthy status", serviceName);
            }
        } else {
            // 如果服务恢复健康，可以考虑增加副本数
            int desiredReplicas = calculateDesiredReplicas(serviceName);
            if (desiredReplicas > currentReplicas) {
                scaleService(serviceName, desiredReplicas);
                log.info("Scaled up service {} due to healthy status", serviceName);
            }
        }
    }
    
    private int calculateDesiredReplicas(String serviceName) {
        // 基于负载指标计算期望副本数
        double cpuUsage = getAverageCpuUsage(serviceName);
        double requestRate = getAverageRequestRate(serviceName);
        
        // 简单的扩缩容算法
        if (cpuUsage > 0.7 || requestRate > 1000) {
            return getCurrentReplicaCount(serviceName) + 1;
        } else if (cpuUsage < 0.3 && requestRate < 500) {
            return Math.max(1, getCurrentReplicaCount(serviceName) - 1);
        }
        
        return getCurrentReplicaCount(serviceName);
    }
}
```

## 故障自愈机制

### 基于健康检查的自动恢复

```java
@Component
public class HealthCheckSelfHealing {
    
    private final Map<String, Instant> lastRecoveryAttempts = new ConcurrentHashMap<>();
    
    @EventListener
    public void handleHealthCheckFailure(HealthCheckEvent event) {
        if (event.getStatus() == HealthStatus.DOWN) {
            attemptSelfHealing(event);
        }
    }
    
    private void attemptSelfHealing(HealthCheckEvent event) {
        String serviceKey = event.getServiceName();
        Instant lastAttempt = lastRecoveryAttempts.get(serviceKey);
        
        // 限制自愈尝试频率（至少间隔10分钟）
        if (lastAttempt != null && 
            Instant.now().isBefore(lastAttempt.plus(Duration.ofMinutes(10)))) {
            return;
        }
        
        try {
            // 尝试不同的自愈策略
            if (attemptConnectionPoolRecovery(event)) {
                log.info("Connection pool recovery successful for service: {}", serviceKey);
                return;
            }
            
            if (attemptCacheRecovery(event)) {
                log.info("Cache recovery successful for service: {}", serviceKey);
                return;
            }
            
            if (attemptThreadDumpAndRestart(event)) {
                log.info("Thread dump and restart successful for service: {}", serviceKey);
                return;
            }
            
            log.warn("All self-healing attempts failed for service: {}", serviceKey);
        } finally {
            lastRecoveryAttempts.put(serviceKey, Instant.now());
        }
    }
    
    private boolean attemptConnectionPoolRecovery(HealthCheckEvent event) {
        try {
            // 重置数据库连接池
            databaseService.resetConnectionPool();
            
            // 等待一段时间让连接池重新建立
            Thread.sleep(5000);
            
            // 检查是否恢复
            return databaseService.isHealthy();
        } catch (Exception e) {
            log.warn("Connection pool recovery failed", e);
            return false;
        }
    }
    
    private boolean attemptCacheRecovery(HealthCheckEvent event) {
        try {
            // 清理并重新初始化缓存
            cacheService.clearAndReinitialize();
            
            // 等待缓存预热
            Thread.sleep(3000);
            
            // 检查是否恢复
            return cacheService.isHealthy();
        } catch (Exception e) {
            log.warn("Cache recovery failed", e);
            return false;
        }
    }
    
    private boolean attemptThreadDumpAndRestart(HealthCheckEvent event) {
        try {
            // 生成线程转储用于分析
            generateThreadDump();
            
            // 重新加载部分组件
            reloadComponents();
            
            // 等待系统稳定
            Thread.sleep(10000);
            
            // 检查是否恢复
            return healthChecker.performHealthCheck() == HealthStatus.UP;
        } catch (Exception e) {
            log.warn("Thread dump and restart failed", e);
            return false;
        }
    }
}
```

## 最佳实践

### 1. 健康检查设计原则

```java
public class HealthCheckDesignPrinciples {
    
    // 原则1：存活检查应该简单快速
    @GetMapping("/health/live")
    public ResponseEntity<String> simpleLivenessCheck() {
        // 只返回应用是否在运行，不进行复杂检查
        return ResponseEntity.ok("OK");
    }
    
    // 原则2：就绪检查应该包含关键依赖
    @GetMapping("/health/ready")
    public ResponseEntity<HealthStatus> comprehensiveReadinessCheck() {
        // 检查数据库、缓存等关键依赖
        // 但不要检查所有依赖以避免单点故障
        return ResponseEntity.ok(performEssentialReadinessChecks());
    }
    
    // 原则3：实现适当的超时控制
    @GetMapping("/health/ready")
    public ResponseEntity<HealthStatus> timeoutControlledCheck() {
        // 使用Future实现超时控制
        return ResponseEntity.ok(executeWithTimeout(this::performReadinessChecks, 5000));
    }
    
    // 原则4：提供详细的健康信息
    @GetMapping("/health/detailed")
    public ResponseEntity<DetailedHealthReport> detailedHealthCheck() {
        // 提供详细的健康状态信息，包括各组件状态和指标
        return ResponseEntity.ok(performDetailedHealthCheck());
    }
}
```

### 2. 健康检查监控集成

```java
@Component
public class HealthCheckMonitoringIntegration {
    
    private final MeterRegistry meterRegistry;
    
    // 将健康检查结果转化为指标
    @EventListener
    public void recordHealthCheckMetrics(HealthCheckEvent event) {
        Tags tags = Tags.of(
            "service", event.getServiceName(),
            "status", event.getStatus().toString()
        );
        
        // 记录健康检查状态
        Gauge.builder("service.health.status")
            .tags(tags)
            .register(meterRegistry, event, e -> e.getStatus() == HealthStatus.UP ? 1.0 : 0.0);
        
        // 记录健康检查持续时间
        Timer.builder("health.check.duration")
            .tags(tags)
            .register(meterRegistry)
            .record(event.getDuration());
    }
    
    // 基于健康检查指标触发告警
    @Scheduled(fixedRate = 60000) // 每分钟检查一次
    public void checkHealthMetricsAndAlert() {
        // 检查健康检查失败率
        double failureRate = calculateHealthCheckFailureRate();
        if (failureRate > 0.1) { // 失败率超过10%
            alertService.sendAlert(new Alert()
                .setType("HIGH_HEALTH_CHECK_FAILURE_RATE")
                .setSeverity(AlertSeverity.WARNING)
                .setMessage("Health check failure rate is high: " + failureRate));
        }
    }
}
```

### 3. 健康检查配置管理

```java
@ConfigurationProperties(prefix = "health.check")
@Component
public class HealthCheckConfiguration {
    
    private Liveness liveness = new Liveness();
    private Readiness readiness = new Readiness();
    private Startup startup = new Startup();
    
    // 健活检查配置
    public static class Liveness {
        private boolean enabled = true;
        private int initialDelaySeconds = 60;
        private int periodSeconds = 30;
        private int timeoutSeconds = 10;
        private int failureThreshold = 5;
        
        // getters and setters
    }
    
    // 就绪检查配置
    public static class Readiness {
        private boolean enabled = true;
        private int initialDelaySeconds = 30;
        private int periodSeconds = 10;
        private int timeoutSeconds = 5;
        private int failureThreshold = 3;
        
        // getters and setters
    }
    
    // 启动检查配置
    public static class Startup {
        private boolean enabled = true;
        private int initialDelaySeconds = 10;
        private int periodSeconds = 5;
        private int timeoutSeconds = 3;
        private int failureThreshold = 30;
        
        // getters and setters
    }
    
    // getters and setters
}
```

## 总结

健康检查与监控的集成是构建可靠微服务系统的关键。通过实施分层健康检查策略、将健康状态指标化、与Kubernetes等容器编排系统集成，以及实现故障自愈机制，我们可以构建一个健壮的系统观测体系。

在实际应用中，需要注意健康检查的设计原则，包括简单快速的存活检查、包含关键依赖的就绪检查、适当的超时控制和详细的健康信息提供。同时，要将健康检查与监控系统紧密结合，通过指标化和告警机制实现主动的系统管理。

在下一章中，我们将探讨监控工具与技术栈，包括Prometheus、Grafana、OpenTelemetry等主流工具的使用方法和最佳实践。