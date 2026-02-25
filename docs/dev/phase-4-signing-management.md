# Phase 4：合同签署与管理

**目标**：实现合同签署（H5 集成 + 签署意愿验证）、合同列表与管理、状态机流转、签署通知、法律合规保障（文档哈希 + 证据链）。这是 MVP 的核心阶段。

**前置依赖**：Phase 2 + Phase 3

## 后端任务

| # | 任务 | 说明 |
|---|------|------|
| 4.1 | 发起签署 | 合同从草稿(1)转为签署中(2)，向签署方发送通知 |
| 4.2 | 合同状态机 | 状态流转：草稿(1)→签署中(2)→已完成(3)/已拒签(5)/已过期(6)，发起方可取消(4) |
| 4.3 | 签署方状态 | participant 状态：pending(0)→signed(2)/rejected(3)；所有人签完→合同已完成 |
| 4.4 | 合同列表 | `GET /seal/sign-task/page`，筛选：role(creator/signer/all)、status、keyword、startDate、endDate |
| 4.5 | 合同统计 | `GET /seal/sign-task/statistics`，返回 total/signing/completed/draft 计数 |
| 4.6 | 合同详情 | `GET /seal/sign-task/get`，返回合同信息 + 签署方列表 + 签署状态 |
| 4.7 | 合同操作 | 取消 `DELETE .../cancel`、删除 `DELETE .../delete`、催签 `POST .../{id}/urge` |
| 4.8 | 合同下载 | `GET /seal/sign-tasks/{id}/download`，返回已签署 PDF |
| 4.9 | 签署通知 | 发起签署时发送微信模板消息/短信通知签署方，催签时再次通知 |
| 4.10 | 权限校验 | `GET /seal/sign-task/validate-permission`，确认当前用户是合同的签署方 |
| **4.11** | **签署意愿验证** | **签署前发送短信验证码到签署方手机，`POST /seal/sign-task/{id}/send-sign-code` + `POST /seal/sign-task/{id}/verify-sign-code`，验证通过后才允许执行签署操作** |
| **4.12** | **文档哈希** | **合同创建时计算文件 SHA-256 哈希存入 `sign_task.file_hash`，签署完成后计算签署文件哈希存入 `signed_file_hash`；提供 `GET /seal/sign-task/{id}/verify-hash` 校验接口** |
| **4.13** | **签署证据链** | **每个关键操作写入 `sign_evidence_log` 表，记录 action/user_id/timestamp/ip/device/data_hash** |

### 证据链记录的操作类型

| action | 触发时机 | 记录内容 |
|--------|---------|---------|
| `CONTRACT_CREATED` | 合同创建 | 创建人、文件哈希 |
| `CONTRACT_SENT` | 发起签署 | 发起人、签署方列表 |
| `SIGNER_VIEWED` | 签署方打开合同 | 查看人、查看时间 |
| `SIGN_CODE_SENT` | 发送签署验证码 | 接收手机号、发送时间 |
| `SIGN_CODE_VERIFIED` | 验证码验证通过 | 验证人、验证时间 |
| `CONTRACT_SIGNED` | 签署完成 | 签署人、签名数据哈希、文档哈希 |
| `CONTRACT_COMPLETED` | 所有方签署完成 | 签署文件哈希、完成时间 |
| `CONTRACT_CANCELLED` | 合同取消 | 操作人、取消原因 |
| `CONTRACT_REJECTED` | 签署方拒签 | 拒签人、拒签原因 |

**Pydantic Schemas**：`SignTaskResp`, `SignTaskPageReq`, `SignTaskStatisticsResp`, `ParticipantResp`, `SignCodeReq`, `SignCodeVerifyReq`, `EvidenceLogResp`

**数据表**：`sign_task`, `sign_task_participant`, `sign_evidence_log`

## 前端任务

| # | 任务 | 说明 |
|---|------|------|
| 4.14 | Contract API 层（完整） | `api/contract.ts`：page、get、statistics、cancel、delete、urge、download、sendSignCode、verifySignCode |
| 4.15 | useContractStore | Zustand store：当前合同详情、统计数据 |
| 4.16 | 首页 | 合同统计卡片（total/signing/completed/draft）、快捷创建入口、最近合同列表 |
| 4.17 | 合同管理页 | Tab 分类（全部/待签署/签署中/已完成/草稿）、搜索、筛选、下拉刷新+加载更多 |
| 4.18 | 合同详情页 | 合同信息、签署方状态列表、操作按钮（发起签署/催签/取消/下载）、证据链时间线展示 |
| 4.19 | H5 签署页 | WebView 嵌入 Seal Core H5（mode=sign），URL：`{H5_URL}/h5/sign?token={sealToken}&taskId={id}` |
| 4.20 | WebView 通信 | 监听 postMessage 事件：signComplete→刷新详情、signCancel→返回、signError→提示 |
| **4.21** | **签署验证码弹窗** | **签署前弹出验证码确认弹窗：显示签署方手机号（脱敏）→ 发送验证码 → 输入验证码 → 验证通过后进入 H5 签署页** |
| 4.22 | 签署结果页 | 签署成功/失败提示，返回合同详情或合同列表 |

## 测试任务

| 测试文件 | 覆盖内容 |
|----------|---------|
| `test_contract_service.py` | 发起签署、状态流转合法性检查（如已完成不可取消）、签署方全部完成自动更新状态 |
| `test_contract_api.py` | 列表分页筛选（role/status/keyword）、统计数据正确、操作权限 |
| `test_contract_state_machine.py` | 所有合法/非法状态转换、边界条件测试 |
| `test_participant.py` | 签署方状态流转、顺序签署逻辑（前一个签完才轮到下一个） |
| `test_notification.py` | respx mock 微信模板消息 API、短信 API，验证通知触发时机 |
| **`test_sign_verification.py`** | **签署验证码发送/验证、验证码过期拒绝、错误验证码拒绝、未验证不能签署** |
| **`test_document_hash.py`** | **创建时哈希计算并存储、签署后哈希更新、哈希校验接口（匹配/不匹配）** |
| **`test_evidence_log.py`** | **每个操作类型正确记录、时间戳/IP/设备信息完整、证据链查询按时间排序** |
| `contract-list.test.tsx` | Tab 切换、筛选、搜索、列表渲染、空状态、下拉刷新 |
| `contract-detail.test.tsx` | 详情渲染、签署方状态展示、操作按钮显隐逻辑（基于状态和角色） |
| `home-page.test.tsx` | 统计卡片数据、快捷入口、最近合同列表 |
| `webview-bridge.test.ts` | postMessage 事件处理、签署完成/取消/错误回调 |
| **`sign-verify-modal.test.tsx`** | **验证码弹窗渲染、发送倒计时、输入验证、验证通过后跳转签署** |

### 集成测试

- `test_full_signing_flow.py`：用户 A 创建合同 → 指定用户 B 为签署方 → 发起签署 → 用户 B 查看待签列表 → **用户 B 输入短信验证码** → 用户 B 签署 → 合同状态变为已完成 → **验证文档哈希一致** → **验证证据链完整（9 条记录）**

## 交付物

- [ ] 创建合同 → 发送给签署方 → 签署方登录看到待签合同 → **验证码确认** → 签署 → 合同生效 **完整流程跑通**
- [ ] 合同状态机流转正确（草稿→签署中→已完成/已拒签/已过期/已取消）
- [ ] H5 签署集成正常（WebView 双向通信）
- [ ] 首页统计和合同管理页完整
- [ ] 签署通知发送正常（微信模板消息/短信）
- [ ] 催签和取消操作正常
- [ ] **签署意愿验证**：签署前必须通过短信验证码确认
- [ ] **文档防篡改**：合同文件哈希在创建和签署后均有记录，可校验
- [ ] **证据链完整**：每个关键操作均有时间戳、用户、IP 记录，可导出
