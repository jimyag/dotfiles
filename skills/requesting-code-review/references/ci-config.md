# CI、工作流与配置文件专项检查

只在本轮 diff 修改 CI workflow、自动化脚本入口、YAML/JSON 配置或依赖 manifest 时加载。规则必须结合实际触发器、权限、数据来源和项目约定判断；不要把通用加固建议包装成当前缺陷。

## GitHub Actions 安全边界

- `pull_request_target` 是否 checkout、执行或间接加载 PR head 的不可信代码；该事件通常拥有 base 仓库上下文和更高权限
- `${{ github.event.* }}` 等外部可控 expression 是否直接插入 `run:`，形成 shell/script 注入；优先经 `env:` 传递并正确引用
- secrets 是否被输出到日志、写入 artifact/cache，或传给不需要它的 step、容器和第三方 action
- workflow/job `permissions` 是否符合最小权限；只有出现真实越权面时才报告，不能机械要求每个 job 重复声明
- 第三方 action 是否使用可变 tag；高信任或可访问 secrets 的链路优先固定完整 commit SHA，并结合仓库既有依赖更新策略判断
- fork PR、Dependabot、外部 contributor 和手工触发路径是否会跨越不同信任边界

## GitHub Actions 正确性

- `needs` 是否引用真实 job ID，条件执行后下游是否会被意外 skipped，依赖图是否存在断链或循环
- action input、output、secret 名称是否拼错；未知 input 可能只产生 warning 或被静默忽略
- 需要 tag、merge-base、changelog 或历史提交时，checkout 深度是否足够；不要对不需要历史的 job 强制 `fetch-depth: 0`
- `if:` 中事件名、布尔值、字符串和表达式上下文是否正确
- matrix 是否覆盖承诺的平台和版本；只有所有组合都必须执行时，才把默认 `fail-fast` 视为问题
- self-hosted 或跨平台 runner 上的 shell、路径、权限和工具可用性是否被错误假设
- source、generated artifact、bundle、release asset、版本号和 changelog 是否需要同步

## 可靠性与失败可见性

- 长时间或外部依赖 job 是否缺少合理的 `timeout-minutes`
- `|| true`、`continue-on-error`、宽泛重试或吞错是否让关键验证虚假通过
- concurrency/cancel-in-progress 是否符合任务语义；发布、部署和有副作用任务不能机械取消旧运行
- cache key、restore key 和缓存内容是否可能跨分支、架构、工具链或信任边界污染
- 容器、工具和依赖是否使用不可复现的 `latest`、`*` 或未固定 git revision
- 新增网络、发布、部署步骤失败时，是否保留足够日志且不会泄露敏感信息

## 依赖 manifest

- 新增依赖是否位于正确区段，例如 runtime、dev、build 或 target-specific
- 同一依赖是否在不同区段重复或版本冲突
- scripts 中新增的 eslint、jest、prettier 等工具是否有对应依赖或由项目明确全局提供
- POM/Gradle/Cargo/package manifest 是否引入 snapshot、wildcard、`latest` 或未固定 git dependency，破坏生产构建可复现性
- 版本由 parent、workspace、lockfile 或集中配置管理时，不要误报“缺少版本”
- lockfile 是否应随 manifest 更新，以及平台可选依赖是否会造成无关的大范围 lockfile churn

## YAML/JSON 与通用配置

- 重复 key、错误层级、字段拼写或类型是否会被解析器覆盖、忽略或解释成另一种语义
- 默认值、枚举、单位和环境变量名是否与代码读取方一致
- plaintext secret、连接串、token 或私有地址是否被提交
- anchor、merge key、模板插值和 quoting 是否改变最终值，尤其是布尔、数字、通配符和包含特殊字符的字符串
- 配置删除、重命名或默认值变化是否有旧环境兼容、升级和回滚路径

## 判断原则

- 安全问题必须说明不可信输入、权限上下文和执行 sink
- 可靠性问题必须说明具体失败模式，不能因为“最好有 timeout/cache/concurrency”就报告
- 配置项是否有效应优先查实际 schema、action 定义或读取代码
- 测试 workflow 也在审查范围内，不因路径或文件名自动排除
