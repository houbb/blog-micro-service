---
title: 附录B：事件驱动架构设计模板与示例
date: 2025-08-31
categories: [Write]
tags: [write]
published: true
---

事件驱动架构（Event-Driven Architecture, EDA）的设计和实现需要遵循一定的模式和最佳实践。为了帮助开发者更好地理解和应用EDA，本附录提供了详细的设计模板和实际示例，涵盖从基础概念到高级应用的各个方面。

## 基础设计模板

### 事件定义模板

```java
// 事件基类模板
public abstract class DomainEvent {
    private final String eventId;
    private final long timestamp;
    private final String aggregateId;
    private final int version;
    
    protected DomainEvent(String aggregateId) {
        this.eventId = UUID.randomUUID().toString();
        this.timestamp = System.currentTimeMillis();
        this.aggregateId = aggregateId;
        this.version = 1;
    }
    
    // getter方法
    public String getEventId() { return eventId; }
    public long getTimestamp() { return timestamp; }
    public String getAggregateId() { return aggregateId; }
    public int getVersion() { return version; }
    
    // 事件类型
    public abstract String getType();
}

// 具体事件模板
public class OrderCreatedEvent extends DomainEvent {
    private final String customerId;
    private final List<OrderItem> items;
    private final BigDecimal totalAmount;
    
    public OrderCreatedEvent(String orderId, String customerId, List<OrderItem> items) {
        super(orderId);
        this.customerId = customerId;
        this.items = Collections.unmodifiableList(new ArrayList<>(items));
        this.totalAmount = calculateTotalAmount(items);
    }
    
    private BigDecimal calculateTotalAmount(List<OrderItem> items) {
        return items.stream()
            .map(item -> item.getPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
    
    @Override
    public String getType() {
        return "OrderCreated";
    }
    
    // getter方法
    public String getCustomerId() { return customerId; }
    public List<OrderItem> getItems() { return items; }
    public BigDecimal getTotalAmount() { return totalAmount; }
}
```

### 聚合根模板

```java
// 聚合根基类模板
public abstract class AggregateRoot {
    protected String id;
    protected long version = 0;
    protected List<Event> uncommittedEvents = new ArrayList<>();
    
    public String getId() {
        return id;
    }
    
    public long getVersion() {
        return version;
    }
    
    public List<Event> getUncommittedEvents() {
        return new ArrayList<>(uncommittedEvents);
    }
    
    public void clearUncommittedEvents() {
        uncommittedEvents.clear();
    }
    
    protected void apply(Event event) {
        mutate(event);
        uncommittedEvents.add(event);
        version++;
    }
    
    protected abstract void mutate(Event event);
}

// 具体聚合根模板
public class Order extends AggregateRoot {
    private String customerId;
    private List<OrderItem> items;
    private OrderStatus status;
    
    private Order() {
        // 私有构造函数，只能通过工厂方法创建
    }
    
    public static Order create(String id, String customerId, List<OrderItem> items) {
        Order order = new Order();
        order.id = id;
        OrderCreatedEvent event = new OrderCreatedEvent(id, customerId, items);
        order.apply(event);
        return order;
    }
    
    public void pay() {
        if (status != OrderStatus.CREATED) {
            throw new IllegalStateException("Order must be created to be paid");
        }
        OrderPaidEvent event = new OrderPaidEvent(id);
        apply(event);
    }
    
    public void cancel() {
        if (status == OrderStatus.SHIPPED || status == OrderStatus.DELIVERED) {
            throw new IllegalStateException("Cannot cancel shipped or delivered order");
        }
        OrderCancelledEvent event = new OrderCancelledEvent(id);
        apply(event);
    }
    
    @Override
    protected void mutate(Event event) {
        if (event instanceof OrderCreatedEvent) {
            OrderCreatedEvent created = (OrderCreatedEvent) event;
            this.customerId = created.getCustomerId();
            this.items = created.getItems();
            this.status = OrderStatus.CREATED;
        } else if (event instanceof OrderPaidEvent) {
            this.status = OrderStatus.PAID;
        } else if (event instanceof OrderCancelledEvent) {
            this.status = OrderStatus.CANCELLED;
        }
    }
    
    // getter方法
    public String getCustomerId() { return customerId; }
    public List<OrderItem> getItems() { return items; }
    public OrderStatus getStatus() { return status; }
}
```

### 事件处理器模板

```java
// 事件处理器基类模板
@Component
public abstract class EventHandler<T extends Event> {
    private final Class<T> eventType;
    
    protected EventHandler(Class<T> eventType) {
        this.eventType = eventType;
    }
    
    public boolean supports(Event event) {
        return eventType.isInstance(event);
    }
    
    public void handle(Event event) {
        if (supports(event)) {
            handleEvent(eventType.cast(event));
        }
    }
    
    protected abstract void handleEvent(T event);
}

// 具体事件处理器模板
@Component
public class OrderCreatedEventHandler extends EventHandler<OrderCreatedEvent> {
    private final InventoryService inventoryService;
    private final PaymentService paymentService;
    private final NotificationService notificationService;
    
    public OrderCreatedEventHandler(InventoryService inventoryService,
                                  PaymentService paymentService,
                                  NotificationService notificationService) {
        super(OrderCreatedEvent.class);
        this.inventoryService = inventoryService;
        this.paymentService = paymentService;
        this.notificationService = notificationService;
    }
    
    @Override
    protected void handleEvent(OrderCreatedEvent event) {
        try {
            // 处理库存预留
            inventoryService.reserveItems(event.getItems());
            
            // 初始化支付
            paymentService.initializePayment(event.getAggregateId(), event.getTotalAmount());
            
            // 发送确认通知
            notificationService.sendOrderConfirmation(event.getCustomerId(), event.getAggregateId());
            
            log.info("Order created event processed successfully: {}", event.getAggregateId());
        } catch (Exception e) {
            log.error("Failed to process order created event: {}", event.getAggregateId(), e);
            // 根据业务需求决定是否需要补偿操作
            handleFailure(event, e);
        }
    }
    
    private void handleFailure(OrderCreatedEvent event, Exception error) {
        // 发送告警
        alertService.sendAlert("Order Processing Failed", 
            "Failed to process order: " + event.getAggregateId() + ", error: " + error.getMessage());
        
        // 记录失败日志
        failureLogService.recordFailure("OrderCreated", event.getAggregateId(), error);
    }
}
```

## 高级设计模板

### Saga模式模板

```java
// Saga编排器模板
@Component
public class SagaOrchestrator {
    private final EventBus eventBus;
    private final SagaStateRepository stateRepository;
    
    public void startSaga(String sagaType, Object requestData) {
        SagaInstance saga = new SagaInstance(
            UUID.randomUUID().toString(),
            sagaType,
            requestData
        );
        
        stateRepository.save(saga);
        executeNextStep(saga);
    }
    
    @EventListener
    public void handleSagaEvent(SagaEvent event) {
        SagaInstance saga = stateRepository.findById(event.getSagaId());
        if (saga == null) {
            log.warn("Saga not found: {}", event.getSagaId());
            return;
        }
        
        if (event instanceof SagaStepCompletedEvent) {
            handleStepCompleted(saga, (SagaStepCompletedEvent) event);
        } else if (event instanceof SagaStepFailedEvent) {
            handleStepFailed(saga, (SagaStepFailedEvent) event);
        }
    }
    
    private void executeNextStep(SagaInstance saga) {
        SagaStep nextStep = saga.getNextStep();
        if (nextStep != null) {
            Command command = nextStep.createCommand(saga);
            eventBus.publish(command);
        } else {
            // Saga完成
            saga.markAsCompleted();
            stateRepository.update(saga);
            eventBus.publish(new SagaCompletedEvent(saga.getId()));
        }
    }
    
    private void handleStepCompleted(SagaInstance saga, SagaStepCompletedEvent event) {
        saga.markStepAsCompleted(event.getStepName());
        stateRepository.update(saga);
        executeNextStep(saga);
    }
    
    private void handleStepFailed(SagaInstance saga, SagaStepFailedEvent event) {
        saga.markStepAsFailed(event.getStepName(), event.getErrorMessage());
        stateRepository.update(saga);
        compensateSaga(saga);
    }
    
    private void compensateSaga(SagaInstance saga) {
        List<SagaStep> completedSteps = saga.getCompletedSteps();
        // 逆序执行补偿操作
        for (int i = completedSteps.size() - 1; i >= 0; i--) {
            SagaStep step = completedSteps.get(i);
            Command compensationCommand = step.createCompensationCommand(saga);
            eventBus.publish(compensationCommand);
        }
        
        saga.markAsFailed();
        stateRepository.update(saga);
        eventBus.publish(new SagaFailedEvent(saga.getId(), saga.getFailureReason()));
    }
}

// Saga步骤定义模板
public abstract class SagaStep {
    private final String name;
    private final boolean compensatable;
    
    protected SagaStep(String name, boolean compensatable) {
        this.name = name;
        this.compensatable = compensatable;
    }
    
    public String getName() {
        return name;
    }
    
    public boolean isCompensatable() {
        return compensatable;
    }
    
    public abstract Command createCommand(SagaInstance saga);
    public abstract Command createCompensationCommand(SagaInstance saga);
}

// 具体Saga步骤模板
public class CreateOrderStep extends SagaStep {
    public CreateOrderStep() {
        super("create-order", true);
    }
    
    @Override
    public Command createCommand(SagaInstance saga) {
        OrderRequest request = (OrderRequest) saga.getRequestData();
        return new CreateOrderCommand(saga.getId(), request);
    }
    
    @Override
    public Command createCompensationCommand(SagaInstance saga) {
        return new CancelOrderCommand(saga.getId(), saga.getOrderId());
    }
}
```

### CQRS模式模板

```java
// 命令模型模板
@Component
public class OrderCommandService {
    private final EventStore eventStore;
    private final EventBus eventBus;
    
    public String createOrder(CreateOrderCommand command) {
        String orderId = UUID.randomUUID().toString();
        Order order = Order.create(orderId, command.getCustomerId(), command.getItems());
        
        // 保存事件
        eventStore.saveEvents(order.getId(), order.getUncommittedEvents(), 0);
        
        // 发布事件
        order.getUncommittedEvents().forEach(eventBus::publish);
        order.clearUncommittedEvents();
        
        return orderId;
    }
    
    public void payOrder(PayOrderCommand command) {
        List<Event> history = eventStore.getEvents(command.getOrderId(), 0);
        Order order = new Order();
        history.forEach(order::mutate);
        
        order.pay();
        
        // 保存事件
        eventStore.saveEvents(order.getId(), order.getUncommittedEvents(), order.getVersion());
        
        // 发布事件
        order.getUncommittedEvents().forEach(eventBus::publish);
        order.clearUncommittedEvents();
    }
}

// 查询模型模板
@Component
public class OrderQueryService {
    private final MongoTemplate mongoTemplate;
    
    public OrderDetailView getOrderDetail(String orderId) {
        return mongoTemplate.findById(orderId, OrderDetailView.class, "order_read_model");
    }
    
    public List<OrderSummary> searchOrders(OrderSearchCriteria criteria) {
        Query query = buildSearchQuery(criteria);
        return mongoTemplate.find(query, OrderSummary.class, "order_read_model");
    }
    
    public OrderStatistics getOrderStatistics(LocalDateTime from, LocalDateTime to) {
        Aggregation aggregation = Aggregation.newAggregation(
            Aggregation.match(Criteria.where("createdAt").gte(from).lte(to)),
            Aggregation.group("status")
                .count().as("count")
                .sum("totalAmount").as("totalAmount"),
            Aggregation.project("count", "totalAmount")
        );
        
        return mongoTemplate.aggregate(aggregation, "order_read_model", OrderStatistics.class)
            .getUniqueMappedResult();
    }
}

// 读模型更新模板
@Component
public class ReadModelUpdater {
    private final MongoTemplate mongoTemplate;
    
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        OrderDetailView view = new OrderDetailView(
            event.getAggregateId(),
            event.getCustomerId(),
            event.getItems(),
            event.getTotalAmount(),
            OrderStatus.CREATED,
            Instant.ofEpochMilli(event.getTimestamp())
        );
        mongoTemplate.save(view, "order_read_model");
    }
    
    @EventListener
    public void handleOrderPaid(OrderPaidEvent event) {
        Query query = new Query(Criteria.where("id").is(event.getAggregateId()));
        Update update = new Update()
            .set("status", OrderStatus.PAID)
            .set("paidAt", Instant.ofEpochMilli(event.getTimestamp()));
        mongoTemplate.updateFirst(query, update, OrderDetailView.class, "order_read_model");
    }
}
```

## 实际应用示例

### 电商订单处理系统

```java
// 电商订单处理系统示例
public class ECommerceOrderSystem {
    // 1. 订单创建流程
    @Service
    public class OrderCreationService {
        private final EventBus eventBus;
        
        public String createOrder(OrderRequest request) {
            String orderId = UUID.randomUUID().toString();
            
            // 创建订单
            OrderCreatedEvent event = new OrderCreatedEvent(
                orderId,
                request.getCustomerId(),
                request.getItems()
            );
            
            // 发布事件
            eventBus.publish(event);
            
            return orderId;
        }
    }
    
    // 2. 库存服务
    @Service
    public class InventoryService {
        @EventListener
        public void handleOrderCreated(OrderCreatedEvent event) {
            try {
                // 预留库存
                reserveInventory(event.getItems());
                
                // 发布库存预留完成事件
                InventoryReservedEvent reservedEvent = new InventoryReservedEvent(
                    event.getAggregateId()
                );
                eventBus.publish(reservedEvent);
                
            } catch (InsufficientInventoryException e) {
                // 发布库存不足事件
                InventoryInsufficientEvent insufficientEvent = new InventoryInsufficientEvent(
                    event.getAggregateId(),
                    e.getMessage()
                );
                eventBus.publish(insufficientEvent);
            }
        }
    }
    
    // 3. 支付服务
    @Service
    public class PaymentService {
        @EventListener
        public void handleInventoryReserved(InventoryReservedEvent event) {
            try {
                // 处理支付
                processPayment(event.getOrderId());
                
                // 发布支付完成事件
                PaymentProcessedEvent processedEvent = new PaymentProcessedEvent(
                    event.getOrderId()
                );
                eventBus.publish(processedEvent);
                
            } catch (PaymentException e) {
                // 发布支付失败事件
                PaymentFailedEvent failedEvent = new PaymentFailedEvent(
                    event.getOrderId(),
                    e.getMessage()
                );
                eventBus.publish(failedEvent);
            }
        }
    }
    
    // 4. 订单确认服务
    @Service
    public class OrderConfirmationService {
        @EventListener
        public void handlePaymentProcessed(PaymentProcessedEvent event) {
            // 更新订单状态
            updateOrderStatus(event.getOrderId(), OrderStatus.CONFIRMED);
            
            // 发送确认邮件
            sendOrderConfirmationEmail(event.getOrderId());
            
            // 发布订单确认事件
            OrderConfirmedEvent confirmedEvent = new OrderConfirmedEvent(
                event.getOrderId()
            );
            eventBus.publish(confirmedEvent);
        }
    }
}
```

### 用户注册与通知系统

```java
// 用户注册与通知系统示例
public class UserRegistrationSystem {
    // 1. 用户注册服务
    @Service
    public class UserRegistrationService {
        private final EventBus eventBus;
        
        public String registerUser(UserRegistrationRequest request) {
            String userId = UUID.randomUUID().toString();
            
            // 创建用户
            UserCreatedEvent event = new UserCreatedEvent(
                userId,
                request.getEmail(),
                request.getUsername()
            );
            
            // 发布事件
            eventBus.publish(event);
            
            return userId;
        }
    }
    
    // 2. 邮件服务
    @Service
    public class EmailService {
        @EventListener
        public void handleUserCreated(UserCreatedEvent event) {
            try {
                // 发送欢迎邮件
                sendWelcomeEmail(event.getEmail(), event.getUsername());
                
                // 发布邮件发送完成事件
                WelcomeEmailSentEvent sentEvent = new WelcomeEmailSentEvent(
                    event.getAggregateId()
                );
                eventBus.publish(sentEvent);
                
            } catch (EmailException e) {
                // 发布邮件发送失败事件
                WelcomeEmailFailedEvent failedEvent = new WelcomeEmailFailedEvent(
                    event.getAggregateId(),
                    e.getMessage()
                );
                eventBus.publish(failedEvent);
            }
        }
    }
    
    // 3. 通知服务
    @Service
    public class NotificationService {
        @EventListener
        public void handleUserCreated(UserCreatedEvent event) {
            // 发送系统通知
            sendSystemNotification("new_user", 
                "New user registered: " + event.getUsername());
        }
        
        @EventListener
        public void handleWelcomeEmailSent(WelcomeEmailSentEvent event) {
            // 记录用户激活状态
            updateUserActivationStatus(event.getUserId(), true);
        }
    }
    
    // 4. 分析服务
    @Service
    public class AnalyticsService {
        @EventListener
        public void handleUserCreated(UserCreatedEvent event) {
            // 记录用户注册数据
            recordUserRegistration(event);
        }
        
        @EventListener
        public void handleWelcomeEmailSent(WelcomeEmailSentEvent event) {
            // 更新用户参与度指标
            updateUserEngagementMetric(event.getUserId(), "welcome_email_sent");
        }
    }
}
```

## 微服务集成示例

### 服务间通信模板

```java
// 微服务事件发布模板
@Service
public class MicroserviceEventPublisher {
    private final EventBus eventBus;
    
    public void publishOrderCreated(Order order) {
        OrderCreatedEvent event = new OrderCreatedEvent(
            order.getId(),
            order.getCustomerId(),
            order.getItems(),
            order.getTotalAmount()
        );
        eventBus.publish(event);
    }
    
    public void publishOrderStatusChanged(String orderId, OrderStatus oldStatus, OrderStatus newStatus) {
        OrderStatusChangedEvent event = new OrderStatusChangedEvent(
            orderId,
            oldStatus,
            newStatus
        );
        eventBus.publish(event);
    }
}

// 微服务事件监听模板
@Service
public class MicroserviceEventListener {
    // 库存服务监听订单创建事件
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        try {
            inventoryService.reserveItems(event.getItems());
        } catch (Exception e) {
            // 处理库存预留失败
            handleInventoryReservationFailure(event, e);
        }
    }
    
    // 支付服务监听库存预留完成事件
    @EventListener
    public void handleInventoryReserved(InventoryReservedEvent event) {
        try {
            paymentService.processPayment(event.getOrderId());
        } catch (Exception e) {
            // 处理支付失败
            handlePaymentFailure(event, e);
        }
    }
    
    // 物流服务监听支付完成事件
    @EventListener
    public void handlePaymentProcessed(PaymentProcessedEvent event) {
        try {
            shippingService.createShipment(event.getOrderId());
        } catch (Exception e) {
            // 处理发货失败
            handleShippingFailure(event, e);
        }
    }
}
```

## 配置与部署模板

### Docker配置模板

```dockerfile
# 事件驱动服务Dockerfile模板
FROM openjdk:11-jre-slim

# 设置环境变量
ENV SERVICE_NAME=event-driven-service
ENV PROFILE=production

# 创建应用目录
WORKDIR /app

# 复制应用文件
COPY target/${SERVICE_NAME}.jar app.jar

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

# 启动应用
ENTRYPOINT ["java", "-jar", "app.jar", "--spring.profiles.active=${PROFILE}"]
```

### Kubernetes部署模板

```yaml
# Kubernetes部署模板
apiVersion: apps/v1
kind: Deployment
metadata:
  name: event-driven-service
  labels:
    app: event-driven-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: event-driven-service
  template:
    metadata:
      labels:
        app: event-driven-service
    spec:
      containers:
      - name: event-driven-service
        image: event-driven-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "production"
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "kafka-service:9092"
        - name: DATABASE_URL
          value: "postgresql://postgres-service:5432/events"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /actuator/health/liveness
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: event-driven-service
spec:
  selector:
    app: event-driven-service
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: event-driven-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: event-driven-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: External
    external:
      metric:
        name: event_queue_length
      target:
        type: Value
        value: "1000"
```

## 监控与告警示例

### 指标收集模板

```java
// 事件处理指标收集模板
@Component
public class EventProcessingMetrics {
    private final MeterRegistry meterRegistry;
    
    @EventListener
    public void handleEvent(Event event) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            processEvent(event);
            
            // 记录成功处理指标
            sample.stop(Timer.builder("event.processing.duration")
                .tag("type", event.getClass().getSimpleName())
                .tag("status", "success")
                .register(meterRegistry));
                
            Counter.builder("events.processed")
                .tag("type", event.getClass().getSimpleName())
                .tag("status", "success")
                .register(meterRegistry)
                .increment();
                
        } catch (Exception e) {
            // 记录错误指标
            sample.stop(Timer.builder("event.processing.duration")
                .tag("type", event.getClass().getSimpleName())
                .tag("status", "error")
                .register(meterRegistry));
                
            Counter.builder("events.processed")
                .tag("type", event.getClass().getSimpleName())
                .tag("status", "error")
                .register(meterRegistry)
                .increment();
                
            throw e;
        }
    }
    
    // 队列积压监控
    @Scheduled(fixedRate = 30000)
    public void monitorQueueBacklog() {
        List<QueueInfo> queues = getQueueInformation();
        
        for (QueueInfo queue : queues) {
            Gauge.builder("queue.message.count")
                .tag("queue", queue.getName())
                .register(meterRegistry, queue, QueueInfo::getMessageCount);
        }
    }
}
```

## 测试模板

### 单元测试模板

```java
// 事件处理器单元测试模板
@ExtendWith(MockitoExtension.class)
class OrderEventHandlerTest {
    @Mock
    private InventoryService inventoryService;
    
    @Mock
    private PaymentService paymentService;
    
    @InjectMocks
    private OrderEventHandler orderEventHandler;
    
    @Test
    void shouldHandleOrderCreatedEvent() {
        // Given
        OrderCreatedEvent event = new OrderCreatedEvent(
            "order-123",
            "customer-456", 
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        );
        
        // When
        orderEventHandler.handle(event);
        
        // Then
        verify(inventoryService).reserveItems(event.getItems());
        verify(paymentService).initializePayment(event.getAggregateId(), event.getTotalAmount());
    }
    
    @Test
    void shouldHandleOrderCreatedEventWithException() {
        // Given
        OrderCreatedEvent event = new OrderCreatedEvent(
            "order-123",
            "customer-456", 
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        );
        
        doThrow(new RuntimeException("Service unavailable"))
            .when(inventoryService).reserveItems(any());
        
        // When & Then
        assertThrows(RuntimeException.class, () -> {
            orderEventHandler.handle(event);
        });
        
        verify(paymentService, never()).initializePayment(anyString(), any());
    }
}
```

### 集成测试模板

```java
// 集成测试模板
@SpringBootTest
@Testcontainers
class OrderProcessingIntegrationTest {
    @Container
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:latest")
    );
    
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(
        DockerImageName.parse("postgres:13")
    );
    
    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
    
    @Autowired
    private OrderService orderService;
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Test
    void shouldProcessOrderEndToEnd() {
        // Given
        OrderRequest request = new OrderRequest(
            "customer-456",
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        );
        
        // When
        String orderId = orderService.createOrder(request);
        
        // Then
        await().atMost(Duration.ofSeconds(30))
            .untilAsserted(() -> {
                Order order = orderRepository.findById(orderId);
                assertThat(order).isNotNull();
                assertThat(order.getStatus()).isEqualTo(OrderStatus.CONFIRMED);
            });
    }
}
```

## 最佳实践总结

### 设计原则

1. **事件不可变性**：事件一旦创建就不应该被修改
2. **事件幂等性**：确保事件处理的幂等性
3. **松耦合**：服务间通过事件进行通信，避免直接依赖
4. **最终一致性**：采用最终一致性而非强一致性
5. **可追溯性**：确保事件的完整性和可追溯性

### 实现要点

1. **事件版本管理**：实现事件的版本控制和升级机制
2. **错误处理**：建立完善的错误处理和重试机制
3. **监控告警**：建立全面的监控和告警体系
4. **性能优化**：优化事件处理性能和系统吞吐量
5. **安全控制**：确保事件传输和存储的安全性

### 运维建议

1. **容量规划**：根据业务需求合理规划系统容量
2. **备份恢复**：建立数据备份和恢复机制
3. **版本升级**：制定平滑的版本升级策略
4. **故障处理**：建立完善的故障处理流程
5. **性能调优**：持续监控和优化系统性能

通过这些模板和示例，开发者可以更好地理解和应用事件驱动架构，构建出高性能、高可用、易维护的分布式系统。