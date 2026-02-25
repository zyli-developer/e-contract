# Test Case Format Conventions

## Test Layering Strategy

项目采用**分层测试策略**，每层有不同的抽象级别和用途：

| Layer | Files | Purpose | Abstraction | Implementation |
|-------|-------|---------|-------------|----------------|
| **基础层** | 01-10 | CRUD 和约束验证 | 单个实体/操作 | `app/tests/` pytest |
| **桥接层** | 11 | 用户旅程集成测试 | **完整业务流程** | `e2e/test_journey_*.py` |
| **高级层** | 12-17 | 高级功能测试 | 规则引擎、转移等 | `app/tests/` pytest |
| **场景层** | 18-33 | 细粒度端到端场景 | 按 User Journey 细分 | `e2e/test_*_integration.py` |

### 层级选择指南

**何时使用 11-user-journeys.md（桥接层）：**
- 测试涵盖**多步骤、跨实体**的完整业务流程
- 例如：团队创建 → 成员加入 → 报名活动 → 提交作品
- TC 数量少（每旅程 1-2 个），但覆盖完整链路

**何时使用 18-33（场景层）：**
- 测试单个 User Journey 中的**具体场景变体**
- 例如：TC-TEAM-020 搜索并邀请成员 vs TC-TEAM-022 被邀请成员拒绝邀请
- TC 数量多，覆盖正向/负向/边界条件

**两层关系：**
```
11-user-journeys.md        18-33 细分文件
   TC-JOUR-005       ←→    22-team-management.md (TC-TEAM-*)
   (完整团队加入流程)         (团队管理各场景)

   TC-JOUR-013       ←→    25-social-interaction.md (TC-SOCIAL-*)
   (完整社区互动流程)         (社区互动各场景)
```

### E2E 实现映射

| 规范文件 | 实现文件 |
|---------|---------|
| `specs/testcases/11-user-journeys.md` | `e2e/test_journey_*.py` (8 文件) |
| `specs/testcases/18-*.md` ~ `specs/testcases/33-*.md` | `e2e/test_*_integration.py` |
| `specs/testcases/01-*.md` ~ `specs/testcases/10-*.md` | `app/tests/` pytest |

---

## File Naming

Files are numbered sequentially: `NN-module-name.md` (e.g., `01-user.md`, `08-relations.md`).

Next available number: check `ls specs/testcases/` for the highest existing number.

## File Structure

```markdown
# Module Name (Chinese)

> **格式约定：** 每条用例仅描述「场景」与「预期结果」，不包含测试方法和执行过程。

---

## N.1 Section Name

**TC-PREFIX-NNN：Test Case Title (Chinese)**
Description paragraph: scenario setup + expected result. Single paragraph, no bullet points
unless describing multiple cascading effects.

## N.M 负向/边界

**TC-PREFIX-900：Negative Case Title**
Description of the negative scenario and expected rejection/error.
```

## TC ID Conventions

Format: `TC-{PREFIX}-{NUMBER}`

### Existing Prefixes

| Prefix | Module | Number Ranges |
|--------|--------|---------------|
| USER | User | 001-020, 900-903 |
| CAT | Event | 001-020, 900-902 |
| RULE | Rule | 001-020, 100-109, 900-901 |
| GRP | Group | 001-020, 900-901 |
| POST | Post | 001-076, 900-903 |
| RES | Resource | 001-045, 900-903 |
| IACT | Interaction | 001-063, 900-905 |
| REL-CR | Relations (event:rule) | 001-003, 900 |
| REL-CP | Relations (event:post) | 001-004, 900-902 |
| REL-CG | Relations (event:group) | 001-003, 900-901 |
| REL-PP | Relations (post:post) | 001-005 |
| REL-PR | Relations (post:resource) | 001-005 |
| REL-GU | Relations (group:user) | 001, 900-902 |
| REL-TI | Relations (target:interaction) | 001-002 |
| DEL | Cascade Delete | 001-022 |
| PERM | Permissions | 001-025 |
| JOUR | User Journeys | 002-013 |
| TRANSFER | Resource Transfer | 001-004 |
| FRIEND | User Follow | 001-007, 900-902 |
| STAGE | Event Stages | 001-004 |
| TRACK | Event Tracks | 001-003 |
| PREREQ | Prerequisites | 001-004 |
| CATREL | Event Relations | 010-021, 900-905 |
| ENTRY | Entry Rules | 001-031, 900-902 |
| CLOSE | Closure Rules | 001-040, 900-902 |
| ENGINE | Rule Engine | 001-061 |
| BROWSE | Content Browsing | 001-051, 900-903 |
| AUTH | Authentication | 001-013, 900-905 |
| PROFILE | User Profile | 001-022 |
| NOTIF | Notification | 001-033, 900-901 |
| CATMGMT | Event Management | 001-042, 900-903 |
| TEAM | Team Management | 001-033, 900-903 |
| PART | Activity Participation | 001-033, 900-903 |
| CREATE | Content Creation | 001-072, 900-903 |
| SOCIAL | Social Interaction | 001-052, 900-905 |
| SETTLE | Settlement & Reward | 001-043, 900-903 |
| BOUNTY | Bounty Activities | 001-017, 900-902 |
| ENTERPRISE | Enterprise Activities | 001-014, 900-901 |
| VISIBLE | Visibility Control | 001-006 |
| PERSONAL | Personalization | 001-043, 900-903 |
| PLANET | Planet Page | 001-007, 900-902 |
| CAMP | Camp Page | 001-022 |
| NAV | Navigation | 001-004 |
| PROPOSAL | Proposal Iteration | 001-021, 900-902 |
| PAGEUI | Page Interaction | 001-025, 900-901 |
| ASSETCOPY | Asset Copy Request | 001-012, 900-903 |
| CATTRACK | Event Track | 010-011 |

### Number Range Convention

- **001-099**: Positive/happy-path test cases (CRUD, workflows)
- **100-199**: Feature-specific enforcement cases
- **900-999**: Negative/boundary test cases

## Writing Rules

1. **Chinese only** — All test case descriptions are in Chinese
2. **Scenario + Expected Result** — Each test case describes only the scenario and expected outcome
3. **No test method** — Do not include test implementation details or execution steps
4. **Single paragraph** — Each test case is typically one paragraph. Use bullet points only for cascading/multi-effect outcomes
5. **Bold title** — Use `**TC-XXX-NNN：Title**` format on its own line
6. **Section grouping** — Group related test cases under `## N.M Section Name`
7. **Negative section last** — Place negative/boundary tests at the end under `## N.M 负向/边界`
