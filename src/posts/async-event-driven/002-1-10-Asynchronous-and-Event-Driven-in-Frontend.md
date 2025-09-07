---
title: 用户界面与前端中的异步与事件驱动
date: 2025-08-31
categories: [AsyncEventDriven]
tags: [async-event-driven]
published: true
---

在现代Web应用开发中，用户界面的响应性和交互性已成为用户体验的关键因素。随着应用复杂性的增加和用户期望的提高，传统的同步编程模式已难以满足现代前端应用的需求。异步编程和事件驱动架构在前端开发中发挥着至关重要的作用，为构建高性能、高响应性的用户界面提供了强大的技术支持。本文将深入探讨前端开发中的异步通信与AJAX、WebSocket实现实时事件驱动前端、前端事件驱动架构的设计模式，以及UI与服务器间的事件驱动通信。

## 异步通信与 AJAX

### AJAX 的基本概念

AJAX（Asynchronous JavaScript and XML）是一种在不重新加载整个页面的情况下，与服务器交换数据并更新部分网页的技术。AJAX的核心是XMLHttpRequest对象，它允许JavaScript向服务器发送异步请求。

#### XMLHttpRequest 的使用

```javascript
// 传统的 XMLHttpRequest 使用方式
function fetchData(url, callback) {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                callback(null, JSON.parse(xhr.responseText));
            } else {
                callback(new Error('Request failed with status ' + xhr.status));
            }
        }
    };
    
    xhr.onerror = function() {
        callback(new Error('Network error'));
    };
    
    xhr.send();
}

// 使用示例
fetchData('/api/users', (error, users) => {
    if (error) {
        console.error('Failed to fetch users:', error);
    } else {
        displayUsers(users);
    }
});
```

#### jQuery AJAX

jQuery简化了AJAX的使用：

```javascript
// jQuery AJAX 使用方式
$.ajax({
    url: '/api/users',
    method: 'GET',
    dataType: 'json',
    success: function(users) {
        displayUsers(users);
    },
    error: function(xhr, status, error) {
        console.error('Failed to fetch users:', error);
    }
});

// jQuery 的便捷方法
$.get('/api/users')
    .done(function(users) {
        displayUsers(users);
    })
    .fail(function(xhr, status, error) {
        console.error('Failed to fetch users:', error);
    });
```

### 现代异步编程技术

#### Promise 和 Fetch API

现代JavaScript提供了更优雅的异步编程方式：

```javascript
// 使用 Fetch API 和 Promise
function fetchUsers() {
    return fetch('/api/users')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(users => {
            displayUsers(users);
            return users;
        })
        .catch(error => {
            console.error('Failed to fetch users:', error);
            showError('Failed to load users');
        });
}

// 使用示例
fetchUsers().then(users => {
    console.log('Users loaded:', users);
});
```

#### async/await

async/await语法使异步代码看起来像同步代码：

```javascript
// 使用 async/await
async function loadUserProfile(userId) {
    try {
        // 并行获取用户信息和用户订单
        const [user, orders] = await Promise.all([
            fetch(`/api/users/${userId}`).then(r => r.json()),
            fetch(`/api/users/${userId}/orders`).then(r => r.json())
        ]);
        
        displayUserProfile(user);
        displayUserOrders(orders);
        
        return { user, orders };
    } catch (error) {
        console.error('Failed to load user profile:', error);
        showError('Failed to load user profile');
        throw error;
    }
}

// 使用示例
async function handleUserSelection(userId) {
    showLoadingIndicator();
    try {
        await loadUserProfile(userId);
    } finally {
        hideLoadingIndicator();
    }
}
```

### AJAX 的最佳实践

#### 错误处理

```javascript
// 完善的错误处理
async function fetchWithRetry(url, options = {}, maxRetries = 3) {
    for (let i = 0; i <= maxRetries; i++) {
        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                throw new HTTPError(response.status, response.statusText);
            }
            
            return await response.json();
        } catch (error) {
            if (i === maxRetries) {
                throw error;
            }
            
            // 指数退避
            await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
        }
    }
}

class HTTPError extends Error {
    constructor(status, statusText) {
        super(`HTTP ${status}: ${statusText}`);
        this.status = status;
        this.statusText = statusText;
    }
}
```

#### 请求取消

```javascript
// 使用 AbortController 取消请求
class ApiService {
    constructor() {
        this.abortController = null;
    }
    
    async fetchData(url) {
        // 取消之前的请求
        if (this.abortController) {
            this.abortController.abort();
        }
        
        // 创建新的 AbortController
        this.abortController = new AbortController();
        
        try {
            const response = await fetch(url, {
                signal: this.abortController.signal
            });
            
            if (!response.ok) {
                throw new Error('Request failed');
            }
            
            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('Request was cancelled');
                return null;
            }
            throw error;
        }
    }
}
```

## 使用 WebSockets 实现实时事件驱动前端

### WebSocket 的基本概念

WebSocket是一种在单个TCP连接上进行全双工通信的协议，它允许服务器主动向客户端推送数据，实现了真正的实时通信。

#### WebSocket 的基本使用

```javascript
// WebSocket 基本使用
class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.websocket = null;
        this.listeners = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    connect() {
        this.websocket = new WebSocket(this.url);
        
        this.websocket.onopen = (event) => {
            console.log('WebSocket connection opened');
            this.reconnectAttempts = 0;
            this.emit('open', event);
        };
        
        this.websocket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.emit('message', message);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };
        
        this.websocket.onclose = (event) => {
            console.log('WebSocket connection closed');
            this.emit('close', event);
            
            // 自动重连
            if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
            }
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.emit('error', error);
        };
    }
    
    send(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket is not open');
        }
    }
    
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }
    
    emit(event, data) {
        const callbacks = this.listeners.get(event);
        if (callbacks) {
            callbacks.forEach(callback => callback(data));
        }
    }
    
    disconnect() {
        if (this.websocket) {
            this.websocket.close();
        }
    }
}

// 使用示例
const wsClient = new WebSocketClient('ws://localhost:8080/ws');
wsClient.on('open', () => {
    console.log('Connected to WebSocket server');
});

wsClient.on('message', (message) => {
    console.log('Received message:', message);
    handleRealTimeUpdate(message);
});

wsClient.connect();
```

### 实时通知系统

```javascript
// 实时通知系统
class NotificationService {
    constructor() {
        this.wsClient = new WebSocketClient('ws://localhost:8080/notifications');
        this.setupEventHandlers();
    }
    
    setupEventHandlers() {
        this.wsClient.on('message', (message) => {
            switch (message.type) {
                case 'notification':
                    this.showNotification(message.data);
                    break;
                case 'user_status':
                    this.updateUserStatus(message.data);
                    break;
                case 'system_alert':
                    this.showSystemAlert(message.data);
                    break;
            }
        });
    }
    
    showNotification(notification) {
        // 显示桌面通知
        if (Notification.permission === 'granted') {
            new Notification(notification.title, {
                body: notification.message,
                icon: notification.icon
            });
        }
        
        // 在页面上显示通知
        const notificationElement = document.createElement('div');
        notificationElement.className = 'notification';
        notificationElement.innerHTML = `
            <div class="notification-title">${notification.title}</div>
            <div class="notification-message">${notification.message}</div>
        `;
        document.getElementById('notifications-container').appendChild(notificationElement);
        
        // 3秒后自动移除通知
        setTimeout(() => {
            notificationElement.remove();
        }, 3000);
    }
    
    updateUserStatus(status) {
        // 更新用户状态显示
        const statusElement = document.getElementById('user-status');
        statusElement.textContent = status.statusText;
        statusElement.className = `status ${status.statusType}`;
    }
    
    showSystemAlert(alert) {
        // 显示系统警报
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${alert.level}`;
        alertElement.textContent = alert.message;
        document.getElementById('alerts-container').appendChild(alertElement);
    }
}

// 初始化通知服务
const notificationService = new NotificationService();
```

### 实时协作功能

```javascript
// 实时协作编辑器
class CollaborativeEditor {
    constructor(elementId, documentId) {
        this.element = document.getElementById(elementId);
        this.documentId = documentId;
        this.wsClient = new WebSocketClient(`ws://localhost:8080/documents/${documentId}`);
        this.localVersion = 0;
        this.remoteVersion = 0;
        this.pendingChanges = [];
        
        this.initializeEditor();
        this.setupWebSocket();
    }
    
    initializeEditor() {
        // 初始化编辑器
        this.element.addEventListener('input', (event) => {
            this.handleLocalChange(event);
        });
    }
    
    setupWebSocket() {
        this.wsClient.on('message', (message) => {
            switch (message.type) {
                case 'document_update':
                    this.applyRemoteChange(message.change);
                    break;
                case 'cursor_position':
                    this.updateRemoteCursor(message);
                    break;
            }
        });
        
        this.wsClient.on('open', () => {
            // 请求文档内容
            this.wsClient.send({
                type: 'document_request',
                documentId: this.documentId
            });
        });
    }
    
    handleLocalChange(event) {
        const change = {
            type: 'text_change',
            position: event.target.selectionStart,
            text: event.target.value,
            version: ++this.localVersion
        };
        
        // 发送变更到服务器
        this.wsClient.send({
            type: 'document_update',
            change: change
        });
        
        // 保存待确认的变更
        this.pendingChanges.push(change);
    }
    
    applyRemoteChange(change) {
        // 应用远程变更
        this.remoteVersion = change.version;
        
        // 如果是自己的变更，从待确认列表中移除
        if (this.pendingChanges.some(pending => pending.version === change.version)) {
            this.pendingChanges = this.pendingChanges.filter(
                pending => pending.version !== change.version
            );
            return;
        }
        
        // 应用远程变更到编辑器
        this.element.value = change.text;
        
        // 更新版本号
        if (change.version > this.localVersion) {
            this.localVersion = change.version;
        }
    }
    
    updateRemoteCursor(cursorData) {
        // 更新远程用户光标位置显示
        const cursorElement = document.getElementById(`cursor-${cursorData.userId}`);
        if (cursorElement) {
            cursorElement.style.left = `${cursorData.position}ch`;
        } else {
            this.createRemoteCursor(cursorData);
        }
    }
    
    createRemoteCursor(cursorData) {
        const cursorElement = document.createElement('div');
        cursorElement.id = `cursor-${cursorData.userId}`;
        cursorElement.className = 'remote-cursor';
        cursorElement.style.left = `${cursorData.position}ch`;
        cursorElement.title = cursorData.userName;
        this.element.parentNode.appendChild(cursorElement);
    }
}
```

## 前端事件驱动架构的设计模式

### 观察者模式

观察者模式是前端事件驱动架构的基础：

```javascript
// 观察者模式实现
class EventEmitter {
    constructor() {
        this.events = {};
    }
    
    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
    }
    
    off(event, callback) {
        if (this.events[event]) {
            this.events[event] = this.events[event].filter(cb => cb !== callback);
        }
    }
    
    emit(event, data) {
        if (this.events[event]) {
            this.events[event].forEach(callback => callback(data));
        }
    }
    
    once(event, callback) {
        const onceWrapper = (data) => {
            callback(data);
            this.off(event, onceWrapper);
        };
        this.on(event, onceWrapper);
    }
}

// 使用示例
const eventEmitter = new EventEmitter();

eventEmitter.on('user:login', (userData) => {
    console.log('User logged in:', userData);
    updateUIForLoggedInUser(userData);
});

eventEmitter.on('user:logout', () => {
    console.log('User logged out');
    updateUIForLoggedOutUser();
});

// 触发事件
eventEmitter.emit('user:login', { id: 1, name: 'John Doe' });
```

### 发布-订阅模式

发布-订阅模式提供了更松耦合的事件处理机制：

```javascript
// 发布-订阅模式实现
class PubSub {
    constructor() {
        this.subscribers = {};
    }
    
    subscribe(topic, callback) {
        if (!this.subscribers[topic]) {
            this.subscribers[topic] = [];
        }
        const token = Symbol(topic);
        this.subscribers[topic].push({
            token,
            callback
        });
        return token;
    }
    
    unsubscribe(token) {
        for (const topic in this.subscribers) {
            const topicSubscribers = this.subscribers[topic];
            for (let i = 0; i < topicSubscribers.length; i++) {
                if (topicSubscribers[i].token === token) {
                    topicSubscribers.splice(i, 1);
                    return true;
                }
            }
        }
        return false;
    }
    
    publish(topic, data) {
        if (this.subscribers[topic]) {
            this.subscribers[topic].forEach(subscriber => {
                subscriber.callback(data);
            });
        }
    }
}

// 使用示例
const pubSub = new PubSub();

const userLoginToken = pubSub.subscribe('user:login', (userData) => {
    console.log('User login handler 1:', userData);
});

const analyticsToken = pubSub.subscribe('user:login', (userData) => {
    console.log('Analytics handler:', userData);
    trackUserLogin(userData);
});

// 发布事件
pubSub.publish('user:login', { id: 1, name: 'John Doe' });

// 取消订阅
pubSub.unsubscribe(userLoginToken);
```

### 状态管理模式

状态管理模式是现代前端应用中重要的事件驱动架构：

```javascript
// 简单的状态管理模式
class Store {
    constructor(initialState = {}) {
        this.state = initialState;
        this.listeners = [];
    }
    
    getState() {
        return Object.freeze({ ...this.state });
    }
    
    setState(newState) {
        const prevState = this.state;
        this.state = { ...this.state, ...newState };
        this.notifyListeners(prevState, this.state);
    }
    
    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            const index = this.listeners.indexOf(listener);
            if (index > -1) {
                this.listeners.splice(index, 1);
            }
        };
    }
    
    notifyListeners(prevState, newState) {
        this.listeners.forEach(listener => listener(newState, prevState));
    }
}

// 使用示例
const store = new Store({
    user: null,
    notifications: [],
    loading: false
});

// 订阅状态变化
const unsubscribe = store.subscribe((newState, prevState) => {
    if (newState.user !== prevState.user) {
        updateUserInterface(newState.user);
    }
    
    if (newState.notifications !== prevState.notifications) {
        updateNotificationPanel(newState.notifications);
    }
    
    if (newState.loading !== prevState.loading) {
        updateLoadingIndicator(newState.loading);
    }
});

// 更新状态
store.setState({ loading: true });
store.setState({ 
    user: { id: 1, name: 'John Doe' },
    loading: false 
});
```

### Redux 风格的状态管理

```javascript
// Redux 风格的状态管理
class ReduxStore {
    constructor(reducer, initialState) {
        this.reducer = reducer;
        this.state = initialState;
        this.listeners = [];
        this.middleware = [];
    }
    
    getState() {
        return this.state;
    }
    
    dispatch(action) {
        // 应用中间件
        let chain = this.middleware.map(middleware => middleware(this));
        let dispatch = (action) => {
            // 执行 reducer
            this.state = this.reducer(this.state, action);
            // 通知监听器
            this.listeners.forEach(listener => listener());
        };
        
        // 通过中间件链执行
        chain = chain.concat([dispatch]);
        const composedDispatch = this.compose(chain);
        return composedDispatch(action);
    }
    
    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            const index = this.listeners.indexOf(listener);
            if (index > -1) {
                this.listeners.splice(index, 1);
            }
        };
    }
    
    applyMiddleware(...middleware) {
        this.middleware = middleware;
    }
    
    compose(functions) {
        return (action) => {
            functions.reverse().forEach(fn => fn(action));
        };
    }
}

// Reducer 示例
function appReducer(state = { count: 0 }, action) {
    switch (action.type) {
        case 'INCREMENT':
            return { ...state, count: state.count + 1 };
        case 'DECREMENT':
            return { ...state, count: state.count - 1 };
        default:
            return state;
    }
}

// 中间件示例
const loggerMiddleware = (store) => (next) => (action) => {
    console.log('Dispatching:', action);
    const result = next(action);
    console.log('Next state:', store.getState());
    return result;
};

// 使用示例
const store = new ReduxStore(appReducer, { count: 0 });
store.applyMiddleware(loggerMiddleware);

const unsubscribe = store.subscribe(() => {
    console.log('State updated:', store.getState());
});

store.dispatch({ type: 'INCREMENT' });
store.dispatch({ type: 'INCREMENT' });
store.dispatch({ type: 'DECREMENT' });
```

## UI 与服务器间的事件驱动通信

### 事件驱动的 API 设计

```javascript
// 事件驱动的 API 客户端
class EventDrivenApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.eventEmitter = new EventEmitter();
        this.pendingRequests = new Map();
    }
    
    // 发送请求并监听响应事件
    async request(endpoint, data, expectedEvent) {
        const requestId = this.generateRequestId();
        
        // 发送请求
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...data,
                requestId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // 返回 Promise，等待事件响应
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                this.eventEmitter.off(expectedEvent, handler);
                reject(new Error('Request timeout'));
            }, 30000);
            
            const handler = (eventData) => {
                if (eventData.requestId === requestId) {
                    clearTimeout(timeout);
                    this.eventEmitter.off(expectedEvent, handler);
                    resolve(eventData);
                }
            };
            
            this.eventEmitter.on(expectedEvent, handler);
        });
    }
    
    // 监听服务器推送的事件
    on(event, callback) {
        this.eventEmitter.on(event, callback);
    }
    
    // 建立 WebSocket 连接以接收服务器事件
    connect() {
        this.wsClient = new WebSocketClient(`${this.baseUrl.replace('http', 'ws')}/events`);
        
        this.wsClient.on('message', (message) => {
            // 根据消息类型触发相应的事件
            this.eventEmitter.emit(message.type, message.data);
        });
        
        this.wsClient.connect();
    }
    
    generateRequestId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
}

// 使用示例
const apiClient = new EventDrivenApiClient('http://localhost:3000/api');
apiClient.connect();

// 监听订单状态更新事件
apiClient.on('order:status_updated', (orderData) => {
    updateOrderStatus(orderData);
});

// 发送创建订单请求，等待订单创建完成事件
async function createOrder(orderData) {
    try {
        const result = await apiClient.request('/orders', orderData, 'order:created');
        console.log('Order created:', result);
        return result;
    } catch (error) {
        console.error('Failed to create order:', error);
        throw error;
    }
}
```

### 实时数据同步

```javascript
// 实时数据同步服务
class RealTimeSyncService {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.syncedCollections = new Map();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // 监听数据变更事件
        this.apiClient.on('data:created', (eventData) => {
            this.handleDataCreated(eventData);
        });
        
        this.apiClient.on('data:updated', (eventData) => {
            this.handleDataUpdated(eventData);
        });
        
        this.apiClient.on('data:deleted', (eventData) => {
            this.handleDataDeleted(eventData);
        });
    }
    
    // 同步集合数据
    async syncCollection(collectionName, query = {}) {
        if (!this.syncedCollections.has(collectionName)) {
            // 初始化集合
            this.syncedCollections.set(collectionName, {
                data: new Map(),
                listeners: [],
                query
            });
        }
        
        const collection = this.syncedCollections.get(collectionName);
        
        // 获取初始数据
        const initialData = await this.apiClient.request(
            `/collections/${collectionName}/query`,
            query,
            `collection:${collectionName}:queried`
        );
        
        // 初始化数据
        initialData.items.forEach(item => {
            collection.data.set(item.id, item);
        });
        
        return collection;
    }
    
    // 订阅集合变更
    subscribeToCollection(collectionName, listener) {
        if (this.syncedCollections.has(collectionName)) {
            const collection = this.syncedCollections.get(collectionName);
            collection.listeners.push(listener);
            
            // 立即发送当前数据
            listener({
                type: 'initial',
                data: Array.from(collection.data.values())
            });
            
            return () => {
                const index = collection.listeners.indexOf(listener);
                if (index > -1) {
                    collection.listeners.splice(index, 1);
                }
            };
        }
    }
    
    handleDataCreated(eventData) {
        const { collection, item } = eventData;
        if (this.syncedCollections.has(collection)) {
            const collectionData = this.syncedCollections.get(collection);
            collectionData.data.set(item.id, item);
            
            // 通知监听器
            collectionData.listeners.forEach(listener => {
                listener({
                    type: 'created',
                    item
                });
            });
        }
    }
    
    handleDataUpdated(eventData) {
        const { collection, item } = eventData;
        if (this.syncedCollections.has(collection)) {
            const collectionData = this.syncedCollections.get(collection);
            collectionData.data.set(item.id, item);
            
            // 通知监听器
            collectionData.listeners.forEach(listener => {
                listener({
                    type: 'updated',
                    item
                });
            });
        }
    }
    
    handleDataDeleted(eventData) {
        const { collection, itemId } = eventData;
        if (this.syncedCollections.has(collection)) {
            const collectionData = this.syncedCollections.get(collection);
            collectionData.data.delete(itemId);
            
            // 通知监听器
            collectionData.listeners.forEach(listener => {
                listener({
                    type: 'deleted',
                    itemId
                });
            });
        }
    }
}

// 使用示例
const syncService = new RealTimeSyncService(apiClient);

// 同步用户订单数据
async function setupOrderSync() {
    await syncService.syncCollection('orders', { userId: currentUser.id });
    
    const unsubscribe = syncService.subscribeToCollection('orders', (update) => {
        switch (update.type) {
            case 'initial':
                renderOrderList(update.data);
                break;
            case 'created':
                addOrderToUI(update.item);
                break;
            case 'updated':
                updateOrderInUI(update.item);
                break;
            case 'deleted':
                removeOrderFromUI(update.itemId);
                break;
        }
    });
    
    return unsubscribe;
}
```

### 错误处理和重连机制

```javascript
// 带有错误处理和重连机制的事件驱动通信
class ResilientEventClient {
    constructor(config) {
        this.config = config;
        this.wsClient = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = config.maxReconnectAttempts || 5;
        this.reconnectDelay = config.reconnectDelay || 1000;
        this.eventHandlers = new Map();
        this.pendingAcks = new Map();
    }
    
    connect() {
        this.wsClient = new WebSocketClient(this.config.wsUrl);
        
        this.wsClient.on('open', () => {
            console.log('Connected to server');
            this.reconnectAttempts = 0;
            this.handleConnectionOpen();
        });
        
        this.wsClient.on('message', (message) => {
            this.handleMessage(message);
        });
        
        this.wsClient.on('close', (event) => {
            console.log('Connection closed');
            this.handleConnectionClose(event);
        });
        
        this.wsClient.on('error', (error) => {
            console.error('Connection error:', error);
            this.handleConnectionError(error);
        });
        
        this.wsClient.connect();
    }
    
    handleConnectionOpen() {
        // 重新订阅事件
        this.resubscribeEvents();
        
        // 重新发送未确认的消息
        this.resendPendingMessages();
    }
    
    handleConnectionClose(event) {
        if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
            setTimeout(() => this.connect(), delay);
        }
    }
    
    handleConnectionError(error) {
        // 记录错误并触发错误事件
        this.emit('connection:error', error);
    }
    
    sendMessage(message, requireAck = false) {
        if (!this.wsClient || this.wsClient.websocket.readyState !== WebSocket.OPEN) {
            throw new Error('WebSocket is not connected');
        }
        
        const messageWithId = {
            ...message,
            id: this.generateMessageId()
        };
        
        if (requireAck) {
            // 设置确认超时
            const ackTimeout = setTimeout(() => {
                this.pendingAcks.delete(messageWithId.id);
                this.emit('message:ack_timeout', messageWithId);
            }, this.config.ackTimeout || 5000);
            
            this.pendingAcks.set(messageWithId.id, {
                message: messageWithId,
                timeout: ackTimeout
            });
        }
        
        this.wsClient.send(messageWithId);
        return messageWithId.id;
    }
    
    handleMessage(message) {
        // 处理确认消息
        if (message.type === 'ack') {
            const pending = this.pendingAcks.get(message.ackId);
            if (pending) {
                clearTimeout(pending.timeout);
                this.pendingAcks.delete(message.ackId);
                this.emit('message:acknowledged', pending.message);
            }
            return;
        }
        
        // 处理业务消息
        if (this.eventHandlers.has(message.type)) {
            const handlers = this.eventHandlers.get(message.type);
            handlers.forEach(handler => {
                try {
                    handler(message.data, message);
                } catch (error) {
                    console.error(`Error in event handler for ${message.type}:`, error);
                }
            });
        }
        
        // 发送确认（如果需要）
        if (message.requireAck) {
            this.sendMessage({
                type: 'ack',
                ackId: message.id
            });
        }
    }
    
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }
    
    emit(event, data) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            handlers.forEach(handler => handler(data));
        }
    }
    
    resubscribeEvents() {
        // 重新订阅所有事件
        this.eventHandlers.forEach((handlers, event) => {
            if (event !== 'connection:error' && event !== 'message:acknowledged' && event !== 'message:ack_timeout') {
                this.sendMessage({
                    type: 'subscribe',
                    event: event
                });
            }
        });
    }
    
    resendPendingMessages() {
        // 重新发送未确认的消息
        this.pendingAcks.forEach((pending, id) => {
            this.wsClient.send(pending.message);
        });
    }
    
    generateMessageId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
}

// 使用示例
const eventClient = new ResilientEventClient({
    wsUrl: 'ws://localhost:8080/events',
    maxReconnectAttempts: 5,
    reconnectDelay: 1000,
    ackTimeout: 5000
});

eventClient.on('user:updated', (userData) => {
    updateUserProfile(userData);
});

eventClient.on('notification:new', (notification) => {
    showNotification(notification);
});

eventClient.on('connection:error', (error) => {
    showConnectionError('Connection lost. Attempting to reconnect...');
});

eventClient.connect();

// 发送需要确认的消息
const messageId = eventClient.sendMessage({
    type: 'user:profile_update',
    data: userProfileData
}, true);

eventClient.on('message:acknowledged', (message) => {
    console.log('Message acknowledged:', message.id);
    hideLoadingIndicator();
});

eventClient.on('message:ack_timeout', (message) => {
    console.warn('Message acknowledgment timeout:', message.id);
    showRetryDialog();
});
```

## 总结

用户界面与前端中的异步与事件驱动架构为构建高性能、高响应性的现代Web应用提供了强大的技术支持。通过合理应用AJAX、WebSocket、观察者模式、状态管理等技术，可以实现流畅的用户体验和实时的数据交互。

在实际应用中，需要根据具体的业务需求和技术约束选择合适的技术方案，并建立完善的错误处理和重连机制，确保系统的稳定运行。随着前端技术的不断发展，事件驱动架构在前端开发中的应用将更加广泛和深入，为构建更加智能和高效的用户界面提供支持。