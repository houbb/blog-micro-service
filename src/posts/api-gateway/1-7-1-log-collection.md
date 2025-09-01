---
title: 日志采集：API 网关的运行状态记录机制
date: 2025-08-31
categories: [APIGateway]
tags: [api-gateway, log-collection, structured-logging, log-analysis, microservices]
published: true
---

在现代分布式系统中，日志采集是确保系统可观测性的重要组成部分。API 网关作为系统的入口点，需要记录详细的请求和响应信息，以便于问题排查、性能分析和安全审计。本文将深入探讨 API 网关日志采集的实现原理、技术细节和最佳实践。

## 结构化日志

结构化日志是指按照预定义格式记录的日志信息，便于后续的分析和处理。与传统的文本日志相比，结构化日志具有更好的可读性和可分析性。

### 日志格式设计

```go
// 结构化日志实现示例
type APILogEntry struct {
    Timestamp    time.Time              `json:"timestamp"`
    RequestID    string                 `json:"request_id"`
    Method       string                 `json:"method"`
    Path         string                 `json:"path"`
    StatusCode   int                    `json:"status_code"`
    Latency      int64                  `json:"latency_ms"`
    ClientIP     string                 `json:"client_ip"`
    UserAgent    string                 `json:"user_agent"`
    RequestSize  int64                  `json:"request_size"`
    ResponseSize int64                  `json:"response_size"`
    UserID       string                 `json:"user_id,omitempty"`
    Service      string                 `json:"service"`
    Tags         map[string]interface{} `json:"tags,omitempty"`
    Error        string                 `json:"error,omitempty"`
    LogLevel     string                 `json:"log_level"`
}

// 创建日志条目
func NewAPILogEntry(req *http.Request, resp *http.Response, latency time.Duration) *APILogEntry {
    return &APILogEntry{
        Timestamp:    time.Now(),
        RequestID:    getRequestID(req),
        Method:       req.Method,
        Path:         req.URL.Path,
        StatusCode:   resp.StatusCode,
        Latency:      latency.Milliseconds(),
        ClientIP:     getClientIP(req),
        UserAgent:    req.UserAgent(),
        RequestSize:  getRequestSize(req),
        ResponseSize: getResponseSize(resp),
        UserID:       getUserID(req),
        Service:      getServiceName(req),
        LogLevel:     "INFO",
    }
}

// 获取请求 ID
func getRequestID(req *http.Request) string {
    requestID := req.Header.Get("X-Request-ID")
    if requestID == "" {
        requestID = generateRequestID()
    }
    return requestID
}

// 生成请求 ID
func generateRequestID() string {
    return uuid.New().String()
}

// 获取客户端 IP
func getClientIP(req *http.Request) string {
    // 尝试从各种头部获取真实客户端 IP
    if ip := req.Header.Get("X-Forwarded-For"); ip != "" {
        ips := strings.Split(ip, ",")
        return strings.TrimSpace(ips[0])
    }
    
    if ip := req.Header.Get("X-Real-IP"); ip != "" {
        return ip
    }
    
    // 回退到 RemoteAddr
    host, _, _ := net.SplitHostPort(req.RemoteAddr)
    return host
}

// 获取请求大小
func getRequestSize(req *http.Request) int64 {
    if req.ContentLength > 0 {
        return req.ContentLength
    }
    return 0
}

// 获取响应大小
func getResponseSize(resp *http.Response) int64 {
    if resp.ContentLength > 0 {
        return resp.ContentLength
    }
    return 0
}

// 获取用户 ID
func getUserID(req *http.Request) string {
    // 从认证信息中获取用户 ID
    // 这里简化处理，实际应用中需要根据具体的认证机制实现
    return req.Header.Get("X-User-ID")
}

// 获取服务名称
func getServiceName(req *http.Request) string {
    // 从请求路径或其他信息中提取服务名称
    parts := strings.Split(strings.TrimPrefix(req.URL.Path, "/"), "/")
    if len(parts) > 0 {
        return parts[0]
    }
    return "unknown"
}
```

### 日志级别管理

合理的日志级别设置可以帮助区分不同重要程度的日志信息：

```go
// 日志级别管理实现示例
type LogLevel string

const (
    DebugLevel   LogLevel = "DEBUG"
    InfoLevel    LogLevel = "INFO"
    WarnLevel    LogLevel = "WARN"
    ErrorLevel   LogLevel = "ERROR"
    FatalLevel   LogLevel = "FATAL"
)

type Logger struct {
    level     LogLevel
    formatter LogFormatter
    writers   []LogWriter
    mutex     sync.RWMutex
}

type LogFormatter interface {
    Format(entry *APILogEntry) ([]byte, error)
}

type LogWriter interface {
    Write(data []byte) error
    Close() error
}

// JSON 格式化器
type JSONFormatter struct{}

func (jf *JSONFormatter) Format(entry *APILogEntry) ([]byte, error) {
    return json.Marshal(entry)
}

// 文本格式化器
type TextFormatter struct{}

func (tf *TextFormatter) Format(entry *APILogEntry) ([]byte, error) {
    timestamp := entry.Timestamp.Format("2006-01-02T15:04:05.000Z07:00")
    logLine := fmt.Sprintf("[%s] %s [%s] %s %s %d %dms %s %s",
        timestamp,
        entry.LogLevel,
        entry.RequestID,
        entry.Method,
        entry.Path,
        entry.StatusCode,
        entry.Latency,
        entry.ClientIP,
        entry.UserAgent)
    
    if entry.Error != "" {
        logLine += fmt.Sprintf(" ERROR: %s", entry.Error)
    }
    
    return []byte(logLine), nil
}

// 创建日志记录器
func NewLogger(level LogLevel, formatter LogFormatter) *Logger {
    return &Logger{
        level:     level,
        formatter: formatter,
        writers:   make([]LogWriter, 0),
    }
}

// 添加写入器
func (l *Logger) AddWriter(writer LogWriter) {
    l.mutex.Lock()
    defer l.mutex.Unlock()
    l.writers = append(l.writers, writer)
}

// 记录日志
func (l *Logger) Log(entry *APILogEntry) error {
    if !l.shouldLog(entry.LogLevel) {
        return nil
    }
    
    data, err := l.formatter.Format(entry)
    if err != nil {
        return err
    }
    
    l.mutex.RLock()
    defer l.mutex.RUnlock()
    
    for _, writer := range l.writers {
        if err := writer.Write(append(data, '\n')); err != nil {
            // 记录写入错误，但继续尝试其他写入器
            fmt.Printf("Failed to write log: %v\n", err)
        }
    }
    
    return nil
}

// 判断是否应该记录日志
func (l *Logger) shouldLog(level LogLevel) bool {
    levelOrder := map[LogLevel]int{
        DebugLevel: 0,
        InfoLevel:  1,
        WarnLevel:  2,
        ErrorLevel: 3,
        FatalLevel: 4,
    }
    
    return levelOrder[level] >= levelOrder[l.level]
}

// 不同级别的日志记录方法
func (l *Logger) Debug(entry *APILogEntry) {
    entry.LogLevel = string(DebugLevel)
    l.Log(entry)
}

func (l *Logger) Info(entry *APILogEntry) {
    entry.LogLevel = string(InfoLevel)
    l.Log(entry)
}

func (l *Logger) Warn(entry *APILogEntry) {
    entry.LogLevel = string(WarnLevel)
    l.Log(entry)
}

func (l *Logger) Error(entry *APILogEntry) {
    entry.LogLevel = string(ErrorLevel)
    l.Log(entry)
}

func (l *Logger) Fatal(entry *APILogEntry) {
    entry.LogLevel = string(FatalLevel)
    l.Log(entry)
}
```

## 日志写入器实现

不同的日志写入器可以将日志写入到不同的目标：

```go
// 文件写入器
type FileWriter struct {
    file      *os.File
    fileName  string
    maxSize   int64
    maxFiles  int
    currentSize int64
    mutex     sync.Mutex
}

func NewFileWriter(fileName string, maxSize int64, maxFiles int) (*FileWriter, error) {
    file, err := os.OpenFile(fileName, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
    if err != nil {
        return nil, err
    }
    
    stat, err := file.Stat()
    if err != nil {
        file.Close()
        return nil, err
    }
    
    return &FileWriter{
        file:      file,
        fileName:  fileName,
        maxSize:   maxSize,
        maxFiles:  maxFiles,
        currentSize: stat.Size(),
    }, nil
}

func (fw *FileWriter) Write(data []byte) error {
    fw.mutex.Lock()
    defer fw.mutex.Unlock()
    
    // 检查是否需要轮转文件
    if fw.currentSize+int64(len(data)) > fw.maxSize {
        if err := fw.rotate(); err != nil {
            return err
        }
    }
    
    n, err := fw.file.Write(data)
    if err != nil {
        return err
    }
    
    fw.currentSize += int64(n)
    return nil
}

func (fw *FileWriter) rotate() error {
    // 关闭当前文件
    if err := fw.file.Close(); err != nil {
        return err
    }
    
    // 轮转文件
    for i := fw.maxFiles - 1; i > 0; i-- {
        oldName := fmt.Sprintf("%s.%d", fw.fileName, i)
        newName := fmt.Sprintf("%s.%d", fw.fileName, i+1)
        
        if _, err := os.Stat(oldName); err == nil {
            os.Rename(oldName, newName)
        }
    }
    
    // 重命名当前文件
    if _, err := os.Stat(fw.fileName); err == nil {
        os.Rename(fw.fileName, fw.fileName+".1")
    }
    
    // 创建新文件
    file, err := os.OpenFile(fw.fileName, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
    if err != nil {
        return err
    }
    
    fw.file = file
    fw.currentSize = 0
    return nil
}

func (fw *FileWriter) Close() error {
    fw.mutex.Lock()
    defer fw.mutex.Unlock()
    return fw.file.Close()
}

// 标准输出写入器
type StdoutWriter struct{}

func (sw *StdoutWriter) Write(data []byte) error {
    _, err := os.Stdout.Write(data)
    return err
}

func (sw *StdoutWriter) Close() error {
    return nil
}

// 网络写入器（发送到日志收集服务）
type NetworkWriter struct {
    address   string
    conn      net.Conn
    reconnect bool
    mutex     sync.Mutex
}

func NewNetworkWriter(address string) *NetworkWriter {
    return &NetworkWriter{
        address:   address,
        reconnect: true,
    }
}

func (nw *NetworkWriter) Write(data []byte) error {
    nw.mutex.Lock()
    defer nw.mutex.Unlock()
    
    // 建立连接
    if nw.conn == nil {
        conn, err := net.Dial("tcp", nw.address)
        if err != nil {
            return err
        }
        nw.conn = conn
    }
    
    // 发送数据
    _, err := nw.conn.Write(data)
    if err != nil && nw.reconnect {
        // 尝试重新连接
        nw.conn.Close()
        nw.conn = nil
        return nw.Write(data) // 递归调用，但只重试一次
    }
    
    return err
}

func (nw *NetworkWriter) Close() error {
    nw.mutex.Lock()
    defer nw.mutex.Unlock()
    
    if nw.conn != nil {
        err := nw.conn.Close()
        nw.conn = nil
        return err
    }
    
    return nil
}
```

## 日志采集中间件

在 API 网关中实现日志采集中间件：

```go
// 日志采集中间件实现示例
type LoggingMiddleware struct {
    logger    *Logger
    next      http.Handler
}

func NewLoggingMiddleware(logger *Logger, next http.Handler) *LoggingMiddleware {
    return &LoggingMiddleware{
        logger: logger,
        next:   next,
    }
}

func (lm *LoggingMiddleware) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    start := time.Now()
    
    // 创建响应记录器以捕获响应信息
    responseRecorder := &ResponseRecorder{
        ResponseWriter: w,
        StatusCode:     200, // 默认状态码
    }
    
    // 处理请求
    lm.next.ServeHTTP(responseRecorder, r)
    
    // 计算处理时间
    latency := time.Since(start)
    
    // 创建日志条目
    logEntry := NewAPILogEntry(r, &http.Response{
        StatusCode: responseRecorder.StatusCode,
        Header:     responseRecorder.Header(),
    }, latency)
    
    // 记录日志
    lm.logger.Info(logEntry)
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

// 带错误信息的日志记录
func (lm *LoggingMiddleware) ServeHTTPWithErrorHandling(w http.ResponseWriter, r *http.Request) {
    start := time.Now()
    
    // 创建响应记录器
    responseRecorder := &ResponseRecorder{
        ResponseWriter: w,
        StatusCode:     200,
    }
    
    // 使用 defer 捕获可能的 panic
    defer func() {
        if err := recover(); err != nil {
            // 记录 panic 错误
            logEntry := NewAPILogEntry(r, &http.Response{
                StatusCode: 500,
                Header:     responseRecorder.Header(),
            }, time.Since(start))
            logEntry.Error = fmt.Sprintf("panic: %v", err)
            logEntry.LogLevel = string(ErrorLevel)
            
            lm.logger.Error(logEntry)
            
            // 返回 500 错误
            http.Error(w, "Internal Server Error", 500)
        }
    }()
    
    // 处理请求
    lm.next.ServeHTTP(responseRecorder, r)
    
    // 记录正常日志
    latency := time.Since(start)
    logEntry := NewAPILogEntry(r, &http.Response{
        StatusCode: responseRecorder.StatusCode,
        Header:     responseRecorder.Header(),
    }, latency)
    
    // 如果是错误状态码，记录为错误日志
    if responseRecorder.StatusCode >= 400 {
        logEntry.LogLevel = string(ErrorLevel)
        if responseRecorder.StatusCode >= 500 {
            logEntry.Error = "Server error occurred"
        }
    }
    
    lm.logger.Log(logEntry)
}
```

## 异步日志处理

为了提高性能，可以实现异步日志处理：

```go
// 异步日志处理器实现示例
type AsyncLogger struct {
    logger    *Logger
    logChan   chan *APILogEntry
    batchSize int
    batchTimeout time.Duration
    stopChan  chan struct{}
    wg        sync.WaitGroup
}

func NewAsyncLogger(logger *Logger, bufferSize int, batchSize int, batchTimeout time.Duration) *AsyncLogger {
    al := &AsyncLogger{
        logger:       logger,
        logChan:      make(chan *APILogEntry, bufferSize),
        batchSize:    batchSize,
        batchTimeout: batchTimeout,
        stopChan:     make(chan struct{}),
    }
    
    al.startProcessor()
    return al
}

func (al *AsyncLogger) startProcessor() {
    al.wg.Add(1)
    go func() {
        defer al.wg.Done()
        al.processLogs()
    }()
}

func (al *AsyncLogger) processLogs() {
    batch := make([]*APILogEntry, 0, al.batchSize)
    timer := time.NewTimer(al.batchTimeout)
    defer timer.Stop()
    
    for {
        select {
        case logEntry := <-al.logChan:
            batch = append(batch, logEntry)
            
            // 如果批次已满，立即处理
            if len(batch) >= al.batchSize {
                al.processBatch(batch)
                batch = batch[:0]
                if !timer.Stop() {
                    select {
                    case <-timer.C:
                    default:
                    }
                }
                timer.Reset(al.batchTimeout)
            }
            
        case <-timer.C:
            // 批次超时，处理当前批次
            if len(batch) > 0 {
                al.processBatch(batch)
                batch = batch[:0]
            }
            timer.Reset(al.batchTimeout)
            
        case <-al.stopChan:
            // 处理剩余的日志条目
            if len(batch) > 0 {
                al.processBatch(batch)
            }
            return
        }
    }
}

func (al *AsyncLogger) processBatch(batch []*APILogEntry) {
    for _, entry := range batch {
        al.logger.Log(entry)
    }
}

func (al *AsyncLogger) Log(entry *APILogEntry) {
    select {
    case al.logChan <- entry:
    default:
        // 如果通道已满，丢弃日志或记录警告
        fmt.Printf("Log channel full, dropping log entry: %v\n", entry)
    }
}

func (al *AsyncLogger) Close() error {
    close(al.stopChan)
    al.wg.Wait()
    return nil
}

// 不同级别的异步日志记录方法
func (al *AsyncLogger) Debug(entry *APILogEntry) {
    entry.LogLevel = string(DebugLevel)
    al.Log(entry)
}

func (al *AsyncLogger) Info(entry *APILogEntry) {
    entry.LogLevel = string(InfoLevel)
    al.Log(entry)
}

func (al *AsyncLogger) Warn(entry *APILogEntry) {
    entry.LogLevel = string(WarnLevel)
    al.Log(entry)
}

func (al *AsyncLogger) Error(entry *APILogEntry) {
    entry.LogLevel = string(ErrorLevel)
    al.Log(entry)
}

func (al *AsyncLogger) Fatal(entry *APILogEntry) {
    entry.LogLevel = string(FatalLevel)
    al.Log(entry)
}
```

## 日志过滤和采样

在高流量场景下，可能需要对日志进行过滤和采样：

```go
// 日志过滤器实现示例
type LogFilter struct {
    filters []LogFilterFunc
}

type LogFilterFunc func(*APILogEntry) bool

func NewLogFilter() *LogFilter {
    return &LogFilter{
        filters: make([]LogFilterFunc, 0),
    }
}

func (lf *LogFilter) AddFilter(filter LogFilterFunc) {
    lf.filters = append(lf.filters, filter)
}

func (lf *LogFilter) ShouldLog(entry *APILogEntry) bool {
    for _, filter := range lf.filters {
        if !filter(entry) {
            return false
        }
    }
    return true
}

// 常用过滤器函数
func ErrorFilter(entry *APILogEntry) bool {
    return entry.StatusCode >= 400
}

func PathFilter(allowedPaths []string) LogFilterFunc {
    return func(entry *APILogEntry) bool {
        for _, path := range allowedPaths {
            if strings.HasPrefix(entry.Path, path) {
                return true
            }
        }
        return false
    }
}

func UserFilter(allowedUsers []string) LogFilterFunc {
    return func(entry *APILogEntry) bool {
        if entry.UserID == "" {
            return false
        }
        for _, user := range allowedUsers {
            if entry.UserID == user {
                return true
            }
        }
        return false
    }
}

// 日志采样器实现示例
type LogSampler struct {
    rate      float64 // 采样率 (0.0 - 1.0)
    threshold int64   // 采样阈值
}

func NewLogSampler(rate float64) *LogSampler {
    if rate < 0.0 {
        rate = 0.0
    }
    if rate > 1.0 {
        rate = 1.0
    }
    
    return &LogSampler{
        rate:      rate,
        threshold: int64(rate * float64(math.MaxInt64)),
    }
}

func (ls *LogSampler) ShouldSample(entry *APILogEntry) bool {
    if ls.rate >= 1.0 {
        return true
    }
    if ls.rate <= 0.0 {
        return false
    }
    
    // 使用请求 ID 的哈希值进行采样
    hash := hashString(entry.RequestID)
    return hash < ls.threshold
}

func hashString(s string) int64 {
    h := fnv.New64a()
    h.Write([]byte(s))
    return int64(h.Sum64())
}

// 带过滤和采样的日志记录器
type FilteredLogger struct {
    logger  *Logger
    filter  *LogFilter
    sampler *LogSampler
}

func NewFilteredLogger(logger *Logger, filter *LogFilter, sampler *LogSampler) *FilteredLogger {
    return &FilteredLogger{
        logger:  logger,
        filter:  filter,
        sampler: sampler,
    }
}

func (fl *FilteredLogger) Log(entry *APILogEntry) error {
    // 应用过滤器
    if fl.filter != nil && !fl.filter.ShouldLog(entry) {
        return nil
    }
    
    // 应用采样器
    if fl.sampler != nil && !fl.sampler.ShouldSample(entry) {
        return nil
    }
    
    return fl.logger.Log(entry)
}
```

## 最佳实践

### 日志设计原则

1. **一致性**：保持日志格式的一致性，便于分析和处理
2. **完整性**：记录足够的信息以支持问题排查
3. **可读性**：日志信息应该清晰易懂
4. **安全性**：避免记录敏感信息

### 性能优化

1. **异步处理**：使用异步方式处理日志，避免阻塞主流程
2. **批量写入**：批量写入日志以提高性能
3. **过滤采样**：对日志进行过滤和采样以减少存储压力
4. **缓冲写入**：使用缓冲区减少磁盘 I/O 操作

### 存储和管理

1. **日志轮转**：实现日志文件的自动轮转
2. **压缩存储**：对历史日志进行压缩存储
3. **备份策略**：制定日志备份策略以防止数据丢失
4. **清理机制**：定期清理过期日志以释放存储空间

### 监控和告警

1. **日志监控**：监控日志系统的健康状态
2. **错误告警**：对错误日志进行实时告警
3. **性能指标**：收集日志处理的性能指标
4. **容量预警**：监控日志存储容量并及时预警

## 小结

日志采集是 API 网关可观测性体系的重要组成部分。通过实现结构化日志、合理的日志级别管理、多种日志写入器、日志采集中间件、异步日志处理、日志过滤和采样等机制，可以构建一个高效、可靠的日志采集系统。在实际应用中，需要根据业务需求和技术架构选择合适的日志采集策略，并持续优化日志处理性能和存储管理，确保系统能够稳定、高效地记录和处理日志信息。