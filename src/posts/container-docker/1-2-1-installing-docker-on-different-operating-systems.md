---
title: Installing Docker on Different Operating Systems - Windows, macOS, and Linux Guide
date: 2025-08-30
categories: [Write]
tags: [docker, installation, windows, macos, linux]
published: true
---

## 在不同操作系统上安装 Docker（Windows、macOS、Linux）

### Windows 系统安装 Docker

#### 系统要求

在 Windows 上安装 Docker 之前，需要确保系统满足以下要求：

1. **Windows 10/11 Pro, Enterprise, or Education**（Build 15063 或更高版本）
2. **启用 Hyper-V 和 Containers Windows 功能**
3. **启用 BIOS-level 硬件虚拟化支持**

对于不满足上述要求的 Windows 系统，可以考虑使用 Docker Toolbox（已不再维护）或在虚拟机中安装 Linux 来运行 Docker。

#### 安装步骤

1. **下载 Docker Desktop**
   访问 Docker 官方网站 (https://www.docker.com/products/docker-desktop) 下载适用于 Windows 的 Docker Desktop 安装包。

2. **运行安装程序**
   双击下载的安装包，按照安装向导的提示进行安装。安装过程中会自动启用所需的 Windows 功能。

3. **启动 Docker Desktop**
   安装完成后，Docker Desktop 会自动启动。在系统托盘中可以看到 Docker 图标。

4. **验证安装**
   打开 PowerShell 或命令提示符，运行以下命令验证安装：
   ```powershell
   docker --version
   docker run hello-world
   ```

#### Windows 特定配置

Docker Desktop for Windows 提供了丰富的配置选项：

- **资源限制**：可以设置 CPU、内存和磁盘资源的使用限制
- **文件共享**：配置哪些本地目录可以挂载到容器中
- **网络配置**：配置 Docker 的网络设置
- **Kubernetes**：可选择启用内置的 Kubernetes 集群

#### WSL 2 后端

Docker Desktop for Windows 默认使用 WSL 2（Windows Subsystem for Linux 2）作为后端，这提供了更好的性能和与 Linux 的兼容性。

### macOS 系统安装 Docker

#### 系统要求

在 macOS 上安装 Docker 需要满足以下要求：

1. **macOS 10.15 或更高版本**
2. **至少 4GB RAM**
3. **启用 Intel 或 Apple Silicon 处理器**

#### 安装步骤

1. **下载 Docker Desktop**
   访问 Docker 官方网站下载适用于 macOS 的 Docker Desktop 安装包。

2. **安装 Docker Desktop**
   双击下载的 `.dmg` 文件，将 Docker.app 拖拽到 Applications 文件夹中。

3. **启动 Docker Desktop**
   从 Applications 文件夹中启动 Docker。首次启动时需要输入系统密码以安装必要的组件。

4. **验证安装**
   打开终端，运行以下命令验证安装：
   ```bash
   docker --version
   docker run hello-world
   ```

#### macOS 特定配置

Docker Desktop for Mac 提供了以下配置选项：

- **资源限制**：设置 CPU 和内存使用限制
- **文件共享**：配置 `/Users` 目录默认共享到容器中
- **网络配置**：配置 Docker 网络设置
- **Kubernetes**：可选择启用内置的 Kubernetes 集群

### Linux 系统安装 Docker

#### 支持的发行版

Docker 支持大多数 Linux 发行版，包括：

- Ubuntu 18.04 或更高版本
- Debian 10 或更高版本
- CentOS 7 或更高版本
- Fedora 32 或更高版本
- RHEL 7.8 或更高版本

#### Ubuntu 安装步骤

1. **更新系统包**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. **安装必要的工具**
   ```bash
   sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release
   ```

3. **添加 Docker 官方 GPG 密钥**
   ```bash
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
   ```

4. **添加 Docker 仓库**
   ```bash
   echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

5. **安装 Docker Engine**
   ```bash
   sudo apt update
   sudo apt install docker-ce docker-ce-cli containerd.io
   ```

6. **启动并启用 Docker 服务**
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

7. **将用户添加到 docker 组**
   ```bash
   sudo usermod -aG docker $USER
   ```
   注销并重新登录以使组更改生效。

8. **验证安装**
   ```bash
   docker --version
   docker run hello-world
   ```

#### CentOS/RHEL 安装步骤

1. **卸载旧版本**
   ```bash
   sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine
   ```

2. **安装必要的工具**
   ```bash
   sudo yum install -y yum-utils
   ```

3. **添加 Docker 仓库**
   ```bash
   sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
   ```

4. **安装 Docker Engine**
   ```bash
   sudo yum install docker-ce docker-ce-cli containerd.io
   ```

5. **启动并启用 Docker 服务**
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

6. **将用户添加到 docker 组**
   ```bash
   sudo usermod -aG docker $USER
   ```
   注销并重新登录以使组更改生效。

7. **验证安装**
   ```bash
   docker --version
   docker run hello-world
   ```

#### 其他 Linux 发行版

对于其他 Linux 发行版，可以参考 Docker 官方文档中的安装指南，或使用发行版特定的包管理器进行安装。

### 安装后配置

#### 配置镜像仓库

为了提高镜像拉取速度，可以配置国内镜像仓库：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```

将上述配置保存到 `/etc/docker/daemon.json` 文件中，然后重启 Docker 服务。

#### 验证安装

安装完成后，可以通过以下命令验证 Docker 是否正常工作：

```bash
# 查看 Docker 版本
docker --version

# 查看 Docker 系统信息
docker info

# 运行测试容器
docker run hello-world

# 运行交互式容器
docker run -it ubuntu bash
```

#### 常见问题解决

1. **权限问题**
   如果遇到权限问题，确保用户已添加到 docker 组，并重新登录。

2. **网络问题**
   如果无法拉取镜像，检查网络连接和镜像仓库配置。

3. **资源不足**
   如果容器运行缓慢，检查系统资源限制设置。

### 不同平台的比较

#### 性能对比

在不同平台上，Docker 的性能表现略有差异：

- **Linux**：性能最佳，因为 Docker 原生运行在 Linux 内核上
- **macOS**：性能良好，通过 HyperKit 虚拟化提供接近原生的性能
- **Windows**：性能取决于是否使用 WSL 2 后端，WSL 2 提供了更好的性能

#### 功能对比

| 功能 | Windows | macOS | Linux |
|------|---------|-------|-------|
| Docker Desktop | ✓ | ✓ | ✗ (需要单独安装) |
| 命令行工具 | ✓ | ✓ | ✓ |
| GUI 管理界面 | ✓ | ✓ | 有限 |
| Kubernetes 集成 | ✓ | ✓ | 需要单独安装 |
| 资源限制 | ✓ | ✓ | ✓ |

### 最佳实践

#### 安全考虑

1. **定期更新**：保持 Docker 和相关组件的最新版本
2. **最小权限原则**：仅授予必要的权限
3. **镜像安全**：使用可信的镜像源，定期扫描镜像漏洞

#### 性能优化

1. **资源分配**：合理分配 CPU 和内存资源
2. **磁盘空间**：定期清理未使用的镜像和容器
3. **网络配置**：优化网络设置以提高容器间通信效率

通过本节内容，我们详细介绍了在 Windows、macOS 和 Linux 系统上安装 Docker 的具体步骤和注意事项。无论您使用哪种操作系统，都可以按照相应的指南成功安装和配置 Docker，为后续的容器化应用开发做好准备。