---
title: 防护措施：API 网关的安全防护体系
date: 2025-08-31
categories: [APIGateway]
tags: [api-gateway, security, waf, anti-bot, ddos-protection, microservices]
published: true
---

在现代分布式系统中，API 网关作为系统的入口点，面临着各种安全威胁。为了保护系统免受攻击，API 网关需要实现多层次的安全防护措施。本文将深入探讨 Web 应用防火墙（WAF）、防爬虫措施、DDoS 防护等核心防护机制的实现原理、技术细节和最佳实践。

## Web 应用防火墙（WAF）

WAF 是保护 Web 应用免受常见攻击的重要防护措施，能够检测和阻止 SQL 注入、跨站脚本（XSS）等攻击。

### SQL 注入防护

SQL 注入攻击通过在输入中插入恶意 SQL 代码来操纵数据库查询：

```go
// SQL 注入防护实现示例
type SQLInjectionProtection struct {
    patterns []*regexp.Regexp
}

func NewSQLInjectionProtection() *SQLInjectionProtection {
    patterns := []*regexp.Regexp{
        // 检测常见的 SQL 关键字
        regexp.MustCompile(`(?i)\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b`),
        // 检测常见的 SQL 操作符
        regexp.MustCompile(`(?i)(\b(AND|OR)\b\s*\d+\s*=\s*\d+|--|\b0x[0-9a-f]+\b)`),
        // 检测常见的 SQL 注入模式
        regexp.MustCompile(`(?i)('\s*(OR|AND)\s*'\s*=\s*')|('\s*(OR|AND)\s*\d+\s*=\s*\d+')`),
    }
    
    return &SQLInjectionProtection{
        patterns: patterns,
    }
}

// 检测 SQL 注入
func (s *SQLInjectionProtection) DetectSQLInjection(input string) bool {
    // 统一处理输入，转换为小写并移除多余空格
    normalized := strings.ToLower(strings.TrimSpace(input))
    
    // 检查是否匹配任何 SQL 注入模式
    for _, pattern := range s.patterns {
        if pattern.MatchString(normalized) {
            return true
        }
    }
    
    return false
}

// 清理 SQL 注入
func (s *SQLInjectionProtection) SanitizeInput(input string) string {
    // 移除潜在的危险字符
    sanitized := input
    dangerousChars := []string{"'", "\"", ";", "--", "/*", "*/", "xp_", "sp_"}
    
    for _, char := range dangerousChars {
        sanitized = strings.ReplaceAll(sanitized, char, "")
    }
    
    return sanitized
}

// 高级 SQL 注入检测
func (s *SQLInjectionProtection) AdvancedDetection(input string) *DetectionResult {
    result := &DetectionResult{
        IsThreat: false,
        Score:    0,
        Details:  make([]string, 0),
    }
    
    // 检查输入长度
    if len(input) > 1000 {
        result.Score += 20
        result.Details = append(result.Details, "input too long")
    }
    
    // 检查特殊字符频率
    specialCharCount := 0
    for _, char := range input {
        if char == '\'' || char == '"' || char == ';' || char == '-' {
            specialCharCount++
        }
    }
    
    if specialCharCount > len(input)/10 {
        result.Score += 30
        result.Details = append(result.Details, "high special character frequency")
    }
    
    // 检查 SQL 关键字
    sqlKeywords := []string{"select", "union", "insert", "update", "delete", "drop", "create", "alter"}
    keywordCount := 0
    lowerInput := strings.ToLower(input)
    
    for _, keyword := range sqlKeywords {
        if strings.Contains(lowerInput, keyword) {
            keywordCount++
        }
    }
    
    if keywordCount > 2 {
        result.Score += 40
        result.Details = append(result.Details, "multiple SQL keywords detected")
    }
    
    // 判断是否为威胁
    if result.Score > 50 {
        result.IsThreat = true
    }
    
    return result
}

type DetectionResult struct {
    IsThreat bool
    Score    int
    Details  []string
}
```

### 跨站脚本（XSS）防护

XSS 攻击通过在网页中注入恶意脚本来窃取用户信息或执行恶意操作：

```go
// XSS 防护实现示例
type XSSProtection struct {
    htmlEntityMap map[string]string
    jsEntityMap   map[string]string
    patterns      []*regexp.Regexp
}

func NewXSSProtection() *XSSProtection {
    htmlEntityMap := map[string]string{
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "'": "&#x27;",
        "/": "&#x2F;",
    }
    
    jsEntityMap := map[string]string{
        "\\": "\\\\",
        "'": "\\'",
        "\"": "\\\"",
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
        "<": "\\u003c",
        ">": "\\u003e",
        "&": "\\u0026",
    }
    
    patterns := []*regexp.Regexp{
        // 检测 script 标签
        regexp.MustCompile(`(?i)<\s*script[^>]*>`),
        // 检测 on* 事件处理器
        regexp.MustCompile(`(?i)\b(on\w+)\s*=`),
        // 检测 javascript: 协议
        regexp.MustCompile(`(?i)javascript\s*:`),
        // 检测 data: 协议
        regexp.MustCompile(`(?i)data\s*:`),
        // 检测 eval 函数
        regexp.MustCompile(`(?i)\beval\s*\(`),
    }
    
    return &XSSProtection{
        htmlEntityMap: htmlEntityMap,
        jsEntityMap:   jsEntityMap,
        patterns:      patterns,
    }
}

// HTML 转义
func (x *XSSProtection) EscapeHTML(input string) string {
    result := input
    for char, entity := range x.htmlEntityMap {
        result = strings.ReplaceAll(result, char, entity)
    }
    return result
}

// JavaScript 转义
func (x *XSSProtection) EscapeJS(input string) string {
    result := input
    for char, entity := range x.jsEntityMap {
        result = strings.ReplaceAll(result, char, entity)
    }
    return result
}

// 检测 XSS
func (x *XSSProtection) DetectXSS(input string) bool {
    normalized := strings.ToLower(strings.TrimSpace(input))
    
    for _, pattern := range x.patterns {
        if pattern.MatchString(normalized) {
            return true
        }
    }
    
    return false
}

// 清理 XSS
func (x *XSSProtection) SanitizeInput(input string) string {
    // 移除潜在的危险标签和属性
    dangerousTags := []string{"script", "iframe", "object", "embed", "link", "meta", "style"}
    dangerousAttributes := []string{"onload", "onerror", "onclick", "onmouseover", "onfocus"}
    
    result := input
    
    // 移除危险标签
    for _, tag := range dangerousTags {
        re := regexp.MustCompile(`(?i)<\s*` + tag + `\b[^>]*>.*?</\s*` + tag + `\s*>`)
        result = re.ReplaceAllString(result, "")
        
        re = regexp.MustCompile(`(?i)<\s*` + tag + `\b[^>]*/?>`)
        result = re.ReplaceAllString(result, "")
    }
    
    // 移除危险属性
    for _, attr := range dangerousAttributes {
        re := regexp.MustCompile(`(?i)\b` + attr + `\s*=\s*["'][^"']*["']`)
        result = re.ReplaceAllString(result, "")
    }
    
    return result
}

// 内容安全策略（CSP）
func (x *XSSProtection) GenerateCSP() string {
    return "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self';"
}
```

### 跨站请求伪造（CSRF）防护

CSRF 攻击通过诱使用户在已认证的 Web 应用程序中执行非预期的操作：

```go
// CSRF 防护实现示例
type CSRFProtection struct {
    tokenStore TokenStore
    cookieName string
    headerName string
}

type TokenStore interface {
    GenerateToken(userID string) (string, error)
    ValidateToken(userID, token string) bool
    RemoveToken(userID, token string) error
}

type InMemoryTokenStore struct {
    tokens map[string]map[string]time.Time
    mutex  sync.RWMutex
}

func NewInMemoryTokenStore() *InMemoryTokenStore {
    return &InMemoryTokenStore{
        tokens: make(map[string]map[string]time.Time),
    }
}

func (ts *InMemoryTokenStore) GenerateToken(userID string) (string, error) {
    ts.mutex.Lock()
    defer ts.mutex.Unlock()
    
    token := generateRandomToken(32)
    expiry := time.Now().Add(24 * time.Hour)
    
    if ts.tokens[userID] == nil {
        ts.tokens[userID] = make(map[string]time.Time)
    }
    
    ts.tokens[userID][token] = expiry
    
    return token, nil
}

func (ts *InMemoryTokenStore) ValidateToken(userID, token string) bool {
    ts.mutex.RLock()
    defer ts.mutex.RUnlock()
    
    if userTokens, exists := ts.tokens[userID]; exists {
        if expiry, exists := userTokens[token]; exists {
            if time.Now().Before(expiry) {
                return true
            }
        }
    }
    
    return false
}

func (ts *InMemoryTokenStore) RemoveToken(userID, token string) error {
    ts.mutex.Lock()
    defer ts.mutex.Unlock()
    
    if userTokens, exists := ts.tokens[userID]; exists {
        delete(userTokens, token)
    }
    
    return nil
}

// 生成随机令牌
func generateRandomToken(length int) string {
    bytes := make([]byte, length)
    rand.Read(bytes)
    return base64.URLEncoding.EncodeToString(bytes)
}

// CSRF 中间件
func (cp *CSRFProtection) CSRFMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 对于安全方法（GET, HEAD, OPTIONS, TRACE），生成并设置 CSRF 令牌
        if isSafeMethod(r.Method) {
            userID := getUserIDFromRequest(r)
            if userID != "" {
                token, err := cp.tokenStore.GenerateToken(userID)
                if err == nil {
                    // 设置 CSRF 令牌 Cookie
                    http.SetCookie(w, &http.Cookie{
                        Name:     cp.cookieName,
                        Value:    token,
                        Path:     "/",
                        HttpOnly: true,
                        Secure:   true,
                        SameSite: http.SameSiteStrictMode,
                    })
                }
            }
            next.ServeHTTP(w, r)
            return
        }
        
        // 对于不安全方法，验证 CSRF 令牌
        userID := getUserIDFromRequest(r)
        if userID == "" {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        
        // 从请求头获取令牌
        token := r.Header.Get(cp.headerName)
        if token == "" {
            // 从表单数据获取令牌
            token = r.FormValue("_csrf")
        }
        
        if token == "" {
            http.Error(w, "CSRF token missing", http.StatusForbidden)
            return
        }
        
        // 验证令牌
        if !cp.tokenStore.ValidateToken(userID, token) {
            http.Error(w, "Invalid CSRF token", http.StatusForbidden)
            return
        }
        
        // 验证成功，继续处理请求
        next.ServeHTTP(w, r)
    })
}

func isSafeMethod(method string) bool {
    safeMethods := []string{"GET", "HEAD", "OPTIONS", "TRACE"}
    for _, m := range safeMethods {
        if m == method {
            return true
        }
    }
    return false
}

func getUserIDFromRequest(r *http.Request) string {
    // 从认证信息中获取用户 ID
    // 这里简化处理，实际应用中需要根据具体的认证机制实现
    return r.Header.Get("X-User-ID")
}
```

## 防爬虫措施

防止恶意爬虫对系统造成压力，保护系统资源：

```go
// 防爬虫实现示例
type AntiBotProtection struct {
    rateLimiter    *RateLimiter
    userAgentChecker *UserAgentChecker
    behaviorAnalyzer *BehaviorAnalyzer
    ipBlacklist    *IPBlacklist
}

type RateLimiter struct {
    limits map[string]*ClientLimit
    mutex  sync.RWMutex
}

type ClientLimit struct {
    requests     int64
    lastReset    time.Time
    window       time.Duration
    maxRequests  int64
}

func NewRateLimiter(window time.Duration, maxRequests int64) *RateLimiter {
    return &RateLimiter{
        limits: make(map[string]*ClientLimit),
        window: window,
        maxRequests: maxRequests,
    }
}

func (rl *RateLimiter) CheckRateLimit(clientID string) bool {
    rl.mutex.Lock()
    defer rl.mutex.Unlock()
    
    now := time.Now()
    limit, exists := rl.limits[clientID]
    
    if !exists {
        rl.limits[clientID] = &ClientLimit{
            requests: 1,
            lastReset: now,
            window: rl.window,
            maxRequests: rl.maxRequests,
        }
        return true
    }
    
    // 检查是否需要重置计数器
    if now.Sub(limit.lastReset) > limit.window {
        limit.requests = 0
        limit.lastReset = now
    }
    
    // 检查是否超过限制
    if limit.requests >= limit.maxRequests {
        return false
    }
    
    limit.requests++
    return true
}

type UserAgentChecker struct {
    knownBots []string
    patterns  []*regexp.Regexp
}

func NewUserAgentChecker() *UserAgentChecker {
    knownBots := []string{
        "bot", "crawler", "spider", "scraper", "archiver",
        "Googlebot", "Bingbot", "Slurp", "DuckDuckBot",
        "Baiduspider", "YandexBot", "Sogou", "Exabot",
    }
    
    patterns := make([]*regexp.Regexp, len(knownBots))
    for i, bot := range knownBots {
        patterns[i] = regexp.MustCompile(`(?i)` + regexp.QuoteMeta(bot))
    }
    
    return &UserAgentChecker{
        knownBots: knownBots,
        patterns:  patterns,
    }
}

func (uac *UserAgentChecker) IsBot(userAgent string) bool {
    for _, pattern := range uac.patterns {
        if pattern.MatchString(userAgent) {
            return true
        }
    }
    return false
}

type BehaviorAnalyzer struct {
    clientBehaviors map[string]*ClientBehavior
    mutex           sync.RWMutex
}

type ClientBehavior struct {
    requestTimes    []time.Time
    requestPaths    []string
    requestIntervals []time.Duration
}

func NewBehaviorAnalyzer() *BehaviorAnalyzer {
    return &BehaviorAnalyzer{
        clientBehaviors: make(map[string]*ClientBehavior),
    }
}

func (ba *BehaviorAnalyzer) AnalyzeBehavior(clientID string, path string) bool {
    ba.mutex.Lock()
    defer ba.mutex.Unlock()
    
    behavior, exists := ba.clientBehaviors[clientID]
    if !exists {
        behavior = &ClientBehavior{
            requestTimes: make([]time.Time, 0, 100),
            requestPaths: make([]string, 0, 100),
        }
        ba.clientBehaviors[clientID] = behavior
    }
    
    now := time.Now()
    behavior.requestTimes = append(behavior.requestTimes, now)
    behavior.requestPaths = append(behavior.requestPaths, path)
    
    // 保持最近 100 次请求的记录
    if len(behavior.requestTimes) > 100 {
        behavior.requestTimes = behavior.requestTimes[1:]
        behavior.requestPaths = behavior.requestPaths[1:]
    }
    
    // 分析行为模式
    return ba.detectSuspiciousBehavior(behavior)
}

func (ba *BehaviorAnalyzer) detectSuspiciousBehavior(behavior *ClientBehavior) bool {
    if len(behavior.requestTimes) < 10 {
        return false
    }
    
    // 检查请求频率
    recentRequests := behavior.requestTimes[len(behavior.requestTimes)-10:]
    timeSpan := recentRequests[len(recentRequests)-1].Sub(recentRequests[0])
    if timeSpan < time.Second && len(recentRequests) == 10 {
        // 10 次请求在 1 秒内，可能是爬虫
        return true
    }
    
    // 检查请求路径模式
    if ba.detectSequentialPattern(behavior.requestPaths) {
        return true
    }
    
    return false
}

func (ba *BehaviorAnalyzer) detectSequentialPattern(paths []string) bool {
    if len(paths) < 5 {
        return false
    }
    
    // 检查是否有明显的顺序模式（如 /page/1, /page/2, /page/3）
    sequentialCount := 0
    for i := 1; i < len(paths); i++ {
        if ba.isSequentialPath(paths[i-1], paths[i]) {
            sequentialCount++
        }
    }
    
    // 如果超过 70% 的请求是顺序的，认为是可疑行为
    return float64(sequentialCount)/float64(len(paths)-1) > 0.7
}

func (ba *BehaviorAnalyzer) isSequentialPath(path1, path2 string) bool {
    // 简化的顺序路径检测
    // 实际应用中需要更复杂的逻辑
    re := regexp.MustCompile(`/(\d+)$`)
    matches1 := re.FindStringSubmatch(path1)
    matches2 := re.FindStringSubmatch(path2)
    
    if len(matches1) > 1 && len(matches2) > 1 {
        num1, err1 := strconv.Atoi(matches1[1])
        num2, err2 := strconv.Atoi(matches2[1])
        
        if err1 == nil && err2 == nil && num2 == num1+1 {
            return true
        }
    }
    
    return false
}

type IPBlacklist struct {
    blacklistedIPs map[string]time.Time
    mutex          sync.RWMutex
}

func NewIPBlacklist() *IPBlacklist {
    return &IPBlacklist{
        blacklistedIPs: make(map[string]time.Time),
    }
}

func (ib *IPBlacklist) AddIP(ip string, duration time.Duration) {
    ib.mutex.Lock()
    defer ib.mutex.Unlock()
    
    ib.blacklistedIPs[ip] = time.Now().Add(duration)
}

func (ib *IPBlacklist) IsBlacklisted(ip string) bool {
    ib.mutex.RLock()
    defer ib.mutex.RUnlock()
    
    if expiry, exists := ib.blacklistedIPs[ip]; exists {
        if time.Now().Before(expiry) {
            return true
        }
        // 过期的 IP 从黑名单中移除
        delete(ib.blacklistedIPs, ip)
    }
    
    return false
}

func (ib *IPBlacklist) RemoveIP(ip string) {
    ib.mutex.Lock()
    defer ib.mutex.Unlock()
    
    delete(ib.blacklistedIPs, ip)
}

// 防爬虫中间件
func (abp *AntiBotProtection) AntiBotMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        clientIP := getClientIP(r)
        userAgent := r.Header.Get("User-Agent")
        clientID := fmt.Sprintf("%s:%s", clientIP, userAgent)
        
        // 检查 IP 是否在黑名单中
        if abp.ipBlacklist.IsBlacklisted(clientIP) {
            http.Error(w, "Access denied", http.StatusForbidden)
            return
        }
        
        // 检查 User-Agent 是否为已知爬虫
        if abp.userAgentChecker.IsBot(userAgent) {
            // 对已知爬虫应用更严格的限制
            if !abp.rateLimiter.CheckRateLimit(clientID + ":bot") {
                abp.ipBlacklist.AddIP(clientIP, 1*time.Hour)
                http.Error(w, "Rate limit exceeded", http.StatusTooManyRequests)
                return
            }
        } else {
            // 对普通用户应用常规限制
            if !abp.rateLimiter.CheckRateLimit(clientID) {
                http.Error(w, "Rate limit exceeded", http.StatusTooManyRequests)
                return
            }
        }
        
        // 行为分析
        if abp.behaviorAnalyzer.AnalyzeBehavior(clientID, r.URL.Path) {
            // 检测到可疑行为，加入黑名单
            abp.ipBlacklist.AddIP(clientIP, 24*time.Hour)
            http.Error(w, "Suspicious activity detected", http.StatusForbidden)
            return
        }
        
        next.ServeHTTP(w, r)
    })
}

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

## DDoS 防护

防止分布式拒绝服务攻击，保护系统免受大规模流量冲击：

```go
// DDoS 防护实现示例
type DDoSProtection struct {
    connectionLimiter *ConnectionLimiter
    rateLimiter       *RateLimiter
    trafficAnalyzer   *TrafficAnalyzer
    ipWhitelist       *IPWhitelist
    mitigationEngine  *MitigationEngine
}

type ConnectionLimiter struct {
    maxConnections int64
    currentConnections int64
    mutex          sync.RWMutex
}

func NewConnectionLimiter(maxConnections int64) *ConnectionLimiter {
    return &ConnectionLimiter{
        maxConnections: maxConnections,
    }
}

func (cl *ConnectionLimiter) AcquireConnection() bool {
    cl.mutex.Lock()
    defer cl.mutex.Unlock()
    
    if cl.currentConnections >= cl.maxConnections {
        return false
    }
    
    cl.currentConnections++
    return true
}

func (cl *ConnectionLimiter) ReleaseConnection() {
    cl.mutex.Lock()
    defer cl.mutex.Unlock()
    
    if cl.currentConnections > 0 {
        cl.currentConnections--
    }
}

type TrafficAnalyzer struct {
    trafficStats map[string]*TrafficStat
    mutex        sync.RWMutex
}

type TrafficStat struct {
    bytesIn      int64
    bytesOut     int64
    requestCount int64
    lastUpdate   time.Time
}

func NewTrafficAnalyzer() *TrafficAnalyzer {
    return &TrafficAnalyzer{
        trafficStats: make(map[string]*TrafficStat),
    }
}

func (ta *TrafficAnalyzer) RecordTraffic(clientID string, bytesIn, bytesOut int64) {
    ta.mutex.Lock()
    defer ta.mutex.Unlock()
    
    stat, exists := ta.trafficStats[clientID]
    if !exists {
        stat = &TrafficStat{}
        ta.trafficStats[clientID] = stat
    }
    
    stat.bytesIn += bytesIn
    stat.bytesOut += bytesOut
    stat.requestCount++
    stat.lastUpdate = time.Now()
}

func (ta *TrafficAnalyzer) DetectDDoS() []string {
    ta.mutex.RLock()
    defer ta.mutex.RUnlock()
    
    var suspiciousClients []string
    now := time.Now()
    
    for clientID, stat := range ta.trafficStats {
        // 检查最近 10 秒内的流量
        if now.Sub(stat.lastUpdate) < 10*time.Second {
            // 如果请求频率过高，认为是可疑客户端
            if stat.requestCount > 1000 { // 10 秒内超过 1000 次请求
                suspiciousClients = append(suspiciousClients, clientID)
            }
        }
    }
    
    return suspiciousClients
}

type IPWhitelist struct {
    whitelistedIPs map[string]bool
    mutex          sync.RWMutex
}

func NewIPWhitelist() *IPWhitelist {
    return &IPWhitelist{
        whitelistedIPs: make(map[string]bool),
    }
}

func (iw *IPWhitelist) AddIP(ip string) {
    iw.mutex.Lock()
    defer iw.mutex.Unlock()
    
    iw.whitelistedIPs[ip] = true
}

func (iw *IPWhitelist) IsWhitelisted(ip string) bool {
    iw.mutex.RLock()
    defer iw.mutex.RUnlock()
    
    return iw.whitelistedIPs[ip]
}

type MitigationEngine struct {
    mitigationRules []MitigationRule
    activeMitigations map[string]*MitigationAction
    mutex             sync.RWMutex
}

type MitigationRule struct {
    Condition     MitigationCondition
    Action        MitigationActionType
    Duration      time.Duration
    Threshold     float64
}

type MitigationCondition struct {
    Metric        string // "requests_per_second", "bandwidth", "error_rate"
    Aggregation   string // "ip", "user_agent", "path"
    Comparison    string // "gt", "lt", "eq"
}

type MitigationActionType string

const (
    BlockIP        MitigationActionType = "block_ip"
    RateLimit      MitigationActionType = "rate_limit"
    Challenge      MitigationActionType = "challenge"
    Redirect       MitigationActionType = "redirect"
)

type MitigationAction struct {
    Type      MitigationActionType
    StartTime time.Time
    EndTime   time.Time
    Target    string
}

func NewMitigationEngine() *MitigationEngine {
    return &MitigationEngine{
        mitigationRules: []MitigationRule{
            {
                Condition: MitigationCondition{
                    Metric:      "requests_per_second",
                    Aggregation: "ip",
                    Comparison:  "gt",
                },
                Action:    RateLimit,
                Duration:  5 * time.Minute,
                Threshold: 1000,
            },
            {
                Condition: MitigationCondition{
                    Metric:      "bandwidth",
                    Aggregation: "ip",
                    Comparison:  "gt",
                },
                Action:    BlockIP,
                Duration:  1 * time.Hour,
                Threshold: 100 * 1024 * 1024, // 100 MB
            },
        },
        activeMitigations: make(map[string]*MitigationAction),
    }
}

func (me *MitigationEngine) ApplyMitigation(clientID string, metric string, value float64) *MitigationAction {
    me.mutex.Lock()
    defer me.mutex.Unlock()
    
    now := time.Now()
    
    // 检查是否有活动的缓解措施
    if action, exists := me.activeMitigations[clientID]; exists {
        if now.Before(action.EndTime) {
            return action
        }
        // 缓解措施已过期，移除
        delete(me.activeMitigations, clientID)
    }
    
    // 检查是否触发缓解规则
    for _, rule := range me.mitigationRules {
        if rule.Condition.Metric == metric {
            triggered := false
            switch rule.Condition.Comparison {
            case "gt":
                triggered = value > rule.Threshold
            case "lt":
                triggered = value < rule.Threshold
            case "eq":
                triggered = value == rule.Threshold
            }
            
            if triggered {
                action := &MitigationAction{
                    Type:      rule.Action,
                    StartTime: now,
                    EndTime:   now.Add(rule.Duration),
                    Target:    clientID,
                }
                
                me.activeMitigations[clientID] = action
                return action
            }
        }
    }
    
    return nil
}

// DDoS 防护中间件
func (ddos *DDoSProtection) DDoSMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        clientIP := getClientIP(r)
        clientID := fmt.Sprintf("%s:%s", clientIP, r.Header.Get("User-Agent"))
        
        // 检查 IP 是否在白名单中
        if ddos.ipWhitelist.IsWhitelisted(clientIP) {
            next.ServeHTTP(w, r)
            return
        }
        
        // 检查连接限制
        if !ddos.connectionLimiter.AcquireConnection() {
            http.Error(w, "Service temporarily unavailable", http.StatusServiceUnavailable)
            return
        }
        defer ddos.connectionLimiter.ReleaseConnection()
        
        // 记录流量统计
        contentLength := r.ContentLength
        if contentLength < 0 {
            contentLength = 0
        }
        ddos.trafficAnalyzer.RecordTraffic(clientID, contentLength, 0)
        
        // 检查是否触发缓解措施
        action := ddos.mitigationEngine.ApplyMitigation(clientID, "requests_per_second", 1)
        if action != nil {
            switch action.Type {
            case BlockIP:
                http.Error(w, "Access denied", http.StatusForbidden)
                return
            case RateLimit:
                // 应用速率限制
                time.Sleep(100 * time.Millisecond)
            case Challenge:
                // 实施挑战（如 CAPTCHA）
                // 这里简化处理，实际应用中需要实现具体的挑战机制
            }
        }
        
        next.ServeHTTP(w, r)
    })
}

// 流量清洗功能
func (ddos *DDoSProtection) StartTrafficCleaning() {
    ticker := time.NewTicker(10 * time.Second)
    go func() {
        for range ticker.C {
            ddos.cleanTraffic()
        }
    }()
}

func (ddos *DDoSProtection) cleanTraffic() {
    // 检测 DDoS 攻击
    suspiciousClients := ddos.trafficAnalyzer.DetectDDoS()
    
    for _, clientID := range suspiciousClients {
        // 对可疑客户端应用缓解措施
        ddos.mitigationEngine.ApplyMitigation(clientID, "bandwidth", 100*1024*1024)
    }
    
    // 清理过期的统计数据
    ddos.trafficAnalyzer.mutex.Lock()
    now := time.Now()
    for clientID, stat := range ddos.trafficAnalyzer.trafficStats {
        if now.Sub(stat.lastUpdate) > 5*time.Minute {
            delete(ddos.trafficAnalyzer.trafficStats, clientID)
        }
    }
    ddos.trafficAnalyzer.mutex.Unlock()
}
```

## 最佳实践

### 防护策略配置

```yaml
# 防护策略配置示例
security:
  waf:
    sql_injection:
      enabled: true
      sensitivity: high
      block_mode: true
      
    xss:
      enabled: true
      sanitize_mode: true
      csp_enabled: true
      
    csrf:
      enabled: true
      token_length: 32
      token_expiry: 24h
      
  anti_bot:
    rate_limiting:
      requests_per_minute: 100
      bot_requests_per_minute: 10
      
    behavior_analysis:
      enabled: true
      detection_window: 60s
      threshold: 0.7
      
    ip_blacklist:
      auto_blacklist: true
      blacklist_duration: 24h
      
  ddos_protection:
    connection_limit:
      max_connections: 10000
      
    rate_limiting:
      requests_per_second: 1000
      
    traffic_analysis:
      enabled: true
      analysis_window: 10s
      detection_threshold: 1000
      
    mitigation:
      auto_mitigation: true
      mitigation_duration: 5m
```

### 监控与告警

```go
// 安全监控实现示例
type SecurityMonitor struct {
    metrics      *SecurityMetrics
    alertManager *AlertManager
}

type SecurityMetrics struct {
    totalRequests     int64
    blockedRequests   int64
    sqlInjectionAttempts int64
    xssAttempts      int64
    csrfViolations   int64
    botRequests      int64
    ddosAttacks      int64
    mutex            sync.RWMutex
}

type AlertManager struct {
    alerts []Alert
    mutex  sync.RWMutex
}

type Alert struct {
    Type        string
    Severity    string
    Message     string
    Timestamp   time.Time
    Source      string
}

func (sm *SecurityMonitor) RecordMetric(metric string, value int64) {
    sm.metrics.mutex.Lock()
    defer sm.metrics.mutex.Unlock()
    
    switch metric {
    case "total_requests":
        sm.metrics.totalRequests += value
    case "blocked_requests":
        sm.metrics.blockedRequests += value
    case "sql_injection_attempts":
        sm.metrics.sqlInjectionAttempts += value
    case "xss_attempts":
        sm.metrics.xssAttempts += value
    case "csrf_violations":
        sm.metrics.csrfViolations += value
    case "bot_requests":
        sm.metrics.botRequests += value
    case "ddos_attacks":
        sm.metrics.ddosAttacks += value
    }
}

func (sm *SecurityMonitor) CheckAlerts() {
    sm.metrics.mutex.RLock()
    defer sm.metrics.mutex.RUnlock()
    
    // 检查 SQL 注入攻击
    if sm.metrics.sqlInjectionAttempts > 100 {
        sm.alertManager.CreateAlert("SQL_INJECTION", "HIGH", 
            fmt.Sprintf("High number of SQL injection attempts detected: %d", 
                sm.metrics.sqlInjectionAttempts), "WAF")
    }
    
    // 检查 XSS 攻击
    if sm.metrics.xssAttempts > 100 {
        sm.alertManager.CreateAlert("XSS_ATTACK", "HIGH", 
            fmt.Sprintf("High number of XSS attempts detected: %d", 
                sm.metrics.xssAttempts), "WAF")
    }
    
    // 检查 DDoS 攻击
    if sm.metrics.ddosAttacks > 10 {
        sm.alertManager.CreateAlert("DDOS_ATTACK", "CRITICAL", 
            fmt.Sprintf("DDoS attack detected: %d attacks", 
                sm.metrics.ddosAttacks), "DDoS Protection")
    }
}
```

## 小结

API 网关的安全防护体系是保护系统免受各种安全威胁的重要屏障。通过实现 Web 应用防火墙、防爬虫措施、DDoS 防护等多层次的安全机制，可以有效提升系统的安全性和稳定性。在实际应用中，需要根据业务特点和安全要求选择合适的防护策略，并持续监控和优化防护效果，确保系统在面对各种安全威胁时能够保持稳定运行。