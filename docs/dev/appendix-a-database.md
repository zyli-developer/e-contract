# 附录 A：MVP 数据库表清单

## 表清单

| 模块 | 表名 | 所属阶段 |
|------|------|---------|
| 用户 | `member` | Phase 0 (建表) / Phase 1 (业务) |
| 用户 | `member_social_user` | Phase 0 / Phase 1 |
| 用户 | `member_token` | Phase 0 / Phase 1 |
| 印章 | `seal_info` | Phase 0 / Phase 2 |
| 印章 | `seal_template` | Phase 0 / Phase 2 |
| 模板 | `contract_template` | Phase 0 / Phase 3 |
| 合同 | `sign_task` | Phase 0 / Phase 3+4 |
| 合同 | `sign_task_participant` | Phase 0 / Phase 3+4 |
| 合规 | `sign_evidence_log` | Phase 0 / Phase 4 |
| 基础 | `infra_file` | Phase 0 |

## sign_evidence_log 表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | bigint PK | 主键 |
| `task_id` | bigint FK | 关联合同 |
| `action` | varchar(50) | 操作类型（见 [Phase 4](./phase-4-signing-management.md) 操作类型表） |
| `user_id` | bigint | 操作用户（可为空，如系统自动操作） |
| `ip` | varchar(45) | 操作 IP 地址 |
| `device` | varchar(255) | 设备信息（UA / 微信小程序版本） |
| `data_hash` | varchar(64) | 操作时的文档 SHA-256 哈希 |
| `detail` | json | 操作详情（签署方列表、拒签原因等） |
| `create_time` | datetime | 操作时间（精确到毫秒） |

## 后续版本需新增的表

| 模块 | 表名 | 版本 |
|------|------|------|
| 用户 | `member_verify` (KYC) | v2 |
| 企业 | `enterprise`, `enterprise_member` | v2 |
| 印章 | `seal_grant` (印章授权) | v2 |
| AI | `ai_conversation`, `ai_message`, `ai_contract`, `ai_draft_template` | v3 |
| 配额 | `quota_account`, `quota_log`, `quota_package`, `quota_order` | v3 |
| 验真 | `contract_verification` | v3 |
