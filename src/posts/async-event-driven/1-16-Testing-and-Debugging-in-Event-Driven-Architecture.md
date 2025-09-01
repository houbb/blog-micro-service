---
title: 事件驱动架构的测试与调试
date: 2025-08-31
categories: [AsyncEventDriven]
tags: [async-event-driven]
published: true
---

在事件驱动架构中，测试和调试面临着独特的挑战。由于系统的异步性、分布式特性和松耦合设计，传统的测试方法往往难以直接应用。本文将深入探讨事件驱动架构中的单元测试与集成测试、消息队列与事件流的模拟测试、事件驱动系统中的错误处理与容错，以及测试工具与框架等关键测试与调试主题。

## 事件驱动架构中的单元测试与集成测试

### 单元测试策略

在事件驱动架构中，单元测试需要关注事件的生成、处理和状态变更等核心逻辑。

```java
// 事件处理器单元测试
@ExtendWith(MockitoExtension.class)
class OrderEventHandlerTest {
    @Mock
    private OrderRepository orderRepository;
    
    @Mock
    private InventoryService inventoryService;
    
    @Mock
    private PaymentService paymentService;
    
    @InjectMocks
    private OrderEventHandler orderEventHandler;
    
    @Test
    void shouldHandleOrderCreatedEvent() {
        // Given
        String orderId = "order-123";
        String customerId = "customer-456";
        List<OrderItem> items = Arrays.asList(
            new OrderItem("product-1", 2, new BigDecimal("10.00"))
        );
        
        OrderCreatedEvent event = new OrderCreatedEvent(
            "event-789", orderId, customerId, items
        );
        
        Order order = new Order(orderId, customerId, items);
        when(orderRepository.findById(orderId)).thenReturn(order);
        
        // When
        orderEventHandler.handleOrderCreated(event);
        
        // Then
        verify(inventoryService).reserveItems(items);
        verify(paymentService).initializePayment(orderId, order.getTotalAmount());
        verify(orderRepository).save(argThat(o -> o.getStatus() == OrderStatus.PROCESSING));
    }
    
    @Test
    void shouldHandleOrderCreatedEventWithException() {
        // Given
        OrderCreatedEvent event = new OrderCreatedEvent(
            "event-789", "order-123", "customer-456", 
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        );
        
        doThrow(new RuntimeException("Database error"))
            .when(orderRepository).findById("order-123");
        
        // When & Then
        assertThrows(RuntimeException.class, () -> {
            orderEventHandler.handleOrderCreated(event);
        });
        
        verify(inventoryService, never()).reserveItems(any());
        verify(paymentService, never()).initializePayment(anyString(), any());
    }
}

// 聚合根单元测试
class OrderAggregateTest {
    @Test
    void shouldCreateOrder() {
        // Given
        String orderId = "order-123";
        String customerId = "customer-456";
        List<OrderItem> items = Arrays.asList(
            new OrderItem("product-1", 2, new BigDecimal("10.00"))
        );
        
        // When
        Order order = Order.create(orderId, customerId, items);
        
        // Then
        assertThat(order.getId()).isEqualTo(orderId);
        assertThat(order.getCustomerId()).isEqualTo(customerId);
        assertThat(order.getItems()).containsExactlyElementsOf(items);
        assertThat(order.getStatus()).isEqualTo(OrderStatus.CREATED);
        
        // 验证事件
        List<Event> events = order.getUncommittedEvents();
        assertThat(events).hasSize(1);
        assertThat(events.get(0)).isInstanceOf(OrderCreatedEvent.class);
    }
    
    @Test
    void shouldPayOrder() {
        // Given
        Order order = createTestOrder();
        order.clearUncommittedEvents(); // 清除创建事件
        
        // When
        order.pay();
        
        // Then
        assertThat(order.getStatus()).isEqualTo(OrderStatus.PAID);
        
        // 验证事件
        List<Event> events = order.getUncommittedEvents();
        assertThat(events).hasSize(1);
        assertThat(events.get(0)).isInstanceOf(OrderPaidEvent.class);
    }
    
    private Order createTestOrder() {
        return Order.create(
            "order-123", 
            "customer-456", 
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        );
    }
}
```

### 集成测试策略

集成测试需要验证组件间的协作和整个业务流程的正确性。

```java
// 集成测试配置
@SpringBootTest
@Testcontainers
class OrderProcessingIntegrationTest {
    @Container
    static RabbitMQContainer rabbitMQ = new RabbitMQContainer(
        DockerImageName.parse("rabbitmq:3.8-management")
    );
    
    @Container
    static MongoDBContainer mongoDB = new MongoDBContainer(
        DockerImageName.parse("mongo:4.4")
    );
    
    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.rabbitmq.host", rabbitMQ::getHost);
        registry.add("spring.rabbitmq.port", rabbitMQ::getAmqpPort);
        registry.add("spring.data.mongodb.uri", mongoDB::getReplicaSetUrl);
    }
    
    @Autowired
    private OrderService orderService;
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private TestEventListener testEventListener;
    
    @Test
    void shouldProcessOrderSuccessfully() {
        // Given
        OrderRequest request = new OrderRequest(
            "customer-456",
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        );
        
        // When
        String orderId = orderService.createOrder(request);
        
        // Then
        // 等待事件处理完成
        await().atMost(Duration.ofSeconds(10))
            .until(() -> testEventListener.getOrderCreatedEvents().size() > 0);
        
        // 验证订单状态
        Order order = orderRepository.findById(orderId);
        assertThat(order).isNotNull();
        assertThat(order.getStatus()).isEqualTo(OrderStatus.PROCESSING);
        
        // 验证事件处理
        List<OrderCreatedEvent> events = testEventListener.getOrderCreatedEvents();
        assertThat(events).hasSize(1);
        assertThat(events.get(0).getOrderId()).isEqualTo(orderId);
    }
}

// 测试事件监听器
@Component
@TestComponent
public class TestEventListener {
    private final List<OrderCreatedEvent> orderCreatedEvents = new CopyOnWriteArrayList<>();
    private final List<PaymentProcessedEvent> paymentProcessedEvents = new CopyOnWriteArrayList<>();
    
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        orderCreatedEvents.add(event);
    }
    
    @EventListener
    public void handlePaymentProcessed(PaymentProcessedEvent event) {
        paymentProcessedEvents.add(event);
    }
    
    // getter方法
    public List<OrderCreatedEvent> getOrderCreatedEvents() {
        return new ArrayList<>(orderCreatedEvents);
    }
    
    public List<PaymentProcessedEvent> getPaymentProcessedEvents() {
        return new ArrayList<>(paymentProcessedEvents);
    }
    
    public void clear() {
        orderCreatedEvents.clear();
        paymentProcessedEvents.clear();
    }
}
```

## 消息队列与事件流的模拟测试

### 消息队列模拟

```java
// 消息队列模拟器
public class MockMessageQueue {
    private final Map<String, List<Message>> queues = new ConcurrentHashMap<>();
    private final Map<String, List<MessageListener>> listeners = new ConcurrentHashMap<>();
    private final ExecutorService executorService = Executors.newCachedThreadPool();
    
    public void send(String queueName, Message message) {
        queues.computeIfAbsent(queueName, k -> new ArrayList<>()).add(message);
        notifyListeners(queueName, message);
    }
    
    public Message receive(String queueName) {
        List<Message> queue = queues.get(queueName);
        if (queue != null && !queue.isEmpty()) {
            return queue.remove(0);
        }
        return null;
    }
    
    public void subscribe(String queueName, MessageListener listener) {
        listeners.computeIfAbsent(queueName, k -> new ArrayList<>()).add(listener);
    }
    
    private void notifyListeners(String queueName, Message message) {
        List<MessageListener> queueListeners = listeners.get(queueName);
        if (queueListeners != null) {
            for (MessageListener listener : queueListeners) {
                executorService.submit(() -> listener.onMessage(message));
            }
        }
    }
    
    public int getMessageCount(String queueName) {
        List<Message> queue = queues.get(queueName);
        return queue != null ? queue.size() : 0;
    }
    
    public void clear() {
        queues.clear();
        listeners.clear();
    }
}

// 消息监听器接口
public interface MessageListener {
    void onMessage(Message message);
}

// 使用模拟队列的测试
@ExtendWith(MockitoExtension.class)
class EventDrivenServiceTest {
    private MockMessageQueue mockMessageQueue;
    private EventDrivenService eventDrivenService;
    
    @BeforeEach
    void setUp() {
        mockMessageQueue = new MockMessageQueue();
        eventDrivenService = new EventDrivenService(mockMessageQueue);
    }
    
    @Test
    void shouldPublishEventToQueue() {
        // Given
        OrderCreatedEvent event = new OrderCreatedEvent(
            "order-123", "customer-456", 
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        );
        
        // When
        eventDrivenService.publishEvent(event);
        
        // Then
        assertThat(mockMessageQueue.getMessageCount("order-events")).isEqualTo(1);
        
        Message message = mockMessageQueue.receive("order-events");
        assertThat(message).isNotNull();
        assertThat(deserializeEvent(message.getBody())).isEqualTo(event);
    }
    
    @Test
    void shouldProcessEventsFromQueue() {
        // Given
        OrderCreatedEvent event = new OrderCreatedEvent(
            "order-123", "customer-456", 
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        );
        
        mockMessageQueue.send("order-events", serializeEvent(event));
        
        // When
        eventDrivenService.processEvents();
        
        // Then
        // 验证事件被正确处理
        verify(eventDrivenService.getOrderService()).handleOrderCreated(event);
    }
}
```

### 事件流模拟测试

```java
// 事件流模拟器
public class EventStreamSimulator {
    private final List<Event> eventStream = new ArrayList<>();
    private final Map<Class<? extends Event>, List<EventHandler>> handlers = new HashMap<>();
    private int currentIndex = 0;
    
    public void addEvent(Event event) {
        eventStream.add(event);
    }
    
    public void registerHandler(Class<? extends Event> eventType, EventHandler handler) {
        handlers.computeIfAbsent(eventType, k -> new ArrayList<>()).add(handler);
    }
    
    public void processNextEvent() {
        if (currentIndex < eventStream.size()) {
            Event event = eventStream.get(currentIndex++);
            List<EventHandler> eventHandlers = handlers.get(event.getClass());
            if (eventHandlers != null) {
                eventHandlers.forEach(handler -> handler.handle(event));
            }
        }
    }
    
    public void processAllEvents() {
        while (currentIndex < eventStream.size()) {
            processNextEvent();
        }
    }
    
    public int getCurrentIndex() {
        return currentIndex;
    }
    
    public int getEventCount() {
        return eventStream.size();
    }
    
    public void reset() {
        currentIndex = 0;
    }
    
    public void clear() {
        eventStream.clear();
        handlers.clear();
        currentIndex = 0;
    }
}

// 事件处理器接口
public interface EventHandler {
    void handle(Event event);
}

// 事件流测试示例
class OrderProcessingEventStreamTest {
    private EventStreamSimulator eventStreamSimulator;
    private OrderService orderService;
    private InventoryService inventoryService;
    private PaymentService paymentService;
    
    @BeforeEach
    void setUp() {
        eventStreamSimulator = new EventStreamSimulator();
        orderService = mock(OrderService.class);
        inventoryService = mock(InventoryService.class);
        paymentService = mock(PaymentService.class);
        
        // 注册事件处理器
        eventStreamSimulator.registerHandler(OrderCreatedEvent.class, 
            event -> orderService.handleOrderCreated((OrderCreatedEvent) event));
        eventStreamSimulator.registerHandler(OrderPaidEvent.class, 
            event -> inventoryService.handleOrderPaid((OrderPaidEvent) event));
        eventStreamSimulator.registerHandler(InventoryReservedEvent.class, 
            event -> paymentService.handleInventoryReserved((InventoryReservedEvent) event));
    }
    
    @Test
    void shouldProcessOrderEventStream() {
        // Given
        eventStreamSimulator.addEvent(new OrderCreatedEvent(
            "order-123", "customer-456", 
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        ));
        eventStreamSimulator.addEvent(new OrderPaidEvent("order-123"));
        eventStreamSimulator.addEvent(new InventoryReservedEvent("order-123"));
        
        // When
        eventStreamSimulator.processAllEvents();
        
        // Then
        verify(orderService).handleOrderCreated(any(OrderCreatedEvent.class));
        verify(inventoryService).handleOrderPaid(any(OrderPaidEvent.class));
        verify(paymentService).handleInventoryReserved(any(InventoryReservedEvent.class));
    }
    
    @Test
    void shouldHandleEventStreamPartially() {
        // Given
        eventStreamSimulator.addEvent(new OrderCreatedEvent(
            "order-123", "customer-456", 
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        ));
        eventStreamSimulator.addEvent(new OrderPaidEvent("order-123"));
        eventStreamSimulator.addEvent(new InventoryReservedEvent("order-123"));
        
        // When
        eventStreamSimulator.processNextEvent(); // 处理第一个事件
        eventStreamSimulator.processNextEvent(); // 处理第二个事件
        
        // Then
        verify(orderService).handleOrderCreated(any(OrderCreatedEvent.class));
        verify(inventoryService).handleOrderPaid(any(OrderPaidEvent.class));
        verify(paymentService, never()).handleInventoryReserved(any(InventoryReservedEvent.class));
        
        assertThat(eventStreamSimulator.getCurrentIndex()).isEqualTo(2);
    }
}
```

## 事件驱动系统中的错误处理与容错

### 错误处理测试

```java
// 错误处理测试
@ExtendWith(MockitoExtension.class)
class ErrorHandlingTest {
    @Mock
    private EventStore eventStore;
    
    @Mock
    private DeadLetterQueue deadLetterQueue;
    
    @InjectMocks
    private FaultTolerantEventProcessor eventProcessor;
    
    @Test
    void shouldHandleTransientExceptionWithRetry() {
        // Given
        OrderCreatedEvent event = new OrderCreatedEvent(
            "order-123", "customer-456", 
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        );
        
        // 第一次调用抛出瞬时异常，第二次调用成功
        doThrow(new TransientException("Database temporarily unavailable"))
            .doNothing()
            .when(eventStore).saveEvent(event);
        
        // When
        eventProcessor.processEvent(event);
        
        // Then
        verify(eventStore, times(2)).saveEvent(event);
        verify(deadLetterQueue, never()).send(any(Event.class), any(Exception.class));
    }
    
    @Test
    void shouldSendToDeadLetterQueueAfterMaxRetries() {
        // Given
        OrderCreatedEvent event = new OrderCreatedEvent(
            "order-123", "customer-456", 
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        );
        
        // 持续抛出瞬时异常
        doThrow(new TransientException("Database temporarily unavailable"))
            .when(eventStore).saveEvent(event);
        
        // When & Then
        assertThrows(RuntimeException.class, () -> {
            eventProcessor.processEvent(event);
        });
        
        verify(eventStore, times(3)).saveEvent(event); // 最大重试次数
        verify(deadLetterQueue).send(event, any(TransientException.class));
    }
    
    @Test
    void shouldHandleBusinessExceptionWithoutRetry() {
        // Given
        OrderCreatedEvent event = new OrderCreatedEvent(
            "order-123", "customer-456", 
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        );
        
        doThrow(new BusinessException("Invalid order data"))
            .when(eventStore).saveEvent(event);
        
        // When & Then
        assertThrows(BusinessException.class, () -> {
            eventProcessor.processEvent(event);
        });
        
        verify(eventStore, times(1)).saveEvent(event);
        verify(deadLetterQueue, never()).send(any(Event.class), any(Exception.class));
    }
}

// 异常类型定义
public class TransientException extends RuntimeException {
    public TransientException(String message) {
        super(message);
    }
}

public class BusinessException extends RuntimeException {
    public BusinessException(String message) {
        super(message);
    }
}
```

### 容错机制测试

```java
// 熔断器测试
class CircuitBreakerTest {
    private CircuitBreaker circuitBreaker;
    
    @BeforeEach
    void setUp() {
        circuitBreaker = CircuitBreaker.ofDefaults("test-circuit");
    }
    
    @Test
    void shouldOpenCircuitAfterFailures() {
        // Given
        Supplier<String> guardedSupplier = CircuitBreaker.decorateSupplier(
            circuitBreaker, 
            () -> { throw new RuntimeException("Service failure"); }
        );
        
        // When & Then
        // 连续失败5次（默认熔断阈值）
        for (int i = 0; i < 5; i++) {
            assertThrows(RuntimeException.class, guardedSupplier::get);
        }
        
        // 第6次调用应该直接熔断
        CircuitBreakerOpenException exception = assertThrows(
            CircuitBreakerOpenException.class, 
            guardedSupplier::get
        );
        
        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.OPEN);
    }
    
    @Test
    void shouldCloseCircuitAfterSuccess() throws InterruptedException {
        // Given
        Supplier<String> guardedSupplier = CircuitBreaker.decorateSupplier(
            circuitBreaker, 
            () -> { throw new RuntimeException("Service failure"); }
        );
        
        // 先让熔断器打开
        for (int i = 0; i < 5; i++) {
            assertThrows(RuntimeException.class, guardedSupplier::get);
        }
        
        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.OPEN);
        
        // 等待熔断器半开
        Thread.sleep(6000); // 默认等待时间
        
        // When - 成功调用
        Supplier<String> successSupplier = CircuitBreaker.decorateSupplier(
            circuitBreaker, 
            () -> "success"
        );
        
        String result = successSupplier.get();
        
        // Then
        assertThat(result).isEqualTo("success");
        assertThat(circuitBreaker.getState()).isEqualTo(CircuitBreaker.State.CLOSED);
    }
}

// 限流器测试
class RateLimiterTest {
    private RateLimiter rateLimiter;
    
    @BeforeEach
    void setUp() {
        // 每秒允许2个请求
        rateLimiter = RateLimiter.of("test-rate-limiter", 
            RateLimiterConfig.custom()
                .limitRefreshPeriod(Duration.ofSeconds(1))
                .limitForPeriod(2)
                .timeoutDuration(Duration.ofMillis(100))
                .build()
        );
    }
    
    @Test
    void shouldAllowRequestsWithinLimit() {
        // When & Then
        // 前两个请求应该被允许
        assertThat(rateLimiter.acquirePermission()).isTrue();
        assertThat(rateLimiter.acquirePermission()).isTrue();
    }
    
    @Test
    void shouldRejectRequestsExceedingLimit() {
        // Given
        rateLimiter.acquirePermission(); // 第1个请求
        rateLimiter.acquirePermission(); // 第2个请求
        
        // When
        boolean allowed = rateLimiter.acquirePermission(); // 第3个请求
        
        // Then
        assertThat(allowed).isFalse();
    }
    
    @Test
    void shouldAllowRequestsAfterRefill() throws InterruptedException {
        // Given
        rateLimiter.acquirePermission(); // 第1个请求
        rateLimiter.acquirePermission(); // 第2个请求
        rateLimiter.acquirePermission(); // 第3个请求（被拒绝）
        
        // When
        Thread.sleep(1000); // 等待令牌刷新
        
        // Then
        assertThat(rateLimiter.acquirePermission()).isTrue(); // 应该被允许
    }
}
```

## 测试工具与框架

### Testcontainers集成测试

```java
// 使用Testcontainers的集成测试
@SpringBootTest
@Testcontainers
class FullStackIntegrationTest {
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
        // 等待Kafka事件处理完成
        await().atMost(Duration.ofSeconds(30))
            .untilAsserted(() -> {
                Order order = orderRepository.findById(orderId);
                assertThat(order).isNotNull();
                assertThat(order.getStatus()).isEqualTo(OrderStatus.COMPLETED);
            });
    }
}
```

### WireMock模拟外部服务

```java
// 使用WireMock模拟外部服务
@ExtendWith(MockitoExtension.class)
class ExternalServiceIntegrationTest {
    @RegisterExtension
    static WireMockExtension wireMock = WireMockExtension.newInstance()
        .options(wireMockConfig().port(8089))
        .build();
    
    private PaymentService paymentService;
    
    @BeforeEach
    void setUp() {
        paymentService = new PaymentService("http://localhost:8089");
    }
    
    @Test
    void shouldProcessPaymentSuccessfully() {
        // Given
        wireMock.stubFor(post(urlEqualTo("/payments"))
            .willReturn(aResponse()
                .withStatus(200)
                .withHeader("Content-Type", "application/json")
                .withBody("{\"paymentId\":\"pay-123\",\"status\":\"SUCCESS\"}")));
        
        PaymentRequest request = new PaymentRequest("order-123", new BigDecimal("20.00"));
        
        // When
        PaymentResult result = paymentService.processPayment(request);
        
        // Then
        assertThat(result.getPaymentId()).isEqualTo("pay-123");
        assertThat(result.getStatus()).isEqualTo(PaymentStatus.SUCCESS);
        
        wireMock.verify(postRequestedFor(urlEqualTo("/payments"))
            .withRequestBody(matchingJsonPath("$.orderId", equalTo("order-123")))
            .withRequestBody(matchingJsonPath("$.amount", equalTo("20.00"))));
    }
    
    @Test
    void shouldHandlePaymentFailure() {
        // Given
        wireMock.stubFor(post(urlEqualTo("/payments"))
            .willReturn(aResponse()
                .withStatus(400)
                .withHeader("Content-Type", "application/json")
                .withBody("{\"error\":\"Insufficient funds\"}")));
        
        PaymentRequest request = new PaymentRequest("order-123", new BigDecimal("20.00"));
        
        // When & Then
        PaymentException exception = assertThrows(PaymentException.class, () -> {
            paymentService.processPayment(request);
        });
        
        assertThat(exception.getMessage()).contains("Insufficient funds");
    }
}
```

### 自定义测试工具

```java
// 事件断言工具
public class EventAssertions {
    private final List<Event> events;
    
    private EventAssertions(List<Event> events) {
        this.events = events;
    }
    
    public static EventAssertions assertThatEvents(List<Event> events) {
        return new EventAssertions(events);
    }
    
    public EventAssertions containsEventOfType(Class<? extends Event> eventType) {
        boolean found = events.stream().anyMatch(eventType::isInstance);
        if (!found) {
            throw new AssertionError("Expected event of type " + eventType.getSimpleName() + 
                                   " but was not found in " + events);
        }
        return this;
    }
    
    public EventAssertions containsEventMatching(Predicate<Event> predicate) {
        boolean found = events.stream().anyMatch(predicate);
        if (!found) {
            throw new AssertionError("Expected event matching predicate but was not found in " + events);
        }
        return this;
    }
    
    public EventAssertions hasSize(int expectedSize) {
        if (events.size() != expectedSize) {
            throw new AssertionError("Expected " + expectedSize + " events but found " + events.size());
        }
        return this;
    }
    
    public <T extends Event> EventAssertions withEventOfType(Class<T> eventType, Consumer<T> consumer) {
        List<T> typedEvents = events.stream()
            .filter(eventType::isInstance)
            .map(eventType::cast)
            .collect(Collectors.toList());
        
        if (typedEvents.isEmpty()) {
            throw new AssertionError("No events of type " + eventType.getSimpleName() + " found");
        }
        
        typedEvents.forEach(consumer);
        return this;
    }
}

// 使用事件断言工具的测试
class OrderEventAssertionTest {
    @Test
    void shouldGenerateCorrectEvents() {
        // Given
        Order order = Order.create(
            "order-123", 
            "customer-456", 
            Arrays.asList(new OrderItem("product-1", 2, new BigDecimal("10.00")))
        );
        
        // When
        order.pay();
        
        // Then
        EventAssertions.assertThatEvents(order.getUncommittedEvents())
            .hasSize(2)
            .containsEventOfType(OrderCreatedEvent.class)
            .containsEventOfType(OrderPaidEvent.class)
            .withEventOfType(OrderCreatedEvent.class, event -> {
                assertThat(event.getOrderId()).isEqualTo("order-123");
                assertThat(event.getCustomerId()).isEqualTo("customer-456");
            })
            .withEventOfType(OrderPaidEvent.class, event -> {
                assertThat(event.getOrderId()).isEqualTo("order-123");
            });
    }
}

// 测试数据生成器
public class TestDataGenerator {
    private static final Random random = new Random();
    
    public static Order createRandomOrder() {
        return Order.create(
            "order-" + random.nextInt(1000),
            "customer-" + random.nextInt(1000),
            Arrays.asList(
                new OrderItem("product-" + random.nextInt(100), 
                             random.nextInt(10) + 1, 
                             new BigDecimal(random.nextInt(100) + 1))
            )
        );
    }
    
    public static List<Event> createRandomEventStream(int size) {
        List<Event> events = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            events.add(createRandomEvent());
        }
        return events;
    }
    
    private static Event createRandomEvent() {
        int eventType = random.nextInt(3);
        switch (eventType) {
            case 0:
                return new OrderCreatedEvent(
                    "event-" + random.nextInt(1000),
                    "order-" + random.nextInt(1000),
                    "customer-" + random.nextInt(1000),
                    Arrays.asList(new OrderItem("product-" + random.nextInt(100), 1, BigDecimal.TEN))
                );
            case 1:
                return new OrderPaidEvent("order-" + random.nextInt(1000));
            case 2:
                return new InventoryReservedEvent("order-" + random.nextInt(1000));
            default:
                throw new IllegalStateException("Unexpected event type: " + eventType);
        }
    }
}
```

## 总结

事件驱动架构的测试与调试需要采用专门的策略和工具。通过合理的单元测试、集成测试、模拟测试以及错误处理测试，可以确保系统的正确性和可靠性。

关键的测试策略包括：
1. **隔离测试**：使用模拟对象隔离被测组件
2. **事件流测试**：验证事件的正确生成和处理顺序
3. **容错测试**：验证系统的错误处理和恢复能力
4. **集成测试**：使用Testcontainers等工具进行全栈测试

在实际应用中，需要根据具体的业务需求和技术栈选择合适的测试工具和框架，并建立完善的测试体系。随着系统复杂性的增加，测试策略也需要不断优化和完善，以适应不断变化的业务需求和技术环境。

通过持续的测试和优化，可以确保事件驱动架构系统在高并发、高可用的环境下稳定运行，为业务提供可靠的技术支撑。