---
title: 云原生时代的存储：构建弹性、可扩展的现代化存储架构
date: 2025-08-31
categories: [Write]
tags: [write]
published: true
---

在云原生时代，传统的存储架构正在被重新定义。容器化、微服务、DevOps等云原生存储理念的兴起，对数据存储提出了新的要求：更高的弹性、更强的可扩展性、更好的可移植性以及更紧密的与应用生命周期集成。云原生存储不仅要满足数据持久化的基本需求，还要能够适应动态变化的云环境，支持敏捷开发和快速部署。本文将深入探讨云原生存储的核心概念、关键技术、架构模式以及最佳实践，帮助读者理解如何在云原生环境中构建现代化的存储解决方案。

## 云原生存储基础

### 云原生存储的定义与特征

云原生存储是专为云原生应用设计的存储解决方案，它具备动态配置、弹性扩展、声明式管理等特征，能够与Kubernetes等容器编排平台无缝集成。

#### 云原生存储核心特征
```python
# 云原生存储特征示例
class CloudNativeStorageCharacteristics:
    """云原生存储特征"""
    
    def __init__(self):
        self.characteristics = {
            "declarative_management": {
                "description": "声明式管理",
                "features": [
                    "通过YAML/JSON定义存储需求",
                    "基础设施即代码(IaC)",
                    "版本控制和回滚能力"
                ],
                "benefits": [
                    "提高配置一致性",
                    "简化管理操作",
                    "支持自动化部署"
                ]
            },
            "dynamic_provisioning": {
                "description": "动态配置",
                "features": [
                    "按需自动创建存储卷",
                    "存储类(StorageClass)管理",
                    "参数化存储配置"
                ],
                "benefits": [
                    "减少手动配置工作",
                    "提高资源利用率",
                    "支持快速扩展"
                ]
            },
            "container_aware": {
                "description": "容器感知",
                "features": [
                    "与容器生命周期同步",
                    "支持多容器共享",
                    "容器本地存储优化"
                ],
                "benefits": [
                    "提高数据访问性能",
                    "简化数据管理",
                    "增强应用可移植性"
                ]
            },
            "scalability": {
                "description": "可扩展性",
                "features": [
                    "水平和垂直扩展能力",
                    "自动扩缩容",
                    "多区域部署支持"
                ],
                "benefits": [
                    "适应业务负载变化",
                    "优化成本效益",
                    "提高系统可用性"
                ]
            },
            "observability": {
                "description": "可观察性",
                "features": [
                    "内置监控和告警",
                    "性能指标收集",
                    "日志和追踪集成"
                ],
                "benefits": [
                    "实时了解系统状态",
                    "快速故障诊断",
                    "支持容量规划"
                ]
            }
        }
    
    def analyze_characteristics(self):
        """分析云原生存储特征"""
        print("云原生存储核心特征分析:")
        for char_key, char_info in self.characteristics.items():
            print(f"\n{char_info['description']} ({char_key}):")
            print("  特性:")
            for feature in char_info['features']:
                print(f"    - {feature}")
            print("  收益:")
            for benefit in char_info['benefits']:
                print(f"    - {benefit}")
    
    def compare_with_traditional_storage(self):
        """与传统存储对比"""
        comparison = {
            "aspect": ["配置方式", "扩展性", "管理复杂度", "可移植性", "成本模型"],
            "traditional": ["手动配置", "垂直扩展为主", "高", "低", "固定成本"],
            "cloud_native": ["声明式自动配置", "水平+垂直扩展", "低", "高", "按需付费"]
        }
        
        print("\n云原生存储 vs 传统存储对比:")
        print("  {:<15} {:<20} {:<20}".format("方面", "传统存储", "云原生存储"))
        print("  " + "-" * 55)
        for i in range(len(comparison["aspect"])):
            print("  {:<15} {:<20} {:<20}".format(
                comparison["aspect"][i], 
                comparison["traditional"][i], 
                comparison["cloud_native"][i]
            ))
    
    def get_adoption_recommendations(self):
        """获取采用建议"""
        return {
            "start_with": "从容器持久化卷开始，逐步迁移到云原生存储",
            "key_areas": [
                "容器编排平台集成",
                "存储类管理",
                "备份和恢复策略",
                "监控和告警体系"
            ],
            "success_factors": [
                "团队技能提升",
                "渐进式迁移",
                "充分的测试验证",
                "完善的监控体系"
            ]
        }

# 使用示例
cn_storage = CloudNativeStorageCharacteristics()
cn_storage.analyze_characteristics()
cn_storage.compare_with_traditional_storage()

recommendations = cn_storage.get_adoption_recommendations()
print(f"\n采用建议:")
print(f"  入手点: {recommendations['start_with']}")
print(f"  关键领域:")
for area in recommendations['key_areas']:
    print(f"    - {area}")
print(f"  成功因素:")
for factor in recommendations['success_factors']:
    print(f"    - {factor}")
```

### 容器存储接口(CSI)

容器存储接口(CSI)是云原生存储的关键技术标准，它定义了容器编排系统与存储系统之间的标准接口，实现了存储插件的标准化和可移植性。

#### CSI实现示例
```python
# CSI实现示例
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

class CSIVolume:
    """CSI卷对象"""
    
    def __init__(self, volume_id: str, capacity_bytes: int, parameters: Dict[str, Any]):
        self.volume_id = volume_id
        self.capacity_bytes = capacity_bytes
        self.parameters = parameters
        self.created_at = datetime.now()
        self.status = "available"
        self.attached_node = None
        self.mounted_path = None

class CSIControllerService:
    """CSI控制器服务"""
    
    def __init__(self, driver_name: str):
        self.driver_name = driver_name
        self.volumes = {}  # 卷管理
        self.snapshots = {}  # 快照管理
        self.capabilities = [
            "CREATE_DELETE_VOLUME",
            "CREATE_DELETE_SNAPSHOT",
            "CLONE_VOLUME",
            "EXPAND_VOLUME"
        ]
    
    async def create_volume(self, name: str, capacity_bytes: int, 
                          parameters: Dict[str, Any], 
                          volume_capabilities: List[Dict[str, Any]]) -> CSIVolume:
        """创建卷"""
        print(f"CSI控制器: 创建卷 {name}")
        
        # 模拟卷创建过程
        await asyncio.sleep(0.1)  # 模拟I/O操作
        
        volume_id = f"vol-{uuid.uuid4().hex[:8]}"
        volume = CSIVolume(volume_id, capacity_bytes, parameters)
        self.volumes[volume_id] = volume
        
        print(f"卷创建成功: {volume_id}")
        return volume
    
    async def delete_volume(self, volume_id: str) -> bool:
        """删除卷"""
        print(f"CSI控制器: 删除卷 {volume_id}")
        
        if volume_id not in self.volumes:
            print(f"卷 {volume_id} 不存在")
            return False
        
        # 检查卷状态
        volume = self.volumes[volume_id]
        if volume.status == "in-use":
            raise Exception(f"卷 {volume_id} 正在使用中，无法删除")
        
        # 模拟删除过程
        await asyncio.sleep(0.05)
        
        del self.volumes[volume_id]
        print(f"卷 {volume_id} 删除成功")
        return True
    
    async def create_snapshot(self, source_volume_id: str, 
                            snapshot_name: str) -> str:
        """创建快照"""
        print(f"CSI控制器: 为卷 {source_volume_id} 创建快照 {snapshot_name}")
        
        if source_volume_id not in self.volumes:
            raise Exception(f"源卷 {source_volume_id} 不存在")
        
        # 模拟快照创建
        await asyncio.sleep(0.08)
        
        snapshot_id = f"snap-{uuid.uuid4().hex[:8]}"
        self.snapshots[snapshot_id] = {
            'source_volume_id': source_volume_id,
            'name': snapshot_name,
            'created_at': datetime.now(),
            'size_bytes': self.volumes[source_volume_id].capacity_bytes
        }
        
        print(f"快照创建成功: {snapshot_id}")
        return snapshot_id
    
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """删除快照"""
        print(f"CSI控制器: 删除快照 {snapshot_id}")
        
        if snapshot_id not in self.snapshots:
            print(f"快照 {snapshot_id} 不存在")
            return False
        
        # 模拟删除过程
        await asyncio.sleep(0.03)
        
        del self.snapshots[snapshot_id]
        print(f"快照 {snapshot_id} 删除成功")
        return True
    
    async def expand_volume(self, volume_id: str, new_capacity_bytes: int) -> bool:
        """扩展卷"""
        print(f"CSI控制器: 扩展卷 {volume_id} 到 {new_capacity_bytes} 字节")
        
        if volume_id not in self.volumes:
            raise Exception(f"卷 {volume_id} 不存在")
        
        volume = self.volumes[volume_id]
        if new_capacity_bytes <= volume.capacity_bytes:
            raise Exception("新容量必须大于当前容量")
        
        # 模拟扩展过程
        await asyncio.sleep(0.06)
        
        volume.capacity_bytes = new_capacity_bytes
        print(f"卷 {volume_id} 扩展成功")
        return True
    
    def get_volume_stats(self, volume_id: str) -> Dict[str, Any]:
        """获取卷统计信息"""
        if volume_id not in self.volumes:
            raise Exception(f"卷 {volume_id} 不存在")
        
        volume = self.volumes[volume_id]
        return {
            'volume_id': volume_id,
            'capacity_bytes': volume.capacity_bytes,
            'status': volume.status,
            'attached_node': volume.attached_node,
            'created_at': volume.created_at.isoformat()
        }
    
    def list_volumes(self) -> List[Dict[str, Any]]:
        """列出所有卷"""
        return [
            {
                'volume_id': vol_id,
                'capacity_bytes': volume.capacity_bytes,
                'status': volume.status,
                'created_at': volume.created_at.isoformat()
            }
            for vol_id, volume in self.volumes.items()
        ]

class CSINodeService:
    """CSI节点服务"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.mounted_volumes = {}  # 已挂载卷
        self.staging_paths = {}  # 预挂载路径
    
    async def node_stage_volume(self, volume_id: str, 
                              staging_target_path: str,
                              volume_capability: Dict[str, Any]) -> bool:
        """节点预挂载卷"""
        print(f"CSI节点 {self.node_id}: 预挂载卷 {volume_id} 到 {staging_target_path}")
        
        # 模拟预挂载过程
        await asyncio.sleep(0.04)
        
        self.staging_paths[volume_id] = {
            'path': staging_target_path,
            'capability': volume_capability,
            'staged_at': datetime.now()
        }
        
        print(f"卷 {volume_id} 预挂载成功")
        return True
    
    async def node_unstage_volume(self, volume_id: str, 
                                staging_target_path: str) -> bool:
        """节点取消预挂载卷"""
        print(f"CSI节点 {self.node_id}: 取消预挂载卷 {volume_id}")
        
        if volume_id not in self.staging_paths:
            print(f"卷 {volume_id} 未预挂载")
            return True
        
        # 模拟取消预挂载过程
        await asyncio.sleep(0.02)
        
        del self.staging_paths[volume_id]
        print(f"卷 {volume_id} 取消预挂载成功")
        return True
    
    async def node_publish_volume(self, volume_id: str,
                                target_path: str,
                                staging_target_path: str) -> bool:
        """节点发布卷（挂载到容器）"""
        print(f"CSI节点 {self.node_id}: 发布卷 {volume_id} 到 {target_path}")
        
        # 模拟挂载过程
        await asyncio.sleep(0.05)
        
        self.mounted_volumes[volume_id] = {
            'target_path': target_path,
            'staging_path': staging_target_path,
            'published_at': datetime.now()
        }
        
        print(f"卷 {volume_id} 发布成功")
        return True
    
    async def node_unpublish_volume(self, volume_id: str,
                                  target_path: str) -> bool:
        """节点取消发布卷"""
        print(f"CSI节点 {self.node_id}: 取消发布卷 {volume_id}")
        
        if volume_id not in self.mounted_volumes:
            print(f"卷 {volume_id} 未发布")
            return True
        
        # 模拟取消挂载过程
        await asyncio.sleep(0.03)
        
        del self.mounted_volumes[volume_id]
        print(f"卷 {volume_id} 取消发布成功")
        return True
    
    def get_node_info(self) -> Dict[str, Any]:
        """获取节点信息"""
        return {
            'node_id': self.node_id,
            'mounted_volumes': len(self.mounted_volumes),
            'staged_volumes': len(self.staging_paths),
            'capabilities': ['STAGE_UNSTAGE_VOLUME']
        }

class CSIStorageSystem:
    """完整的CSI存储系统"""
    
    def __init__(self, driver_name: str):
        self.driver_name = driver_name
        self.controller_service = CSIControllerService(driver_name)
        self.node_services = {}  # 节点服务
    
    def add_node_service(self, node_id: str, node_service: CSINodeService):
        """添加节点服务"""
        self.node_services[node_id] = node_service
        print(f"节点服务 {node_id} 已添加到CSI系统")
    
    async def create_and_mount_volume(self, volume_name: str, 
                                    capacity_bytes: int,
                                    node_id: str,
                                    container_path: str) -> str:
        """创建并挂载卷到容器"""
        print(f"创建并挂载卷: {volume_name}")
        
        # 1. 创建卷
        parameters = {'type': 'ssd', 'replication': '3'}
        volume = await self.controller_service.create_volume(
            volume_name, capacity_bytes, parameters, []
        )
        
        # 2. 获取节点服务
        if node_id not in self.node_services:
            raise Exception(f"节点 {node_id} 不存在")
        
        node_service = self.node_services[node_id]
        
        # 3. 预挂载
        staging_path = f"/var/lib/kubelet/plugins/kubernetes.io/csi/volume/{volume.volume_id}"
        await node_service.node_stage_volume(
            volume.volume_id, staging_path, {}
        )
        
        # 4. 发布到容器
        await node_service.node_publish_volume(
            volume.volume_id, container_path, staging_path
        )
        
        # 5. 更新卷状态
        volume.status = "in-use"
        volume.attached_node = node_id
        volume.mounted_path = container_path
        
        print(f"卷 {volume.volume_id} 已成功挂载到节点 {node_id} 的 {container_path}")
        return volume.volume_id
    
    async def unmount_and_delete_volume(self, volume_id: str, node_id: str):
        """卸载并删除卷"""
        print(f"卸载并删除卷: {volume_id}")
        
        # 1. 获取节点服务
        if node_id not in self.node_services:
            raise Exception(f"节点 {node_id} 不存在")
        
        node_service = self.node_services[node_id]
        
        # 2. 获取卷信息
        if volume_id not in self.controller_service.volumes:
            raise Exception(f"卷 {volume_id} 不存在")
        
        volume = self.controller_service.volumes[volume_id]
        
        # 3. 取消发布
        if volume_id in node_service.mounted_volumes:
            await node_service.node_unpublish_volume(
                volume_id, volume.mounted_path
            )
        
        # 4. 取消预挂载
        staging_path = f"/var/lib/kubelet/plugins/kubernetes.io/csi/volume/{volume_id}"
        await node_service.node_unstage_volume(volume_id, staging_path)
        
        # 5. 删除卷
        await self.controller_service.delete_volume(volume_id)
        
        print(f"卷 {volume_id} 已成功卸载并删除")
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        controller_stats = self.controller_service.list_volumes()
        node_stats = [node.get_node_info() for node in self.node_services.values()]
        
        total_volumes = len(controller_stats)
        mounted_volumes = sum(1 for vol in controller_stats if vol['status'] == 'in-use')
        
        return {
            'driver_name': self.driver_name,
            'total_volumes': total_volumes,
            'mounted_volumes': mounted_volumes,
            'available_volumes': total_volumes - mounted_volumes,
            'nodes_count': len(self.node_services),
            'controller_stats': controller_stats,
            'node_stats': node_stats
        }

# 使用示例
async def main():
    # 创建CSI存储系统
    csi_system = CSIStorageSystem("example-csi-driver")
    
    # 创建节点服务
    node1_service = CSINodeService("node-001")
    node2_service = CSINodeService("node-002")
    
    # 添加节点服务
    csi_system.add_node_service("node-001", node1_service)
    csi_system.add_node_service("node-002", node2_service)
    
    # 创建并挂载卷
    volume_id = await csi_system.create_and_mount_volume(
        "app-data-volume", 
        10 * 1024 * 1024 * 1024,  # 10GB
        "node-001", 
        "/app/data"
    )
    
    # 获取系统状态
    status = csi_system.get_system_status()
    print("CSI系统状态:")
    print(f"  驱动名称: {status['driver_name']}")
    print(f"  总卷数: {status['total_volumes']}")
    print(f"  已挂载卷数: {status['mounted_volumes']}")
    print(f"  可用卷数: {status['available_volumes']}")
    print(f"  节点数: {status['nodes_count']}")
    
    # 卸载并删除卷
    await csi_system.unmount_and_delete_volume(volume_id, "node-001")
    
    # 再次获取系统状态
    status = csi_system.get_system_status()
    print("\n操作后系统状态:")
    print(f"  总卷数: {status['total_volumes']}")
    print(f"  已挂载卷数: {status['mounted_volumes']}")

# 运行示例
# asyncio.run(main())
```

## 云原生存储架构模式

### 有状态应用的存储管理

在云原生环境中，有状态应用的存储管理是一个重要挑战。需要考虑数据持久性、一致性、备份恢复等多个方面。

#### 有状态应用存储管理实现
```python
# 有状态应用存储管理示例
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib

class StatefulApplicationStorage:
    """有状态应用存储管理"""
    
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.volumes = {}  # 应用卷
        self.backups = {}  # 备份
        self.replication_config = {}  # 复制配置
        self.disaster_recovery_plan = {}  # 灾难恢复计划
    
    def define_storage_class(self, storage_class_name: str, 
                           parameters: Dict[str, Any]) -> Dict[str, Any]:
        """定义存储类"""
        storage_class = {
            'name': storage_class_name,
            'parameters': parameters,
            'created_at': datetime.now().isoformat(),
            'provisioner': parameters.get('provisioner', 'kubernetes.io/aws-ebs')
        }
        
        print(f"存储类 {storage_class_name} 已定义")
        return storage_class
    
    def create_persistent_volume_claim(self, pvc_name: str, 
                                     storage_class: str,
                                     capacity: str,
                                     access_modes: List[str]) -> Dict[str, Any]:
        """创建持久化卷声明"""
        pvc = {
            'name': pvc_name,
            'storage_class': storage_class,
            'capacity': capacity,
            'access_modes': access_modes,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        # 模拟PVC创建
        pvc['status'] = 'bound'
        pvc['bound_at'] = datetime.now().isoformat()
        
        self.volumes[pvc_name] = pvc
        print(f"PVC {pvc_name} 已创建并绑定")
        return pvc
    
    def configure_volume_replication(self, volume_name: str, 
                                   replication_factor: int,
                                   regions: List[str]) -> bool:
        """配置卷复制"""
        if volume_name not in self.volumes:
            raise Exception(f"卷 {volume_name} 不存在")
        
        self.replication_config[volume_name] = {
            'replication_factor': replication_factor,
            'regions': regions,
            'configured_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        print(f"卷 {volume_name} 复制配置已生效")
        return True
    
    def create_backup_policy(self, policy_name: str, 
                           schedule: str,
                           retention_days: int,
                           snapshot: bool = True) -> Dict[str, Any]:
        """创建备份策略"""
        policy = {
            'name': policy_name,
            'schedule': schedule,
            'retention_days': retention_days,
            'snapshot': snapshot,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        print(f"备份策略 {policy_name} 已创建")
        return policy
    
    async def execute_backup(self, volume_name: str, 
                           backup_name: str,
                           backup_policy: Dict[str, Any]) -> str:
        """执行备份"""
        if volume_name not in self.volumes:
            raise Exception(f"卷 {volume_name} 不存在")
        
        print(f"开始备份卷 {volume_name}")
        
        # 模拟备份过程
        import asyncio
        await asyncio.sleep(0.1)
        
        backup_id = f"backup-{hashlib.md5(backup_name.encode()).hexdigest()[:8]}"
        self.backups[backup_id] = {
            'name': backup_name,
            'volume_name': volume_name,
            'policy': backup_policy['name'],
            'created_at': datetime.now().isoformat(),
            'size_bytes': 1024 * 1024 * 1024,  # 1GB模拟数据
            'status': 'completed'
        }
        
        print(f"备份 {backup_name} ({backup_id}) 完成")
        return backup_id
    
    def restore_from_backup(self, backup_id: str, 
                          target_volume: str) -> bool:
        """从备份恢复"""
        if backup_id not in self.backups:
            raise Exception(f"备份 {backup_id} 不存在")
        
        if target_volume not in self.volumes:
            raise Exception(f"目标卷 {target_volume} 不存在")
        
        print(f"从备份 {backup_id} 恢复到卷 {target_volume}")
        
        # 模拟恢复过程
        import time
        time.sleep(0.05)
        
        backup = self.backups[backup_id]
        print(f"恢复完成: {backup['name']} -> {target_volume}")
        return True
    
    def setup_disaster_recovery(self, dr_plan_name: str,
                              primary_region: str,
                              backup_regions: List[str],
                              failover_policy: str) -> Dict[str, Any]:
        """设置灾难恢复"""
        self.disaster_recovery_plan = {
            'name': dr_plan_name,
            'primary_region': primary_region,
            'backup_regions': backup_regions,
            'failover_policy': failover_policy,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        print(f"灾难恢复计划 {dr_plan_name} 已设置")
        return self.disaster_recovery_plan
    
    def get_storage_overview(self) -> Dict[str, Any]:
        """获取存储概览"""
        total_volumes = len(self.volumes)
        replicated_volumes = len([
            vol for vol in self.volumes.keys() 
            if vol in self.replication_config
        ])
        
        total_backups = len(self.backups)
        recent_backups = len([
            backup for backup in self.backups.values()
            if datetime.fromisoformat(backup['created_at']) > 
               datetime.now() - timedelta(hours=24)
        ])
        
        return {
            'application': self.app_name,
            'total_volumes': total_volumes,
            'replicated_volumes': replicated_volumes,
            'replication_rate': (replicated_volumes / total_volumes * 100) if total_volumes > 0 else 0,
            'total_backups': total_backups,
            'recent_backups_24h': recent_backups,
            'disaster_recovery_active': bool(self.disaster_recovery_plan),
            'volumes': list(self.volumes.values()),
            'backups': list(self.backups.values())
        }

# 使用示例
async def main():
    # 创建有状态应用存储管理器
    app_storage = StatefulApplicationStorage("mysql-database")
    
    # 定义存储类
    storage_class = app_storage.define_storage_class(
        "fast-ssd", 
        {
            'provisioner': 'kubernetes.io/aws-ebs',
            'type': 'gp3',
            'iops': 3000,
            'throughput': 125
        }
    )
    
    # 创建持久化卷声明
    data_pvc = app_storage.create_persistent_volume_claim(
        "mysql-data", 
        "fast-ssd", 
        "100Gi", 
        ["ReadWriteOnce"]
    )
    
    logs_pvc = app_storage.create_persistent_volume_claim(
        "mysql-logs", 
        "fast-ssd", 
        "20Gi", 
        ["ReadWriteOnce"]
    )
    
    # 配置卷复制
    app_storage.configure_volume_replication(
        "mysql-data", 
        replication_factor=3, 
        regions=["us-east-1", "us-west-2", "eu-west-1"]
    )
    
    # 创建备份策略
    daily_backup_policy = app_storage.create_backup_policy(
        "daily-backup", 
        "0 2 * * *",  # 每天凌晨2点
        retention_days=30,
        snapshot=True
    )
    
    # 执行备份
    backup_id = await app_storage.execute_backup(
        "mysql-data", 
        "mysql-data-backup-20250831", 
        daily_backup_policy
    )
    
    # 设置灾难恢复
    dr_plan = app_storage.setup_disaster_recovery(
        "mysql-dr-plan",
        primary_region="us-east-1",
        backup_regions=["us-west-2", "eu-west-1"],
        failover_policy="manual"
    )
    
    # 获取存储概览
    overview = app_storage.get_storage_overview()
    print("应用存储概览:")
    print(f"  应用名称: {overview['application']}")
    print(f"  总卷数: {overview['total_volumes']}")
    print(f"  复制卷数: {overview['replicated_volumes']}")
    print(f"  复制率: {overview['replication_rate']:.1f}%")
    print(f"  总备份数: {overview['total_backups']}")
    print(f"  24小时备份数: {overview['recent_backups_24h']}")
    print(f"  灾难恢复激活: {overview['disaster_recovery_active']}")

# 运行示例
# asyncio.run(main())
```

通过以上对云原生存储的深入探讨，我们可以看到云原生时代的数据存储正在经历深刻的变革。从声明式管理到容器存储接口，从有状态应用的存储管理到现代化的架构模式，云原生存储为我们提供了更加灵活、可扩展和高效的存储解决方案。随着云原生技术的不断发展，存储系统将变得更加智能化和自动化，为现代应用提供更好的支撑。