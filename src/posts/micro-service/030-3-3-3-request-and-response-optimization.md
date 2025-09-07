---
title: 请求与响应的优化：提升微服务通信效率
date: 2025-08-30
categories: [Microservices]
tags: [micro-service]
published: true
---

在微服务架构中，服务间的通信效率直接影响整个系统的性能表现。随着服务数量的增加和调用链路的复杂化，请求与响应的优化成为提升系统整体性能的关键因素。本文将深入探讨微服务中请求与响应优化的策略、技术和最佳实践，帮助构建高效、可靠的分布式系统。

## 微服务通信优化基础

### 通信协议选择

选择合适的通信协议是优化的第一步。

#### REST vs gRPC

```java
// RESTful API示例
@RestController
public class UserServiceRest {
    
    @GetMapping("/api/users/{id}")
    public ResponseEntity<UserDto> getUser(@PathVariable Long id) {
        User user = userService.getUser(id);
        UserDto userDto = UserDto.from(user);
        return ResponseEntity.ok(userDto);
    }
    
    @PostMapping("/api/users")
    public ResponseEntity<UserDto> createUser(@RequestBody CreateUserRequest request) {
        User user = userService.createUser(request);
        UserDto userDto = UserDto.from(user);
        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(user.getId())
            .toUri();
        return ResponseEntity.created(location).body(userDto);
    }
}

// gRPC服务示例
@GrpcService
public class UserServiceGrpc extends UserServiceGrpc.UserServiceImplBase {
    
    @Override
    public void getUser(GetUserRequest request, 
                       StreamObserver<GetUserResponse> responseObserver) {
        try {
            User user = userService.getUser(request.getUserId());
            
            GetUserResponse response = GetUserResponse.newBuilder()
                .setUser(UserProto.newBuilder()
                    .setId(user.getId())
                    .setName(user.getName())
                    .setEmail(user.getEmail())
                    .build())
                .build();
                
            responseObserver.onNext(response);
            responseObserver.onCompleted();
        } catch (Exception e) {
            responseObserver.onError(e);
        }
    }
    
    @Override
    public void createUser(CreateUserRequest request, 
                          StreamObserver<CreateUserResponse> responseObserver) {
        try {
            User user = userService.createUser(request.getName(), request.getEmail());
            
            CreateUserResponse response = CreateUserResponse.newBuilder()
                .setUser(UserProto.newBuilder()
                    .setId(user.getId())
                    .setName(user.getName())
                    .setEmail(user.getEmail())
                    .build())
                .build();
                
            responseObserver.onNext(response);
            responseObserver.onCompleted();
        } catch (Exception e) {
            responseObserver.onError(e);
        }
    }
}
```

#### 协议性能对比

```java
// 性能测试对比
@Component
public class ProtocolPerformanceTest {
    
    public void compareProtocols() {
        // 测试REST性能
        long restStartTime = System.currentTimeMillis();
        for (int i = 0; i < 1000; i++) {
            restTemplate.getForObject("http://user-service/api/users/1", UserDto.class);
        }
        long restEndTime = System.currentTimeMillis();
        long restDuration = restEndTime - restStartTime;
        
        // 测试gRPC性能
        long grpcStartTime = System.currentTimeMillis();
        for (int i = 0; i < 1000; i++) {
            userServiceGrpcStub.getUser(GetUserRequest.newBuilder().setUserId(1).build());
        }
        long grpcEndTime = System.currentTimeMillis();
        long grpcDuration = grpcEndTime - grpcStartTime;
        
        logger.info("REST duration: {}ms", restDuration);
        logger.info("gRPC duration: {}ms", grpcDuration);
        logger.info("Performance improvement: {}%", 
            (restDuration - grpcDuration) * 100 / restDuration);
    }
}
```

### 数据序列化优化

选择高效的序列化方式可以显著提升通信性能。

```java
// 不同序列化方式对比
@Component
public class SerializationBenchmark {
    
    public void benchmarkSerializations() {
        User user = createTestUser();
        
        // JSON序列化
        long jsonStart = System.currentTimeMillis();
        String jsonString = objectMapper.writeValueAsString(user);
        User userFromJson = objectMapper.readValue(jsonString, User.class);
        long jsonEnd = System.currentTimeMillis();
        
        // Protocol Buffers序列化
        long protobufStart = System.currentTimeMillis();
        UserProto userProto = convertToProto(user);
        byte[] protoBytes = userProto.toByteArray();
        UserProto userProtoFromBytes = UserProto.parseFrom(protoBytes);
        User userFromProto = convertFromProto(userProtoFromBytes);
        long protobufEnd = System.currentTimeMillis();
        
        // Java原生序列化
        long javaStart = System.currentTimeMillis();
        byte[] javaBytes = serializeJava(user);
        User userFromJava = deserializeJava(javaBytes);
        long javaEnd = System.currentTimeMillis();
        
        logger.info("JSON serialization time: {}ms", jsonEnd - jsonStart);
        logger.info("Protocol Buffers serialization time: {}ms", protobufEnd - protobufStart);
        logger.info("Java serialization time: {}ms", javaEnd - javaStart);
    }
    
    private User createTestUser() {
        return new User(1L, "John Doe", "john.doe@example.com", 
            Arrays.asList("ROLE_USER", "ROLE_CUSTOMER"));
    }
    
    private UserProto convertToProto(User user) {
        return UserProto.newBuilder()
            .setId(user.getId())
            .setName(user.getName())
            .setEmail(user.getEmail())
            .addAllRoles(user.getRoles())
            .build();
    }
    
    private User convertFromProto(UserProto userProto) {
        return new User(userProto.getId(), userProto.getName(), userProto.getEmail(),
            userProto.getRolesList());
    }
}
```

## 请求优化策略

### 1. 批量请求处理

批量处理可以减少网络往返次数，提升整体性能。

```java
// 批量请求处理
@RestController
public class BatchUserController {
    
    @PostMapping("/api/users/batch")
    public ResponseEntity<List<UserDto>> batchCreateUsers(
            @RequestBody List<CreateUserRequest> requests) {
        // 批量创建用户
        List<User> users = userService.batchCreateUsers(requests);
        
        List<UserDto> userDtos = users.stream()
            .map(UserDto::from)
            .collect(Collectors.toList());
            
        return ResponseEntity.ok(userDtos);
    }
    
    @GetMapping("/api/users/batch")
    public ResponseEntity<List<UserDto>> batchGetUsers(
            @RequestParam List<Long> userIds) {
        // 批量获取用户
        List<User> users = userService.batchGetUsers(userIds);
        
        List<UserDto> userDtos = users.stream()
            .map(UserDto::from)
            .collect(Collectors.toList());
            
        return ResponseEntity.ok(userDtos);
    }
}

// 服务层批量处理实现
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public List<User> batchCreateUsers(List<CreateUserRequest> requests) {
        List<User> users = requests.stream()
            .map(request -> new User(request.getName(), request.getEmail()))
            .collect(Collectors.toList());
            
        // 批量插入数据库
        return userRepository.saveAll(users);
    }
    
    public List<User> batchGetUsers(List<Long> userIds) {
        // 使用IN查询批量获取
        return userRepository.findAllById(userIds);
    }
}
```

### 2. 请求缓存

合理使用缓存可以避免重复请求，提升响应速度。

```java
// 请求缓存实现
@Service
public class CachedUserService {
    
    @Autowired
    private UserService userService;
    
    // 本地缓存
    private final Cache<String, User> localCache = Caffeine.newBuilder()
        .maximumSize(1000)
        .expireAfterWrite(10, TimeUnit.MINUTES)
        .build();
    
    // 分布式缓存
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    @Cacheable(value = "users", key = "#userId")
    public User getUser(Long userId) {
        // 首先检查本地缓存
        User user = localCache.getIfPresent("user:" + userId);
        if (user != null) {
            return user;
        }
        
        // 检查分布式缓存
        user = (User) redisTemplate.opsForValue().get("user:" + userId);
        if (user != null) {
            localCache.put("user:" + userId, user);
            return user;
        }
        
        // 查询数据库
        user = userService.getUser(userId);
        if (user != null) {
            // 更新缓存
            redisTemplate.opsForValue().set("user:" + userId, user, 
                Duration.ofHours(1));
            localCache.put("user:" + userId, user);
        }
        
        return user;
    }
    
    @CacheEvict(value = "users", key = "#user.id")
    public User updateUser(User user) {
        User updatedUser = userService.updateUser(user);
        
        // 更新缓存
        redisTemplate.opsForValue().set("user:" + user.getId(), updatedUser, 
            Duration.ofHours(1));
        localCache.put("user:" + user.getId(), updatedUser);
        
        return updatedUser;
    }
}
```

### 3. 请求合并

将多个小请求合并为一个大请求，减少网络开销。

```java
// 请求合并实现
@Service
public class RequestAggregationService {
    
    private final ExecutorService executorService = 
        Executors.newFixedThreadPool(10);
    
    public CompletableFuture<AggregatedResponse> aggregateRequests(
            List<Request> requests) {
        // 将请求按服务分组
        Map<String, List<Request>> groupedRequests = 
            requests.stream().collect(Collectors.groupingBy(Request::getService));
        
        // 并行处理各组请求
        List<CompletableFuture<ServiceResponse>> futures = 
            groupedRequests.entrySet().stream()
                .map(entry -> processServiceRequests(entry.getKey(), entry.getValue()))
                .collect(Collectors.toList());
        
        // 等待所有请求完成并合并结果
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> {
                AggregatedResponse response = new AggregatedResponse();
                futures.forEach(future -> {
                    try {
                        response.addServiceResponse(future.get());
                    } catch (Exception e) {
                        logger.error("Error processing service response", e);
                    }
                });
                return response;
            });
    }
    
    private CompletableFuture<ServiceResponse> processServiceRequests(
            String service, List<Request> requests) {
        return CompletableFuture.supplyAsync(() -> {
            // 批量处理同一服务的请求
            return callServiceBatch(service, requests);
        }, executorService);
    }
    
    private ServiceResponse callServiceBatch(String service, List<Request> requests) {
        // 实现批量调用逻辑
        return new ServiceResponse(service, requests);
    }
}
```

## 响应优化策略

### 1. 数据压缩

对响应数据进行压缩可以减少网络传输量。

```java
// 响应压缩配置
@Configuration
public class CompressionConfig {
    
    @Bean
    public CompressionCustomizer compressionCustomizer() {
        return compression -> {
            compression.setEnabled(true);
            compression.setMimeTypes("application/json", "text/html", 
                "text/css", "application/javascript");
            compression.setMinResponseSize(DataSize.ofBytes(2048));
        };
    }
}

// 自定义响应压缩
@RestController
public class OptimizedResponseController {
    
    @GetMapping(value = "/api/data", produces = "application/json")
    public ResponseEntity<List<Data>> getLargeData() {
        List<Data> data = dataService.getLargeDataset();
        
        // 根据客户端支持的编码格式返回压缩数据
        return ResponseEntity.ok()
            .header("Content-Encoding", "gzip")
            .body(data);
    }
    
    // 字段选择优化
    @GetMapping("/api/users/{id}")
    public ResponseEntity<UserDto> getUser(
            @PathVariable Long id,
            @RequestParam(required = false) String fields) {
        User user = userService.getUser(id);
        
        if (fields != null) {
            // 只返回指定字段
            UserDto userDto = UserDto.from(user, fields);
            return ResponseEntity.ok(userDto);
        }
        
        return ResponseEntity.ok(UserDto.from(user));
    }
}
```

### 2. 分页和懒加载

合理使用分页和懒加载避免一次性返回大量数据。

```java
// 分页优化实现
@RestController
public class PaginatedUserController {
    
    @GetMapping("/api/users")
    public ResponseEntity<Page<UserDto>> getUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "id") String sortBy,
            @RequestParam(defaultValue = "asc") String sortDir) {
        
        Sort sort = sortDir.equalsIgnoreCase("desc") ? 
            Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<User> users = userService.getUsers(pageable);
        Page<UserDto> userDtos = users.map(UserDto::from);
        
        return ResponseEntity.ok(userDtos);
    }
    
    // 游标分页
    @GetMapping("/api/users/cursor")
    public ResponseEntity<CursorPage<UserDto>> getUsersWithCursor(
            @RequestParam(required = false) Long cursor,
            @RequestParam(defaultValue = "20") int limit) {
        
        CursorPage<User> users = userService.getUsersWithCursor(cursor, limit);
        CursorPage<UserDto> userDtos = users.map(UserDto::from);
        
        return ResponseEntity.ok(userDtos);
    }
}

// 游标分页实现
@Service
public class UserService {
    
    public CursorPage<User> getUsersWithCursor(Long cursor, int limit) {
        List<User> users;
        Long nextCursor;
        
        if (cursor == null) {
            // 第一页
            users = userRepository.findFirstNOrderByCreatedTimeAsc(limit + 1);
        } else {
            // 后续页
            users = userRepository.findNAfterCursorOrderByCreatedTimeAsc(cursor, limit + 1);
        }
        
        boolean hasNext = users.size() > limit;
        if (hasNext) {
            users = users.subList(0, limit);
            nextCursor = users.get(users.size() - 1).getId();
        } else {
            nextCursor = null;
        }
        
        return new CursorPage<>(users, nextCursor, hasNext);
    }
}
```

### 3. 响应缓存

合理使用响应缓存减少重复计算。

```java
// 响应缓存实现
@RestController
public class CachedResponseController {
    
    @GetMapping("/api/reports/sales")
    @Cacheable(value = "sales-reports", key = "{#startDate, #endDate}")
    public ResponseEntity<SalesReport> getSalesReport(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        
        SalesReport report = reportService.generateSalesReport(startDate, endDate);
        return ResponseEntity.ok(report);
    }
    
    // 条件缓存
    @GetMapping("/api/users/{id}")
    @Cacheable(value = "users", key = "#id", condition = "#id > 0")
    public ResponseEntity<UserDto> getUser(@PathVariable Long id) {
        User user = userService.getUser(id);
        return ResponseEntity.ok(UserDto.from(user));
    }
    
    // 缓存更新
    @PutMapping("/api/users/{id}")
    @CacheEvict(value = "users", key = "#id")
    public ResponseEntity<UserDto> updateUser(@PathVariable Long id, 
                                            @RequestBody UpdateUserRequest request) {
        User user = userService.updateUser(id, request);
        return ResponseEntity.ok(UserDto.from(user));
    }
}
```

## 高级优化技术

### 1. 异步处理

使用异步处理提升并发性能。

```java
// 异步响应处理
@RestController
public class AsyncResponseController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping("/api/users/{id}/async")
    public CompletableFuture<ResponseEntity<UserDto>> getUserAsync(
            @PathVariable Long id) {
        return CompletableFuture.supplyAsync(() -> {
            User user = userService.getUser(id);
            return ResponseEntity.ok(UserDto.from(user));
        });
    }
    
    // WebFlux异步处理
    @GetMapping("/api/users/{id}/reactive")
    public Mono<ResponseEntity<UserDto>> getUserReactive(@PathVariable Long id) {
        return userService.getUserReactive(id)
            .map(UserDto::from)
            .map(ResponseEntity::ok)
            .defaultIfEmpty(ResponseEntity.notFound().build());
    }
}

// Reactive服务实现
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public Mono<User> getUserReactive(Long id) {
        return userRepository.findByIdReactive(id)
            .switchIfEmpty(Mono.error(new UserNotFoundException(id)));
    }
    
    public Flux<User> getUsersReactive(Pageable pageable) {
        return userRepository.findAllReactive(pageable);
    }
}
```

### 2. 连接池优化

优化网络连接池提升并发处理能力。

```java
// HTTP客户端连接池配置
@Configuration
public class HttpClientConfig {
    
    @Bean
    public WebClient webClient() {
        return WebClient.builder()
            .clientConnector(new ReactorClientHttpConnector(
                HttpClient.create()
                    .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 5000)
                    .responseTimeout(Duration.ofSeconds(10))
                    .compress(true)
                    .keepAlive(true)
                    .tcpConfiguration(tcpClient -> 
                        tcpClient.option(ChannelOption.SO_KEEPALIVE, true)
                                 .option(ChannelOption.TCP_NODELAY, true)
                                 .option(ChannelOption.SO_REUSEADDR, true)
                    )
            ))
            .build();
    }
    
    // 数据库连接池优化
    @Bean
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:mysql://localhost:3306/mydb");
        config.setUsername("user");
        config.setPassword("password");
        config.setMaximumPoolSize(50);      // 最大连接数
        config.setMinimumIdle(10);          // 最小空闲连接
        config.setConnectionTimeout(30000); // 连接超时
        config.setIdleTimeout(600000);      // 空闲超时
        config.setMaxLifetime(1800000);     // 最大生命周期
        config.setLeakDetectionThreshold(60000); // 连接泄漏检测
        return new HikariDataSource(config);
    }
}
```

### 3. 预加载和预取

使用预加载和预取技术提升用户体验。

```java
// 预加载实现
@Service
public class PreloadService {
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private OrderService orderService;
    
    public CompletableFuture<PreloadedData> preloadUserData(Long userId) {
        // 并行预加载用户相关数据
        CompletableFuture<User> userFuture = 
            CompletableFuture.supplyAsync(() -> userService.getUser(userId));
        
        CompletableFuture<List<Order>> ordersFuture = 
            CompletableFuture.supplyAsync(() -> orderService.getUserOrders(userId));
        
        CompletableFuture<UserProfile> profileFuture = 
            CompletableFuture.supplyAsync(() -> userService.getUserProfile(userId));
        
        // 等待所有数据加载完成
        return CompletableFuture.allOf(userFuture, ordersFuture, profileFuture)
            .thenApply(v -> new PreloadedData(
                userFuture.join(),
                ordersFuture.join(),
                profileFuture.join()
            ));
    }
}

// 预取实现
@RestController
public class PrefetchController {
    
    @GetMapping("/api/dashboard")
    public ResponseEntity<DashboardData> getDashboard(
            @RequestParam Long userId,
            @RequestParam(defaultValue = "false") boolean prefetch) {
        
        DashboardData dashboard = dashboardService.getDashboard(userId);
        
        if (prefetch) {
            // 异步预取下一页数据
            CompletableFuture.runAsync(() -> {
                prefetchNextPageData(userId);
            });
        }
        
        return ResponseEntity.ok(dashboard);
    }
    
    private void prefetchNextPageData(Long userId) {
        // 实现预取逻辑
        logger.info("Prefetching data for user: {}", userId);
    }
}
```

## 性能优化最佳实践

### 1. 监控和度量

建立完善的监控体系跟踪优化效果。

```java
// 性能监控指标
@Component
public class RequestResponseMetrics {
    
    private final MeterRegistry meterRegistry;
    
    // 请求处理时间
    private final Timer requestProcessingTimer;
    
    // 响应大小
    private final DistributionSummary responseSizeSummary;
    
    // 缓存命中率
    private final Counter cacheHitCounter;
    private final Counter cacheMissCounter;
    
    public RequestResponseMetrics(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.requestProcessingTimer = Timer.builder("http.request.processing.time")
            .description("HTTP Request Processing Time")
            .register(meterRegistry);
        this.responseSizeSummary = DistributionSummary.builder("http.response.size")
            .description("HTTP Response Size")
            .register(meterRegistry);
        this.cacheHitCounter = Counter.builder("cache.hits")
            .description("Cache Hits")
            .register(meterRegistry);
        this.cacheMissCounter = Counter.builder("cache.misses")
            .description("Cache Misses")
            .register(meterRegistry);
    }
    
    public <T> T recordRequestProcessing(Supplier<T> operation) {
        return requestProcessingTimer.record(operation);
    }
    
    public void recordResponseSize(long size) {
        responseSizeSummary.record(size);
    }
    
    public void recordCacheHit() {
        cacheHitCounter.increment();
    }
    
    public void recordCacheMiss() {
        cacheMissCounter.increment();
    }
    
    public double getCacheHitRate() {
        long hits = (long) cacheHitCounter.count();
        long misses = (long) cacheMissCounter.count();
        long total = hits + misses;
        
        return total > 0 ? (double) hits / total : 0.0;
    }
}
```

### 2. A/B测试

通过A/B测试验证优化效果。

```java
// A/B测试实现
@Service
public class OptimizationABTest {
    
    private final Map<String, OptimizationStrategy> strategies = new HashMap<>();
    
    public OptimizationABTest() {
        strategies.put("baseline", new BaselineStrategy());
        strategies.put("optimized", new OptimizedStrategy());
    }
    
    public ResponseEntity<?> handleRequest(String strategyName, Request request) {
        OptimizationStrategy strategy = strategies.get(strategyName);
        if (strategy == null) {
            strategy = strategies.get("baseline");
        }
        
        long startTime = System.currentTimeMillis();
        ResponseEntity<?> response = strategy.processRequest(request);
        long endTime = System.currentTimeMillis();
        
        // 记录性能指标
        recordPerformanceMetrics(strategyName, endTime - startTime, response);
        
        return response;
    }
    
    private void recordPerformanceMetrics(String strategy, long duration, 
                                        ResponseEntity<?> response) {
        logger.info("Strategy: {}, Duration: {}ms, Status: {}", 
            strategy, duration, response.getStatusCode());
    }
    
    interface OptimizationStrategy {
        ResponseEntity<?> processRequest(Request request);
    }
    
    class BaselineStrategy implements OptimizationStrategy {
        @Override
        public ResponseEntity<?> processRequest(Request request) {
            // 基线处理逻辑
            return ResponseEntity.ok("Baseline response");
        }
    }
    
    class OptimizedStrategy implements OptimizationStrategy {
        @Override
        public ResponseEntity<?> processRequest(Request request) {
            // 优化处理逻辑
            return ResponseEntity.ok("Optimized response");
        }
    }
}
```

## 实际案例分析

### 电商平台请求响应优化

在一个典型的电商平台中，请求响应优化需要关注关键业务场景。

#### 商品列表页优化

```java
// 商品列表页优化实现
@RestController
public class OptimizedProductController {
    
    @Autowired
    private ProductService productService;
    
    @Autowired
    private CacheService cacheService;
    
    @GetMapping("/api/products")
    public ResponseEntity<ProductListResponse> getProducts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String sortBy,
            @RequestParam(required = false) String fields) {
        
        // 生成缓存键
        String cacheKey = generateCacheKey(page, size, category, search, sortBy);
        
        // 尝试从缓存获取
        ProductListResponse cachedResponse = 
            cacheService.get(cacheKey, ProductListResponse.class);
        if (cachedResponse != null) {
            return ResponseEntity.ok(cachedResponse);
        }
        
        // 查询数据库
        Pageable pageable = PageRequest.of(page, size);
        Page<Product> products = productService.getProducts(pageable, category, search, sortBy);
        
        // 字段过滤
        List<ProductDto> productDtos = products.getContent().stream()
            .map(product -> ProductDto.from(product, fields))
            .collect(Collectors.toList());
        
        ProductListResponse response = ProductListResponse.builder()
            .products(productDtos)
            .totalElements(products.getTotalElements())
            .totalPages(products.getTotalPages())
            .currentPage(page)
            .pageSize(size)
            .build();
        
        // 缓存响应
        cacheService.set(cacheKey, response, Duration.ofMinutes(5));
        
        return ResponseEntity.ok(response);
    }
    
    private String generateCacheKey(int page, int size, String category, 
                                  String search, String sortBy) {
        return String.format("products:%d:%d:%s:%s:%s", 
            page, size, category, search, sortBy);
    }
}
```

#### 用户购物车优化

```java
// 购物车优化实现
@RestController
public class OptimizedCartController {
    
    @Autowired
    private CartService cartService;
    
    @GetMapping("/api/carts/{userId}")
    public ResponseEntity<CartDto> getUserCart(@PathVariable Long userId) {
        // 异步获取购物车数据
        CompletableFuture<Cart> cartFuture = 
            CompletableFuture.supplyAsync(() -> cartService.getCart(userId));
        
        // 异步预加载商品信息
        CompletableFuture<List<Product>> productsFuture = 
            cartFuture.thenCompose(cart -> 
                CompletableFuture.supplyAsync(() -> 
                    cartService.getCartProducts(cart)));
        
        // 等待所有数据准备完成
        CompletableFuture.allOf(cartFuture, productsFuture).join();
        
        Cart cart = cartFuture.join();
        List<Product> products = productsFuture.join();
        
        // 构建响应
        CartDto cartDto = CartDto.from(cart, products);
        
        return ResponseEntity.ok(cartDto);
    }
    
    // 批量操作优化
    @PostMapping("/api/carts/{userId}/items/batch")
    public ResponseEntity<CartDto> batchUpdateCartItems(
            @PathVariable Long userId,
            @RequestBody List<CartItemUpdateRequest> updates) {
        
        // 批量更新购物车项
        Cart updatedCart = cartService.batchUpdateCartItems(userId, updates);
        
        // 异步更新相关缓存
        CompletableFuture.runAsync(() -> {
            cacheService.evict("cart:" + userId);
            cacheService.evictPattern("product:*");
        });
        
        return ResponseEntity.ok(CartDto.from(updatedCart));
    }
}
```

## 总结

请求与响应的优化是提升微服务通信效率的关键环节。通过选择合适的通信协议、优化数据序列化、实施批量处理、合理使用缓存、优化分页策略、采用异步处理等技术手段，我们可以显著提升微服务系统的性能表现。在实际项目中，需要根据具体的业务需求和技术约束，选择合适的优化策略，并建立完善的监控体系来跟踪优化效果，持续改进系统性能。