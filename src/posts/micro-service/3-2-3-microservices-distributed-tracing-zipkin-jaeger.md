---
title: 微服务的分布式追踪：Zipkin与Jaeger实践
date: 2025-08-30
categories: [Microservices]
tags: [microservices, distributed-tracing, zipkin, jaeger]
published: true
---

在微服务架构中，一个用户请求可能涉及多个服务的协作，这使得问题排查和性能分析变得极其复杂。分布式追踪技术应运而生，它能够追踪请求在各个服务间的流转过程，帮助开发者理解系统行为、诊断性能问题和分析错误根源。Zipkin和Jaeger作为业界领先的分布式追踪系统，为微服务架构提供了强大的追踪能力。本文将深入探讨分布式追踪的核心概念和实践方法。

## 分布式追踪核心概念

### Trace和Span

在分布式追踪中，**Trace**表示一个完整的请求链路，**Span**表示链路中的一个工作单元。

```java
// Trace示例：用户下单流程
// Trace ID: abc123def456
// 
// Span 1: API Gateway接收请求
//   ├── Span 2: 用户服务验证用户
//   │     └── Span 3: 数据库查询用户信息
//   ├── Span 4: 订单服务创建订单
//   │     ├── Span 5: 库存服务扣减库存
//   │     └── Span 6: 数据库插入订单记录
//   └── Span 7: 支付服务处理支付
//         └── Span 8: 第三方支付API调用
```

### 上下文传播

分布式追踪需要在服务间传播追踪上下文，通常通过HTTP头传递。

```java
// 追踪上下文传播示例
@RestController
public class OrderController {
    
    @Autowired
    private Tracer tracer;
    
    @PostMapping("/orders")
    public Order createOrder(@RequestBody OrderRequest request, HttpServletRequest httpRequest) {
        // 从HTTP头中提取追踪上下文
        SpanContext spanContext = extractSpanContext(httpRequest);
        
        // 创建新的Span
        Span span = tracer.buildSpan("createOrder")
            .asChildOf(spanContext)
            .start();
        
        try {
            span.setTag("user.id", request.getUserId().toString());
            span.setTag("order.total", request.getTotalAmount().toString());
            
            // 业务逻辑
            Order order = orderService.createOrder(request);
            
            // 调用其他服务时传播追踪上下文
            HttpHeaders headers = new HttpHeaders();
            injectSpanContext(span.context(), headers);
            
            // 调用库存服务
            inventoryService.reserveStock(order.getProductId(), order.getQuantity(), headers);
            
            return order;
        } finally {
            span.finish();
        }
    }
    
    private SpanContext extractSpanContext(HttpServletRequest request) {
        // 从HTTP头中提取追踪上下文
        return tracer.extract(Format.Builtin.HTTP_HEADERS, 
            new HttpServletRequestTextMap(request));
    }
    
    private void injectSpanContext(SpanContext spanContext, HttpHeaders headers) {
        // 将追踪上下文注入HTTP头
        tracer.inject(spanContext, Format.Builtin.HTTP_HEADERS, 
            new HttpHeadersTextMap(headers));
    }
}
```

## Zipkin分布式追踪

### Zipkin架构

Zipkin由四个核心组件组成：

1. **Collector**：收集追踪数据
2. **Storage**：存储追踪数据
3. **Search**：提供查询API
4. **Web UI**：提供可视化界面

### Zipkin部署

```yaml
# Zipkin部署配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zipkin
spec:
  replicas: 1
  selector:
    matchLabels:
      app: zipkin
  template:
    metadata:
      labels:
        app: zipkin
    spec:
      containers:
      - name: zipkin
        image: openzipkin/zipkin:latest
        ports:
        - containerPort: 9411
        env:
        - name: STORAGE_TYPE
          value: elasticsearch
        - name: ES_HOSTS
          value: http://elasticsearch:9200
        - name: ES_INDEX
          value: zipkin
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
# Zipkin Service
apiVersion: v1
kind: Service
metadata:
  name: zipkin
spec:
  selector:
    app: zipkin
  ports:
  - port: 9411
    targetPort: 9411
  type: LoadBalancer
```

### Spring Boot集成Zipkin

```java
// Maven依赖
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-zipkin</artifactId>
</dependency>

// application.yml配置
spring:
  application:
    name: user-service
  zipkin:
    base-url: http://zipkin:9411
  sleuth:
    sampler:
      probability: 1.0  # 采样率100%
```

```java
// 服务间调用示例
@Service
public class UserService {
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Autowired
    private Tracer tracer;
    
    public User getUser(Long userId) {
        // 创建Span
        Span span = tracer.nextSpan().name("getUser").start();
        try (Tracer.SpanInScope ws = tracer.withSpanInScope(span)) {
            span.tag("user.id", userId.toString());
            
            // 调用其他服务
            String url = "http://order-service/orders?userId=" + userId;
            ResponseEntity<List<Order>> response = restTemplate.getForEntity(url, 
                new ParameterizedTypeReference<List<Order>>() {});
            
            // 处理响应
            List<Order> orders = response.getBody();
            
            return new User(userId, "John Doe", orders);
        } finally {
            span.finish();
        }
    }
}
```

### 自定义Span注解

```java
// 自定义追踪注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Traced {
    String value() default "";
}

// 追踪切面
@Aspect
@Component
public class TracingAspect {
    
    @Autowired
    private Tracer tracer;
    
    @Around("@annotation(traced)")
    public Object traceMethod(ProceedingJoinPoint joinPoint, Traced traced) throws Throwable {
        String spanName = traced.value().isEmpty() ? 
            joinPoint.getSignature().getName() : traced.value();
        
        Span span = tracer.nextSpan().name(spanName).start();
        try (Tracer.SpanInScope ws = tracer.withSpanInScope(span)) {
            span.tag("class", joinPoint.getTarget().getClass().getSimpleName());
            span.tag("method", joinPoint.getSignature().getName());
            
            Object result = joinPoint.proceed();
            
            span.tag("result", result != null ? "success" : "null");
            return result;
        } catch (Exception e) {
            span.tag("error", e.getMessage());
            throw e;
        } finally {
            span.finish();
        }
    }
}

// 使用自定义注解
@Service
public class OrderService {
    
    @Traced("createOrder")
    public Order createOrder(OrderRequest request) {
        // 业务逻辑
        return orderRepository.save(new Order(request));
    }
    
    @Traced("processPayment")
    public Payment processPayment(PaymentRequest request) {
        // 业务逻辑
        return paymentService.process(request);
    }
}
```

## Jaeger分布式追踪

### Jaeger架构

Jaeger由以下组件组成：

1. **Jaeger Agent**：接收客户端数据并转发给Collector
2. **Jaeger Collector**：接收追踪数据并存储
3. **Jaeger Query**：提供查询API
4. **Jaeger UI**：提供可视化界面

### Jaeger部署

```yaml
# Jaeger All-in-One部署
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
      - name: jaeger
        image: jaegertracing/all-in-one:latest
        ports:
        - containerPort: 16686  # UI端口
        - containerPort: 14268  # 接收集端口
        - containerPort: 14250  # gRPC端口
        env:
        - name: SPAN_STORAGE_TYPE
          value: elasticsearch
        - name: ES_SERVER_URLS
          value: http://elasticsearch:9200
        - name: ES_INDEX_PREFIX
          value: jaeger
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
# Jaeger Service
apiVersion: v1
kind: Service
metadata:
  name: jaeger
spec:
  selector:
    app: jaeger
  ports:
  - name: ui
    port: 16686
    targetPort: 16686
  - name: collector
    port: 14268
    targetPort: 14268
  - name: grpc
    port: 14250
    targetPort: 14250
  type: LoadBalancer
```

### Spring Boot集成Jaeger

```java
// Maven依赖
<dependency>
    <groupId>io.opentracing.contrib</groupId>
    <artifactId>opentracing-spring-jaeger-cloud-starter</artifactId>
    <version>3.3.1</version>
</dependency>

// application.yml配置
opentracing:
  jaeger:
    service-name: user-service
    udp-sender:
      host: jaeger-agent
      port: 6831
    sampler-type: const
    sampler-param: 1
```

```java
// 手动创建Span
@RestController
public class UserController {
    
    @Autowired
    private Tracer tracer;
    
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        // 创建Span
        Span span = tracer.buildSpan("getUser")
            .withTag("user.id", id.toString())
            .start();
        
        try {
            // 业务逻辑
            User user = userService.getUser(id);
            
            // 添加标签
            span.setTag("username", user.getUsername());
            span.setTag("order.count", user.getOrders().size());
            
            return user;
        } catch (Exception e) {
            // 记录错误
            Tags.ERROR.set(span, true);
            span.log(ImmutableMap.of(
                "event", "error",
                "error.object", e));
            throw e;
        } finally {
            span.finish();
        }
    }
}
```

### 追踪上下文传播

```java
// HTTP客户端追踪
@Service
public class OrderServiceClient {
    
    @Autowired
    private Tracer tracer;
    
    public List<Order> getOrdersByUserId(Long userId) {
        Span span = tracer.buildSpan("getOrdersByUserId").start();
        try {
            String url = "http://order-service/orders?userId=" + userId;
            
            // 创建HTTP请求
            HttpHeaders headers = new HttpHeaders();
            
            // 注入追踪上下文
            tracer.inject(span.context(), Format.Builtin.HTTP_HEADERS, 
                new HttpHeadersTextMap(headers));
            
            HttpEntity<?> entity = new HttpEntity<>(headers);
            
            // 发送请求
            ResponseEntity<List<Order>> response = restTemplate.exchange(
                url, HttpMethod.GET, entity, 
                new ParameterizedTypeReference<List<Order>>() {});
            
            return response.getBody();
        } finally {
            span.finish();
        }
    }
}

// HTTP服务端提取追踪上下文
@RestController
public class OrderController {
    
    @Autowired
    private Tracer tracer;
    
    @GetMapping("/orders")
    public List<Order> getOrders(@RequestParam Long userId, HttpServletRequest request) {
        // 提取追踪上下文
        SpanContext spanContext = tracer.extract(Format.Builtin.HTTP_HEADERS, 
            new HttpServletRequestTextMap(request));
        
        // 创建Span
        Span span = tracer.buildSpan("getOrders")
            .asChildOf(spanContext)
            .start();
        
        try {
            span.setTag("user.id", userId.toString());
            
            // 业务逻辑
            return orderService.getOrdersByUserId(userId);
        } finally {
            span.finish();
        }
    }
}
```

## 分布式追踪最佳实践

### 1. 合理采样

根据系统负载和存储容量设置合适的采样率。

```yaml
# Jaeger采样配置
opentracing:
  jaeger:
    sampler-type: probabilistic  # 概率采样
    sampler-param: 0.1           # 10%采样率
```

```java
// 自适应采样
@Component
public class AdaptiveSampler {
    
    private static final double HIGH_TRAFFIC_SAMPLING_RATE = 0.01;  // 1%
    private static final double LOW_TRAFFIC_SAMPLING_RATE = 1.0;    // 100%
    
    public boolean shouldSample(String serviceName, long requestCount) {
        if (requestCount > 1000) {
            return Math.random() < HIGH_TRAFFIC_SAMPLING_RATE;
        } else {
            return Math.random() < LOW_TRAFFIC_SAMPLING_RATE;
        }
    }
}
```

### 2. 关键业务路径追踪

重点关注核心业务流程的追踪。

```java
// 电商平台核心业务追踪
@Service
public class EcommerceTracingService {
    
    @Autowired
    private Tracer tracer;
    
    public void traceUserCheckout(CheckoutRequest request) {
        Span span = tracer.buildSpan("user.checkout")
            .withTag("user.id", request.getUserId().toString())
            .withTag("cart.items", request.getCartItems().size())
            .withTag("total.amount", request.getTotalAmount().toString())
            .start();
        
        try {
            // 追踪购物车验证
            traceCartValidation(request, span);
            
            // 追踪库存检查
            traceInventoryCheck(request, span);
            
            // 追踪订单创建
            traceOrderCreation(request, span);
            
            // 追踪支付处理
            tracePaymentProcessing(request, span);
        } finally {
            span.finish();
        }
    }
    
    private void traceCartValidation(CheckoutRequest request, Span parentSpan) {
        Span span = tracer.buildSpan("cart.validation")
            .asChildOf(parentSpan)
            .start();
        
        try {
            span.setTag("items.count", request.getCartItems().size());
            // 验证逻辑
        } finally {
            span.finish();
        }
    }
    
    private void traceInventoryCheck(CheckoutRequest request, Span parentSpan) {
        Span span = tracer.buildSpan("inventory.check")
            .asChildOf(parentSpan)
            .start();
        
        try {
            for (CartItem item : request.getCartItems()) {
                span.setTag("product." + item.getProductId(), item.getQuantity());
            }
            // 库存检查逻辑
        } finally {
            span.finish();
        }
    }
}
```

### 3. 错误追踪和日志关联

将错误信息与追踪数据关联。

```java
// 错误追踪示例
@RestController
public class PaymentController {
    
    @Autowired
    private Tracer tracer;
    
    @PostMapping("/payments")
    public Payment processPayment(@RequestBody PaymentRequest request) {
        Span span = tracer.buildSpan("processPayment")
            .withTag("payment.method", request.getPaymentMethod())
            .withTag("amount", request.getAmount().toString())
            .start();
        
        try {
            Payment payment = paymentService.process(request);
            span.setTag("payment.id", payment.getId().toString());
            span.setTag("status", "success");
            return payment;
        } catch (PaymentException e) {
            // 记录错误信息
            Tags.ERROR.set(span, true);
            span.log(ImmutableMap.of(
                "event", "error",
                "error.kind", e.getClass().getSimpleName(),
                "error.message", e.getMessage(),
                "stacktrace", ExceptionUtils.getStackTrace(e)
            ));
            
            span.setTag("status", "failed");
            span.setTag("error.code", e.getErrorCode());
            
            throw e;
        } finally {
            span.finish();
        }
    }
}
```

### 4. 性能监控集成

将追踪数据与性能监控结合。

```java
// 性能监控集成
@Component
public class PerformanceTracingService {
    
    @Autowired
    private Tracer tracer;
    
    @Autowired
    private MeterRegistry meterRegistry;
    
    private final Timer databaseQueryTimer;
    private final Timer externalApiTimer;
    
    public PerformanceTracingService(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.databaseQueryTimer = Timer.builder("database.query.duration")
            .description("Database query duration")
            .register(meterRegistry);
        this.externalApiTimer = Timer.builder("external.api.duration")
            .description("External API call duration")
            .register(meterRegistry);
    }
    
    public <T> T traceDatabaseQuery(Supplier<T> queryOperation) {
        Span span = tracer.buildSpan("database.query").start();
        try {
            return databaseQueryTimer.recordCallable(() -> {
                T result = queryOperation.get();
                span.setTag("result.count", getResultCount(result));
                return result;
            });
        } catch (Exception e) {
            Tags.ERROR.set(span, true);
            span.log(Collections.singletonMap("error", e.getMessage()));
            throw e;
        } finally {
            span.finish();
        }
    }
    
    public <T> T traceExternalApiCall(String apiName, Supplier<T> apiOperation) {
        Span span = tracer.buildSpan("external.api.call")
            .withTag("api.name", apiName)
            .start();
        
        try {
            return externalApiTimer.recordCallable(() -> {
                T result = apiOperation.get();
                span.setTag("status", "success");
                return result;
            });
        } catch (Exception e) {
            Tags.ERROR.set(span, true);
            span.log(Collections.singletonMap("error", e.getMessage()));
            span.setTag("status", "failed");
            throw e;
        } finally {
            span.finish();
        }
    }
    
    private int getResultCount(Object result) {
        if (result instanceof Collection) {
            return ((Collection<?>) result).size();
        }
        return result != null ? 1 : 0;
    }
}
```

## 实际案例分析

### 电商平台分布式追踪

在一个典型的电商平台中，分布式追踪需要覆盖完整的用户购物流程。

#### 核心追踪链路

1. **用户浏览商品**：用户服务 → 商品服务 → 搜索服务
2. **添加购物车**：购物车服务 → 商品服务 → 库存服务
3. **下单支付**：订单服务 → 库存服务 → 支付服务 → 第三方支付API
4. **订单处理**：订单服务 → 物流服务 → 通知服务

#### 追踪配置

```java
// 电商平台追踪配置
@Configuration
public class EcommerceTracingConfig {
    
    @Bean
    public Tracer jaegerTracer() {
        return new Configuration("ecommerce-platform")
            .withSampler(new ConstSampler(true))
            .withReporter(ReporterConfiguration.fromEnv()
                .withSender(SenderConfiguration.fromEnv()
                    .withAgentHost("jaeger-agent")
                    .withAgentPort(6831)))
            .getTracer();
    }
}

// 核心业务追踪
@Service
public class CheckoutService {
    
    @Autowired
    private Tracer tracer;
    
    public CheckoutResult processCheckout(CheckoutRequest request) {
        Span span = tracer.buildSpan("checkout.process")
            .withTag("user.id", request.getUserId().toString())
            .withTag("items.count", request.getItems().size())
            .withTag("total.amount", request.getTotalAmount().toString())
            .start();
        
        try {
            // 验证购物车
            validateCart(request, span);
            
            // 检查库存
            checkInventory(request, span);
            
            // 创建订单
            Order order = createOrder(request, span);
            
            // 处理支付
            Payment payment = processPayment(order, span);
            
            // 发送确认通知
            sendConfirmation(request, order, payment, span);
            
            return new CheckoutResult(order, payment);
        } catch (Exception e) {
            Tags.ERROR.set(span, true);
            span.log(ImmutableMap.of(
                "event", "checkout.failed",
                "error", e.getMessage()
            ));
            throw e;
        } finally {
            span.finish();
        }
    }
    
    private void validateCart(CheckoutRequest request, Span parentSpan) {
        Span span = tracer.buildSpan("cart.validate")
            .asChildOf(parentSpan)
            .start();
        
        try {
            cartService.validate(request.getItems());
            span.setTag("validation.result", "passed");
        } catch (ValidationException e) {
            Tags.ERROR.set(span, true);
            span.log(ImmutableMap.of(
                "event", "validation.failed",
                "error", e.getMessage()
            ));
            span.setTag("validation.result", "failed");
            throw e;
        } finally {
            span.finish();
        }
    }
}
```

## 总结

分布式追踪是微服务架构中不可或缺的可观测性工具。通过Zipkin和Jaeger等追踪系统，我们可以深入了解请求在服务间的流转过程，快速定位性能瓶颈和错误根源。在实际项目中，需要合理配置采样策略、关注核心业务路径、关联错误信息，并将追踪数据与性能监控相结合，以构建全面的微服务可观测性体系。