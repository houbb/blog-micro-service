---
title: Docker 安装与配置
date: 2025-08-30
categories: [Write]
tags: [docker, installation, configuration]
published: true
---

## 第2章：Docker 安装与配置

### 在不同操作系统上安装 Docker（Windows、macOS、Linux）

Docker 支持在多种操作系统上运行，包括 Windows、macOS 和各种 Linux 发行版。不同操作系统的安装方式略有差异，但 Docker 都提供了简便的安装工具来帮助用户快速上手。

在 Windows 上，用户可以选择安装 Docker Desktop，它提供了图形化界面和命令行工具。对于 macOS 用户，Docker Desktop 同样提供了完整的 Docker 功能。而在 Linux 系统上，可以通过包管理器或直接下载安装包来安装 Docker Engine。

### Docker 桌面版与命令行工具

Docker 提供了两种主要的使用方式：图形化界面的 Docker Desktop 和命令行工具。Docker Desktop 适合初学者和需要图形化操作的用户，它提供了直观的界面来管理容器、镜像和 Docker Compose 应用。而命令行工具则更适合开发者和运维人员，它提供了更灵活和强大的功能。

Docker CLI（命令行界面）是与 Docker Daemon 交互的主要方式，通过一系列命令可以完成镜像构建、容器运行、网络配置等操作。熟练掌握 Docker CLI 是使用 Docker 的基础。

### 配置 Docker 环境与常用命令

安装 Docker 后，需要进行一些基本的环境配置，以确保 Docker 能够正常运行。这包括配置镜像仓库、设置资源限制、配置网络等。此外，掌握常用的 Docker 命令对于日常使用至关重要。

常用的 Docker 命令包括：
- `docker run`：运行容器
- `docker ps`：查看运行中的容器
- `docker images`：查看本地镜像
- `docker build`：构建镜像
- `docker pull/push`：拉取/推送镜像
- `docker exec`：在运行的容器中执行命令

本章将详细介绍在不同操作系统上安装 Docker 的具体步骤，Docker Desktop 和命令行工具的使用方法，以及 Docker 环境的基本配置和常用命令的使用。