# Interaction Patterns

常见交互模式库，用于 AI UX 生成时的交互设计。

## CRUD 操作

### Create (创建)

```yaml
trigger: form_submit
action: call_api
api_call:
  method: POST
  endpoint: "/api/{resource}"
  body: "{form_data}"
loading_state: submit-button
on_success:
  - action: show_toast
    message: "创建成功"
  - action: navigate
    target: "/{resource}/{new_item.id}"
on_error:
  - action: show_form_errors
  - action: show_toast
    type: error
    message: "{error.message}"
```

### Read (查看)

```yaml
# 列表
trigger: page_load
action: call_api
api_call:
  method: GET
  endpoint: "/api/{resource}?skip={skip}&limit={limit}"
loading_state: list-skeleton
on_success:
  - action: render_list

# 详情
trigger: page_load
action: call_api
api_call:
  method: GET
  endpoint: "/api/{resource}/{id}"
loading_state: page-skeleton
on_error:
  - action: navigate
    target: "/404"
```

### Update (更新)

```yaml
trigger: form_submit
action: call_api
api_call:
  method: PUT
  endpoint: "/api/{resource}/{id}"
  body: "{form_data}"
loading_state: submit-button
on_success:
  - action: show_toast
    message: "保存成功"
  - action: refresh_data
```

### Delete (删除)

```yaml
trigger: click delete-button
action: show_confirm
confirm:
  title: "确认删除"
  description: "删除后无法恢复，确定要删除吗？"
  confirm_text: "删除"
  confirm_variant: destructive
on_confirm:
  action: call_api
  api_call:
    method: DELETE
    endpoint: "/api/{resource}/{id}"
  on_success:
    - action: show_toast
      message: "删除成功"
    - action: navigate
      target: "/{resource}"
```

---

## 列表交互

### 搜索筛选

```yaml
# 搜索框
trigger: input (debounce 300ms)
action: update_url_param
params:
  q: "{input.value}"
then:
  action: refetch_list

# 筛选下拉
trigger: select_change
action: update_url_param
params:
  type: "{selected_value}"
then:
  action: refetch_list

# 重置筛选
trigger: click reset-button
action: clear_url_params
then:
  action: refetch_list
```

### 分页

```yaml
# 页码点击
trigger: click page-button
action: update_url_param
params:
  page: "{page_number}"
then:
  action: refetch_list
  scroll_to: list-top

# 无限滚动
trigger: scroll_near_bottom
condition: "!is_loading && has_more"
action: call_api
api_call:
  method: GET
  endpoint: "/api/{resource}?skip={current_count}&limit=20"
on_success:
  - action: append_to_list
```

### 排序

```yaml
trigger: click sort-header
action: update_url_param
params:
  sort: "{field}"
  order: "{current_order === 'asc' ? 'desc' : 'asc'}"
then:
  action: refetch_list
```

---

## 表单交互

### 实时验证

```yaml
trigger: input
action: validate_field
field: "{field_name}"
on_invalid:
  - action: show_field_error
    message: "{validation_message}"
on_valid:
  - action: clear_field_error
```

### 表单提交

```yaml
trigger: form_submit
action: validate_all_fields
on_valid:
  - action: disable_submit
  - action: call_api
    api_call: {...}
on_invalid:
  - action: scroll_to_first_error
  - action: focus_first_error
```

### 文件上传

```yaml
trigger: file_selected
action: upload_file
api_call:
  method: POST
  endpoint: "/api/resources"
  body: FormData
loading_state: upload-progress
on_progress:
  - action: update_progress
    value: "{percent}"
on_success:
  - action: insert_file_reference
    value: "{response.url}"
on_error:
  - action: show_toast
    type: error
    message: "上传失败"
```

### 自动保存

```yaml
trigger: input (debounce 3000ms)
condition: "is_dirty"
action: call_api
api_call:
  method: PATCH
  endpoint: "/api/{resource}/{id}"
  body: "{form_data}"
silent: true  # 不显示 loading
on_success:
  - action: update_save_status
    message: "已自动保存"
```

---

## 社交交互

### 点赞 (乐观更新)

```yaml
trigger: click like-button
condition: "is_authenticated"
action: toggle_like
optimistic_update:
  - field: liked
    operation: toggle
  - field: like_count
    operation: "{liked ? decrement : increment}"
api_call:
  method: POST
  endpoint: "/api/interactions"
  body:
    type: like
    target_type: "{target_type}"
    target_id: "{target_id}"
error_rollback: true
on_unauthenticated:
  action: show_modal
  target: login-prompt
```

### 关注

```yaml
trigger: click follow-button
action: toggle_follow
api_call:
  method: "{is_following ? 'DELETE' : 'POST'}"
  endpoint: "/api/users/{user_id}/followers"
optimistic_update:
  - field: is_following
    operation: toggle
  - field: follower_count
    operation: "{is_following ? decrement : increment}"
```

### 评论

```yaml
trigger: comment_submit
action: call_api
api_call:
  method: POST
  endpoint: "/api/interactions"
  body:
    type: comment
    target_type: "{target_type}"
    target_id: "{target_id}"
    content: "{comment_content}"
on_success:
  - action: prepend_to_comments
    item: "{response}"
  - action: clear_comment_input
  - action: increment_comment_count
```

---

## 导航交互

### Tab 切换

```yaml
trigger: click tab
action: update_url_param
params:
  tab: "{tab_value}"
then:
  action: filter_content
  # 或
  action: navigate
  target: "{tab_route}"
```

### 面包屑

```yaml
trigger: click breadcrumb-item
action: navigate
target: "{item.route}"
```

### 返回

```yaml
trigger: click back-button
action: navigate_back
fallback: "/"  # 如果没有历史记录
```

---

## 模态框交互

### 打开

```yaml
trigger: click open-button
action: show_modal
target: "{modal_id}"
```

### 关闭

```yaml
# 点击关闭按钮
trigger: click close-button
action: close_modal

# 点击遮罩
trigger: click overlay
action: close_modal

# 按 Escape
trigger: keydown Escape
action: close_modal

# 提交成功后
on_success:
  - action: close_modal
  - action: refresh_data
```

### 确认对话框

```yaml
trigger: click action-button
action: show_confirm
confirm:
  title: "{confirm_title}"
  description: "{confirm_description}"
  confirm_text: "确认"
  cancel_text: "取消"
on_confirm:
  action: "{confirmed_action}"
on_cancel:
  action: close_modal
```

---

## 状态处理

### Loading

```yaml
loading_states:
  button:
    style: spinner
    disabled: true
  list:
    style: skeleton
    count: 3
  page:
    style: progress-bar
```

### Error

```yaml
error_handling:
  network_error:
    action: show_toast
    type: error
    message: "网络连接失败，请重试"
    retry_button: true

  auth_required:
    action: show_modal
    target: login-prompt

  permission_denied:
    action: show_toast
    type: error
    message: "您没有权限执行此操作"

  not_found:
    action: navigate
    target: "/404"

  validation_error:
    action: show_form_errors
    scroll_to_first: true
```

### Empty State

```yaml
empty_state:
  list:
    icon: inbox
    title: "暂无数据"
    description: "还没有相关内容"
    action:
      text: "创建第一个"
      route: "/create"

  search:
    icon: search
    title: "未找到结果"
    description: "换个关键词试试？"
```
