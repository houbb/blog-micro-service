---
title: 社交平台与IoT中的微服务架构：构建海量用户和设备的分布式系统
date: 2025-08-31
categories: [Microservices]
tags: [microservices, social platforms, IoT, scalability, real-time]
published: true
---

# 社交平台与IoT中的微服务架构

社交平台和IoT应用具有用户量大、数据量大、实时性要求高等特点。微服务架构能够很好地应对这些挑战，通过弹性扩展和实时数据处理能力，为用户提供流畅的体验。本章将深入探讨社交平台和IoT应用中微服务架构的设计原则、核心服务划分和最佳实践。

## 社交平台业务特点与挑战

### 海量用户与高并发

社交平台通常拥有数亿甚至数十亿用户，需要处理极高的并发访问和数据处理需求。

```java
// 社交平台高并发处理策略
public class SocialPlatformHighConcurrency {
    // 1. 分层缓存策略
    public class LayeredCachingStrategy {
        // L1缓存：本地缓存（Caffeine）
        private Cache<String, Object> localCache;
        
        // L2缓存：分布式缓存（Redis集群）
        @Autowired
        private RedisTemplate<String, Object> redisTemplate;
        
        // L3缓存：CDN缓存
        @Autowired
        private CDNService cdnService;
        
        public Object getData(String key) {
            // 1. 查找本地缓存
            Object value = localCache.getIfPresent(key);
            if (value != null) {
                return value;
            }
            
            // 2. 查找分布式缓存
            value = redisTemplate.opsForValue().get(key);
            if (value != null) {
                // 回填本地缓存
                localCache.put(key, value);
                return value;
            }
            
            // 3. 查找CDN缓存
            value = cdnService.getFromCDN(key);
            if (value != null) {
                // 回填分布式缓存
                redisTemplate.opsForValue().set(key, value, Duration.ofMinutes(30));
                // 回填本地缓存
                localCache.put(key, value);
                return value;
            }
            
            // 4. 查询数据库
            value = databaseService.query(key);
            if (value != null) {
                // 回填所有缓存层
                cdnService.putToCDN(key, value);
                redisTemplate.opsForValue().set(key, value, Duration.ofMinutes(30));
                localCache.put(key, value);
            }
            
            return value;
        }
    }
    
    // 2. 数据分片策略
    public class DataShardingStrategy {
        // 用户数据分片
        public String getUserShard(String userId) {
            // 根据用户ID进行分片
            int shardIndex = userId.hashCode() % getUserShardCount();
            return "user_shard_" + shardIndex;
        }
        
        // 内容数据分片
        public String getContentShard(String contentId) {
            // 根据内容ID进行分片
            int shardIndex = contentId.hashCode() % getContentShardCount();
            return "content_shard_" + shardIndex;
        }
        
        // 关系数据分片
        public String getRelationShard(String userId) {
            // 根据用户ID进行分片
            int shardIndex = userId.hashCode() % getRelationShardCount();
            return "relation_shard_" + shardIndex;
        }
    }
    
    // 3. 读写分离策略
    public class ReadWriteSeparationStrategy {
        private List<DataSource> readDataSources;
        private DataSource writeDataSource;
        private LoadBalancer loadBalancer;
        
        public Object readData(String query) {
            // 负载均衡选择读库
            DataSource readDataSource = loadBalancer.select(readDataSources);
            return readDataSource.executeQuery(query);
        }
        
        public void writeData(String sql, Object... params) {
            // 写操作发送到主库
            writeDataSource.executeWrite(sql, params);
        }
    }
}
```

### 实时性要求

社交平台需要实时处理用户动态、消息推送、在线状态等实时性要求高的功能。

```java
// 实时处理架构
@Component
public class RealTimeProcessingArchitecture {
    // WebSocket长连接管理
    public class WebSocketConnectionManager {
        private ConcurrentHashMap<String, WebSocketSession> userSessions;
        private ScheduledExecutorService heartbeatScheduler;
        
        // 建立连接
        public void connectUser(String userId, WebSocketSession session) {
            userSessions.put(userId, session);
            
            // 发送连接确认消息
            sendMessage(userId, new ConnectionAckMessage());
            
            // 启动心跳检测
            startHeartbeat(userId, session);
        }
        
        // 断开连接
        public void disconnectUser(String userId) {
            WebSocketSession session = userSessions.remove(userId);
            if (session != null && session.isOpen()) {
                try {
                    session.close();
                } catch (IOException e) {
                    log.error("Failed to close WebSocket session for user: " + userId, e);
                }
            }
        }
        
        // 发送实时消息
        public void sendRealTimeMessage(String userId, RealTimeMessage message) {
            WebSocketSession session = userSessions.get(userId);
            if (session != null && session.isOpen()) {
                try {
                    session.sendMessage(new TextMessage(objectMapper.writeValueAsString(message)));
                } catch (Exception e) {
                    log.error("Failed to send real-time message to user: " + userId, e);
                    // 处理发送失败的情况
                    handleSendMessageFailure(userId, message);
                }
            }
        }
        
        // 心跳检测
        private void startHeartbeat(String userId, WebSocketSession session) {
            heartbeatScheduler.scheduleAtFixedRate(() -> {
                if (session.isOpen()) {
                    try {
                        session.sendMessage(new PingMessage());
                    } catch (IOException e) {
                        log.warn("Heartbeat failed for user: " + userId, e);
                        disconnectUser(userId);
                    }
                }
            }, 30, 30, TimeUnit.SECONDS); // 每30秒发送一次心跳
        }
    }
    
    // 消息队列实时处理
    public class MessageQueueProcessing {
        // 实时消息处理
        @RabbitListener(queues = "realtime.notifications")
        public void handleRealTimeNotification(NotificationEvent event) {
            try {
                // 处理通知事件
                processNotification(event);
                
                // 推送实时消息
                pushRealTimeMessage(event);
                
            } catch (Exception e) {
                log.error("Failed to process real-time notification", e);
                // 发送到死信队列进行重试
                deadLetterQueue.send(event, e);
            }
        }
        
        // 流数据处理
        @KafkaListener(topics = "user.activities")
        public void handleUserActivity(ConsumerRecord<String, UserActivity> record) {
            try {
                UserActivity activity = record.value();
                
                // 实时更新用户动态
                updateUserFeed(activity);
                
                // 实时更新好友动态
                updateFriendFeeds(activity);
                
                // 实时更新推荐系统
                updateRecommendationSystem(activity);
                
            } catch (Exception e) {
                log.error("Failed to process user activity", e);
                // 记录处理失败的日志
                failedActivityLogService.logFailedActivity(record, e);
            }
        }
    }
    
    // 流处理引擎
    public class StreamProcessingEngine {
        // 用户行为流处理
        public void processUserBehaviorStream() {
            StreamsBuilder builder = new StreamsBuilder();
            
            // 读取用户行为流
            KStream<String, UserBehavior> userBehaviors = builder.stream("user-behaviors");
            
            // 实时计算用户活跃度
            KTable<String, Long> userActivityScores = userBehaviors
                .groupBy((userId, behavior) -> userId)
                .windowedBy(TimeWindows.of(Duration.ofMinutes(5)))
                .count();
            
            // 实时计算热门内容
            KTable<String, Long> trendingContent = userBehaviors
                .filter((userId, behavior) -> behavior.getType() == BehaviorType.VIEW_CONTENT)
                .mapValues(behavior -> behavior.getContentId())
                .groupBy((userId, contentId) -> contentId)
                .windowedBy(TimeWindows.of(Duration.ofMinutes(10)))
                .count();
            
            // 输出结果
            userActivityScores.toStream().to("user-activity-scores");
            trendingContent.toStream().to("trending-content");
            
            // 启动流处理应用
            KafkaStreams streams = new KafkaStreams(builder.build(), streamProps);
            streams.start();
        }
    }
}
```

## IoT平台业务特点与挑战

### 海量设备连接

IoT平台需要处理数百万甚至数千万设备的连接和数据传输。

```java
// IoT平台架构设计
public class IoTPlatformArchitecture {
    // 设备连接管理
    public class DeviceConnectionManager {
        private ConcurrentHashMap<String, DeviceSession> deviceSessions;
        private LoadBalancer loadBalancer;
        private List<ConnectionServer> connectionServers;
        
        // 设备连接
        public void connectDevice(DeviceInfo deviceInfo, Channel channel) {
            // 负载均衡选择连接服务器
            ConnectionServer server = loadBalancer.select(connectionServers);
            
            // 创建设备会话
            DeviceSession session = new DeviceSession(deviceInfo, channel, server);
            deviceSessions.put(deviceInfo.getDeviceId(), session);
            
            // 记录连接日志
            connectionLogService.logConnection(deviceInfo, ConnectionStatus.CONNECTED);
            
            // 发送连接确认
            sendConnectionAck(deviceInfo.getDeviceId());
        }
        
        // 设备断开连接
        public void disconnectDevice(String deviceId) {
            DeviceSession session = deviceSessions.remove(deviceId);
            if (session != null) {
                session.close();
                connectionLogService.logConnection(session.getDeviceInfo(), 
                                                 ConnectionStatus.DISCONNECTED);
            }
        }
        
        // 心跳管理
        public void handleHeartbeat(String deviceId) {
            DeviceSession session = deviceSessions.get(deviceId);
            if (session != null) {
                session.updateLastHeartbeat();
                
                // 检查设备状态
                checkDeviceStatus(session);
            }
        }
    }
    
    // 协议适配器
    public class ProtocolAdapter {
        // MQTT协议适配
        public class MQTTProtocolAdapter {
            public void handleMQTTMessage(MqttMessage message, DeviceSession session) {
                try {
                    // 解析MQTT消息
                    IoTMessage iotMessage = parseMQTTMessage(message);
                    
                    // 转换为内部消息格式
                    InternalMessage internalMessage = convertToInternalMessage(
                        iotMessage, session.getDeviceInfo());
                        
                    // 发送到消息队列
                    messageQueue.send("device.data", internalMessage);
                    
                } catch (Exception e) {
                    log.error("Failed to handle MQTT message", e);
                    // 发送错误响应
                    sendErrorResponse(session, e);
                }
            }
        }
        
        // CoAP协议适配
        public class CoAPProtocolAdapter {
            public void handleCoAPMessage(CoapMessage message, DeviceSession session) {
                try {
                    // 解析CoAP消息
                    IoTMessage iotMessage = parseCoAPMessage(message);
                    
                    // 转换为内部消息格式
                    InternalMessage internalMessage = convertToInternalMessage(
                        iotMessage, session.getDeviceInfo());
                        
                    // 发送到消息队列
                    messageQueue.send("device.data", internalMessage);
                    
                } catch (Exception e) {
                    log.error("Failed to handle CoAP message", e);
                    // 发送错误响应
                    sendErrorResponse(session, e);
                }
            }
        }
        
        // HTTP协议适配
        public class HTTPProtocolAdapter {
            public void handleHTTPMessage(HttpServletRequest request, 
                                        HttpServletResponse response) {
                try {
                    // 解析HTTP请求
                    IoTMessage iotMessage = parseHTTPMessage(request);
                    
                    // 获取设备信息
                    DeviceInfo deviceInfo = getDeviceInfo(request);
                    
                    // 转换为内部消息格式
                    InternalMessage internalMessage = convertToInternalMessage(
                        iotMessage, deviceInfo);
                        
                    // 发送到消息队列
                    messageQueue.send("device.data", internalMessage);
                    
                    // 发送响应
                    sendHTTPResponse(response, HttpStatus.OK);
                    
                } catch (Exception e) {
                    log.error("Failed to handle HTTP message", e);
                    // 发送错误响应
                    sendHTTPResponse(response, HttpStatus.INTERNAL_SERVER_ERROR);
                }
            }
        }
    }
    
    // 数据处理流水线
    public class DataProcessingPipeline {
        // 设备数据预处理
        public class DataPreprocessor {
            public ProcessedData preprocess(RawDeviceData rawData) {
                ProcessedData processedData = new ProcessedData();
                
                // 数据清洗
                processedData.setCleanedData(cleanData(rawData));
                
                // 数据验证
                if (!validateData(processedData.getCleanedData())) {
                    throw new InvalidDataException("Invalid device data");
                }
                
                // 数据转换
                processedData.setTransformedData(transformData(processedData.getCleanedData()));
                
                // 数据 enrich
                processedData.setEnrichedData(enrichData(processedData.getTransformedData()));
                
                return processedData;
            }
        }
        
        // 实时数据处理
        public class RealTimeDataProcessor {
            @RabbitListener(queues = "device.data")
            public void processDeviceData(InternalMessage message) {
                try {
                    // 预处理数据
                    ProcessedData processedData = dataPreprocessor.preprocess(
                        message.getRawData());
                    
                    // 实时分析
                    AnalysisResult analysisResult = realTimeAnalyzer.analyze(
                        processedData.getEnrichedData());
                        
                    // 规则引擎处理
                    RuleEngineResult ruleResult = ruleEngine.evaluate(
                        analysisResult, message.getDeviceInfo());
                        
                    // 执行动作
                    if (ruleResult.shouldTriggerAction()) {
                        actionExecutor.execute(ruleResult.getAction(), 
                                             message.getDeviceInfo());
                    }
                    
                    // 存储数据
                    dataStorageService.store(processedData, message.getDeviceInfo());
                    
                } catch (Exception e) {
                    log.error("Failed to process device data", e);
                    // 发送到死信队列
                    deadLetterQueue.send(message, e);
                }
            }
        }
    }
}
```

### 边缘计算集成

IoT平台通常需要与边缘计算结合，以降低延迟和减少云端负载。

```java
// 边缘计算集成
public class EdgeComputingIntegration {
    // 边缘节点管理
    public class EdgeNodeManager {
        private ConcurrentHashMap<String, EdgeNode> edgeNodes;
        private LoadBalancer loadBalancer;
        
        // 注册边缘节点
        public void registerEdgeNode(EdgeNodeRegistration registration) {
            EdgeNode node = new EdgeNode(registration);
            edgeNodes.put(node.getId(), node);
            
            // 更新节点状态
            updateNodeStatus(node.getId(), NodeStatus.ONLINE);
            
            // 同步配置
            syncConfiguration(node);
        }
        
        // 分配设备到边缘节点
        public EdgeNode assignDeviceToDeviceNode(String deviceId) {
            // 根据设备位置和负载情况选择边缘节点
            EdgeNode selectedNode = loadBalancer.selectEdgeNode(
                edgeNodes.values(), deviceId);
                
            if (selectedNode != null) {
                // 更新设备与边缘节点的映射关系
                deviceEdgeNodeMapping.put(deviceId, selectedNode.getId());
                
                // 通知边缘节点
                notifyEdgeNode(selectedNode, deviceId);
            }
            
            return selectedNode;
        }
        
        // 边缘计算任务分发
        public void distributeEdgeComputingTask(EdgeComputingTask task) {
            // 根据任务类型和设备位置选择边缘节点
            List<EdgeNode> suitableNodes = findSuitableEdgeNodes(task);
            
            // 负载均衡分发任务
            EdgeNode selectedNode = loadBalancer.select(suitableNodes);
            
            // 发送任务到边缘节点
            edgeNodeClient.sendTask(selectedNode, task);
        }
    }
    
    // 边缘计算任务管理
    public class EdgeComputingTaskManager {
        // 数据预处理任务
        public class DataPreprocessingTask extends EdgeComputingTask {
            @Override
            public TaskResult execute(EdgeNodeContext context) {
                // 在边缘节点进行数据预处理
                ProcessedData processedData = preprocessData(context.getRawData());
                
                // 判断是否需要上传到云端
                if (shouldUploadToCloud(processedData)) {
                    // 上传到云端
                    cloudUploadService.upload(processedData);
                }
                
                return TaskResult.success(processedData);
            }
        }
        
        // 实时分析任务
        public class RealTimeAnalysisTask extends EdgeComputingTask {
            @Override
            public TaskResult execute(EdgeNodeContext context) {
                // 在边缘节点进行实时分析
                AnalysisResult result = performRealTimeAnalysis(context.getData());
                
                // 判断是否需要触发本地动作
                if (shouldTriggerLocalAction(result)) {
                    // 执行本地动作
                    localActionExecutor.execute(result.getAction());
                }
                
                // 判断是否需要上传到云端
                if (shouldUploadToCloud(result)) {
                    // 上传到云端
                    cloudUploadService.upload(result);
                }
                
                return TaskResult.success(result);
            }
        }
        
        // 机器学习推理任务
        public class MLInferenceTask extends EdgeComputingTask {
            @Override
            public TaskResult execute(EdgeNodeContext context) {
                // 在边缘节点进行机器学习推理
                MLModel model = loadMLModel(context.getModelId());
                InferenceResult result = model.infer(context.getInputData());
                
                // 判断是否需要上传到云端
                if (shouldUploadToCloud(result)) {
                    // 上传到云端
                    cloudUploadService.upload(result);
                }
                
                return TaskResult.success(result);
            }
        }
    }
}
```

## 核心服务设计

### 用户服务

社交平台的用户服务需要处理用户注册、登录、个人信息管理等功能。

```java
// 用户服务架构
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private UserCache userCache;
    
    @Autowired
    private SecurityService securityService;
    
    @Autowired
    private RecommendationService recommendationService;
    
    // 用户注册
    public User registerUser(UserRegistrationRequest request) {
        // 数据验证
        validateRegistrationRequest(request);
        
        // 检查用户名是否已存在
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new UsernameAlreadyExistsException("Username already exists: " + 
                                                   request.getUsername());
        }
        
        // 密码加密
        String encryptedPassword = securityService.encryptPassword(request.getPassword());
        
        // 创建用户
        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setEncryptedPassword(encryptedPassword);
        user.setProfile(new UserProfile());
        user.setPrivacySettings(new PrivacySettings());
        user.setStatus(UserStatus.ACTIVE);
        user.setCreatedAt(LocalDateTime.now());
        user.setLastLoginAt(LocalDateTime.now());
        
        // 保存用户
        user = userRepository.save(user);
        
        // 清除相关缓存
        userCache.invalidateUserCache(user.getId());
        
        // 初始化推荐系统
        recommendationService.initializeUserRecommendations(user.getId());
        
        // 发送欢迎消息
        notificationService.sendWelcomeMessage(user);
        
        return user;
    }
    
    // 用户登录
    public UserLoginResponse loginUser(UserLoginRequest request) {
        // 查找用户
        User user = userRepository.findByUsername(request.getUsername());
        if (user == null) {
            throw new UserNotFoundException("User not found: " + request.getUsername());
        }
        
        // 验证密码
        if (!securityService.verifyPassword(request.getPassword(), user.getEncryptedPassword())) {
            throw new InvalidPasswordException("Invalid password");
        }
        
        // 生成访问令牌
        String accessToken = tokenService.generateAccessToken(user.getId());
        
        // 更新最后登录时间
        user.setLastLoginAt(LocalDateTime.now());
        userRepository.save(user);
        
        // 记录登录日志
        loginLogService.logLogin(user.getId(), getClientIpAddress(), getUserAgent());
        
        return new UserLoginResponse(user, accessToken);
    }
    
    // 获取用户信息
    public User getUserProfile(String userId) {
        // 先从缓存获取
        User user = userCache.getUser(userId);
        if (user != null) {
            return user;
        }
        
        // 缓存未命中，从数据库获取
        user = userRepository.findById(userId);
        if (user != null) {
            userCache.putUser(user);
        }
        
        return user;
    }
    
    // 更新用户信息
    public User updateUserProfile(String userId, UpdateUserProfileRequest request) {
        // 获取用户
        User user = userRepository.findById(userId);
        if (user == null) {
            throw new UserNotFoundException("User not found: " + userId);
        }
        
        // 更新用户信息
        if (request.getProfile() != null) {
            user.setProfile(request.getProfile());
        }
        
        if (request.getPrivacySettings() != null) {
            user.setPrivacySettings(request.getPrivacySettings());
        }
        
        user.setUpdatedAt(LocalDateTime.now());
        user = userRepository.save(user);
        
        // 清除缓存
        userCache.invalidateUserCache(userId);
        
        // 更新推荐系统
        recommendationService.updateUserPreferences(userId, request.getProfile());
        
        return user;
    }
}
```

### 内容服务

社交平台的内容服务负责处理用户发布的内容、评论、点赞等操作。

```java
// 内容服务架构
@Service
public class ContentService {
    @Autowired
    private ContentRepository contentRepository;
    
    @Autowired
    private ContentCache contentCache;
    
    @Autowired
    private SearchService searchService;
    
    @Autowired
    private NotificationService notificationService;
    
    // 发布内容
    public Content publishContent(PublishContentRequest request) {
        // 数据验证
        validateContentRequest(request);
        
        // 创建内容对象
        Content content = new Content();
        content.setUserId(request.getUserId());
        content.setType(request.getType());
        content.setText(request.getText());
        content.setMediaUrls(request.getMediaUrls());
        content.setTags(request.getTags());
        content.setVisibility(request.getVisibility());
        content.setStatus(ContentStatus.PUBLISHED);
        content.setCreatedAt(LocalDateTime.now());
        content.setLikeCount(0L);
        content.setCommentCount(0L);
        content.setShareCount(0L);
        
        // 保存内容
        content = contentRepository.save(content);
        
        // 更新缓存
        contentCache.putContent(content);
        
        // 更新搜索引擎索引
        searchService.indexContent(content);
        
        // 更新用户内容计数
        userStatisticsService.incrementContentCount(request.getUserId());
        
        // 通知关注者
        notifyFollowers(content);
        
        return content;
    }
    
    // 获取内容详情
    public Content getContentDetail(String contentId) {
        // 先从缓存获取
        Content content = contentCache.getContent(contentId);
        if (content != null) {
            return content;
        }
        
        // 缓存未命中，从数据库获取
        content = contentRepository.findById(contentId);
        if (content != null) {
            contentCache.putContent(content);
        }
        
        return content;
    }
    
    // 获取用户内容流
    public ContentFeed getUserFeed(GetUserFeedRequest request) {
        // 从缓存获取用户关注列表
        List<String> followingUsers = userRelationshipCache.getFollowingUsers(
            request.getUserId());
            
        // 构建查询条件
        ContentQuery query = new ContentQuery();
        query.setUserIds(followingUsers);
        query.setPage(request.getPage());
        query.setSize(request.getSize());
        query.setSortBy(ContentSortBy.CREATED_AT_DESC);
        
        // 查询内容
        List<Content> contents = contentRepository.query(query);
        
        // 补充用户信息
        enrichContentsWithUserInfo(contents);
        
        return new ContentFeed(contents);
    }
    
    // 点赞内容
    public LikeResult likeContent(String userId, String contentId) {
        // 检查内容是否存在
        Content content = contentRepository.findById(contentId);
        if (content == null) {
            throw new ContentNotFoundException("Content not found: " + contentId);
        }
        
        // 检查是否已点赞
        if (likeRepository.existsByUserIdAndContentId(userId, contentId)) {
            throw new AlreadyLikedException("Content already liked");
        }
        
        // 创建点赞记录
        Like like = new Like();
        like.setUserId(userId);
        like.setContentId(contentId);
        like.setCreatedAt(LocalDateTime.now());
        likeRepository.save(like);
        
        // 更新内容点赞数
        content.setLikeCount(content.getLikeCount() + 1);
        content.setUpdatedAt(LocalDateTime.now());
        contentRepository.save(content);
        
        // 清除缓存
        contentCache.invalidateContent(contentId);
        
        // 发送点赞通知
        notificationService.sendLikeNotification(content.getUserId(), userId, contentId);
        
        // 更新用户互动统计
        userStatisticsService.incrementLikeCount(userId);
        userStatisticsService.incrementReceivedLikeCount(content.getUserId());
        
        return LikeResult.success();
    }
    
    // 评论内容
    public Comment addComment(AddCommentRequest request) {
        // 检查内容是否存在
        Content content = contentRepository.findById(request.getContentId());
        if (content == null) {
            throw new ContentNotFoundException("Content not found: " + request.getContentId());
        }
        
        // 创建评论对象
        Comment comment = new Comment();
        comment.setUserId(request.getUserId());
        comment.setContentId(request.getContentId());
        comment.setText(request.getText());
        comment.setParentCommentId(request.getParentCommentId());
        comment.setStatus(CommentStatus.PUBLISHED);
        comment.setCreatedAt(LocalDateTime.now());
        comment.setLikeCount(0L);
        
        // 保存评论
        comment = commentRepository.save(comment);
        
        // 更新内容评论数
        content.setCommentCount(content.getCommentCount() + 1);
        content.setUpdatedAt(LocalDateTime.now());
        contentRepository.save(content);
        
        // 清除缓存
        contentCache.invalidateContent(request.getContentId());
        
        // 发送评论通知
        notificationService.sendCommentNotification(content.getUserId(), 
                                                   request.getUserId(), 
                                                   request.getContentId(), 
                                                   request.getText());
        
        // 更新用户互动统计
        userStatisticsService.incrementCommentCount(request.getUserId());
        
        return comment;
    }
}
```

### 消息服务

社交平台的消息服务负责处理用户间的私信、群聊等实时通信功能。

```java
// 消息服务架构
@Service
public class MessageService {
    @Autowired
    private MessageRepository messageRepository;
    
    @Autowired
    private ConversationRepository conversationRepository;
    
    @Autowired
    private WebSocketConnectionManager webSocketManager;
    
    @Autowired
    private NotificationService notificationService;
    
    // 发送私信
    public Message sendPrivateMessage(SendPrivateMessageRequest request) {
        // 创建会话（如果不存在）
        Conversation conversation = getOrCreateConversation(
            request.getSenderId(), request.getRecipientId());
            
        // 创建消息对象
        Message message = new Message();
        message.setConversationId(conversation.getId());
        message.setSenderId(request.getSenderId());
        message.setRecipientId(request.getRecipientId());
        message.setContent(request.getContent());
        message.setMessageType(MessageType.PRIVATE);
        message.setStatus(MessageStatus.SENT);
        message.setCreatedAt(LocalDateTime.now());
        
        // 保存消息
        message = messageRepository.save(message);
        
        // 更新会话
        conversation.setLastMessageId(message.getId());
        conversation.setLastMessagePreview(getMessagePreview(message));
        conversation.setLastMessageTimestamp(message.getCreatedAt());
        conversation.setUpdatedAt(LocalDateTime.now());
        conversationRepository.save(conversation);
        
        // 实时推送消息
        pushRealTimeMessage(message);
        
        // 发送通知（如果接收方不在线）
        if (!webSocketManager.isUserOnline(request.getRecipientId())) {
            notificationService.sendPrivateMessageNotification(
                request.getRecipientId(), request.getSenderId(), request.getContent());
        }
        
        return message;
    }
    
    // 发送群聊消息
    public Message sendGroupMessage(SendGroupMessageRequest request) {
        // 检查群组是否存在
        Group group = groupRepository.findById(request.getGroupId());
        if (group == null) {
            throw new GroupNotFoundException("Group not found: " + request.getGroupId());
        }
        
        // 检查发送者是否在群组中
        if (!groupMemberRepository.existsByGroupIdAndUserId(
                request.getGroupId(), request.getSenderId())) {
            throw new NotGroupMemberException("User is not a member of the group");
        }
        
        // 创建消息对象
        Message message = new Message();
        message.setGroupId(request.getGroupId());
        message.setSenderId(request.getSenderId());
        message.setContent(request.getContent());
        message.setMessageType(MessageType.GROUP);
        message.setStatus(MessageStatus.SENT);
        message.setCreatedAt(LocalDateTime.now());
        
        // 保存消息
        message = messageRepository.save(message);
        
        // 更新群组最后消息
        group.setLastMessageId(message.getId());
        group.setLastMessagePreview(getMessagePreview(message));
        group.setLastMessageTimestamp(message.getCreatedAt());
        group.setUpdatedAt(LocalDateTime.now());
        groupRepository.save(group);
        
        // 实时推送消息给所有群成员
        List<String> groupMemberIds = groupMemberRepository
            .findUserIdsByGroupId(request.getGroupId());
        pushRealTimeGroupMessage(message, groupMemberIds);
        
        return message;
    }
    
    // 获取会话历史
    public MessageHistory getConversationHistory(GetConversationHistoryRequest request) {
        // 验证会话访问权限
        if (!hasAccessToConversation(request.getUserId(), request.getConversationId())) {
            throw new UnauthorizedAccessException("User has no access to this conversation");
        }
        
        // 构建查询条件
        MessageQuery query = new MessageQuery();
        query.setConversationId(request.getConversationId());
        query.setPage(request.getPage());
        query.setSize(request.getSize());
        query.setSortBy(MessageSortBy.CREATED_AT_ASC);
        
        // 查询消息历史
        List<Message> messages = messageRepository.query(query);
        
        // 补充用户信息
        enrichMessagesWithUserInfo(messages);
        
        return new MessageHistory(messages);
    }
    
    // 标记消息为已读
    public void markMessagesAsRead(MarkMessagesAsReadRequest request) {
        // 更新消息状态
        messageRepository.updateStatusByIds(
            request.getMessageIds(), MessageStatus.READ);
            
        // 更新会话未读计数
        conversationRepository.decrementUnreadCount(
            request.getConversationId(), request.getUserId(), 
            request.getMessageIds().size());
    }
    
    // 实时消息推送
    private void pushRealTimeMessage(Message message) {
        // 推送给接收方
        RealTimeMessage realTimeMessage = new RealTimeMessage();
        realTimeMessage.setType(RealTimeMessageType.NEW_MESSAGE);
        realTimeMessage.setData(message);
        realTimeMessage.setTimestamp(LocalDateTime.now());
        
        webSocketManager.sendRealTimeMessage(message.getRecipientId(), realTimeMessage);
    }
    
    // 实时群聊消息推送
    private void pushRealTimeGroupMessage(Message message, List<String> memberIds) {
        RealTimeMessage realTimeMessage = new RealTimeMessage();
        realTimeMessage.setType(RealTimeMessageType.NEW_GROUP_MESSAGE);
        realTimeMessage.setData(message);
        realTimeMessage.setTimestamp(LocalDateTime.now());
        
        // 推送给所有群成员
        for (String memberId : memberIds) {
            // 不推送给发送者自己
            if (!memberId.equals(message.getSenderId())) {
                webSocketManager.sendRealTimeMessage(memberId, realTimeMessage);
            }
        }
    }
}
```

## 实时处理与推送

### 消息推送系统

社交平台和IoT平台都需要高效的消息推送系统。

```java
// 消息推送系统
@Component
public class MessagePushSystem {
    // 多通道推送
    public class MultiChannelPush {
        private List<PushChannel> pushChannels;
        
        // 推送消息
        public PushResult pushMessage(PushMessage message, List<String> userIds) {
            List<PushTask> pushTasks = new ArrayList<>();
            
            // 为每个用户创建推送任务
            for (String userId : userIds) {
                // 根据用户偏好选择推送通道
                List<PushChannel> preferredChannels = getUserPreferredChannels(userId);
                
                for (PushChannel channel : preferredChannels) {
                    PushTask task = new PushTask();
                    task.setUserId(userId);
                    task.setChannel(channel);
                    task.setMessage(message);
                    task.setPriority(getPushPriority(message, userId));
                    pushTasks.add(task);
                }
            }
            
            // 并行执行推送任务
            List<CompletableFuture<PushResult>> futures = pushTasks.stream()
                .map(task -> CompletableFuture.supplyAsync(() -> 
                    executePushTask(task), executorService))
                .collect(Collectors.toList());
                
            // 等待所有任务完成
            List<PushResult> results = futures.stream()
                .map(CompletableFuture::join)
                .collect(Collectors.toList());
                
            // 合并结果
            return mergePushResults(results);
        }
        
        // 执行推送任务
        private PushResult executePushTask(PushTask task) {
            try {
                switch (task.getChannel()) {
                    case PUSH_NOTIFICATION:
                        return pushNotificationService.push(task.getUserId(), 
                                                          task.getMessage());
                    case SMS:
                        return smsService.send(task.getUserId(), task.getMessage());
                    case EMAIL:
                        return emailService.send(task.getUserId(), task.getMessage());
                    case IN_APP:
                        return inAppNotificationService.notify(task.getUserId(), 
                                                             task.getMessage());
                    default:
                        return PushResult.failure("Unsupported push channel");
                }
            } catch (Exception e) {
                log.error("Failed to execute push task", e);
                return PushResult.failure(e.getMessage());
            }
        }
    }
    
    // 智能推送策略
    public class IntelligentPushStrategy {
        // 基于用户行为的推送时机优化
        public LocalDateTime calculateOptimalPushTime(String userId, PushMessage message) {
            // 获取用户活跃时间分布
            UserActivityPattern pattern = userActivityService.getActivityPattern(userId);
            
            // 获取消息紧急程度
            MessagePriority priority = message.getPriority();
            
            // 计算最优推送时间
            if (priority == MessagePriority.HIGH) {
                // 高优先级消息立即推送
                return LocalDateTime.now();
            } else {
                // 低优先级消息在用户活跃时段推送
                return pattern.getOptimalPushTime();
            }
        }
        
        // 个性化推送内容
        public PersonalizedPushMessage personalizeMessage(String userId, 
                                                        PushMessage message) {
            // 获取用户偏好
            UserPreferences preferences = userPreferenceService.getPreferences(userId);
            
            // 获取用户上下文
            UserContext context = userContextService.getContext(userId);
            
            // 个性化消息内容
            String personalizedContent = messageTemplateService.personalize(
                message.getContent(), preferences, context);
                
            return new PersonalizedPushMessage(message, personalizedContent);
        }
    }
}
```

### 流数据处理

处理实时数据流是社交平台和IoT平台的核心能力。

```java
// 流数据处理系统
@Component
public class StreamDataProcessingSystem {
    // 用户行为流处理
    public class UserBehaviorStreamProcessor {
        public void processUserBehaviorStream() {
            StreamsBuilder builder = new StreamsBuilder();
            
            // 读取用户行为流
            KStream<String, UserBehavior> userBehaviors = builder.stream("user-behaviors");
            
            // 实时计算用户兴趣标签
            KTable<String, Set<String>> userInterestTags = userBehaviors
                .groupBy((userId, behavior) -> userId)
                .aggregate(
                    HashSet::new,
                    (userId, behavior, tags) -> {
                        tags.addAll(extractTagsFromBehavior(behavior));
                        return tags;
                    }
                );
            
            // 实时计算内容热度
            KTable<String, Long> contentHotness = userBehaviors
                .filter((userId, behavior) -> 
                    behavior.getType() == BehaviorType.VIEW_CONTENT ||
                    behavior.getType() == BehaviorType.LIKE_CONTENT ||
                    behavior.getType() == BehaviorType.SHARE_CONTENT)
                .mapValues(behavior -> behavior.getContentId())
                .groupBy((userId, contentId) -> contentId)
                .windowedBy(TimeWindows.of(Duration.ofMinutes(30)))
                .count();
            
            // 实时计算用户关系强度
            KTable<String, Map<String, Double>> userRelationshipStrength = userBehaviors
                .filter((userId, behavior) -> 
                    behavior.getType() == BehaviorType.INTERACT_WITH_USER)
                .mapValues(behavior -> behavior.getTargetUserId())
                .groupBy((userId, targetUserId) -> userId + ":" + targetUserId)
                .windowedBy(TimeWindows.of(Duration.ofHours(1)))
                .aggregate(
                    () -> new HashMap<String, Double>(),
                    (key, targetUserId, strengthMap) -> {
                        strengthMap.merge(targetUserId, 1.0, Double::sum);
                        return strengthMap;
                    }
                );
            
            // 输出结果到存储
            userInterestTags.toStream().to("user-interest-tags");
            contentHotness.toStream().to("content-hotness");
            userRelationshipStrength.toStream().to("user-relationship-strength");
            
            // 启动流处理应用
            KafkaStreams streams = new KafkaStreams(builder.build(), streamProps);
            streams.start();
        }
    }
    
    // 设备数据流处理
    public class DeviceDataStreamProcessor {
        public void processDeviceDataStream() {
            StreamsBuilder builder = new StreamsBuilder();
            
            // 读取设备数据流
            KStream<String, DeviceData> deviceData = builder.stream("device-data");
            
            // 实时异常检测
            KStream<String, AnomalyAlert> anomalies = deviceData
                .filter((deviceId, data) -> isAnomalous(data))
                .mapValues(data -> generateAnomalyAlert(data));
            
            // 实时聚合统计
            KTable<String, DeviceStatistics> deviceStats = deviceData
                .groupBy((deviceId, data) -> deviceId)
                .windowedBy(TimeWindows.of(Duration.ofMinutes(5)))
                .aggregate(
                    DeviceStatistics::new,
                    (deviceId, data, stats) -> {
                        stats.updateWithNewData(data);
                        return stats;
                    }
                );
            
            // 实时设备状态更新
            KTable<String, DeviceStatus> deviceStatus = deviceData
                .groupBy((deviceId, data) -> deviceId)
                .aggregate(
                    () -> DeviceStatus.UNKNOWN,
                    (deviceId, data, status) -> determineDeviceStatus(data)
                );
            
            // 输出结果
            anomalies.to("device-anomalies");
            deviceStats.toStream().to("device-statistics");
            deviceStatus.toStream().to("device-status");
            
            // 启动流处理应用
            KafkaStreams streams = new KafkaStreams(builder.build(), streamProps);
            streams.start();
        }
    }
    
    // 复杂事件处理
    public class ComplexEventProcessor {
        // 用户行为模式检测
        public void detectUserBehaviorPatterns() {
            // 定义复杂事件模式
            Pattern<UserBehavior, ?> pattern = Pattern.<UserBehavior>begin("first")
                .where(behavior -> behavior.getType() == BehaviorType.VIEW_CONTENT)
                .next("second")
                .where(behavior -> behavior.getType() == BehaviorType.LIKE_CONTENT)
                .within(Duration.ofMinutes(5));
                
            // 创建模式流
            PatternStream<UserBehavior> patternStream = CEP.pattern(
                userBehaviorStream, pattern);
                
            // 处理匹配的模式
            patternStream.select(
                (Map<String, List<UserBehavior>> patternMap) -> {
                    UserBehavior first = patternMap.get("first").get(0);
                    UserBehavior second = patternMap.get("second").get(0);
                    
                    // 生成用户兴趣增强事件
                    UserInterestEnhancedEvent event = new UserInterestEnhancedEvent();
                    event.setUserId(first.getUserId());
                    event.setContentId(first.getContentId());
                    event.setInterestScore(1.5); // 增强的兴趣分数
                    
                    // 发送到消息队列
                    messageQueue.send("user-interest-enhanced", event);
                    
                    return event;
                }
            );
        }
        
        // 设备故障预测
        public void predictDeviceFailures() {
            // 定义设备故障模式
            Pattern<DeviceData, ?> failurePattern = Pattern.<DeviceData>begin("warning")
                .where(data -> data.getTemperature() > 80)
                .next("critical")
                .where(data -> data.getTemperature() > 90)
                .within(Duration.ofMinutes(10));
                
            // 创建模式流
            PatternStream<DeviceData> patternStream = CEP.pattern(
                deviceDataStream, failurePattern);
                
            // 处理匹配的模式
            patternStream.select(
                (Map<String, List<DeviceData>> patternMap) -> {
                    DeviceData warning = patternMap.get("warning").get(0);
                    DeviceData critical = patternMap.get("critical").get(0);
                    
                    // 生成设备故障预警
                    DeviceFailurePrediction prediction = new DeviceFailurePrediction();
                    prediction.setDeviceId(warning.getDeviceId());
                    prediction.setPredictedFailureTime(
                        LocalDateTime.now().plusHours(2)); // 预测2小时后可能故障
                    prediction.setConfidence(0.85); // 置信度85%
                    prediction.setReason("Temperature rising pattern detected");
                    
                    // 发送到消息队列
                    messageQueue.send("device-failure-prediction", prediction);
                    
                    return prediction;
                }
            );
        }
    }
}
```

通过以上架构设计和实现，社交平台和IoT应用能够构建出高并发、实时性强、可扩展的微服务系统，有效应对海量用户和设备带来的挑战。