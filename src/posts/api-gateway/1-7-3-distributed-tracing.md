---
title: 分布式追踪：API 网关的端到端请求追踪能力
date: 2025-08-31
categories: [APIGateway]
tags: [api-gateway, distributed-tracing, opentelemetry, jaeger, zipkin, microservices]
published: true
---

在现代微服务架构中，一个用户请求可能涉及多个服务的协同处理。分布式追踪技术能够提供端到端的请求追踪能力，帮助开发者和运维人员理解请求在系统中的流转过程，识别性能瓶颈，诊断问题根源。本文将深入探讨 API 网关中分布式追踪的实现原理、技术细节和最佳实践。

## 追踪基础概念

分布式追踪的核心概念包括 Trace、Span 和上下文传播。

### Trace 和 Span

```go
// 分布式追踪核心概念实现示例
type TraceID string
type SpanID string

// Trace 表示一个完整的请求链路
type Trace struct {
    TraceID    TraceID
    Spans      []*Span
    StartTime  time.Time
    EndTime    time.Time
    Duration   time.Duration
}

// Span 表示链路中的一个操作单元
type Span struct {
    SpanID       SpanID
    TraceID      TraceID
    ParentSpanID SpanID
    Operation    string
    StartTime    time.Time
    EndTime      time.Time
    Duration     time.Duration
    Tags         map[string]string
    Logs         []LogRecord
    References   []SpanReference
}

// Span 引用关系
type SpanReference struct {
    ReferenceType ReferenceType
    TraceID       TraceID
    SpanID        SpanID
}

type ReferenceType string

const (
    ChildOf    ReferenceType = "CHILD_OF"
    FollowsFrom ReferenceType = "FOLLOWS_FROM"
)

// 日志记录
type LogRecord struct {
    Timestamp time.Time
    Fields    map[string]string
}

// 创建新的 Trace
func NewTrace() *Trace {
    traceID := generateTraceID()
    return &Trace{
        TraceID:   traceID,
        Spans:     make([]*Span, 0),
        StartTime: time.Now(),
    }
}

// 创建新的 Span
func (t *Trace) NewSpan(operation string, parentSpanID SpanID) *Span {
    spanID := generateSpanID()
    span := &Span{
        SpanID:       spanID,
        TraceID:      t.TraceID,
        ParentSpanID: parentSpanID,
        Operation:    operation,
        StartTime:    time.Now(),
        Tags:         make(map[string]string),
        Logs:         make([]LogRecord, 0),
    }
    
    t.Spans = append(t.Spans, span)
    return span
}

// 完成 Span
func (s *Span) Finish() {
    s.EndTime = time.Now()
    s.Duration = s.EndTime.Sub(s.StartTime)
}

// 添加标签
func (s *Span) SetTag(key, value string) {
    s.Tags[key] = value
}

// 添加日志
func (s *Span) Log(fields map[string]string) {
    logRecord := LogRecord{
        Timestamp: time.Now(),
        Fields:    fields,
    }
    s.Logs = append(s.Logs, logRecord)
}

// 生成 Trace ID
func generateTraceID() TraceID {
    return TraceID(uuid.New().String())
}

// 生成 Span ID
func generateSpanID() SpanID {
    return SpanID(uuid.New().String()[:16])
}
```

## 上下文传播

在分布式系统中，追踪上下文需要在服务间传播：

```go
// 追踪上下文传播实现示例
type SpanContext struct {
    TraceID  TraceID
    SpanID   SpanID
    Sampled  bool
    Baggage  map[string]string
}

// HTTP 头部传播格式
const (
    TraceIDHeader    = "X-Trace-Id"
    SpanIDHeader     = "X-Span-Id"
    SampledHeader    = "X-Sampled"
    BaggageHeaderPrefix = "X-Baggage-"
)

// 从 HTTP 请求中提取 Span 上下文
func ExtractSpanContext(r *http.Request) *SpanContext {
    traceID := TraceID(r.Header.Get(TraceIDHeader))
    spanID := SpanID(r.Header.Get(SpanIDHeader))
    sampled := r.Header.Get(SampledHeader) == "true"
    
    // 提取 Baggage
    baggage := make(map[string]string)
    for key, values := range r.Header {
        if strings.HasPrefix(key, BaggageHeaderPrefix) {
            baggageKey := strings.TrimPrefix(key, BaggageHeaderPrefix)
            baggage[baggageKey] = values[0]
        }
    }
    
    // 如果没有 Trace ID，创建新的上下文
    if traceID == "" {
        traceID = generateTraceID()
        spanID = generateSpanID()
        sampled = shouldSample() // 决定是否采样
    }
    
    return &SpanContext{
        TraceID: traceID,
        SpanID:  spanID,
        Sampled: sampled,
        Baggage: baggage,
    }
}

// 将 Span 上下文注入到 HTTP 请求中
func InjectSpanContext(ctx *SpanContext, req *http.Request) {
    req.Header.Set(TraceIDHeader, string(ctx.TraceID))
    req.Header.Set(SpanIDHeader, string(ctx.SpanID))
    req.Header.Set(SampledHeader, fmt.Sprintf("%t", ctx.Sampled))
    
    // 注入 Baggage
    for key, value := range ctx.Baggage {
        req.Header.Set(BaggageHeaderPrefix+key, value)
    }
}

// 决定是否采样
func shouldSample() bool {
    // 简单的采样策略：10% 的请求被采样
    return rand.Float64() < 0.1
}

// 添加 Baggage
func (sc *SpanContext) SetBaggageItem(key, value string) {
    if sc.Baggage == nil {
        sc.Baggage = make(map[string]string)
    }
    sc.Baggage[key] = value
}

// 获取 Baggage
func (sc *SpanContext) GetBaggageItem(key string) string {
    if sc.Baggage == nil {
        return ""
    }
    return sc.Baggage[key]
}
```

## 追踪采样策略

为了控制追踪数据的存储和处理成本，需要实现合理的采样策略：

```go
// 追踪采样策略实现示例
type Sampler interface {
    IsSampled(traceID TraceID, operation string) bool
}

// 常量采样器
type ConstantSampler struct {
    sampled bool
}

func NewConstantSampler(sampled bool) *ConstantSampler {
    return &ConstantSampler{sampled: sampled}
}

func (cs *ConstantSampler) IsSampled(traceID TraceID, operation string) bool {
    return cs.sampled
}

// 概率采样器
type ProbabilisticSampler struct {
    samplingRate float64
}

func NewProbabilisticSampler(rate float64) *ProbabilisticSampler {
    if rate < 0.0 {
        rate = 0.0
    }
    if rate > 1.0 {
        rate = 1.0
    }
    
    return &ProbabilisticSampler{samplingRate: rate}
}

func (ps *ProbabilisticSampler) IsSampled(traceID TraceID, operation string) bool {
    if ps.samplingRate >= 1.0 {
        return true
    }
    if ps.samplingRate <= 0.0 {
        return false
    }
    
    // 使用 Trace ID 的哈希值进行采样
    hash := hashString(string(traceID))
    threshold := uint64(ps.samplingRate * float64(math.MaxUint64))
    
    return hash < threshold
}

// 速率限制采样器
type RateLimitingSampler struct {
    maxTracesPerSecond float64
    lastTick           time.Time
    tracesThisSecond   float64
    mutex              sync.Mutex
}

func NewRateLimitingSampler(maxTracesPerSecond float64) *RateLimitingSampler {
    return &RateLimitingSampler{
        maxTracesPerSecond: maxTracesPerSecond,
        lastTick:           time.Now(),
    }
}

func (rls *RateLimitingSampler) IsSampled(traceID TraceID, operation string) bool {
    rls.mutex.Lock()
    defer rls.mutex.Unlock()
    
    now := time.Now()
    elapsed := now.Sub(rls.lastTick).Seconds()
    
    // 重置计数器
    if elapsed >= 1.0 {
        rls.tracesThisSecond = 0
        rls.lastTick = now
        elapsed = 0
    }
    
    // 计算当前秒内允许的追踪数
    allowedTraces := rls.maxTracesPerSecond * (1.0 - elapsed)
    
    if rls.tracesThisSecond < allowedTraces {
        rls.tracesThisSecond++
        return true
    }
    
    return false
}

// 自适应采样器
type AdaptiveSampler struct {
    targetSamplesPerSecond float64
    currentRate            float64
    mutex                  sync.RWMutex
}

func NewAdaptiveSampler(targetSamplesPerSecond float64) *AdaptiveSampler {
    return &AdaptiveSampler{
        targetSamplesPerSecond: targetSamplesPerSecond,
        currentRate:            1.0, // 初始采样率为 100%
    }
}

func (as *AdaptiveSampler) IsSampled(traceID TraceID, operation string) bool {
    as.mutex.RLock()
    rate := as.currentRate
    as.mutex.RUnlock()
    
    return rand.Float64() < rate
}

func (as *AdaptiveSampler) UpdateRate(actualRate float64) {
    as.mutex.Lock()
    defer as.mutex.Unlock()
    
    // 根据实际速率调整采样率
    if actualRate > as.targetSamplesPerSecond {
        as.currentRate *= 0.9 // 降低采样率
    } else if actualRate < as.targetSamplesPerSecond*0.8 {
        as.currentRate *= 1.1 // 提高采样率
    }
    
    // 限制采样率在合理范围内
    if as.currentRate > 1.0 {
        as.currentRate = 1.0
    }
    if as.currentRate < 0.01 {
        as.currentRate = 0.01
    }
}

// 哈希函数
func hashString(s string) uint64 {
    h := fnv.New64a()
    h.Write([]byte(s))
    return h.Sum64()
}
```

## 追踪数据收集

追踪数据需要被收集并发送到追踪系统：

```go
// 追踪数据收集器实现示例
type Tracer struct {
    serviceName    string
    sampler        Sampler
    reporter       Reporter
    activeSpans    map[SpanID]*Span
    mutex          sync.RWMutex
}

type Reporter interface {
    ReportSpan(span *Span) error
    Close() error
}

// 创建追踪器
func NewTracer(serviceName string, sampler Sampler, reporter Reporter) *Tracer {
    return &Tracer{
        serviceName: serviceName,
        sampler:     sampler,
        reporter:    reporter,
        activeSpans: make(map[SpanID]*Span),
    }
}

// 开始新的 Span
func (t *Tracer) StartSpan(operation string, parentContext *SpanContext) (*Span, *SpanContext) {
    var traceID TraceID
    var parentSpanID SpanID
    var sampled bool
    
    if parentContext != nil {
        traceID = parentContext.TraceID
        parentSpanID = parentContext.SpanID
        sampled = parentContext.Sampled
    } else {
        traceID = generateTraceID()
        sampled = t.sampler.IsSampled(traceID, operation)
    }
    
    if !sampled {
        return nil, &SpanContext{
            TraceID: traceID,
            SpanID:  "",
            Sampled: false,
        }
    }
    
    span := &Span{
        SpanID:       generateSpanID(),
        TraceID:      traceID,
        ParentSpanID: parentSpanID,
        Operation:    operation,
        StartTime:    time.Now(),
        Tags:         make(map[string]string),
        Logs:         make([]LogRecord, 0),
    }
    
    // 添加默认标签
    span.SetTag("service.name", t.serviceName)
    span.SetTag("span.kind", "server")
    
    // 存储活跃的 Span
    t.mutex.Lock()
    t.activeSpans[span.SpanID] = span
    t.mutex.Unlock()
    
    spanContext := &SpanContext{
        TraceID:  traceID,
        SpanID:   span.SpanID,
        Sampled:  true,
        Baggage:  make(map[string]string),
    }
    
    if parentContext != nil {
        // 继承父 Span 的 Baggage
        for k, v := range parentContext.Baggage {
            spanContext.Baggage[k] = v
        }
    }
    
    return span, spanContext
}

// 完成 Span
func (t *Tracer) FinishSpan(span *Span) {
    if span == nil {
        return
    }
    
    span.Finish()
    
    // 从活跃 Span 中移除
    t.mutex.Lock()
    delete(t.activeSpans, span.SpanID)
    t.mutex.Unlock()
    
    // 报告 Span
    if t.reporter != nil {
        go t.reporter.ReportSpan(span) // 异步报告
    }
}

// 添加标签
func (t *Tracer) SetTag(span *Span, key, value string) {
    if span != nil {
        span.SetTag(key, value)
    }
}

// 添加日志
func (t *Tracer) Log(span *Span, fields map[string]string) {
    if span != nil {
        span.Log(fields)
    }
}
```

## 追踪 Reporter 实现

不同的追踪系统需要不同的 Reporter 实现：

```go
// Jaeger Reporter 实现示例
type JaegerReporter struct {
    agentHost string
    agentPort string
    client    *jaegerclient.AgentClientUDP
    processor *jaegerclient.BatchProcessor
    mutex     sync.Mutex
}

// 创建 Jaeger Reporter
func NewJaegerReporter(agentHost, agentPort string) (*JaegerReporter, error) {
    reporter := &JaegerReporter{
        agentHost: agentHost,
        agentPort: agentPort,
    }
    
    err := reporter.initClient()
    if err != nil {
        return nil, err
    }
    
    return reporter, nil
}

// 初始化客户端
func (jr *JaegerReporter) initClient() error {
    jr.mutex.Lock()
    defer jr.mutex.Unlock()
    
    // 创建 UDP 客户端
    client, err := jaegerclient.NewAgentClientUDP(jr.agentHost, jr.agentPort)
    if err != nil {
        return err
    }
    
    jr.client = client
    
    // 创建批处理处理器
    jr.processor = jaegerclient.NewBatchProcessor(
        "api-gateway",
        jaegerclient.ReporterOptions.BufferFlushInterval(1*time.Second),
        jaegerclient.ReporterOptions.Logger(jaegerclient.StdLogger),
    )
    
    return nil
}

// 报告 Span
func (jr *JaegerReporter) ReportSpan(span *Span) error {
    jr.mutex.Lock()
    defer jr.mutex.Unlock()
    
    if jr.client == nil {
        return errors.New("jaeger client not initialized")
    }
    
    // 转换为 Jaeger Span
    jaegerSpan := jr.convertToJaegerSpan(span)
    
    // 发送到 Jaeger Agent
    return jr.client.EmitBatch(&jaeger.Batch{
        Spans: []*jaeger.Span{jaegerSpan},
    })
}

// 转换为 Jaeger Span
func (jr *JaegerReporter) convertToJaegerSpan(span *Span) *jaeger.Span {
    // 创建 Jaeger Span
    jaegerSpan := &jaeger.Span{
        TraceIdLow:    int64(hashString(string(span.TraceID))),
        TraceIdHigh:   0,
        SpanId:        int64(hashString(string(span.SpanID))),
        ParentSpanId:  int64(hashString(string(span.ParentSpanID))),
        OperationName: span.Operation,
        StartTime:     span.StartTime.UnixNano() / 1000, // microseconds
        Duration:      int64(span.Duration.Microseconds()),
        Tags:          make([]*jaeger.Tag, 0),
        Logs:          make([]*jaeger.Log, 0),
    }
    
    // 转换标签
    for key, value := range span.Tags {
        jaegerSpan.Tags = append(jaegerSpan.Tags, &jaeger.Tag{
            Key:   key,
            VStr:  &value,
            VType: jaeger.TagType_STRING,
        })
    }
    
    // 转换日志
    for _, logRecord := range span.Logs {
        fields := make([]*jaeger.Tag, 0)
        for key, value := range logRecord.Fields {
            fields = append(fields, &jaeger.Tag{
                Key:   key,
                VStr:  &value,
                VType: jaeger.TagType_STRING,
            })
        }
        
        jaegerSpan.Logs = append(jaegerSpan.Logs, &jaeger.Log{
            Timestamp: logRecord.Timestamp.UnixNano() / 1000, // microseconds
            Fields:    fields,
        })
    }
    
    return jaegerSpan
}

// 关闭 Reporter
func (jr *JaegerReporter) Close() error {
    jr.mutex.Lock()
    defer jr.mutex.Unlock()
    
    if jr.client != nil {
        return jr.client.Close()
    }
    
    return nil
}

// Zipkin Reporter 实现示例
type ZipkinReporter struct {
    baseURL   string
    client    *http.Client
    batchSize int
    batch     []*zipkinmodel.SpanModel
    mutex     sync.Mutex
}

// 创建 Zipkin Reporter
func NewZipkinReporter(baseURL string) *ZipkinReporter {
    return &ZipkinReporter{
        baseURL:   baseURL,
        client:    &http.Client{Timeout: 5 * time.Second},
        batchSize: 10,
        batch:     make([]*zipkinmodel.SpanModel, 0, 10),
    }
}

// 报告 Span
func (zr *ZipkinReporter) ReportSpan(span *Span) error {
    zr.mutex.Lock()
    defer zr.mutex.Unlock()
    
    // 转换为 Zipkin Span
    zipkinSpan := zr.convertToZipkinSpan(span)
    zr.batch = append(zr.batch, zipkinSpan)
    
    // 检查是否需要发送批次
    if len(zr.batch) >= zr.batchSize {
        return zr.flushBatch()
    }
    
    return nil
}

// 转换为 Zipkin Span
func (zr *ZipkinReporter) convertToZipkinSpan(span *Span) *zipkinmodel.SpanModel {
    // 解析 Trace ID
    traceID, _ := zipkinmodel.TraceIDFromHex(string(span.TraceID))
    
    // 解析 Span ID
    spanID, _ := zipkinmodel.SpanIDFromHex(string(span.SpanID))
    
    // 解析 Parent Span ID
    var parentID *zipkinmodel.SpanID
    if span.ParentSpanID != "" {
        pid, _ := zipkinmodel.SpanIDFromHex(string(span.ParentSpanID))
        parentID = &pid
    }
    
    // 创建 Zipkin Span
    zipkinSpan := &zipkinmodel.SpanModel{
        SpanContext: zipkinmodel.SpanContext{
            TraceID:  traceID,
            ID:       spanID,
            ParentID: parentID,
        },
        Name:      span.Operation,
        Timestamp: span.StartTime,
        Duration:  span.Duration,
        Tags:      span.Tags,
        Logs:      make([]zipkinmodel.Annotation, 0),
    }
    
    // 转换日志
    for _, logRecord := range span.Logs {
        zipkinSpan.Logs = append(zipkinSpan.Logs, zipkinmodel.Annotation{
            Timestamp: logRecord.Timestamp,
            Value:     fmt.Sprintf("%v", logRecord.Fields),
        })
    }
    
    return zipkinSpan
}

// 刷新批次
func (zr *ZipkinReporter) flushBatch() error {
    if len(zr.batch) == 0 {
        return nil
    }
    
    // 发送到 Zipkin
    spansJSON, err := json.Marshal(zr.batch)
    if err != nil {
        return err
    }
    
    req, err := http.NewRequest("POST", zr.baseURL+"/api/v2/spans", bytes.NewReader(spansJSON))
    if err != nil {
        return err
    }
    
    req.Header.Set("Content-Type", "application/json")
    
    resp, err := zr.client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    // 清空批次
    zr.batch = zr.batch[:0]
    
    if resp.StatusCode >= 400 {
        return fmt.Errorf("zipkin server returned status %d", resp.StatusCode)
    }
    
    return nil
}

// 关闭 Reporter
func (zr *ZipkinReporter) Close() error {
    zr.mutex.Lock()
    defer zr.mutex.Unlock()
    
    return zr.flushBatch()
}
```

## 追踪中间件

在 API 网关中实现分布式追踪中间件：

```go
// 分布式追踪中间件实现示例
type TracingMiddleware struct {
    tracer  *Tracer
    next    http.Handler
}

// 创建追踪中间件
func NewTracingMiddleware(tracer *Tracer, next http.Handler) *TracingMiddleware {
    return &TracingMiddleware{
        tracer: tracer,
        next:   next,
    }
}

// 处理 HTTP 请求
func (tm *TracingMiddleware) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // 从请求中提取 Span 上下文
    parentContext := ExtractSpanContext(r)
    
    // 开始新的 Span
    span, spanContext := tm.tracer.StartSpan("http_request", parentContext)
    if span != nil {
        defer tm.tracer.FinishSpan(span)
        
        // 添加请求相关信息到 Span
        tm.tracer.SetTag(span, "http.method", r.Method)
        tm.tracer.SetTag(span, "http.url", r.URL.String())
        tm.tracer.SetTag(span, "http.user_agent", r.UserAgent())
        tm.tracer.SetTag(span, "http.client_ip", getClientIP(r))
        
        // 记录开始处理日志
        tm.tracer.Log(span, map[string]string{
            "event": "start_processing",
            "method": r.Method,
            "url": r.URL.String(),
        })
    }
    
    // 创建响应记录器
    responseRecorder := &ResponseRecorder{
        ResponseWriter: w,
        StatusCode:     200,
    }
    
    // 将 Span 上下文注入到请求中（供下游服务使用）
    if spanContext != nil {
        InjectSpanContext(spanContext, r)
    }
    
    // 处理请求
    startTime := time.Now()
    tm.next.ServeHTTP(responseRecorder, r)
    duration := time.Since(startTime)
    
    // 记录响应信息到 Span
    if span != nil {
        tm.tracer.SetTag(span, "http.status_code", strconv.Itoa(responseRecorder.StatusCode))
        tm.tracer.SetTag(span, "http.duration", fmt.Sprintf("%.2fms", float64(duration.Milliseconds())))
        
        // 如果是错误状态码，添加错误标签
        if responseRecorder.StatusCode >= 400 {
            tm.tracer.SetTag(span, "error", "true")
            tm.tracer.SetTag(span, "http.error_message", http.StatusText(responseRecorder.StatusCode))
        }
        
        // 记录完成处理日志
        tm.tracer.Log(span, map[string]string{
            "event": "finish_processing",
            "status_code": strconv.Itoa(responseRecorder.StatusCode),
            "duration": fmt.Sprintf("%.2fms", float64(duration.Milliseconds())),
        })
    }
}

// 响应记录器
type ResponseRecorder struct {
    http.ResponseWriter
    StatusCode int
    Written    int64
}

func (rr *ResponseRecorder) WriteHeader(statusCode int) {
    rr.StatusCode = statusCode
    rr.ResponseWriter.WriteHeader(statusCode)
}

func (rr *ResponseRecorder) Write(data []byte) (int, error) {
    n, err := rr.ResponseWriter.Write(data)
    rr.Written += int64(n)
    return n, err
}

// 获取客户端 IP
func getClientIP(r *http.Request) string {
    // 尝试从各种头部获取真实客户端 IP
    if ip := r.Header.Get("X-Forwarded-For"); ip != "" {
        ips := strings.Split(ip, ",")
        return strings.TrimSpace(ips[0])
    }
    
    if ip := r.Header.Get("X-Real-IP"); ip != "" {
        return ip
    }
    
    // 回退到 RemoteAddr
    host, _, _ := net.SplitHostPort(r.RemoteAddr)
    return host
}
```

## 追踪数据查询和分析

```go
// 追踪数据查询 API 实现示例
type TracingQueryAPI struct {
    tracer *Tracer
}

// 创建追踪查询 API
func NewTracingQueryAPI(tracer *Tracer) *TracingQueryAPI {
    return &TracingQueryAPI{
        tracer: tracer,
    }
}

// 查询 Trace
func (tqa *TracingQueryAPI) QueryTrace(w http.ResponseWriter, r *http.Request) {
    // 解析查询参数
    traceID := r.URL.Query().Get("trace_id")
    if traceID == "" {
        http.Error(w, "trace_id is required", http.StatusBadRequest)
        return
    }
    
    // 这里需要实现具体的 Trace 查询逻辑
    // 实际应用中会查询 Jaeger、Zipkin 等追踪系统
    
    // 为简化示例，返回模拟数据
    trace := &Trace{
        TraceID: TraceID(traceID),
        Spans: []*Span{
            {
                SpanID:    "span1",
                TraceID:   TraceID(traceID),
                Operation: "http_request",
                StartTime: time.Now().Add(-100 * time.Millisecond),
                EndTime:   time.Now(),
                Duration:  100 * time.Millisecond,
                Tags: map[string]string{
                    "http.method": "GET",
                    "http.url":    "/api/users",
                    "http.status_code": "200",
                },
            },
            {
                SpanID:       "span2",
                TraceID:      TraceID(traceID),
                ParentSpanID: "span1",
                Operation:    "user_service_call",
                StartTime:    time.Now().Add(-80 * time.Millisecond),
                EndTime:      time.Now().Add(-20 * time.Millisecond),
                Duration:     60 * time.Millisecond,
                Tags: map[string]string{
                    "service.name": "user-service",
                    "grpc.method":  "/UserService/GetUser",
                },
            },
        },
    }
    
    // 返回结果
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(trace)
}

// 查询服务依赖关系
func (tqa *TracingQueryAPI) QueryServiceDependencies(w http.ResponseWriter, r *http.Request) {
    // 解析查询参数
    service := r.URL.Query().Get("service")
    lookback := r.URL.Query().Get("lookback")
    
    // 设置默认值
    if service == "" {
        service = "api-gateway"
    }
    
    // 这里需要实现具体的服务依赖查询逻辑
    
    // 为简化示例，返回模拟数据
    dependencies := map[string]interface{}{
        "service": service,
        "dependencies": []map[string]interface{}{
            {"service": "user-service", "calls": 100, "errors": 2},
            {"service": "order-service", "calls": 80, "errors": 1},
            {"service": "payment-service", "calls": 60, "errors": 0},
        },
    }
    
    // 返回结果
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(dependencies)
}

// 查询性能统计
func (tqa *TracingQueryAPI) QueryPerformanceStats(w http.ResponseWriter, r *http.Request) {
    // 解析查询参数
    service := r.URL.Query().Get("service")
    operation := r.URL.Query().Get("operation")
    
    // 这里需要实现具体的性能统计查询逻辑
    
    // 为简化示例，返回模拟数据
    stats := map[string]interface{}{
        "service":   service,
        "operation": operation,
        "stats": map[string]interface{}{
            "p50": "50ms",
            "p90": "120ms",
            "p95": "200ms",
            "p99": "500ms",
            "max": "2s",
        },
    }
    
    // 返回结果
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(stats)
}
```

## 最佳实践

### 追踪设计原则

1. **低侵入性**：追踪实现应尽量减少对业务代码的侵入
2. **高性能**：追踪机制不应显著影响系统性能
3. **可配置性**：支持灵活的采样策略和配置选项
4. **标准化**：遵循 OpenTracing 或 OpenTelemetry 等标准

### 采样策略

1. **分层采样**：对不同服务或操作采用不同的采样率
2. **错误优先**：优先采样错误请求以确保问题可追踪
3. **动态调整**：根据系统负载动态调整采样率
4. **业务相关**：对关键业务流程采用更高的采样率

### 数据管理

1. **存储策略**：制定合理的追踪数据存储和清理策略
2. **索引优化**：为追踪数据建立合适的索引以提高查询性能
3. **压缩传输**：对追踪数据进行压缩以减少网络传输开销
4. **批量处理**：批量发送追踪数据以提高效率

### 监控和告警

1. **追踪覆盖率**：监控追踪数据的覆盖率和质量
2. **性能指标**：监控追踪系统的性能指标
3. **错误追踪**：对错误请求的追踪数据进行特别关注
4. **依赖分析**：定期分析服务间的依赖关系

## 小结

分布式追踪是现代微服务架构中不可或缺的可观测性工具。通过实现 Trace 和 Span 的核心概念、上下文传播机制、采样策略、数据收集和 Reporter、追踪中间件、数据查询分析等功能，可以构建一个完整的分布式追踪系统。在实际应用中，需要根据业务需求和技术架构选择合适的追踪方案，并持续优化追踪性能和数据管理策略，确保系统能够有效地提供端到端的请求追踪能力，为系统监控、问题诊断和性能优化提供有力支持。