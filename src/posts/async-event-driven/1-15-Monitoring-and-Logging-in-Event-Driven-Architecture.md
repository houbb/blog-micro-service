---
title: 事件驱动架构的监控与日志
date: 2025-08-31
categories: [Write]
tags: [write]
published: true
---

在复杂的事件驱动架构中，监控和日志系统是确保系统稳定性和可维护性的关键组成部分。由于事件驱动系统具有高度的分布式和异步特性，传统的监控和日志方法往往难以满足需求。本文将深入探讨事件流的监控与追踪、分布式追踪与调试工具、消息队列与事件源的健康检查，以及异常检测与故障预警等关键监控和日志主题。

## 事件流的监控与追踪

### 分布式追踪基础

分布式追踪是监控事件驱动架构的核心技术，它能够追踪事件在整个系统中的流转过程。

```java
// 分布式追踪上下文
public class TraceContext {
    private final String traceId;
    private final String spanId;
    private final String parentSpanId;
    private final Map<String, String> baggage;
    
    private TraceContext(Builder builder) {
        this.traceId = builder.traceId;
        this.spanId = builder.spanId;
        this.parentSpanId = builder.parentSpanId;
        this.baggage = Collections.unmodifiableMap(new HashMap<>(builder.baggage));
    }
    
    public static class Builder {
        private String traceId;
        private String spanId;
        private String parentSpanId;
        private Map<String, String> baggage = new HashMap<>();
        
        public Builder traceId(String traceId) {
            this.traceId = traceId;
            return this;
        }
        
        public Builder spanId(String spanId) {
            this.spanId = spanId;
            return this;
        }
        
        public Builder parentSpanId(String parentSpanId) {
            this.parentSpanId = parentSpanId;
            return this;
        }
        
        public Builder addBaggage(String key, String value) {
            this.baggage.put(key, value);
            return this;
        }
        
        public TraceContext build() {
            return new TraceContext(this);
        }
    }
    
    // getter方法
}

// 追踪跨度
public class Span {
    private final String traceId;
    private final String spanId;
    private final String operationName;
    private final long startTime;
    private long endTime;
    private final List<Tag> tags;
    private final List<LogEntry> logs;
    private SpanStatus status = SpanStatus.UNSET;
    
    public Span(String traceId, String spanId, String operationName) {
        this.traceId = traceId;
        this.spanId = spanId;
        this.operationName = operationName;
        this.startTime = System.currentTimeMillis();
        this.tags = new ArrayList<>();
        this.logs = new ArrayList<>();
    }
    
    public void addTag(String key, String value) {
        tags.add(new Tag(key, value));
    }
    
    public void log(String message) {
        logs.add(new LogEntry(System.currentTimeMillis(), message));
    }
    
    public void setStatus(SpanStatus status) {
        this.status = status;
    }
    
    public void end() {
        this.endTime = System.currentTimeMillis();
        // 发送到追踪系统
        TracingSystem.getInstance().reportSpan(this);
    }
}

// 追踪系统实现
public class TracingSystem {
    private static final TracingSystem INSTANCE = new TracingSystem();
    private final Queue<Span> spanQueue = new ConcurrentLinkedQueue<>();
    private final ScheduledExecutorService reporter = Executors.newScheduledThreadPool(1);
    
    private TracingSystem() {
        // 定期上报追踪数据
        reporter.scheduleAtFixedRate(this::reportSpans, 1, 1, TimeUnit.SECONDS);
    }
    
    public static TracingSystem getInstance() {
        return INSTANCE;
    }
    
    public Span createSpan(String operationName, TraceContext parentContext) {
        String traceId = parentContext != null ? parentContext.getTraceId() : generateTraceId();
        String spanId = generateSpanId();
        String parentSpanId = parentContext != null ? parentContext.getSpanId() : null;
        
        Span span = new Span(traceId, spanId, operationName);
        if (parentContext != null) {
            span.addTag("parent_span_id", parentSpanId);
        }
        
        return span;
    }
    
    public void reportSpan(Span span) {
        spanQueue.offer(span);
    }
    
    private void reportSpans() {
        List<Span> spans = new ArrayList<>();
        Span span;
        while ((span = spanQueue.poll()) != null) {
            spans.add(span);
        }
        
        if (!spans.isEmpty()) {
            // 批量上报到追踪系统（如Jaeger、Zipkin等）
            sendToTracingBackend(spans);
        }
    }
    
    private void sendToTracingBackend(List<Span> spans) {
        // 实际的上报逻辑
        // 这里可以集成具体的追踪系统
    }
}
```

### 事件流追踪实现

```java
// 事件流追踪装饰器
@Component
public class EventStreamTracer {
    public <T extends Event> T traceEvent(T event, String operationName) {
        // 创建新的追踪上下文或继承现有上下文
        TraceContext traceContext = extractTraceContext(event);
        if (traceContext == null) {
            traceContext = new TraceContext.Builder()
                .traceId(generateTraceId())
                .spanId(generateSpanId())
                .build();
        }
        
        // 创建新的跨度
        Span span = TracingSystem.getInstance().createSpan(operationName, traceContext);
        span.addTag("event_type", event.getClass().getSimpleName());
        span.addTag("event_id", event.getEventId());
        
        // 将追踪信息注入事件
        T tracedEvent = injectTraceContext(event, traceContext, span.getSpanId());
        
        // 记录事件开始
        span.log("Event processing started");
        
        return tracedEvent;
    }
    
    public void endEventTrace(Event event, Span span, Throwable error) {
        if (error != null) {
            span.setStatus(SpanStatus.ERROR);
            span.addTag("error", error.getClass().getSimpleName());
            span.addTag("error_message", error.getMessage());
            span.log("Event processing failed: " + error.getMessage());
        } else {
            span.setStatus(SpanStatus.OK);
            span.log("Event processing completed");
        }
        
        span.end();
    }
    
    private TraceContext extractTraceContext(Event event) {
        // 从事件中提取追踪上下文
        if (event instanceof TracedEvent) {
            return ((TracedEvent) event).getTraceContext();
        }
        return null;
    }
    
    private <T extends Event> T injectTraceContext(T event, TraceContext context, String spanId) {
        // 将追踪上下文注入事件
        if (event instanceof MutableTracedEvent) {
            ((MutableTracedEvent) event).setTraceContext(context);
            ((MutableTracedEvent) event).setSpanId(spanId);
            return event;
        }
        // 如果事件不可变，创建新的追踪事件
        return (T) new TracedEventWrapper(event, context, spanId);
    }
}

// 带追踪的事件处理器
@Component
public class TracedEventHandler {
    private final EventStreamTracer tracer;
    
    @EventListener
    public void handleEvent(Event event) {
        String operationName = "handle_" + event.getClass().getSimpleName();
        Event tracedEvent = tracer.traceEvent(event, operationName);
        Span span = getCurrentSpan(); // 获取当前跨度
        
        try {
            // 处理事件
            processEvent(tracedEvent);
            
            // 结束追踪
            tracer.endEventTrace(tracedEvent, span, null);
        } catch (Exception e) {
            // 记录错误并结束追踪
            tracer.endEventTrace(tracedEvent, span, e);
            throw e;
        }
    }
    
    private void processEvent(Event event) {
        // 实际的事件处理逻辑
        if (event instanceof OrderCreatedEvent) {
            handleOrderCreated((OrderCreatedEvent) event);
        } else if (event instanceof PaymentProcessedEvent) {
            handlePaymentProcessed((PaymentProcessedEvent) event);
        }
    }
}
```

## 分布式追踪与调试工具

### OpenTelemetry集成

```java
// OpenTelemetry配置
@Configuration
public class OpenTelemetryConfiguration {
    @Bean
    public OpenTelemetry openTelemetry(
            @Value("${otel.service.name}") String serviceName,
            @Value("${otel.exporter.otlp.endpoint}") String endpoint) {
        
        Resource resource = Resource.getDefault()
            .merge(Resource.create(Attributes.of(ResourceAttributes.SERVICE_NAME, serviceName)));
        
        SdkTracerProvider sdkTracerProvider = SdkTracerProvider.builder()
            .addSpanProcessor(BatchSpanProcessor.builder(OtlpGrpcSpanExporter.builder()
                .setEndpoint(endpoint)
                .build()).build())
            .setResource(resource)
            .build();
        
        OpenTelemetrySdk openTelemetry = OpenTelemetrySdk.builder()
            .setTracerProvider(sdkTracerProvider)
            .setPropagators(ContextPropagators.create(W3CTraceContextPropagator.getInstance()))
            .buildAndRegisterGlobal();
        
        return openTelemetry;
    }
    
    @Bean
    public Tracer tracer(OpenTelemetry openTelemetry) {
        return openTelemetry.getTracer("event-driven-system");
    }
}

// 使用OpenTelemetry的事件处理器
@Component
public class OpenTelemetryEventHandler {
    private final Tracer tracer;
    private final Meter meter;
    
    public OpenTelemetryEventHandler(OpenTelemetry openTelemetry) {
        this.tracer = openTelemetry.getTracer("event-handler");
        this.meter = openTelemetry.getMeter("event-handler");
    }
    
    @EventListener
    public void handleEvent(Event event) {
        // 创建跨度
        Span span = tracer.spanBuilder("process_event")
            .setAttribute("event.type", event.getClass().getSimpleName())
            .setAttribute("event.id", event.getEventId())
            .startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            // 记录指标
            Counter eventCounter = meter.counterBuilder("events.processed")
                .setDescription("Number of events processed")
                .setUnit("events")
                .build();
            
            eventCounter.add(1, Attributes.of(
                AttributeKey.stringKey("event_type"), 
                event.getClass().getSimpleName()
            ));
            
            // 处理事件
            processEvent(event);
            
            span.setStatus(StatusCode.OK);
        } catch (Exception e) {
            span.setStatus(StatusCode.ERROR, e.getMessage());
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
}
```

### 调试工具实现

```java
// 事件流调试器
@Component
public class EventStreamDebugger {
    private final Map<String, List<EventTrace>> eventTraces = new ConcurrentHashMap<>();
    private final int maxTraceHistory = 1000;
    
    public void traceEventFlow(Event event, String component, String action) {
        String traceId = getTraceId(event);
        if (traceId != null) {
            EventTrace trace = new EventTrace(
                System.currentTimeMillis(),
                traceId,
                event.getEventId(),
                event.getClass().getSimpleName(),
                component,
                action
            );
            
            eventTraces.computeIfAbsent(traceId, k -> new ArrayList<>()).add(trace);
            
            // 限制历史记录大小
            List<EventTrace> traces = eventTraces.get(traceId);
            if (traces.size() > maxTraceHistory) {
                synchronized (traces) {
                    if (traces.size() > maxTraceHistory) {
                        traces.subList(0, traces.size() - maxTraceHistory).clear();
                    }
                }
            }
        }
    }
    
    public List<EventTrace> getEventFlow(String traceId) {
        return new ArrayList<>(eventTraces.getOrDefault(traceId, new ArrayList<>()));
    }
    
    public void dumpEventFlow(String traceId) {
        List<EventTrace> traces = getEventFlow(traceId);
        if (!traces.isEmpty()) {
            log.info("Event flow for trace {}: ", traceId);
            traces.forEach(trace -> log.info("  {}", trace));
        }
    }
    
    // 调试端点
    @RestController
    @RequestMapping("/debug")
    public class DebugController {
        @Autowired
        private EventStreamDebugger debugger;
        
        @GetMapping("/event-flow/{traceId}")
        public ResponseEntity<List<EventTrace>> getEventFlow(@PathVariable String traceId) {
            List<EventTrace> traces = debugger.getEventFlow(traceId);
            return ResponseEntity.ok(traces);
        }
        
        @PostMapping("/dump-event-flow/{traceId}")
        public ResponseEntity<String> dumpEventFlow(@PathVariable String traceId) {
            debugger.dumpEventFlow(traceId);
            return ResponseEntity.ok("Event flow dumped to logs");
        }
    }
}

// 事件追踪记录
public class EventTrace {
    private final long timestamp;
    private final String traceId;
    private final String eventId;
    private final String eventType;
    private final String component;
    private final String action;
    
    // 构造函数和toString方法
    @Override
    public String toString() {
        return String.format("%tT.%tL [%s] %s.%s - %s (%s)", 
            timestamp, timestamp, traceId, component, action, eventType, eventId);
    }
}
```

## 消息队列与事件源的健康检查

### 消息队列健康检查

```java
// 消息队列健康检查器
@Component
public class MessageQueueHealthChecker {
    private final RabbitTemplate rabbitTemplate;
    private final MeterRegistry meterRegistry;
    
    @Scheduled(fixedRate = 30000) // 每30秒检查一次
    public void checkQueueHealth() {
        try {
            // 检查连接状态
            boolean connectionHealthy = checkConnection();
            Gauge.builder("rabbitmq.connection.healthy")
                .register(meterRegistry, this, self -> connectionHealthy ? 1.0 : 0.0);
            
            if (!connectionHealthy) {
                log.warn("RabbitMQ connection is unhealthy");
                return;
            }
            
            // 检查队列状态
            List<QueueInfo> queues = getQueueInformation();
            for (QueueInfo queue : queues) {
                checkQueueHealth(queue);
            }
            
        } catch (Exception e) {
            log.error("Failed to check message queue health", e);
            Gauge.builder("rabbitmq.connection.healthy")
                .register(meterRegistry, this, self -> 0.0);
        }
    }
    
    private boolean checkConnection() {
        try {
            return rabbitTemplate.execute(channel -> {
                channel.getConnection().isOpen();
                return true;
            });
        } catch (Exception e) {
            return false;
        }
    }
    
    private void checkQueueHealth(QueueInfo queue) {
        String queueName = queue.getName();
        
        // 监控队列消息数量
        Gauge.builder("queue.message.count")
            .tag("queue", queueName)
            .register(meterRegistry, queue, QueueInfo::getMessageCount);
        
        // 监控消费者数量
        Gauge.builder("queue.consumer.count")
            .tag("queue", queueName)
            .register(meterRegistry, queue, QueueInfo::getConsumerCount);
        
        // 监控未确认消息
        Gauge.builder("queue.unacked.count")
            .tag("queue", queueName)
            .register(meterRegistry, queue, QueueInfo::getUnackedMessageCount);
        
        // 检查队列是否健康
        boolean isHealthy = isQueueHealthy(queue);
        Gauge.builder("queue.healthy")
            .tag("queue", queueName)
            .register(meterRegistry, this, self -> isHealthy ? 1.0 : 0.0);
        
        if (!isHealthy) {
            log.warn("Queue {} is unhealthy: messageCount={}, consumerCount={}", 
                    queueName, queue.getMessageCount(), queue.getConsumerCount());
            
            // 触发告警
            alertService.sendAlert("Queue Unhealthy", 
                "Queue " + queueName + " is unhealthy");
        }
    }
    
    private boolean isQueueHealthy(QueueInfo queue) {
        // 队列健康的判断标准
        return queue.getMessageCount() < MAX_MESSAGE_BACKLOG &&
               queue.getConsumerCount() > 0 &&
               queue.getUnackedMessageCount() < MAX_UNACKED_MESSAGES;
    }
}

// 队列信息收集器
@Component
public class QueueInfoCollector {
    private final RabbitAdmin rabbitAdmin;
    private final Map<String, QueueMetrics> queueMetrics = new ConcurrentHashMap<>();
    
    @Scheduled(fixedRate = 10000) // 每10秒收集一次
    public void collectQueueMetrics() {
        try {
            List<QueueInfo> queues = getQueueInformation();
            for (QueueInfo queue : queues) {
                updateQueueMetrics(queue);
            }
        } catch (Exception e) {
            log.error("Failed to collect queue metrics", e);
        }
    }
    
    private void updateQueueMetrics(QueueInfo queue) {
        QueueMetrics metrics = queueMetrics.computeIfAbsent(
            queue.getName(), 
            name -> new QueueMetrics(name)
        );
        
        metrics.update(
            queue.getMessageCount(),
            queue.getConsumerCount(),
            queue.getUnackedMessageCount(),
            queue.getAverageProcessingTime()
        );
    }
    
    private List<QueueInfo> getQueueInformation() {
        List<QueueInfo> queues = new ArrayList<>();
        
        // 获取所有队列名称
        Properties queueNames = rabbitAdmin.getQueues();
        for (Object queueNameObj : queueNames.keySet()) {
            String queueName = (String) queueNameObj;
            
            // 获取队列详细信息
            QueueInformation queueInfo = rabbitAdmin.getQueueInfo(queueName);
            if (queueInfo != null) {
                QueueInfo info = new QueueInfo(
                    queueName,
                    (int) queueInfo.getMessageCount(),
                    (int) queueInfo.getConsumerCount(),
                    (int) queueInfo.getUnacknowledgedMessageCount(),
                    calculateAverageProcessingTime(queueName)
                );
                queues.add(info);
            }
        }
        
        return queues;
    }
    
    private long calculateAverageProcessingTime(String queueName) {
        // 计算平均处理时间的逻辑
        // 这里可以基于历史数据或实时监控数据计算
        return 0L;
    }
}
```

### 事件源健康检查

```java
// 事件源健康检查器
@Component
public class EventStoreHealthChecker {
    private final EventStore eventStore;
    private final MeterRegistry meterRegistry;
    
    @Scheduled(fixedRate = 30000) // 每30秒检查一次
    public void checkEventStoreHealth() {
        try {
            // 检查事件存储连接
            boolean connectionHealthy = checkEventStoreConnection();
            Gauge.builder("eventstore.connection.healthy")
                .register(meterRegistry, this, self -> connectionHealthy ? 1.0 : 0.0);
            
            if (!connectionHealthy) {
                log.warn("Event store connection is unhealthy");
                return;
            }
            
            // 检查事件存储性能
            checkEventStorePerformance();
            
            // 检查事件一致性
            checkEventConsistency();
            
        } catch (Exception e) {
            log.error("Failed to check event store health", e);
            Gauge.builder("eventstore.connection.healthy")
                .register(meterRegistry, this, self -> 0.0);
        }
    }
    
    private boolean checkEventStoreConnection() {
        try {
            // 执行简单的读操作来检查连接
            eventStore.ping();
            return true;
        } catch (Exception e) {
            return false;
        }
    }
    
    private void checkEventStorePerformance() {
        long startTime = System.nanoTime();
        try {
            // 执行性能测试查询
            eventStore.getEvents("health-check", 0, 10);
            
            long endTime = System.nanoTime();
            long duration = endTime - startTime;
            
            Timer.builder("eventstore.query.duration")
                .register(meterRegistry)
                .record(duration, TimeUnit.NANOSECONDS);
                
        } catch (Exception e) {
            log.error("Event store performance check failed", e);
        }
    }
    
    private void checkEventConsistency() {
        try {
            // 检查事件序列的一致性
            List<String> aggregateIds = eventStore.getAggregateIds();
            
            for (String aggregateId : aggregateIds) {
                List<Event> events = eventStore.getEvents(aggregateId, 0);
                if (!isEventSequenceConsistent(events)) {
                    log.warn("Event sequence inconsistency detected for aggregate: {}", aggregateId);
                    Counter.builder("eventstore.inconsistencies")
                        .register(meterRegistry)
                        .increment();
                }
            }
        } catch (Exception e) {
            log.error("Event consistency check failed", e);
        }
    }
    
    private boolean isEventSequenceConsistent(List<Event> events) {
        // 检查事件版本号是否连续
        for (int i = 1; i < events.size(); i++) {
            if (events.get(i).getVersion() != events.get(i-1).getVersion() + 1) {
                return false;
            }
        }
        return true;
    }
}
```

## 异常检测与故障预警

### 异常检测系统

```java
// 异常检测器
@Component
public class AnomalyDetector {
    private final MeterRegistry meterRegistry;
    private final AlertService alertService;
    private final Map<String, TimeSeriesData> metricsHistory = new ConcurrentHashMap<>();
    
    @Scheduled(fixedRate = 60000) // 每分钟检测一次
    public void detectAnomalies() {
        // 收集指标数据
        collectMetrics();
        
        // 检测异常
        detectMetricAnomalies();
        
        // 检测事件流异常
        detectEventFlowAnomalies();
    }
    
    private void collectMetrics() {
        // 收集各种指标数据
        collectQueueMetrics();
        collectProcessingMetrics();
        collectErrorMetrics();
    }
    
    private void detectMetricAnomalies() {
        metricsHistory.forEach((metricName, timeSeries) -> {
            if (timeSeries.hasEnoughData()) {
                double currentValue = timeSeries.getLatestValue();
                double average = timeSeries.getAverage();
                double stdDev = timeSeries.getStandardDeviation();
                
                // 使用3西格玛规则检测异常
                if (Math.abs(currentValue - average) > 3 * stdDev) {
                    log.warn("Anomaly detected in metric {}: current={}, average={}, stdDev={}", 
                            metricName, currentValue, average, stdDev);
                    
                    // 发送告警
                    alertService.sendAlert("Metric Anomaly", 
                        String.format("Anomaly detected in %s: %f (avg: %f, std: %f)", 
                                    metricName, currentValue, average, stdDev));
                }
            }
        });
    }
    
    private void detectEventFlowAnomalies() {
        // 检测事件流异常
        List<EventFlowPattern> normalPatterns = getNormalEventFlowPatterns();
        List<EventFlow> currentFlows = getCurrentEventFlows();
        
        for (EventFlow flow : currentFlows) {
            if (!isNormalEventFlow(flow, normalPatterns)) {
                log.warn("Abnormal event flow detected: {}", flow);
                
                // 发送告警
                alertService.sendAlert("Event Flow Anomaly", 
                    "Abnormal event flow detected: " + flow.toString());
            }
        }
    }
    
    private boolean isNormalEventFlow(EventFlow flow, List<EventFlowPattern> patterns) {
        // 检查事件流是否符合正常模式
        for (EventFlowPattern pattern : patterns) {
            if (pattern.matches(flow)) {
                return true;
            }
        }
        return false;
    }
}

// 时间序列数据
public class TimeSeriesData {
    private final String metricName;
    private final Queue<DataPoint> dataPoints = new LinkedList<>();
    private final int maxSize = 1000;
    
    public void addDataPoint(double value) {
        dataPoints.offer(new DataPoint(System.currentTimeMillis(), value));
        
        // 保持队列大小
        if (dataPoints.size() > maxSize) {
            dataPoints.poll();
        }
    }
    
    public double getLatestValue() {
        return dataPoints.isEmpty() ? 0.0 : dataPoints.peek().getValue();
    }
    
    public double getAverage() {
        return dataPoints.stream()
            .mapToDouble(DataPoint::getValue)
            .average()
            .orElse(0.0);
    }
    
    public double getStandardDeviation() {
        double average = getAverage();
        double variance = dataPoints.stream()
            .mapToDouble(dp -> Math.pow(dp.getValue() - average, 2))
            .average()
            .orElse(0.0);
        return Math.sqrt(variance);
    }
    
    public boolean hasEnoughData() {
        return dataPoints.size() >= 10;
    }
}

// 数据点
public class DataPoint {
    private final long timestamp;
    private final double value;
    
    // 构造函数和getter方法
}
```

### 智能告警系统

```java
// 智能告警系统
@Component
public class IntelligentAlertingSystem {
    private final Map<String, AlertRule> alertRules = new ConcurrentHashMap<>();
    private final Map<String, AlertSuppression> alertSuppressions = new ConcurrentHashMap<>();
    private final NotificationService notificationService;
    
    public void registerAlertRule(AlertRule rule) {
        alertRules.put(rule.getId(), rule);
    }
    
    public void processMetric(String metricName, double value) {
        // 检查是否有匹配的告警规则
        alertRules.values().stream()
            .filter(rule -> rule.getMetricName().equals(metricName))
            .forEach(rule -> evaluateAlertRule(rule, value));
    }
    
    private void evaluateAlertRule(AlertRule rule, double value) {
        if (rule.isTriggered(value)) {
            // 检查是否需要抑制告警
            if (!shouldSuppressAlert(rule.getId())) {
                // 触发告警
                triggerAlert(rule, value);
                
                // 设置告警抑制
                if (rule.getSuppressionDuration() > 0) {
                    suppressAlert(rule.getId(), rule.getSuppressionDuration());
                }
            }
        }
    }
    
    private void triggerAlert(AlertRule rule, double value) {
        Alert alert = new Alert(
            UUID.randomUUID().toString(),
            rule.getId(),
            rule.getName(),
            rule.getSeverity(),
            String.format("Metric %s value %f exceeds threshold %f", 
                         rule.getMetricName(), value, rule.getThreshold()),
            System.currentTimeMillis()
        );
        
        // 发送告警
        notificationService.sendNotification(alert);
        
        // 记录告警
        logAlert(alert);
    }
    
    private boolean shouldSuppressAlert(String ruleId) {
        AlertSuppression suppression = alertSuppressions.get(ruleId);
        if (suppression != null) {
            return suppression.isSuppressed();
        }
        return false;
    }
    
    private void suppressAlert(String ruleId, long duration) {
        alertSuppressions.put(ruleId, 
            new AlertSuppression(System.currentTimeMillis() + duration));
    }
    
    // 告警规则定义
    public class AlertRule {
        private final String id;
        private final String name;
        private final String metricName;
        private final double threshold;
        private final AlertSeverity severity;
        private final long suppressionDuration;
        private final AlertCondition condition;
        
        // 构造函数和getter方法
    }
    
    // 告警条件接口
    public interface AlertCondition {
        boolean isMet(double currentValue, double threshold);
    }
    
    // 告警抑制
    public class AlertSuppression {
        private final long suppressionEndTime;
        
        public AlertSuppression(long suppressionEndTime) {
            this.suppressionEndTime = suppressionEndTime;
        }
        
        public boolean isSuppressed() {
            return System.currentTimeMillis() < suppressionEndTime;
        }
    }
}

// 告警通知服务
@Service
public class NotificationService {
    private final List<NotificationChannel> channels = new ArrayList<>();
    
    public void sendNotification(Alert alert) {
        // 并行发送到所有通知渠道
        channels.parallelStream().forEach(channel -> {
            try {
                channel.send(alert);
            } catch (Exception e) {
                log.error("Failed to send alert to channel: {}", channel.getName(), e);
            }
        });
    }
    
    // 邮件通知渠道
    public class EmailNotificationChannel implements NotificationChannel {
        private final EmailService emailService;
        
        @Override
        public void send(Alert alert) {
            String subject = String.format("[%s] %s", 
                                         alert.getSeverity(), alert.getRuleName());
            String body = String.format(
                "Alert: %s\nSeverity: %s\nTime: %tF %tT\nMessage: %s",
                alert.getRuleName(), alert.getSeverity(), 
                alert.getTimestamp(), alert.getTimestamp(), alert.getMessage()
            );
            
            emailService.sendEmail("alerts@company.com", subject, body);
        }
    }
    
    // Slack通知渠道
    public class SlackNotificationChannel implements NotificationChannel {
        private final SlackService slackService;
        
        @Override
        public void send(Alert alert) {
            String message = String.format(
                "*%s* %s\n%s\n_%tF %tT_",
                alert.getSeverity(), alert.getRuleName(), 
                alert.getMessage(), alert.getTimestamp(), alert.getTimestamp()
            );
            
            slackService.postMessage("#alerts", message);
        }
    }
}
```

### 故障预测和预防

```java
// 故障预测系统
@Component
public class FailurePredictionSystem {
    private final MachineLearningModel failurePredictionModel;
    private final MeterRegistry meterRegistry;
    
    @Scheduled(fixedRate = 300000) // 每5分钟预测一次
    public void predictFailures() {
        try {
            // 收集特征数据
            FeatureVector features = collectFeatures();
            
            // 预测故障概率
            double failureProbability = failurePredictionModel.predict(features);
            
            // 记录预测结果
            Gauge.builder("system.failure.probability")
                .register(meterRegistry, this, self -> failureProbability);
            
            // 如果故障概率高，触发预防措施
            if (failureProbability > FAILURE_THRESHOLD) {
                log.warn("High failure probability detected: {}", failureProbability);
                triggerPreventiveActions(failureProbability);
            }
            
        } catch (Exception e) {
            log.error("Failure prediction failed", e);
        }
    }
    
    private FeatureVector collectFeatures() {
        // 收集系统特征数据
        return new FeatureVector.Builder()
            .addFeature("cpu_usage", getSystemCpuUsage())
            .addFeature("memory_usage", getMemoryUsage())
            .addFeature("disk_usage", getDiskUsage())
            .addFeature("queue_backlog", getTotalQueueBacklog())
            .addFeature("error_rate", getErrorRate())
            .addFeature("processing_latency", getAverageProcessingLatency())
            .build();
    }
    
    private void triggerPreventiveActions(double failureProbability) {
        // 根据故障概率触发不同的预防措施
        if (failureProbability > CRITICAL_THRESHOLD) {
            // 关键预防措施
            scaleOutResources();
            enableCircuitBreakers();
            increaseRetryAttempts();
        } else if (failureProbability > WARNING_THRESHOLD) {
            // 警告预防措施
            preloadResources();
            optimizeQueueConfiguration();
            sendEarlyWarning();
        }
    }
    
    private void scaleOutResources() {
        // 自动扩展资源
        autoScaler.scaleOutAllServices();
    }
    
    private void enableCircuitBreakers() {
        // 启用熔断器
        circuitBreakerManager.enableAllCircuitBreakers();
    }
    
    private void sendEarlyWarning() {
        // 发送早期预警
        alertService.sendAlert("Early Warning", 
            "System failure predicted, taking preventive actions");
    }
}

// 特征向量
public class FeatureVector {
    private final Map<String, Double> features;
    
    private FeatureVector(Builder builder) {
        this.features = Collections.unmodifiableMap(new HashMap<>(builder.features));
    }
    
    public static class Builder {
        private final Map<String, Double> features = new HashMap<>();
        
        public Builder addFeature(String name, double value) {
            features.put(name, value);
            return this;
        }
        
        public FeatureVector build() {
            return new FeatureVector(this);
        }
    }
    
    public double getFeature(String name) {
        return features.getOrDefault(name, 0.0);
    }
    
    public Set<String> getFeatureNames() {
        return features.keySet();
    }
}
```

## 总结

事件驱动架构的监控与日志系统是确保系统稳定性和可维护性的关键。通过实施分布式追踪、健康检查、异常检测和智能告警等机制，可以有效监控系统的运行状态，及时发现和处理潜在问题。

在实际应用中，需要根据具体的业务需求和技术栈选择合适的监控工具和框架，并建立完善的监控指标体系和告警策略。随着系统复杂性的增加，监控和日志系统也需要不断优化和完善，以适应不断变化的业务需求和技术环境。

通过持续的监控和优化，可以确保事件驱动架构系统在高并发、高可用的环境下稳定运行，为业务提供可靠的技术支撑。