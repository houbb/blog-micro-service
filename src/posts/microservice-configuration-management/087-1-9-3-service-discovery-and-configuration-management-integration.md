---
title: 9.3 服务发现与配置管理结合：构建动态配置管理体系
date: 2025-08-31
categories: [Configuration Management]
tags: [microservice-configuration-management]
published: true
---

# 9.3 服务发现与配置管理结合

在微服务架构中，服务发现和配置管理是两个密切相关的核心组件。服务发现帮助服务找到彼此，而配置管理则确保服务具有正确的配置信息。将两者结合可以构建一个动态、自适应的配置管理体系，提高系统的弹性和可维护性。

## 服务注册与发现机制

服务发现是微服务架构的基础，它允许服务动态地注册和发现其他服务的位置和状态。

### 基于Consul的服务发现实现

```go
// service_discovery.go
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/hashicorp/consul/api"
)

// ServiceInfo 服务信息结构
type ServiceInfo struct {
    ID      string            `json:"id"`
    Name    string            `json:"name"`
    Address string            `json:"address"`
    Port    int               `json:"port"`
    Tags    []string          `json:"tags"`
    Meta    map[string]string `json:"meta"`
}

// ServiceDiscovery 服务发现管理器
type ServiceDiscovery struct {
    client     *api.Client
    serviceID  string
    serviceName string
    address    string
    port       int
}

// NewServiceDiscovery 创建新的服务发现实例
func NewServiceDiscovery(consulAddr, serviceName, address string, port int) (*ServiceDiscovery, error) {
    // 创建Consul客户端
    config := api.DefaultConfig()
    config.Address = consulAddr
    
    client, err := api.NewClient(config)
    if err != nil {
        return nil, fmt.Errorf("failed to create Consul client: %v", err)
    }
    
    serviceID := fmt.Sprintf("%s-%s-%d", serviceName, address, port)
    
    return &ServiceDiscovery{
        client:      client,
        serviceID:   serviceID,
        serviceName: serviceName,
        address:     address,
        port:        port,
    }, nil
}

// RegisterService 注册服务
func (sd *ServiceDiscovery) RegisterService(tags []string, meta map[string]string) error {
    // 准备注册信息
    registration := &api.AgentServiceRegistration{
        ID:      sd.serviceID,
        Name:    sd.serviceName,
        Address: sd.address,
        Port:    sd.port,
        Tags:    tags,
        Meta:    meta,
        Check: &api.AgentServiceCheck{
            HTTP:                           fmt.Sprintf("http://%s:%d/health", sd.address, sd.port),
            Interval:                       "10s",
            Timeout:                        "5s",
            DeregisterCriticalServiceAfter: "1m",
        },
    }
    
    // 注册服务
    if err := sd.client.Agent().ServiceRegister(registration); err != nil {
        return fmt.Errorf("failed to register service: %v", err)
    }
    
    log.Printf("Service registered: %s (%s:%d)", sd.serviceID, sd.address, sd.port)
    return nil
}

// DeregisterService 注销服务
func (sd *ServiceDiscovery) DeregisterService() error {
    if err := sd.client.Agent().ServiceDeregister(sd.serviceID); err != nil {
        return fmt.Errorf("failed to deregister service: %v", err)
    }
    
    log.Printf("Service deregistered: %s", sd.serviceID)
    return nil
}

// DiscoverServices 发现服务
func (sd *ServiceDiscovery) DiscoverServices(serviceName string, tag string) ([]*ServiceInfo, error) {
    // 准备查询选项
    queryOptions := &api.QueryOptions{
        UseCache: true,
        MaxAge:   10 * time.Second,
    }
    
    // 添加标签过滤
    if tag != "" {
        queryOptions.Tag = tag
    }
    
    // 查询服务
    services, _, err := sd.client.Health().Service(serviceName, tag, true, queryOptions)
    if err != nil {
        return nil, fmt.Errorf("failed to discover services: %v", err)
    }
    
    // 转换为ServiceInfo结构
    var serviceInfos []*ServiceInfo
    for _, serviceEntry := range services {
        serviceInfo := &ServiceInfo{
            ID:      serviceEntry.Service.ID,
            Name:    serviceEntry.Service.Service,
            Address: serviceEntry.Service.Address,
            Port:    serviceEntry.Service.Port,
            Tags:    serviceEntry.Service.Tags,
            Meta:    serviceEntry.Service.Meta,
        }
        serviceInfos = append(serviceInfos, serviceInfo)
    }
    
    return serviceInfos, nil
}

// GetServiceConfig 获取服务配置
func (sd *ServiceDiscovery) GetServiceConfig(configKey string) (string, error) {
    // 从Consul KV存储获取配置
    kv := sd.client.KV()
    pair, _, err := kv.Get(configKey, nil)
    if err != nil {
        return "", fmt.Errorf("failed to get config from Consul: %v", err)
    }
    
    if pair == nil {
        return "", fmt.Errorf("config key not found: %s", configKey)
    }
    
    return string(pair.Value), nil
}

// SetServiceConfig 设置服务配置
func (sd *ServiceDiscovery) SetServiceConfig(configKey, configValue string) error {
    // 设置配置到Consul KV存储
    kv := sd.client.KV()
    pair := &api.KVPair{
        Key:   configKey,
        Value: []byte(configValue),
    }
    
    _, err := kv.Put(pair, nil)
    if err != nil {
        return fmt.Errorf("failed to set config in Consul: %v", err)
    }
    
    log.Printf("Config set: %s = %s", configKey, configValue)
    return nil
}

// WatchServiceChanges 监听服务变化
func (sd *ServiceDiscovery) WatchServiceChanges(serviceName string, callback func([]*ServiceInfo)) {
    // 创建服务监控计划
    plan := &api.QueryOptions{
        WaitTime: 10 * time.Minute,
    }
    
    go func() {
        for {
            // 监控服务变化
            services, meta, err := sd.client.Health().Service(serviceName, "", true, plan)
            if err != nil {
                log.Printf("Error watching service changes: %v", err)
                time.Sleep(5 * time.Second)
                continue
            }
            
            // 更新等待索引
            plan.WaitIndex = meta.LastIndex
            
            // 转换服务信息
            var serviceInfos []*ServiceInfo
            for _, serviceEntry := range services {
                serviceInfo := &ServiceInfo{
                    ID:      serviceEntry.Service.ID,
                    Name:    serviceEntry.Service.Service,
                    Address: serviceEntry.Service.Address,
                    Port:    serviceEntry.Service.Port,
                    Tags:    serviceEntry.Service.Tags,
                    Meta:    serviceEntry.Service.Meta,
                }
                serviceInfos = append(serviceInfos, serviceInfo)
            }
            
            // 调用回调函数
            callback(serviceInfos)
        }
    }()
}

// HTTP健康检查端点
func healthHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)
    
    response := map[string]interface{}{
        "status":    "healthy",
        "timestamp": time.Now().Format(time.RFC3339),
    }
    
    json.NewEncoder(w).Encode(response)
}

func main() {
    // 获取服务信息
    serviceName := getEnv("SERVICE_NAME", "user-service")
    servicePort := getEnvInt("SERVICE_PORT", 8080)
    consulAddr := getEnv("CONSUL_ADDR", "localhost:8500")
    
    // 获取本地IP地址
    localIP, err := getLocalIP()
    if err != nil {
        log.Fatalf("Failed to get local IP: %v", err)
    }
    
    // 创建服务发现实例
    sd, err := NewServiceDiscovery(consulAddr, serviceName, localIP, servicePort)
    if err != nil {
        log.Fatalf("Failed to create service discovery: %v", err)
    }
    
    // 设置HTTP服务器
    http.HandleFunc("/health", healthHandler)
    http.HandleFunc("/config", func(w http.ResponseWriter, r *http.Request) {
        if r.Method == "GET" {
            key := r.URL.Query().Get("key")
            if key == "" {
                http.Error(w, "Missing config key", http.StatusBadRequest)
                return
            }
            
            value, err := sd.GetServiceConfig(key)
            if err != nil {
                http.Error(w, err.Error(), http.StatusNotFound)
                return
            }
            
            w.Header().Set("Content-Type", "text/plain")
            w.Write([]byte(value))
        } else if r.Method == "POST" {
            key := r.FormValue("key")
            value := r.FormValue("value")
            
            if key == "" || value == "" {
                http.Error(w, "Missing key or value", http.StatusBadRequest)
                return
            }
            
            if err := sd.SetServiceConfig(key, value); err != nil {
                http.Error(w, err.Error(), http.StatusInternalServerError)
                return
            }
            
            w.WriteHeader(http.StatusOK)
            w.Write([]byte("Config updated"))
        }
    })
    
    // 启动HTTP服务器
    go func() {
        log.Printf("Starting HTTP server on %s:%d", localIP, servicePort)
        if err := http.ListenAndServe(fmt.Sprintf(":%d", servicePort), nil); err != nil {
            log.Fatalf("Failed to start HTTP server: %v", err)
        }
    }()
    
    // 注册服务
    tags := []string{"microservice", "user-service", "api"}
    meta := map[string]string{
        "version": "1.0.0",
        "env":     getEnv("ENV", "development"),
    }
    
    if err := sd.RegisterService(tags, meta); err != nil {
        log.Fatalf("Failed to register service: %v", err)
    }
    
    // 监听服务变化
    sd.WatchServiceChanges("order-service", func(services []*ServiceInfo) {
        log.Printf("Order service instances changed: %d instances", len(services))
        for _, service := range services {
            log.Printf("  - %s: %s:%d", service.ID, service.Address, service.Port)
        }
    })
    
    // 设置优雅关闭
    sigChan := make(chan os.Signal, 1)
    signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
    
    <-sigChan
    log.Println("Shutting down...")
    
    // 注销服务
    if err := sd.DeregisterService(); err != nil {
        log.Printf("Failed to deregister service: %v", err)
    }
    
    log.Println("Shutdown complete")
}

// 辅助函数
func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
    if value := os.Getenv(key); value != "" {
        var result int
        if _, err := fmt.Sscanf(value, "%d", &result); err == nil {
            return result
        }
    }
    return defaultValue
}

func getLocalIP() (string, error) {
    conn, err := net.Dial("udp", "8.8.8.8:80")
    if err != nil {
        return "", err
    }
    defer conn.Close()
    
    localAddr := conn.LocalAddr().(*net.UDPAddr)
    return localAddr.IP.String(), nil
}