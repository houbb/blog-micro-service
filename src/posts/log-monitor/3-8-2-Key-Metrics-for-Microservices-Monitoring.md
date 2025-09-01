---
title: 微服务监控的关键指标：构建全面的系统观测体系
date: 2025-08-31
categories: [Microservices, Monitoring]
tags: [log-monitor]
published: true
---

在前一篇文章中，我们探讨了监控的基本概念和重要性。本文将深入研究微服务监控的关键指标，包括服务性能指标、系统资源指标、健康检查指标以及用户体验指标，帮助您构建全面的系统观测体系。

## 服务性能指标

### 响应时间指标

响应时间是衡量服务性能的核心指标，直接影响用户体验和系统效率。

#### 基础响应时间指标

```java
@RestController
public class ResponseTimeMonitoringController {
    
    private final MeterRegistry meterRegistry;
    private final Timer apiResponseTimer;
    private final Timer databaseQueryTimer;
    private final Timer externalServiceTimer;
    
    public ResponseTimeMonitoringController(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        // API响应时间监控
        this.apiResponseTimer = Timer.builder("api.response.time")
            .description("API endpoint response time")
            .tags("service", "user-service")
            .register(meterRegistry);
        
        // 数据库查询时间监控
        this.databaseQueryTimer = Timer.builder("database.query.time")
            .description("Database query execution time")
            .tags("service", "user-service")
            .register(meterRegistry);
        
        // 外部服务调用时间监控
        this.externalServiceTimer = Timer.builder("external.service.time")
            .description("External service call time")
            .tags("service", "user-service")
            .register(meterRegistry);
    }
    
    @GetMapping("/api/users/{id}")
    public User getUser(@PathVariable String id) {
        Timer.Sample apiSample = Timer.start(meterRegistry);
        
        try {
            // 数据库查询时间监控
            Timer.Sample dbSample = Timer.start(meterRegistry);
            User user = userService.findById(id);
            dbSample.stop(databaseQueryTimer);
            
            apiSample.stop(apiResponseTimer);
            return user;
        } catch (Exception e) {
            apiSample.stop(apiResponseTimer);
            throw e;
        }
    }
}
```

#### 分位数响应时间

分位数响应时间能够更全面地反映系统性能分布：

```java
@Component
public class ResponseTimePercentiles {
    
    private final MeterRegistry meterRegistry;
    private final Timer responseTimer;
    
    public ResponseTimePercentiles(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        // 配置包含分位数的Timer
        this.responseTimer = Timer.builder("service.response.time")
            .description("Service response time with percentiles")
            .tags("service", "order-service")
            .publishPercentiles(0.5, 0.95, 0.99) // 50%, 95%, 99%分位数
            .publishPercentileHistogram() // 发布直方图数据
            .sla(Duration.ofMillis(100), Duration.ofMillis(200)) // SLA边界
            .register(meterRegistry);
    }
    
    public void recordResponseTime(Duration duration) {
        responseTimer.record(duration);
    }
    
    public ResponseTimeStats getResponseTimeStats() {
        return new ResponseTimeStats()
            .setAverage(responseTimer.mean(TimeUnit.MILLISECONDS))
            .setP50(responseTimer.percentile(Percentile.of(50), TimeUnit.MILLISECONDS))
            .setP95(responseTimer.percentile(Percentile.of(95), TimeUnit.MILLISECONDS))
            .setP99(responseTimer.percentile(Percentile.of(99), TimeUnit.MILLISECONDS))
            .setMax(responseTimer.max(TimeUnit.MILLISECONDS));
    }
}
```

#### 响应时间趋势分析

```java
@Component
public class ResponseTimeTrendAnalyzer {
    
    private final MeterRegistry meterRegistry;
    
    public ResponseTimeTrendAnalyzer(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }
    
    @Scheduled(fixedRate = 60000) // 每分钟分析一次
    public void analyzeResponseTimeTrends() {
        // 获取最近5分钟的响应时间数据
        List<Double> recentResponseTimes = getRecentResponseTimes(Duration.ofMinutes(5));
        
        // 计算趋势指标
        ResponseTimeTrend trend = calculateTrend(recentResponseTimes);
        
        // 如果响应时间呈上升趋势，触发告警
        if (trend.isDeteriorating() && trend.getRateOfChange() > 0.1) { // 10%的增长率
            alertService.sendAlert(new PerformanceAlert()
                .setType("RESPONSE_TIME_DEGRADATION")
                .setSeverity(AlertSeverity.WARNING)
                .setMessage("Response time is degrading: " + trend.getRateOfChange() * 100 + "% increase")
                .setDetails(objectMapper.writeValueAsString(trend)));
        }
    }
    
    private ResponseTimeTrend calculateTrend(List<Double> responseTimes) {
        if (responseTimes.size() < 2) {
            return new ResponseTimeTrend().setDeteriorating(false);
        }
        
        // 简单线性回归计算趋势
        double[] x = new double[responseTimes.size()];
        double[] y = new double[responseTimes.size()];
        
        for (int i = 0; i < responseTimes.size(); i++) {
            x[i] = i;
            y[i] = responseTimes.get(i);
        }
        
        // 计算斜率
        double slope = calculateSlope(x, y);
        
        return new ResponseTimeTrend()
            .setDeteriorating(slope > 0)
            .setRateOfChange(slope / responseTimes.get(0)) // 相对增长率
            .setSlope(slope);
    }
}
```

### 吞吐量指标

吞吐量反映了系统处理请求的能力，是衡量系统容量的重要指标。

#### 请求速率监控

```java
@Component
public class ThroughputMonitor {
    
    private final MeterRegistry meterRegistry;
    private final Counter totalRequests;
    private final Counter successfulRequests;
    private final Counter failedRequests;
    private final DistributionSummary requestSize;
    
    public ThroughputMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        this.totalRequests = Counter.builder("http.requests.total")
            .description("Total HTTP requests")
            .tags("service", "user-service", "method", "all")
            .register(meterRegistry);
            
        this.successfulRequests = Counter.builder("http.requests.successful")
            .description("Successful HTTP requests")
            .tags("service", "user-service", "method", "all", "status", "2xx")
            .register(meterRegistry);
            
        this.failedRequests = Counter.builder("http.requests.failed")
            .description("Failed HTTP requests")
            .tags("service", "user-service", "method", "all", "status", "5xx")
            .register(meterRegistry);
            
        this.requestSize = DistributionSummary.builder("http.request.size")
            .description("HTTP request size distribution")
            .tags("service", "user-service")
            .register(meterRegistry);
    }
    
    @EventListener
    public void handleHttpRequest(HttpRequestEvent event) {
        totalRequests.increment();
        requestSize.record(event.getRequestSize());
        
        if (event.isSuccessful()) {
            successfulRequests.increment();
        } else {
            failedRequests.increment();
        }
    }
    
    public ThroughputMetrics getThroughputMetrics() {
        return new ThroughputMetrics()
            .setRequestsPerSecond(calculateRPS())
            .setSuccessRate(calculateSuccessRate())
            .setTotalRequests(totalRequests.count())
            .setSuccessfulRequests(successfulRequests.count())
            .setFailedRequests(failedRequests.count());
    }
    
    private double calculateRPS() {
        // 计算最近1分钟的请求速率
        return meterRegistry.find("http.requests.total")
            .counter().count() / 60.0;
    }
    
    private double calculateSuccessRate() {
        long total = totalRequests.count();
        if (total == 0) {
            return 1.0;
        }
        return (double) successfulRequests.count() / total;
    }
}
```

#### 并发处理能力

```java
@Component
public class ConcurrencyMonitor {
    
    private final MeterRegistry meterRegistry;
    private final Gauge activeConnections;
    private final Gauge threadPoolUtilization;
    private final Gauge queueSize;
    
    private final AtomicInteger currentConnections = new AtomicInteger(0);
    private final ThreadPoolExecutor threadPoolExecutor;
    
    public ConcurrencyMonitor(MeterRegistry meterRegistry, 
                            ThreadPoolExecutor threadPoolExecutor) {
        this.meterRegistry = meterRegistry;
        this.threadPoolExecutor = threadPoolExecutor;
        
        this.activeConnections = Gauge.builder("connections.active")
            .description("Number of active connections")
            .tags("service", "user-service")
            .register(meterRegistry, currentConnections, AtomicInteger::get);
            
        this.threadPoolUtilization = Gauge.builder("threadpool.utilization")
            .description("Thread pool utilization ratio")
            .tags("service", "user-service")
            .register(meterRegistry, threadPoolExecutor, 
                     executor -> (double) executor.getActiveCount() / executor.getPoolSize());
            
        this.queueSize = Gauge.builder("threadpool.queue.size")
            .description("Thread pool queue size")
            .tags("service", "user-service")
            .register(meterRegistry, threadPoolExecutor, 
                     executor -> executor.getQueue().size());
    }
    
    public void connectionOpened() {
        currentConnections.incrementAndGet();
    }
    
    public void connectionClosed() {
        currentConnections.decrementAndGet();
    }
    
    public ConcurrencyMetrics getConcurrencyMetrics() {
        return new ConcurrencyMetrics()
            .setActiveConnections(activeConnections.value())
            .setThreadPoolUtilization(threadPoolUtilization.value())
            .setQueueSize(queueSize.value())
            .setMaxPoolSize(threadPoolExecutor.getMaximumPoolSize())
            .setCorePoolSize(threadPoolExecutor.getCorePoolSize());
    }
}
```

### 错误率指标

错误率是衡量系统稳定性和可靠性的重要指标。

#### 错误分类监控

```java
@Component
public class ErrorRateMonitor {
    
    private final MeterRegistry meterRegistry;
    private final Counter totalErrors;
    private final Counter businessErrors;
    private final Counter systemErrors;
    private final Counter networkErrors;
    private final Counter timeoutErrors;
    
    public ErrorRateMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        this.totalErrors = Counter.builder("errors.total")
            .description("Total errors")
            .tags("service", "order-service")
            .register(meterRegistry);
            
        this.businessErrors = Counter.builder("errors.business")
            .description("Business logic errors")
            .tags("service", "order-service", "type", "business")
            .register(meterRegistry);
            
        this.systemErrors = Counter.builder("errors.system")
            .description("System errors")
            .tags("service", "order-service", "type", "system")
            .register(meterRegistry);
            
        this.networkErrors = Counter.builder("errors.network")
            .description("Network errors")
            .tags("service", "order-service", "type", "network")
            .register(meterRegistry);
            
        this.timeoutErrors = Counter.builder("errors.timeout")
            .description("Timeout errors")
            .tags("service", "order-service", "type", "timeout")
            .register(meterRegistry);
    }
    
    public void recordError(ErrorType errorType, Exception exception) {
        totalErrors.increment();
        
        switch (errorType) {
            case BUSINESS:
                businessErrors.increment();
                break;
            case SYSTEM:
                systemErrors.increment();
                break;
            case NETWORK:
                networkErrors.increment();
                break;
            case TIMEOUT:
                timeoutErrors.increment();
                break;
        }
        
        // 记录错误详情用于分析
        recordErrorDetails(errorType, exception);
    }
    
    public ErrorRateMetrics getErrorRateMetrics() {
        long total = totalErrors.count();
        long requests = getTotalRequests(); // 从其他监控获取总请求数
        
        return new ErrorRateMetrics()
            .setErrorRate(total > 0 ? (double) total / requests : 0.0)
            .setTotalErrors(total)
            .setBusinessErrors(businessErrors.count())
            .setSystemErrors(systemErrors.count())
            .setNetworkErrors(networkErrors.count())
            .setTimeoutErrors(timeoutErrors.count())
            .setErrorDistribution(calculateErrorDistribution());
    }
    
    private Map<String, Double> calculateErrorDistribution() {
        Map<String, Double> distribution = new HashMap<>();
        long total = totalErrors.count();
        
        if (total > 0) {
            distribution.put("business", (double) businessErrors.count() / total);
            distribution.put("system", (double) systemErrors.count() / total);
            distribution.put("network", (double) networkErrors.count() / total);
            distribution.put("timeout", (double) timeoutErrors.count() / total);
        }
        
        return distribution;
    }
}
```

#### 错误趋势监控

```java
@Component
public class ErrorTrendMonitor {
    
    private final MeterRegistry meterRegistry;
    private final RollingWindowCounter errorCounter;
    
    public ErrorTrendMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.errorCounter = new RollingWindowCounter(Duration.ofMinutes(10), 60); // 10小时窗口，每10分钟一个桶
    }
    
    @EventListener
    public void handleErrorEvent(ErrorEvent event) {
        errorCounter.increment();
        
        // 检查错误率是否异常
        checkErrorRateAnomaly();
    }
    
    private void checkErrorRateAnomaly() {
        // 计算当前错误率
        double currentErrorRate = errorCounter.getRate(Duration.ofMinutes(5));
        
        // 计算历史平均错误率
        double averageErrorRate = errorCounter.getAverageRate(Duration.ofHours(1));
        
        // 如果当前错误率比平均值高出2倍，触发告警
        if (currentErrorRate > averageErrorRate * 2 && averageErrorRate > 0.01) { // 基础阈值1%
            alertService.sendAlert(new AnomalyAlert()
                .setType("ERROR_RATE_SPIKE")
                .setSeverity(AlertSeverity.WARNING)
                .setMessage("Error rate spike detected: " + currentErrorRate + " vs " + averageErrorRate)
                .setDetails("Current error rate is " + (currentErrorRate / averageErrorRate) + "x higher than average"));
        }
    }
}
```

## 系统资源指标

### CPU使用率指标

CPU使用率反映了系统的计算资源消耗情况。

```java
@Component
public class CPUMonitor {
    
    private final MeterRegistry meterRegistry;
    private final Gauge cpuUsage;
    private final Gauge cpuLoadAverage;
    
    public CPUMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        this.cpuUsage = Gauge.builder("system.cpu.usage")
            .description("CPU usage percentage")
            .tags("service", "user-service")
            .register(meterRegistry, this, CPUMonitor::getCpuUsage);
            
        this.cpuLoadAverage = Gauge.builder("system.cpu.load.average")
            .description("CPU load average")
            .tags("service", "user-service")
            .register(meterRegistry, this, CPUMonitor::getCpuLoadAverage);
    }
    
    public double getCpuUsage() {
        OperatingSystemMXBean osBean = ManagementFactory.getPlatformMXBean(OperatingSystemMXBean.class);
        return osBean.getSystemCpuLoad() * 100;
    }
    
    public double getCpuLoadAverage() {
        OperatingSystemMXBean osBean = ManagementFactory.getPlatformMXBean(OperatingSystemMXBean.class);
        return osBean.getSystemLoadAverage();
    }
    
    @Scheduled(fixedRate = 10000) // 每10秒检查一次
    public void checkCPUUsage() {
        double usage = cpuUsage.value();
        
        // 如果CPU使用率持续超过80%，触发告警
        if (usage > 80.0) {
            alertService.sendAlert(new ResourceAlert()
                .setType("HIGH_CPU_USAGE")
                .setSeverity(AlertSeverity.WARNING)
                .setMessage("High CPU usage detected: " + usage + "%")
                .setDetails("CPU usage has been above 80% for the last check"));
        }
    }
}
```

### 内存使用指标

内存使用情况直接影响应用的稳定性和性能。

```java
@Component
public class MemoryMonitor {
    
    private final MeterRegistry meterRegistry;
    private final Gauge heapMemoryUsed;
    private final Gauge heapMemoryMax;
    private final Gauge nonHeapMemoryUsed;
    private final Gauge memoryPoolUsage;
    
    public MemoryMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        
        this.heapMemoryUsed = Gauge.builder("jvm.memory.heap.used")
            .description("Used heap memory")
            .tags("service", "user-service")
            .register(meterRegistry, memoryBean, 
                     bean -> bean.getHeapMemoryUsage().getUsed());
            
        this.heapMemoryMax = Gauge.builder("jvm.memory.heap.max")
            .description("Max heap memory")
            .tags("service", "user-service")
            .register(meterRegistry, memoryBean, 
                     bean -> bean.getHeapMemoryUsage().getMax());
            
        this.nonHeapMemoryUsed = Gauge.builder("jvm.memory.nonheap.used")
            .description("Used non-heap memory")
            .tags("service", "user-service")
            .register(meterRegistry, memoryBean, 
                     bean -> bean.getNonHeapMemoryUsage().getUsed());
            
        // 监控各个内存池
        List<MemoryPoolMXBean> memoryPools = ManagementFactory.getMemoryPoolMXBeans();
        for (MemoryPoolMXBean pool : memoryPools) {
            Gauge.builder("jvm.memory.pool.used")
                .description("Used memory in pool")
                .tags("service", "user-service", "pool", pool.getName())
                .register(meterRegistry, pool, 
                         p -> p.getUsage().getUsed());
        }
    }
    
    @Scheduled(fixedRate = 30000) // 每30秒检查一次
    public void checkMemoryUsage() {
        double heapUsageRatio = heapMemoryUsed.value() / heapMemoryMax.value();
        
        // 如果堆内存使用率超过90%，触发告警
        if (heapUsageRatio > 0.9) {
            alertService.sendAlert(new ResourceAlert()
                .setType("HIGH_MEMORY_USAGE")
                .setSeverity(AlertSeverity.CRITICAL)
                .setMessage("High heap memory usage: " + (heapUsageRatio * 100) + "%")
                .setDetails("Heap memory usage is critically high, consider garbage collection or memory optimization"));
        }
        
        // 检查内存泄漏迹象
        checkMemoryLeakSigns();
    }
    
    private void checkMemoryLeakSigns() {
        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        long usedMemory = memoryBean.getHeapMemoryUsage().getUsed();
        
        // 如果连续几次检查内存使用量持续增长，可能存在内存泄漏
        if (isMemoryGrowingConsistently(usedMemory)) {
            alertService.sendAlert(new ResourceAlert()
                .setType("POSSIBLE_MEMORY_LEAK")
                .setSeverity(AlertSeverity.WARNING)
                .setMessage("Possible memory leak detected")
                .setDetails("Memory usage is consistently growing, check for memory leaks"));
        }
    }
}
```

### 磁盘I/O指标

磁盘I/O性能影响数据持久化和文件操作的效率。

```java
@Component
public class DiskIOMonitor {
    
    private final MeterRegistry meterRegistry;
    private final Gauge diskSpaceUsed;
    private final Gauge diskSpaceTotal;
    private final Counter diskReads;
    private final Counter diskWrites;
    
    public DiskIOMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        File root = new File("/");
        
        this.diskSpaceUsed = Gauge.builder("disk.space.used")
            .description("Used disk space")
            .tags("service", "user-service", "path", "/")
            .register(meterRegistry, root, 
                     file -> file.getTotalSpace() - file.getFreeSpace());
            
        this.diskSpaceTotal = Gauge.builder("disk.space.total")
            .description("Total disk space")
            .tags("service", "user-service", "path", "/")
            .register(meterRegistry, root, File::getTotalSpace);
            
        this.diskReads = Counter.builder("disk.reads")
            .description("Number of disk reads")
            .tags("service", "user-service")
            .register(meterRegistry);
            
        this.diskWrites = Counter.builder("disk.writes")
            .description("Number of disk writes")
            .tags("service", "user-service")
            .register(meterRegistry);
    }
    
    @Scheduled(fixedRate = 60000) // 每分钟检查一次
    public void checkDiskUsage() {
        double usageRatio = diskSpaceUsed.value() / diskSpaceTotal.value();
        
        // 如果磁盘使用率超过95%，触发告警
        if (usageRatio > 0.95) {
            alertService.sendAlert(new ResourceAlert()
                .setType("LOW_DISK_SPACE")
                .setSeverity(AlertSeverity.CRITICAL)
                .setMessage("Low disk space: " + (usageRatio * 100) + "% used")
                .setDetails("Disk space is critically low, immediate action required"));
        }
    }
    
    public void recordDiskRead() {
        diskReads.increment();
    }
    
    public void recordDiskWrite() {
        diskWrites.increment();
    }
}
```

## 微服务健康检查指标

### 存活检查指标

存活检查用于确定应用进程是否在运行。

```java
@RestController
public class LivenessProbeController {
    
    private final AtomicBoolean applicationRunning = new AtomicBoolean(true);
    
    @GetMapping("/health/live")
    public ResponseEntity<HealthStatus> livenessProbe() {
        if (applicationRunning.get()) {
            return ResponseEntity.ok(new HealthStatus("UP"));
        } else {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(new HealthStatus("DOWN"));
        }
    }
    
    // 模拟应用故障场景
    @PostMapping("/admin/stop")
    public ResponseEntity<String> stopApplication() {
        applicationRunning.set(false);
        return ResponseEntity.ok("Application stopped");
    }
}
```

### 就绪检查指标

就绪检查用于确定应用是否准备好接收流量。

```java
@RestController
public class ReadinessProbeController {
    
    @Autowired
    private DatabaseService databaseService;
    
    @Autowired
    private ExternalService externalService;
    
    @Autowired
    private CacheService cacheService;
    
    @GetMapping("/health/ready")
    public ResponseEntity<ReadinessStatus> readinessProbe() {
        List<ReadinessCheck> checks = new ArrayList<>();
        
        // 检查数据库连接
        ReadinessCheck dbCheck = new ReadinessCheck("database", databaseService.isHealthy());
        checks.add(dbCheck);
        
        // 检查外部服务依赖
        ReadinessCheck externalCheck = new ReadinessCheck("external-service", externalService.isHealthy());
        checks.add(externalCheck);
        
        // 检查缓存服务
        ReadinessCheck cacheCheck = new ReadinessCheck("cache", cacheService.isHealthy());
        checks.add(cacheCheck);
        
        // 如果所有检查都通过，应用就绪
        boolean isReady = checks.stream().allMatch(ReadinessCheck::isHealthy);
        
        ReadinessStatus status = new ReadinessStatus()
            .setReady(isReady)
            .setChecks(checks);
            
        if (isReady) {
            return ResponseEntity.ok(status);
        } else {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(status);
        }
    }
}
```

### 自定义健康检查

```java
@Component
public class CustomHealthIndicators {
    
    @Component
    public static class DatabaseHealthIndicator implements HealthIndicator {
        @Autowired
        private DataSource dataSource;
        
        @Override
        public HealthDetail checkHealth() {
            try {
                Connection connection = dataSource.getConnection();
                boolean isValid = connection.isValid(5);
                connection.close();
                
                if (isValid) {
                    return new HealthDetail(HealthStatus.UP, "Database connection is healthy")
                        .addDetail("responseTime", measureDatabaseResponseTime());
                } else {
                    return new HealthDetail(HealthStatus.DOWN, "Database connection is invalid");
                }
            } catch (SQLException e) {
                return new HealthDetail(HealthStatus.DOWN, 
                    "Database connection failed: " + e.getMessage());
            }
        }
        
        private long measureDatabaseResponseTime() {
            long startTime = System.currentTimeMillis();
            try {
                Connection connection = dataSource.getConnection();
                PreparedStatement stmt = connection.prepareStatement("SELECT 1");
                stmt.execute();
                connection.close();
            } catch (SQLException e) {
                // 忽略错误，只测量时间
            }
            return System.currentTimeMillis() - startTime;
        }
    }
    
    @Component
    public static class CacheHealthIndicator implements HealthIndicator {
        @Autowired
        private RedisTemplate<String, Object> redisTemplate;
        
        @Override
        public HealthDetail checkHealth() {
            try {
                String pingResult = redisTemplate.getConnectionFactory()
                    .getConnection().ping();
                
                if ("PONG".equals(pingResult)) {
                    return new HealthDetail(HealthStatus.UP, "Cache is healthy");
                } else {
                    return new HealthDetail(HealthStatus.DOWN, "Cache ping failed");
                }
            } catch (Exception e) {
                return new HealthDetail(HealthStatus.DOWN, 
                    "Cache connection failed: " + e.getMessage());
            }
        }
    }
}
```

## 用户体验指标

### 端到端响应时间

端到端响应时间反映了用户感受到的整体性能。

```java
@Component
public class EndToEndPerformanceMonitor {
    
    private final MeterRegistry meterRegistry;
    private final Timer endToEndTimer;
    
    public EndToEndPerformanceMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        this.endToEndTimer = Timer.builder("user.experience.endtoend.time")
            .description("End-to-end user experience time")
            .tags("service", "web-frontend")
            .publishPercentiles(0.5, 0.95, 0.99)
            .register(meterRegistry);
    }
    
    public void recordUserJourney(String journeyName, Duration duration) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            // 执行用户旅程
            executeUserJourney(journeyName);
            sample.stop(Timer.builder("user.journey.time")
                .tag("journey", journeyName)
                .register(meterRegistry));
        } finally {
            sample.stop(endToEndTimer);
        }
    }
    
    public UserExperienceMetrics getUserExperienceMetrics() {
        return new UserExperienceMetrics()
            .setAverageResponseTime(endToEndTimer.mean(TimeUnit.MILLISECONDS))
            .setP95ResponseTime(endToEndTimer.percentile(Percentile.of(95), TimeUnit.MILLISECONDS))
            .setP99ResponseTime(endToEndTimer.percentile(Percentile.of(99), TimeUnit.MILLISECONDS))
            .setTotalJourneys(endToEndTimer.count());
    }
}
```

### 用户满意度指标

```java
@Component
public class UserSatisfactionMonitor {
    
    private final MeterRegistry meterRegistry;
    private final DistributionSummary userSatisfactionScore;
    private final Counter positiveFeedback;
    private final Counter negativeFeedback;
    
    public UserSatisfactionMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        
        this.userSatisfactionScore = DistributionSummary.builder("user.satisfaction.score")
            .description("User satisfaction score distribution")
            .tags("service", "user-service")
            .register(meterRegistry);
            
        this.positiveFeedback = Counter.builder("user.feedback.positive")
            .description("Positive user feedback")
            .tags("service", "user-service")
            .register(meterRegistry);
            
        this.negativeFeedback = Counter.builder("user.feedback.negative")
            .description("Negative user feedback")
            .tags("service", "user-service")
            .register(meterRegistry);
    }
    
    public void recordUserSatisfaction(double score) {
        userSatisfactionScore.record(score);
        
        if (score >= 4.0) { // 假设5分制，4分以上为正面反馈
            positiveFeedback.increment();
        } else {
            negativeFeedback.increment();
        }
    }
    
    public UserSatisfactionMetrics getUserSatisfactionMetrics() {
        return new UserSatisfactionMetrics()
            .setAverageScore(userSatisfactionScore.mean())
            .setPositiveFeedbackCount(positiveFeedback.count())
            .setNegativeFeedbackCount(negativeFeedback.count())
            .setNetPromoterScore(calculateNPS())
            .setSatisfactionDistribution(calculateScoreDistribution());
    }
    
    private double calculateNPS() {
        long total = positiveFeedback.count() + negativeFeedback.count();
        if (total == 0) {
            return 0.0;
        }
        return ((double) positiveFeedback.count() / total) * 100;
    }
}
```

## 指标收集与聚合

### 指标收集策略

```java
@Component
public class MetricsCollectionStrategy {
    
    private final MeterRegistry meterRegistry;
    
    // 不同频率的指标收集
    @Scheduled(fixedRate = 1000) // 高频指标每秒收集
    public void collectHighFrequencyMetrics() {
        // 收集CPU、内存等高频变化的指标
        collectSystemMetrics();
    }
    
    @Scheduled(fixedRate = 10000) // 中频指标每10秒收集
    public void collectMediumFrequencyMetrics() {
        // 收集应用性能、错误率等中频变化的指标
        collectApplicationMetrics();
    }
    
    @Scheduled(fixedRate = 60000) // 低频指标每分钟收集
    public void collectLowFrequencyMetrics() {
        // 收集业务指标、用户满意度等低频变化的指标
        collectBusinessMetrics();
    }
    
    private void collectSystemMetrics() {
        // 收集系统级指标
        OperatingSystemMXBean osBean = ManagementFactory.getPlatformMXBean(OperatingSystemMXBean.class);
        
        Gauge.builder("system.cpu.usage")
            .register(meterRegistry, osBean, bean -> bean.getSystemCpuLoad() * 100);
            
        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        Gauge.builder("system.memory.used")
            .register(meterRegistry, memoryBean, 
                     bean -> bean.getHeapMemoryUsage().getUsed());
    }
}
```

### 指标聚合与分析

```java
@Component
public class MetricsAggregator {
    
    private final MeterRegistry meterRegistry;
    
    @Scheduled(fixedRate = 300000) // 每5分钟聚合一次
    public void aggregateMetrics() {
        // 聚合各服务的指标
        Map<String, ServiceMetrics> serviceMetrics = aggregateServiceMetrics();
        
        // 计算整体系统健康度
        SystemHealthScore healthScore = calculateSystemHealth(serviceMetrics);
        
        // 如果健康度低于阈值，触发告警
        if (healthScore.getScore() < 70) { // 健康度低于70分
            alertService.sendAlert(new SystemHealthAlert()
                .setType("SYSTEM_HEALTH_DEGRADATION")
                .setSeverity(AlertSeverity.WARNING)
                .setMessage("System health score is low: " + healthScore.getScore())
                .setDetails(objectMapper.writeValueAsString(healthScore)));
        }
        
        // 发布聚合指标
        publishAggregatedMetrics(serviceMetrics, healthScore);
    }
    
    private SystemHealthScore calculateSystemHealth(Map<String, ServiceMetrics> serviceMetrics) {
        double totalScore = 0;
        int serviceCount = serviceMetrics.size();
        
        for (ServiceMetrics metrics : serviceMetrics.values()) {
            // 基于各项指标计算服务健康度
            double serviceScore = calculateServiceHealth(metrics);
            totalScore += serviceScore;
        }
        
        return new SystemHealthScore()
            .setScore(serviceCount > 0 ? totalScore / serviceCount : 100)
            .setServiceMetrics(serviceMetrics);
    }
    
    private double calculateServiceHealth(ServiceMetrics metrics) {
        // 综合考虑响应时间、错误率、资源使用率等因素
        double responseTimeScore = calculateResponseTimeScore(metrics.getResponseTimeP95());
        double errorRateScore = calculateErrorRateScore(metrics.getErrorRate());
        double resourceScore = calculateResourceScore(metrics);
        
        // 加权计算
        return responseTimeScore * 0.4 + errorRateScore * 0.4 + resourceScore * 0.2;
    }
}
```

## 最佳实践

### 1. 指标命名规范

```java
public class MetricNamingConventions {
    
    // 推荐的命名格式：[domain].[subject].[metric]
    
    // 正确示例
    private static final String GOOD_EXAMPLES = """
        http.server.requests.duration
        jvm.memory.heap.used
        database.connection.pool.active
        user.authentication.success
        order.processing.time
        """;
    
    // 避免的命名方式
    private static final String BAD_EXAMPLES = """
        req_time          // 太简短，不清晰
        HTTP_Server_Requests_Duration  // 大小写混用
        user-auth-success  // 分隔符不一致
        """;
}
```

### 2. 标签使用策略

```java
@Component
public class TaggingStrategy {
    
    // 推荐的标签使用
    public void goodTaggingExample() {
        Timer.builder("http.server.requests")
            .tag("method", "GET")           // HTTP方法
            .tag("uri", "/api/users")       // 请求路径
            .tag("status", "200")           // 响应状态码
            .tag("service", "user-service") // 服务名称
            .tag("version", "1.2.3")        // 服务版本
            .tag("environment", "prod")     // 环境
            .register(meterRegistry);
    }
    
    // 避免高基数标签
    public void avoidHighCardinalityTags() {
        // 避免使用用户ID、订单ID等高基数字段作为标签
        // 错误示例：
        // .tag("user_id", userId)  // 每个用户都会创建新的时间序列
        
        // 正确示例：
        Counter.builder("user.login.attempts")
            .tag("result", "success")  // 使用有限的枚举值
            .register(meterRegistry);
    }
}
```

### 3. 指标生命周期管理

```java
@Component
public class MetricsLifecycleManager {
    
    private final Map<String, Meter> registeredMeters = new ConcurrentHashMap<>();
    
    public <T extends Meter> T registerMeter(String name, T meter) {
        registeredMeters.put(name, meter);
        return meter;
    }
    
    @PreDestroy
    public void cleanupMeters() {
        // 应用关闭时清理注册的指标
        for (Meter meter : registeredMeters.values()) {
            meterRegistry.remove(meter);
        }
        registeredMeters.clear();
    }
    
    @Scheduled(cron = "0 0 3 * * ?") // 每天凌晨3点执行
    public void pruneUnusedMeters() {
        // 定期清理长时间未使用的指标
        List<Meter> metersToRemove = new ArrayList<>();
        
        for (Map.Entry<String, Meter> entry : registeredMeters.entrySet()) {
            Meter meter = entry.getValue();
            if (shouldRemoveMeter(meter)) {
                metersToRemove.add(meter);
            }
        }
        
        for (Meter meter : metersToRemove) {
            meterRegistry.remove(meter);
        }
    }
}
```

## 总结

微服务监控的关键指标涵盖了从基础设施到用户体验的各个层面。通过建立全面的指标体系，我们可以实时了解系统状态，及时发现和解决问题，并为性能优化和容量规划提供数据支持。

在实际应用中，需要根据具体的业务需求和技术架构选择合适的指标，并建立相应的收集、聚合和分析机制。同时，要注意指标的命名规范、标签使用策略和生命周期管理，确保监控系统的可维护性和可扩展性。

在下一章中，我们将探讨监控工具与技术栈，包括Prometheus、Grafana、OpenTelemetry等主流工具的使用方法和最佳实践。