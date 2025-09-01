---
title: Docker 架构与基本概念
date: 2025-08-30
categories: [Write]
tags: [docker, architecture, concepts]
published: true
---

## 第3章：Docker 架构与基本概念

### Docker 引擎与容器

Docker 引擎是 Docker 的核心组件，负责构建、运行和管理容器。它采用客户端-服务器（C/S）架构，由多个组件协同工作。理解 Docker 引擎的架构对于深入掌握 Docker 的工作原理至关重要。

Docker 引擎主要包含以下组件：
- **Docker Daemon**：后台运行的守护进程，负责管理 Docker 对象
- **Docker Client**：用户与 Docker 交互的命令行工具
- **Docker API**：REST API，供程序与 Docker Daemon 通信
- **Docker Objects**：包括镜像、容器、网络、卷等

### 镜像、容器、仓库与 Dockerfile

Docker 的核心概念包括镜像、容器、仓库和 Dockerfile，它们构成了 Docker 生态系统的基础。

**镜像（Image）**是只读的模板，包含创建 Docker 容器的指令。镜像是分层构建的，每一层代表镜像的一个变更。

**容器（Container）**是镜像的运行实例，可以被启动、停止、重启和删除。每个容器都是相互隔离且安全的平台。

**仓库（Registry）**是存储和分发 Docker 镜像的服务。Docker Hub 是默认的公共仓库，用户也可以搭建私有仓库。

**Dockerfile**是一个文本文件，包含一系列指令，用于自动化构建镜像。

### Docker 仓库与镜像拉取

Docker 仓库是 Docker 镜像的存储和分发系统。了解如何使用仓库以及如何高效地拉取镜像是使用 Docker 的重要技能。

本章将深入探讨 Docker 的架构设计、核心概念以及它们之间的关系，为后续章节的学习奠定坚实的基础。