---
title: 微服务架构的行业应用案例：从电商平台到物联网的实战解析
date: 2025-08-31
categories: [Microservices]
tags: [architecture, microservices, case-studies, e-commerce, finance, iot]
published: true
---

# 第17章：微服务架构的行业应用案例

在前几章中，我们系统地探讨了微服务架构的理论基础、设计原则、开发实践、部署管理、监控告警、安全管理、故障恢复、性能优化、可伸缩性、架构演化以及最佳实践等重要内容。本章将通过具体的行业应用案例，深入分析微服务架构在不同领域的实际应用情况，帮助读者更好地理解和掌握微服务架构的实践价值。

## 电商平台中的微服务架构

电商平台是微服务架构应用最为广泛的领域之一，其复杂的业务逻辑和高并发需求非常适合采用微服务架构。

### 1. 业务场景分析

电商平台通常包含以下核心业务模块：

- **用户管理**：用户注册、登录、个人信息管理
- **商品管理**：商品展示、搜索、分类、库存管理
- **订单管理**：购物车、订单创建、订单状态跟踪
- **支付管理**：多种支付方式集成、退款处理
- **物流管理**：配送跟踪、物流合作伙伴管理
- **营销管理**：优惠券、促销活动、推荐系统
- **客服管理**：在线客服、投诉处理、售后服务

### 2. 微服务架构设计

#### 核心服务划分

```java
// 用户服务 (user-service)
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @PostMapping("/register")
    public ResponseEntity<UserRegistrationResponse> registerUser(
            @RequestBody UserRegistrationRequest request) {
        User user = userService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(new UserRegistrationResponse(user.getId(), "User registered successfully"));
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<UserProfile> getUserProfile(@PathVariable Long id) {
        UserProfile profile = userService.getProfile(id);
        return ResponseEntity.ok(profile);
    }
    
    @PutMapping("/{id}/preferences")
    public ResponseEntity<UserProfile> updateUserPreferences(
            @PathVariable Long id, 
            @RequestBody UserPreferences preferences) {
        UserProfile profile = userService.updatePreferences(id, preferences);
        return ResponseEntity.ok(profile);
    }
}

// 商品服务 (product-service)
@RestController
@RequestMapping("/api/products")
public class ProductController {
    
    @GetMapping
    public ResponseEntity<PageResponse<Product>> getProducts(
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        
        ProductSearchCriteria criteria = ProductSearchCriteria.builder()
            .category(category)
            .keyword(keyword)
            .page(page)
            .size(size)
            .build();
            
        Page<Product> products = productService.searchProducts(criteria);
        return ResponseEntity.ok(convertToPageResponse(products));
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<ProductDetail> getProductDetail(@PathVariable Long id) {
        ProductDetail detail = productService.getDetail(id);
        return ResponseEntity.ok(detail);
    }
    
    @GetMapping("/{id}/inventory")
    public ResponseEntity<InventoryInfo> getProductInventory(@PathVariable Long id) {
        InventoryInfo inventory = inventoryService.getInventory(id);
        return ResponseEntity.ok(inventory);
    }
}

// 购物车服务 (cart-service)
@RestController
@RequestMapping("/api/carts")
public class CartController {
    
    @GetMapping("/users/{userId}")
    public ResponseEntity<ShoppingCart> getUserCart(@PathVariable Long userId) {
        ShoppingCart cart = cartService.getCart(userId);
        return ResponseEntity.ok(cart);
    }
    
    @PostMapping("/users/{userId}/items")
    public ResponseEntity<ShoppingCart> addItemToCart(
            @PathVariable Long userId,
            @RequestBody AddCartItemRequest request) {
        ShoppingCart cart = cartService.addItem(userId, request);
        return ResponseEntity.ok(cart);
    }
    
    @DeleteMapping("/users/{userId}/items/{itemId}")
    public ResponseEntity<ShoppingCart> removeItemFromCart(
            @PathVariable Long userId,
            @PathVariable Long itemId) {
        ShoppingCart cart = cartService.removeItem(userId, itemId);
        return ResponseEntity.ok(cart);
    }
}

// 订单服务 (order-service)
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    @PostMapping
    public ResponseEntity<Order> createOrder(@RequestBody CreateOrderRequest request) {
        Order order = orderService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(order);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<OrderDetail> getOrderDetail(@PathVariable Long id) {
        OrderDetail detail = orderService.getDetail(id);
        return ResponseEntity.ok(detail);
    }
    
    @GetMapping("/users/{userId}")
    public ResponseEntity<PageResponse<OrderSummary>> getUserOrders(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        Page<OrderSummary> orders = orderService.getUserOrders(userId, pageable);
        return ResponseEntity.ok(convertToPageResponse(orders));
    }
}

// 支付服务 (payment-service)
@RestController
@RequestMapping("/api/payments")
public class PaymentController {
    
    @PostMapping
    public ResponseEntity<PaymentResult> processPayment(@RequestBody PaymentRequest request) {
        PaymentResult result = paymentService.process(request);
        return ResponseEntity.ok(result);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<PaymentStatus> getPaymentStatus(@PathVariable Long id) {
        PaymentStatus status = paymentService.getStatus(id);
        return ResponseEntity.ok(status);
    }
    
    @PostMapping("/{id}/refund")
    public ResponseEntity<RefundResult> processRefund(
            @PathVariable Long id,
            @RequestBody RefundRequest request) {
        RefundResult result = paymentService.refund(id, request);
        return ResponseEntity.ok(result);
    }
}
```

### 3. 技术实现要点

#### 服务间通信

```java
// 使用Feign客户端进行服务调用
@FeignClient(name = "user-service", fallback = UserServiceFallback.class)
public interface UserServiceClient {
    
    @GetMapping("/api/users/{id}")
    User getUser(@PathVariable("id") Long id);
    
    @GetMapping("/api/users/{id}/preferences")
    UserPreferences getUserPreferences(@PathVariable("id") Long id);
}

@FeignClient(name = "product-service", fallback = ProductServiceFallback.class)
public interface ProductServiceClient {
    
    @GetMapping("/api/products/{id}")
    Product getProduct(@PathVariable("id") Long id);
    
    @GetMapping("/api/products/{id}/inventory")
    InventoryInfo getProductInventory(@PathVariable("id") Long id);
}

// 订单服务中调用其他服务
@Service
public class OrderService {
    
    @Autowired
    private UserServiceClient userServiceClient;
    
    @Autowired
    private ProductServiceClient productServiceClient;
    
    @Autowired
    private PaymentServiceClient paymentServiceClient;
    
    public Order createOrder(CreateOrderRequest request) {
        // 1. 验证用户
        User user = userServiceClient.getUser(request.getUserId());
        
        // 2. 验证商品和库存
        List<OrderItem> items = new ArrayList<>();
        for (OrderItemRequest itemRequest : request.getItems()) {
            Product product = productServiceClient.getProduct(itemRequest.getProductId());
            InventoryInfo inventory = productServiceClient.getProductInventory(itemRequest.getProductId());
            
            if (inventory.getAvailableQuantity() < itemRequest.getQuantity()) {
                throw new InsufficientInventoryException(
                    "Insufficient inventory for product: " + product.getName());
            }
            
            items.add(new OrderItem(product, itemRequest.getQuantity()));
        }
        
        // 3. 创建订单
        Order order = orderRepository.save(new Order(user, items, request));
        
        // 4. 处理支付
        PaymentRequest paymentRequest = new PaymentRequest(
            order.getId(), 
            order.getTotalAmount(), 
            request.getPaymentMethod()
        );
        
        PaymentResult paymentResult = paymentServiceClient.processPayment(paymentRequest);
        
        // 5. 更新订单状态
        order.setPaymentId(paymentResult.getPaymentId());
        order.setStatus(OrderStatus.PAID);
        orderRepository.save(order);
        
        return order;
    }
}
```

#### 数据一致性处理

```java
// 使用Saga模式处理分布式事务
@Service
public class OrderSagaService {
    
    @Autowired
    private EventPublisher eventPublisher;
    
    public Order createOrder(CreateOrderRequest request) {
        // 1. 创建订单
        Order order = orderRepository.save(new Order(request));
        
        // 2. 发布订单创建事件，触发Saga
        eventPublisher.publish(new OrderCreatedEvent(order));
        
        return order;
    }
}

@Component
public class OrderSagaManager {
    
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        // 执行Saga步骤
        sagaOrchestrator.execute(new CreateOrderSaga(event.getOrder()));
    }
    
    @EventListener
    public void handleOrderPaid(OrderPaidEvent event) {
        // 执行后续步骤
        sagaOrchestrator.execute(new ProcessOrderSaga(event.getOrder()));
    }
}

public class CreateOrderSaga implements Saga {
    private final Order order;
    
    @Override
    public List<SagaStep> getSteps() {
        return Arrays.asList(
            new ValidateInventoryStep(order),
            new ReserveInventoryStep(order),
            new ProcessPaymentStep(order),
            new ConfirmOrderStep(order)
        );
    }
    
    @Override
    public List<SagaStep> getCompensationSteps() {
        return Arrays.asList(
            new CancelOrderStep(order),
            new ReleaseInventoryStep(order),
            new RefundPaymentStep(order)
        );
    }
}
```

## 金融行业中的微服务架构

金融行业对系统的安全性、一致性和可靠性要求极高，微服务架构在金融行业的应用需要特别关注这些方面。

### 1. 业务场景分析

金融行业通常包含以下核心业务模块：

- **账户管理**：账户开立、账户信息管理、账户状态管理
- **交易管理**：转账、支付、清算、结算
- **风险管理**：反欺诈、信用评估、合规检查
- **报表管理**：财务报表、交易明细、审计日志
- **客户服务**：客户信息管理、客户服务、投诉处理

### 2. 微服务架构设计

#### 核心服务划分

```java
// 账户服务 (account-service)
@RestController
@RequestMapping("/api/accounts")
public class AccountController {
    
    @PostMapping
    public ResponseEntity<Account> createAccount(@RequestBody CreateAccountRequest request) {
        Account account = accountService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(account);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<AccountDetail> getAccountDetail(@PathVariable Long id) {
        AccountDetail detail = accountService.getDetail(id);
        return ResponseEntity.ok(detail);
    }
    
    @GetMapping("/{id}/balance")
    public ResponseEntity<BigDecimal> getAccountBalance(@PathVariable Long id) {
        BigDecimal balance = accountService.getBalance(id);
        return ResponseEntity.ok(balance);
    }
    
    @PutMapping("/{id}/status")
    public ResponseEntity<Account> updateAccountStatus(
            @PathVariable Long id,
            @RequestBody UpdateAccountStatusRequest request) {
        Account account = accountService.updateStatus(id, request);
        return ResponseEntity.ok(account);
    }
}

// 交易服务 (transaction-service)
@RestController
@RequestMapping("/api/transactions")
public class TransactionController {
    
    @PostMapping("/transfer")
    public ResponseEntity<TransactionResult> transfer(@RequestBody TransferRequest request) {
        TransactionResult result = transactionService.transfer(request);
        return ResponseEntity.ok(result);
    }
    
    @PostMapping("/payment")
    public ResponseEntity<TransactionResult> payment(@RequestBody PaymentRequest request) {
        TransactionResult result = transactionService.payment(request);
        return ResponseEntity.ok(result);
    }
    
    @GetMapping("/accounts/{accountId}")
    public ResponseEntity<PageResponse<Transaction>> getAccountTransactions(
            @PathVariable Long accountId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        Page<Transaction> transactions = transactionService.getByAccount(accountId, pageable);
        return ResponseEntity.ok(convertToPageResponse(transactions));
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<TransactionDetail> getTransactionDetail(@PathVariable Long id) {
        TransactionDetail detail = transactionService.getDetail(id);
        return ResponseEntity.ok(detail);
    }
}

// 风控服务 (risk-service)
@RestController
@RequestMapping("/api/risk")
public class RiskController {
    
    @PostMapping("/assessment")
    public ResponseEntity<RiskAssessment> assessRisk(@RequestBody RiskRequest request) {
        RiskAssessment assessment = riskService.assess(request);
        return ResponseEntity.ok(assessment);
    }
    
    @PostMapping("/fraud/detection")
    public ResponseEntity<FraudDetectionResult> detectFraud(@RequestBody FraudDetectionRequest request) {
        FraudDetectionResult result = fraudService.detect(request);
        return ResponseEntity.ok(result);
    }
    
    @PostMapping("/compliance/check")
    public ResponseEntity<ComplianceCheckResult> checkCompliance(@RequestBody ComplianceCheckRequest request) {
        ComplianceCheckResult result = complianceService.check(request);
        return ResponseEntity.ok(result);
    }
}

// 报表服务 (report-service)
@RestController
@RequestMapping("/api/reports")
public class ReportController {
    
    @GetMapping("/transactions")
    public ResponseEntity<TransactionReport> getTransactionReport(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate,
            @RequestParam(required = false) String accountType) {
        
        TransactionReport report = reportService.generateTransactionReport(startDate, endDate, accountType);
        return ResponseEntity.ok(report);
    }
    
    @GetMapping("/balances")
    public ResponseEntity<BalanceReport> getBalanceReport(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        
        BalanceReport report = reportService.generateBalanceReport(date);
        return ResponseEntity.ok(report);
    }
    
    @GetMapping("/audit")
    public ResponseEntity<AuditReport> getAuditReport(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        
        AuditReport report = reportService.generateAuditReport(startDate, endDate);
        return ResponseEntity.ok(report);
    }
}
```

### 3. 安全与合规实现

#### 身份认证与授权

```java
// JWT认证配置
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(authorize -> authorize
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers("/api/accounts/**").hasAnyRole("USER", "ADMIN")
                .requestMatchers("/api/transactions/**").hasAnyRole("USER", "ADMIN")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(withDefaults())
            )
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            );
        return http.build();
    }
    
    @Bean
    public JwtDecoder jwtDecoder() {
        return NimbusJwtDecoder.withJwkSetUri("https://auth.example.com/.well-known/jwks.json")
            .build();
    }
}

// 权限控制
@RestController
@RequestMapping("/api/accounts")
public class AccountController {
    
    @PreAuthorize("hasRole('ADMIN') or @accountSecurity.hasAccess(#id, authentication)")
    @GetMapping("/{id}")
    public ResponseEntity<AccountDetail> getAccountDetail(@PathVariable Long id) {
        AccountDetail detail = accountService.getDetail(id);
        return ResponseEntity.ok(detail);
    }
    
    @PreAuthorize("hasRole('ADMIN')")
    @PutMapping("/{id}/status")
    public ResponseEntity<Account> updateAccountStatus(
            @PathVariable Long id,
            @RequestBody UpdateAccountStatusRequest request) {
        Account account = accountService.updateStatus(id, request);
        return ResponseEntity.ok(account);
    }
}

@Component("accountSecurity")
public class AccountSecurity {
    
    public boolean hasAccess(Long accountId, Authentication authentication) {
        // 检查用户是否有权访问该账户
        String username = authentication.getName();
        return accountService.isAccountOwner(accountId, username);
    }
}
```

#### 数据加密与审计

```java
// 敏感数据加密
@Entity
@Table(name = "accounts")
public class Account {
    
    @Id
    private Long id;
    
    @Column(name = "account_number")
    @Convert(converter = AccountNumberConverter.class)
    private String accountNumber;
    
    @Column(name = "balance")
    private BigDecimal balance;
    
    // getters and setters
}

@Converter
public class AccountNumberConverter implements AttributeConverter<String, String> {
    
    @Override
    public String convertToDatabaseColumn(String accountNumber) {
        if (accountNumber == null) return null;
        return EncryptionUtil.encrypt(accountNumber);
    }
    
    @Override
    public String convertToEntityAttribute(String encryptedAccountNumber) {
        if (encryptedAccountNumber == null) return null;
        return EncryptionUtil.decrypt(encryptedAccountNumber);
    }
}

// 审计日志
@Entity
@Table(name = "audit_logs")
public class AuditLog {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "user_id")
    private Long userId;
    
    @Column(name = "action")
    private String action;
    
    @Column(name = "resource_type")
    private String resourceType;
    
    @Column(name = "resource_id")
    private Long resourceId;
    
    @Column(name = "timestamp")
    private Instant timestamp;
    
    @Column(name = "ip_address")
    private String ipAddress;
    
    @Column(name = "user_agent")
    private String userAgent;
    
    // getters and setters
}

@Aspect
@Component
public class AuditAspect {
    
    @Autowired
    private AuditLogService auditLogService;
    
    @Around("@annotation(Auditable)")
    public Object audit(ProceedingJoinPoint joinPoint) throws Throwable {
        // 记录操作前的状态
        AuditLog auditLog = createAuditLog(joinPoint);
        
        try {
            Object result = joinPoint.proceed();
            auditLog.setStatus("SUCCESS");
            auditLogService.save(auditLog);
            return result;
        } catch (Exception e) {
            auditLog.setStatus("FAILED");
            auditLog.setErrorMessage(e.getMessage());
            auditLogService.save(auditLog);
            throw e;
        }
    }
    
    private AuditLog createAuditLog(ProceedingJoinPoint joinPoint) {
        AuditLog auditLog = new AuditLog();
        auditLog.setAction(joinPoint.getSignature().getName());
        auditLog.setTimestamp(Instant.now());
        // 设置其他字段...
        return auditLog;
    }
}
```

## 社交平台与游戏中的微服务架构

社交平台和游戏应用具有用户量大、实时性要求高、功能复杂等特点，微服务架构能够很好地满足这些需求。

### 1. 业务场景分析

社交平台和游戏通常包含以下核心业务模块：

- **用户管理**：用户注册、登录、个人信息、好友关系
- **内容管理**：动态发布、评论、点赞、分享
- **消息管理**：私信、通知、推送
- **推荐系统**：内容推荐、好友推荐、游戏匹配
- **游戏管理**：游戏房间、游戏状态、排行榜

### 2. 微服务架构设计

#### 核心服务划分

```java
// 用户服务 (user-service)
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @PostMapping("/register")
    public ResponseEntity<UserRegistrationResponse> registerUser(
            @RequestBody UserRegistrationRequest request) {
        User user = userService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(new UserRegistrationResponse(user.getId(), "User registered successfully"));
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<UserProfile> getUserProfile(@PathVariable Long id) {
        UserProfile profile = userService.getProfile(id);
        return ResponseEntity.ok(profile);
    }
    
    @GetMapping("/{id}/friends")
    public ResponseEntity<List<User>> getUserFriends(@PathVariable Long id) {
        List<User> friends = userService.getFriends(id);
        return ResponseEntity.ok(friends);
    }
    
    @PostMapping("/{id}/friends/{friendId}")
    public ResponseEntity<Friendship> addFriend(
            @PathVariable Long id,
            @PathVariable Long friendId) {
        Friendship friendship = userService.addFriend(id, friendId);
        return ResponseEntity.ok(friendship);
    }
}

// 内容服务 (content-service)
@RestController
@RequestMapping("/api/content")
public class ContentController {
    
    @PostMapping("/posts")
    public ResponseEntity<Post> createPost(@RequestBody CreatePostRequest request) {
        Post post = contentService.createPost(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(post);
    }
    
    @GetMapping("/posts")
    public ResponseEntity<PageResponse<Post>> getPosts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        Page<Post> posts = contentService.getPosts(pageable);
        return ResponseEntity.ok(convertToPageResponse(posts));
    }
    
    @PostMapping("/posts/{postId}/comments")
    public ResponseEntity<Comment> addComment(
            @PathVariable Long postId,
            @RequestBody AddCommentRequest request) {
        Comment comment = contentService.addComment(postId, request);
        return ResponseEntity.status(HttpStatus.CREATED).body(comment);
    }
    
    @PostMapping("/posts/{postId}/likes")
    public ResponseEntity<Like> addLike(@PathVariable Long postId) {
        Like like = contentService.addLike(postId);
        return ResponseEntity.status(HttpStatus.CREATED).body(like);
    }
}

// 消息服务 (message-service)
@RestController
@RequestMapping("/api/messages")
public class MessageController {
    
    @PostMapping("/private")
    public ResponseEntity<PrivateMessage> sendPrivateMessage(
            @RequestBody SendPrivateMessageRequest request) {
        PrivateMessage message = messageService.sendPrivateMessage(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(message);
    }
    
    @GetMapping("/private/conversations/{userId}")
    public ResponseEntity<List<PrivateMessage>> getPrivateMessages(
            @PathVariable Long userId,
            @RequestParam Long otherUserId) {
        List<PrivateMessage> messages = messageService.getPrivateMessages(userId, otherUserId);
        return ResponseEntity.ok(messages);
    }
    
    @PostMapping("/notifications")
    public ResponseEntity<Notification> sendNotification(
            @RequestBody SendNotificationRequest request) {
        Notification notification = notificationService.send(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(notification);
    }
    
    @GetMapping("/notifications/users/{userId}")
    public ResponseEntity<List<Notification>> getUserNotifications(@PathVariable Long userId) {
        List<Notification> notifications = notificationService.getByUser(userId);
        return ResponseEntity.ok(notifications);
    }
}

// 推荐服务 (recommendation-service)
@RestController
@RequestMapping("/api/recommendations")
public class RecommendationController {
    
    @GetMapping("/content/users/{userId}")
    public ResponseEntity<List<RecommendedContent>> getContentRecommendations(@PathVariable Long userId) {
        List<RecommendedContent> recommendations = recommendationService.getContentRecommendations(userId);
        return ResponseEntity.ok(recommendations);
    }
    
    @GetMapping("/friends/users/{userId}")
    public ResponseEntity<List<RecommendedUser>> getFriendRecommendations(@PathVariable Long userId) {
        List<RecommendedUser> recommendations = recommendationService.getFriendRecommendations(userId);
        return ResponseEntity.ok(recommendations);
    }
    
    @PostMapping("/feedback")
    public ResponseEntity<Void> recordFeedback(@RequestBody RecommendationFeedback feedback) {
        recommendationService.recordFeedback(feedback);
        return ResponseEntity.ok().build();
    }
}
```

### 3. 实时通信实现

#### WebSocket支持

```java
// WebSocket配置
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {
    
    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        registry.enableSimpleBroker("/topic", "/queue");
        registry.setApplicationDestinationPrefixes("/app");
    }
    
    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws")
            .setAllowedOriginPatterns("*")
            .withSockJS();
    }
}

// 实时消息控制器
@Controller
public class RealTimeMessageController {
    
    @MessageMapping("/chat")
    @SendTo("/topic/messages")
    public ChatMessage sendChatMessage(ChatMessage message) {
        message.setTimestamp(Instant.now());
        chatService.saveMessage(message);
        return message;
    }
    
    @MessageMapping("/notifications")
    @SendTo("/queue/notifications/{userId}")
    public Notification sendNotification(@DestinationVariable Long userId, Notification notification) {
        notification.setTimestamp(Instant.now());
        notificationService.save(notification);
        return notification;
    }
}

// 前端JavaScript示例
const socket = new SockJS('/ws');
const stompClient = Stomp.over(socket);

stompClient.connect({}, function (frame) {
    console.log('Connected: ' + frame);
    
    // 订阅聊天消息
    stompClient.subscribe('/topic/messages', function (message) {
        showMessage(JSON.parse(message.body));
    });
    
    // 订阅个人通知
    stompClient.subscribe('/queue/notifications/' + userId, function (notification) {
        showNotification(JSON.parse(notification.body));
    });
});
```

#### Redis Pub/Sub

```java
// Redis消息发布
@Service
public class NotificationService {
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    public void sendNotification(Notification notification) {
        // 保存通知到数据库
        notificationRepository.save(notification);
        
        // 发布到Redis频道
        String channel = "notifications:user:" + notification.getUserId();
        redisTemplate.convertAndSend(channel, notification);
    }
}

// Redis消息订阅
@Component
public class NotificationSubscriber {
    
    @Autowired
    private SimpMessagingTemplate messagingTemplate;
    
    @RedisListener(patterns = "notifications:user:*")
    public void handleNotification(Notification notification) {
        // 推送到WebSocket客户端
        String destination = "/queue/notifications/" + notification.getUserId();
        messagingTemplate.convertAndSend(destination, notification);
    }
}
```

## 物联网（IoT）中的微服务架构

物联网应用具有设备量大、数据量大、实时性要求高等特点，微服务架构能够很好地支持这些需求。

### 1. 业务场景分析

物联网应用通常包含以下核心业务模块：

- **设备管理**：设备注册、设备状态、设备配置
- **数据采集**：传感器数据收集、数据预处理
- **数据处理**：数据分析、规则引擎、机器学习
- **设备控制**：远程控制、自动化规则
- **告警管理**：异常检测、告警通知

### 2. 微服务架构设计

#### 核心服务划分

```java
// 设备管理服务 (device-service)
@RestController
@RequestMapping("/api/devices")
public class DeviceController {
    
    @PostMapping
    public ResponseEntity<Device> registerDevice(@RequestBody RegisterDeviceRequest request) {
        Device device = deviceService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(device);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<Device> getDevice(@PathVariable String id) {
        Device device = deviceService.getDevice(id);
        return ResponseEntity.ok(device);
    }
    
    @GetMapping
    public ResponseEntity<PageResponse<Device>> getDevices(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        Page<Device> devices = deviceService.getDevices(pageable);
        return ResponseEntity.ok(convertToPageResponse(devices));
    }
    
    @PutMapping("/{id}/status")
    public ResponseEntity<Device> updateDeviceStatus(
            @PathVariable String id,
            @RequestBody UpdateDeviceStatusRequest request) {
        Device device = deviceService.updateStatus(id, request);
        return ResponseEntity.ok(device);
    }
}

// 数据采集服务 (data-collection-service)
@RestController
@RequestMapping("/api/data")
public class DataCollectionController {
    
    @PostMapping("/telemetry")
    public ResponseEntity<Void> collectTelemetry(@RequestBody TelemetryData data) {
        dataCollectionService.processTelemetry(data);
        return ResponseEntity.ok().build();
    }
    
    @PostMapping("/batch")
    public ResponseEntity<Void> collectBatchData(@RequestBody List<TelemetryData> dataList) {
        dataCollectionService.processBatch(dataList);
        return ResponseEntity.ok().build();
    }
    
    @GetMapping("/devices/{deviceId}")
    public ResponseEntity<PageResponse<TelemetryData>> getDeviceData(
            @PathVariable String deviceId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "100") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        Page<TelemetryData> data = dataCollectionService.getDeviceData(
            deviceId, startTime, endTime, pageable);
        return ResponseEntity.ok(convertToPageResponse(data));
    }
}

// 数据处理服务 (data-processing-service)
@RestController
@RequestMapping("/api/processing")
public class DataProcessingController {
    
    @PostMapping("/rules")
    public ResponseEntity<ProcessingRule> createRule(@RequestBody CreateRuleRequest request) {
        ProcessingRule rule = processingService.createRule(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(rule);
    }
    
    @PostMapping("/analytics")
    public ResponseEntity<AnalyticsResult> runAnalytics(@RequestBody AnalyticsRequest request) {
        AnalyticsResult result = analyticsService.run(request);
        return ResponseEntity.ok(result);
    }
    
    @PostMapping("/ml/predict")
    public ResponseEntity<PredictionResult> predict(@RequestBody PredictionRequest request) {
        PredictionResult result = mlService.predict(request);
        return ResponseEntity.ok(result);
    }
}

// 设备控制服务 (device-control-service)
@RestController
@RequestMapping("/api/control")
public class DeviceControlController {
    
    @PostMapping("/commands")
    public ResponseEntity<CommandResult> sendCommand(@RequestBody SendCommandRequest request) {
        CommandResult result = deviceControlService.sendCommand(request);
        return ResponseEntity.ok(result);
    }
    
    @PostMapping("/rules")
    public ResponseEntity<ControlRule> createControlRule(@RequestBody CreateControlRuleRequest request) {
        ControlRule rule = deviceControlService.createRule(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(rule);
    }
    
    @GetMapping("/rules/devices/{deviceId}")
    public ResponseEntity<List<ControlRule>> getDeviceRules(@PathVariable String deviceId) {
        List<ControlRule> rules = deviceControlService.getDeviceRules(deviceId);
        return ResponseEntity.ok(rules);
    }
}

// 告警服务 (alert-service)
@RestController
@RequestMapping("/api/alerts")
public class AlertController {
    
    @PostMapping
    public ResponseEntity<Alert> createAlert(@RequestBody CreateAlertRequest request) {
        Alert alert = alertService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(alert);
    }
    
    @GetMapping("/devices/{deviceId}")
    public ResponseEntity<PageResponse<Alert>> getDeviceAlerts(
            @PathVariable String deviceId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        Page<Alert> alerts = alertService.getByDevice(deviceId, pageable);
        return ResponseEntity.ok(convertToPageResponse(alerts));
    }
    
    @PostMapping("/notifications")
    public ResponseEntity<Void> sendNotification(@RequestBody AlertNotification notification) {
        notificationService.send(notification);
        return ResponseEntity.ok().build();
    }
}
```

### 3. 高并发处理实现

#### 消息队列处理

```java
// 使用Kafka处理高并发数据
@Configuration
public class KafkaConfig {
    
    @Bean
    public ProducerFactory<String, TelemetryData> producerFactory() {
        Map<String, Object> configProps = new HashMap<>();
        configProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        configProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        configProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
        return new DefaultKafkaProducerFactory<>(configProps);
    }
    
    @Bean
    public KafkaTemplate<String, TelemetryData> kafkaTemplate() {
        return new KafkaTemplate<>(producerFactory());
    }
}

@Service
public class DataCollectionService {
    
    @Autowired
    private KafkaTemplate<String, TelemetryData> kafkaTemplate;
    
    public void processTelemetry(TelemetryData data) {
        // 异步处理数据
        kafkaTemplate.send("telemetry-data", data.getDeviceId(), data);
    }
}

@Component
public class TelemetryDataProcessor {
    
    @KafkaListener(topics = "telemetry-data")
    public void processTelemetryData(ConsumerRecord<String, TelemetryData> record) {
        TelemetryData data = record.value();
        
        try {
            // 1. 数据验证
            if (!validateData(data)) {
                log.warn("Invalid data received: {}", data);
                return;
            }
            
            // 2. 数据存储
            dataStorageService.save(data);
            
            // 3. 规则处理
            ruleEngineService.process(data);
            
            // 4. 异常检测
            anomalyDetectionService.detect(data);
            
        } catch (Exception e) {
            log.error("Error processing telemetry data: {}", data, e);
            // 发送到死信队列进行重试
            kafkaTemplate.send("telemetry-data-dlq", data);
        }
    }
}
```

#### 批量处理优化

```java
@Service
public class BatchProcessingService {
    
    private final List<TelemetryData> batchBuffer = new ArrayList<>();
    private final Object batchLock = new Object();
    private static final int BATCH_SIZE = 1000;
    private static final long BATCH_TIMEOUT = 5000; // 5秒
    
    @Scheduled(fixedRate = 1000) // 每秒检查一次
    public void processBatch() {
        synchronized (batchLock) {
            if (batchBuffer.isEmpty()) {
                return;
            }
            
            // 检查是否达到批次大小或超时
            if (batchBuffer.size() >= BATCH_SIZE || 
                System.currentTimeMillis() - getLastBatchTime() > BATCH_TIMEOUT) {
                
                List<TelemetryData> batch = new ArrayList<>(batchBuffer);
                batchBuffer.clear();
                
                // 异步处理批次
                CompletableFuture.runAsync(() -> processBatchData(batch));
            }
        }
    }
    
    public void addData(TelemetryData data) {
        synchronized (batchLock) {
            batchBuffer.add(data);
        }
    }
    
    private void processBatchData(List<TelemetryData> batch) {
        try {
            // 批量插入数据库
            dataStorageService.batchSave(batch);
            
            // 批量规则处理
            ruleEngineService.batchProcess(batch);
            
        } catch (Exception e) {
            log.error("Error processing batch data, size: {}", batch.size(), e);
            // 重新加入缓冲区进行重试
            synchronized (batchLock) {
                batchBuffer.addAll(batch);
            }
        }
    }
}
```

## 总结

通过以上行业应用案例的分析，我们可以看到微服务架构在不同领域的广泛应用和价值体现：

1. **电商平台**：通过合理的服务划分和分布式事务处理，实现了复杂的业务逻辑和高并发处理能力
2. **金融行业**：通过严格的安全控制和合规要求，确保了系统的安全性和可靠性
3. **社交平台与游戏**：通过实时通信技术和推荐算法，提供了良好的用户体验
4. **物联网**：通过高并发处理和边缘计算，支持了大规模设备连接和数据处理

关键要点包括：

1. **业务驱动**：根据具体业务场景合理划分服务边界
2. **技术选型**：选择合适的技术栈满足业务需求
3. **安全合规**：在金融等敏感行业特别关注安全和合规要求
4. **性能优化**：针对高并发场景采用批量处理、缓存等优化手段
5. **实时性保障**：在社交和游戏场景中重视实时通信能力

在下一章中，我们将对微服务架构进行总结和展望，探讨未来的发展趋势。

通过本章的学习，我们了解了微服务架构在不同行业的实际应用情况。这些案例将帮助我们在实际项目中更好地设计和实施微服务架构，为业务发展提供技术支撑。