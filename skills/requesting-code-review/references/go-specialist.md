# Go 专项 pass — 检查要点

> 仅在检测到 Go 项目时执行（go.mod 或 .go 文件存在）。
> 本文件补充通用 lane 未覆盖的 Go 语言专有风险。

## 目录

- 并发与竞态
- 健壮性
- Go 规范
- Go review 综合准则
- 判断原则

## 并发与竞态

**goroutine 生命周期：**
- goroutine 是否有退出机制（done channel、context cancel、WaitGroup）
- 函数返回后是否有孤立 goroutine 继续运行（goroutine leak）
- 长时间运行的 goroutine 是否有超时控制

**channel 安全：**
- 是否可能向已关闭的 channel 写入（panic）
- 多个 sender 时，close 的责任是否归属明确（通常由单一 sender 或协调者关闭）
- 无缓冲 channel 是否可能造成双端同时阻塞（死锁）
- select 的阻塞行为是否符合预期；需要非阻塞时是否有 default，并避免 busy loop 或丢事件

**竞态与可见性：**
- 多 goroutine 访问的共享变量是否受 sync.Mutex 或 sync.RWMutex 保护
- 是否有通过非同步方式（裸读写）访问共享状态
- sync/atomic 的使用是否正确（LoadInt64/StoreInt64 而非直接赋值）

**context 传递：**
- 长时间操作是否接受并尊重 ctx.Done()
- context 是否作为第一个参数传递，是否在整个调用链中贯穿
- 是否有把 context 存入结构体而非参数传递的情况

## 健壮性

**panic 使用：**
- panic 是否只用于真正不可恢复的场景（如初始化失败）
- 可预期的错误情况是否改为返回 error
- 库代码中是否有 panic（应避免让调用方无法 recover）

**重试与超时：**
- 网络/外部调用是否设置了超时（http.Client.Timeout、context deadline）
- 重试策略是否有退避（指数退避）和最大次数限制
- 重试逻辑是否尊重 context cancel（用户取消时不再重试）

**资源释放：**
- `defer f.Close()` 是否在打开文件/连接后立即写（不要在循环中累积 defer）
- 错误路径是否也正确释放了已获取的资源
- 数据库连接、HTTP 响应 body 是否都有对应的 Close

**类型断言：**
- `x.(T)` 是否改为 `x, ok := x.(T)` 的 comma-ok 模式
- interface{} / any 类型的断言是否覆盖了断言失败的情况

**错误处理（Go 专项）：**
- 所有 error 返回值是否被检查（不要 `_` 忽略 error）
- defer 中修改命名返回值 err 时是否用命名返回值（否则不生效）
- 需要调用方 unwrap 或匹配原始错误时，是否用 `fmt.Errorf("...: %w", err)` 包装；需要隐藏内部细节时是否返回受控错误信息

## Go 规范

**命名：**
- 接收者名称是否使用类型名首字母的小写缩写（`s *Server` 而非 `self`）
- 错误变量是否命名为 `err`（第一个错误）或 `errXxx`
- 导出符号名首字母大写，非导出符号小写，避免 `_` 分隔的蛇形命名
- 接口命名：单方法接口通常以 `-er` 结尾（`Reader`、`Writer`、`Closer`）

**import 分组：**
- 标准库 / 第三方库 / 内部包三组，每组之间空行分隔
- 不要有未使用的 import，也不要缺失必要的 import

**godoc：**
- 导出的函数、类型、常量、变量是否有 doc comment
- doc comment 是否以符号名开头（`// Server is ...` 而非 `// This is ...`）
- 有 example 的包，example 是否能通过 `go test` 运行

**其他惯例：**
- 是否避免了 `init()` 中的副作用（init 难以测试和追踪）
- 是否避免了 package-level 的可变全局变量（测试隔离难）
- 空 struct `struct{}` 是否用于 channel signal 而非传递数据

## Go review 综合准则

> 汇总 Effective Go、Go Code Review Comments、Go Doc Comments、Go Blog、Uber Go Style Guide、Google Go Style Guide 与 Practical Go。优先级：项目约定 > 当前 Go 官方文档 > 官方 wiki/blog > 团队风格指南 > 个人文章。Effective Go 写于早期 Go 版本，遇到泛型、modules、现代标准库或项目约定冲突时，不机械套用。

**格式与控制流：**
- 是否已经由 `gofmt`/`go fmt` 处理，不为对齐或括号风格做手工格式争论
- `if`/`switch` 的短声明是否让作用域更小、更清晰
- 错误分支已经 `return`/`break`/`continue` 后，是否避免不必要的 `else`
- `switch` 是否可替代冗长的 `if-else-if` 链，且没有误用 `fallthrough`
- `range` 中未使用的 key/value 是否用 `_` 明确丢弃，而不是制造哑变量
- 复杂逻辑是否能通过早返回、拆分小函数或减少嵌套降低认知负担，而不是堆叠条件

**命名与 API 形状：**
- package 名是否短、小写、无下划线，且不和目录语义冲突
- package 名是否表达职责，避免 `util`、`common`、`base`、`misc` 这类无边界名称
- package 名是否没有“偷走”调用方常用变量名；导入名是否通常不需要重命名
- getter 是否避免无意义 `Get` 前缀（如 `Owner()` 而不是 `GetOwner()`），setter 才使用 `SetX`
- 导出名是否利用 package 前缀避免重复（如 `bufio.Reader`，不要写成 `bufio.BufReader`）
- 方法名是否尊重标准接口语义：实现 `String`、`Read`、`Write`、`Close` 等时签名和含义应匹配惯例
- initialism 是否按 Go 习惯一致书写（如 `URL`、`HTTP`、`ID`），不要在同一项目中混用 `Url`/`URL`
- receiver 名是否短且稳定，不用 `this`、`self`，同一类型的方法 receiver 名保持一致

**文档与注释：**
- 导出 package、type、func、method、const、var 是否有调用方可理解的 doc comment
- doc comment 是否以被说明的导出名开头，并说明调用方需要知道的行为、限制、错误和并发安全性
- package comment 是否说明包的职责边界，而不是重复目录名
- 注释是否解释“为什么”和外部契约；避免把代码已经表达清楚的“做什么”重复一遍
- examples 是否能通过 `go test`，并展示真实调用方式而不是只能编译的玩具片段
- 文档、README、配置注释与当前 API 签名、默认值、错误语义是否一致

**数据结构与初始化：**
- 类型的零值是否尽量可用；不能可用时，构造函数是否清晰表达必要初始化
- `new` 与 `make` 是否用于正确场景：`make` 只用于 slice、map、channel 初始化
- map 读取是否在需要区分“缺失”和“零值”时使用 comma-ok
- map、slice 作为引用语义传参时，调用方可见的修改是否符合预期
- 跨 API 边界保存 slice/map 时是否需要 copy，避免调用方后续修改破坏内部状态
- 返回内部 slice/map 时是否需要 copy 或只读封装，避免泄露可变内部状态
- struct 字段顺序、可见性与 JSON/DB tag 是否符合对外兼容要求，新增字段是否有零值兼容性

**接口、方法与组合：**
- 接口是否小而聚焦，优先表达调用方需要的行为而不是实现方全部能力
- 接口是否定义在消费方附近；不要为了“以后可能 mock”提前导出宽接口
- 指针接收者和值接收者是否符合语义：需要修改接收者或避免复制大对象时用指针
- receiver 选择是否一致；同一类型混用值/指针 receiver 时是否有明确理由
- 只在缺少静态转换验证且确有必要时使用 `var _ Interface = (*T)(nil)` 编译期断言
- embedding 是否用于组合和方法提升，而不是模拟继承；嵌入字段是否已正确初始化，并避免名称冲突
- 函数参数中多个相同基础类型是否容易调错；是否应使用小 struct 或 option 让调用更清晰
- functional options 是否只在参数确实多且可选时使用，避免为简单构造函数引入过度抽象

**错误与 panic/recover：**
- 函数是否用多返回值返回详细错误，而不是用哨兵零值或 `panic` 表示可预期失败
- error 文本是否包含操作或包名等来源信息，便于远离现场时排查
- error 文本是否小写开头且不以标点结尾，便于被上层包装
- 错误包装是否保留调用方需要判断的 cause；不需要暴露内部细节时是否返回受控错误
- sentinel error、错误类型和 `errors.Is`/`errors.As` 的选择是否形成清晰对外契约
- 是否避免 `_` 忽略 error；确需忽略时是否有注释说明原因
- `panic` 是否只用于不可恢复或包内受控流程；对外 API 不应把内部 panic 暴露给调用方
- 使用 `recover` 时是否只在 deferred 函数中直接调用，且只捕获预期 panic，不吞掉未知运行时错误

**context 与取消：**
- `context.Context` 是否作为函数/方法第一个参数传递，且命名为 `ctx`
- 是否避免把 `context.Context` 存进 struct；若确需存储，是否有生命周期边界说明
- 是否调用 cancel 函数释放资源，尤其是 `context.WithTimeout`、`WithDeadline`、`WithCancel`
- 是否避免用 context value 传递可选参数、日志器、数据库连接等普通依赖
- goroutine、I/O、重试、等待和 select 是否尊重 `ctx.Done()`

**并发管道与 goroutine 设计：**
- 每个启动的 goroutine 是否能说明停止条件；不要 fire-and-forget 后无人管理
- pipeline 上游发送和下游提前返回时，是否有取消机制避免发送方永久阻塞
- channel close 责任是否清晰，通常由唯一 sender 或协调者关闭
- fan-out/fan-in、worker pool 是否有限流或 bounded concurrency，避免无界 goroutine
- 锁保护的数据和不变量是否清楚；不要复制含 mutex 的值，不要把 mutex 暴露为嵌入导出字段

**测试与可维护性：**
- table-driven tests 是否覆盖正常路径、边界、错误路径和回归样例
- 测试失败信息是否说明输入、got/want 和 diff 方向，便于定位
- 并发代码是否有 race-sensitive 测试或至少能用 `go test -race` 覆盖关键路径
- benchmark 是否避免把 setup 计入被测路径，必要时使用 `b.ReportAllocs`
- 包内全局状态、时间、随机数、网络/文件系统依赖是否可替换，避免测试污染
- 代码是否优先组合、小接口、显式依赖；不要为了“模式完整”引入复杂框架

参考：
- [Effective Go](https://go.dev/doc/effective_go)
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
- [Go Doc Comments](https://go.dev/doc/comment)
- [Package names](https://go.dev/blog/package-names)
- [Error handling and Go](https://go.dev/blog/error-handling-and-go)
- [Defer, Panic, and Recover](https://go.dev/blog/defer-panic-and-recover)
- [Go Concurrency Patterns: Context](https://go.dev/blog/context)
- [Contexts and structs](https://go.dev/blog/context-and-structs)
- [Go Concurrency Patterns: Pipelines and cancellation](https://go.dev/blog/pipelines)
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md)
- [Google Go Style Guide](https://google.github.io/styleguide/go/)
- [Practical Go](https://dave.cheney.net/practical-go)

## 判断原则

- Go 专项只记录 Go 语言特有的风险，通用问题（逻辑、性能、安全）已在对应 lane 处理
- 并发问题无法百分之百静态判断时，写"疑似"并说明怀疑依据，不武断定性
- 规范类问题（命名、import）降级为 P2，并发和资源泄漏升级为 P0/P1
- Go 综合准则相关问题仅在影响可读性、API 语义、错误处理、并发安全、测试可靠性或长期维护时写入 findings；不要把纯风格偏好当成缺陷
