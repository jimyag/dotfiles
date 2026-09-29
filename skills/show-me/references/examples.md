# 可视化形式示例

只读取与当前问题对应的示例，不需要同时使用多种形式。

## 伪代码

```text
on(save)
  if content is unchanged
    return cached result
  write new content
  return fresh result
```

## 调用树

```text
submitForm
  createSession
    persistPrompt
    launchAgent
  navigateToSession
```

## 组件树

```tsx
<SessionPage> (apps/example/src/routes/session.tsx)
  useSessionEvents()
  <SessionToolbar>
    <RunSkillButton> (packages/ui)
```

## 文件树

```text
src/
├── commands/       # parses user actions
├── sessions/       # owns session state
└── transport/      # sends API requests
```

## Mermaid 时序

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Daemon
    User->>UI: choose command
    UI->>Daemon: send expanded prompt
    Daemon-->>UI: stream result
```

## 架构与数据流

以下名称仅为示意；实际使用时从代码核对节点、方向和消息类型。

一张图用分组圈出模块，组内展示处理步骤，跨组箭头展示数据交接：

```mermaid
flowchart LR
    subgraph Receive[接收阶段]
        API[接收入口]
        Validate[校验消息]
        API --> Validate
    end
    subgraph Send[发送阶段]
        Inbox[(消息队列)]
        Worker[发送协程]
    end
    subgraph Handle[结果处理阶段]
        Outbox[(接收通道)]
        Consumer[业务处理]
    end
    Validate -->|写入 Message| Inbox
    Inbox -->|读取 Message| Worker
    Worker -->|发送 Message| Remote[远端服务]
    Remote -->|返回 Result| Outbox
    Outbox -->|读取 Result| Consumer
```

说明数据流时按箭头顺序写清：入口产生 `Message` 并写入队列；发送协程读取后交给远端；远端返回 `Result`，由本地处理逻辑消费。队列和通道是异步边界，发送协程与业务处理分别消费不同数据。

## 聚焦差异

```diff
 on(save)
-  write content
+  if content is unchanged
+    return cached result
+  write new content
+  invalidate cache
```

差异只保留理解变化所需的周边结构。大部分内容都是新增、或省略上下文会掩盖归属和顺序时，展示完整目标结构。
