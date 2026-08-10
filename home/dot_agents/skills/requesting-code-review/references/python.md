# Python 专项检查

只在本轮 diff 修改 Python 文件时加载。优先准确率：上下文无法证明的语言惯用法或风格建议不输出。

## 共享状态与对象生命周期

- `def f(x=[])`、`{}`、set 或其他可变默认参数是否跨调用共享并被修改；刻意缓存或只读 sentinel 不误报
- class-level 可变属性是否被错误当作实例字段
- module-level 可变全局状态是否跨请求、测试、线程或进程保留并造成污染
- closure、lambda 或异步回调是否捕获循环变量并在执行时看到最终值
- shallow copy 是否不足以隔离嵌套可变对象

## 边界与 Python 语义

- 空集合进入 `[0]`、`min`、`max`、解包或需要至少一个元素的逻辑
- `None` 是否能沿真实调用链到达解引用、算术或解包位置
- `is` 是否被用于字符串、数字等值比较；`== None` 通常只算风格，不作为阻塞问题
- 除零、精确浮点比较、负索引和切片边界是否违反真实业务契约
- dict key 缺失是否是合法输入；不要机械把所有 `d[k]` 改成 `get`
- iterator/generator 是否被意外消费两次或在资源关闭后继续迭代

## 异常与资源

- bare `except:` 是否吞掉 `KeyboardInterrupt`/`SystemExit`；宽泛 `except Exception` 是否掩盖不相关失败
- catch 后 `pass`、返回默认成功或只记模糊日志是否隐藏真实错误
- 重新抛出是否丢失 traceback/cause；需要时使用裸 `raise` 或 `raise ... from err`
- `assert` 是否被用来校验外部输入或生产不变量，因为 `python -O` 可移除断言
- 文件、socket、锁、事务和数据库连接是否通过 context manager 或 finally 覆盖所有退出路径
- generator 是否让资源生命周期延长到调用方不可控的位置

## Async 与并发

只有存在 async、线程或多进程调用证据时才报告：

- `async def` 内是否直接执行同步网络/文件 I/O、`time.sleep` 或 CPU 重任务，阻塞 event loop
- `create_task` 后是否丢失引用、无人 await/收集异常，或任务越过请求/对象生命周期
- cancellation 是否被宽泛异常捕获吞掉，cleanup 是否在取消路径执行
- check-then-act 或复合更新是否错误依赖 GIL 的“看起来原子”
- CPU-bound 工作是否被放入线程池且确实造成吞吐问题；I/O-bound 线程不误报

## 安全

先确认输入真实可控，再报告：

- `eval`、`exec`、`compile` 或动态 import 处理不可信输入
- `subprocess` 的 `shell=True` 或命令字符串包含外部输入
- `pickle`、`marshal`、不安全 YAML loader 等反序列化不可信数据
- SQL 使用拼接/f-string 而不是驱动参数绑定
- 路径拼接允许越过预期根目录或跟随不可信 symlink
- `random`、MD5/SHA1 被用于 token、密码或安全校验
- secret、token、密码、PII 被写入日志、异常或源码

## 性能与可靠性

- 热点循环中重复 regex 编译、不变量计算或线性 membership；必须先确认数据规模和热点
- 大数据是否被无必要完整 materialize，而流式处理确实符合生命周期
- logging 使用 eager f-string 是否在高频关闭级别路径造成可证明开销
- retry 是否有次数、退避、超时和取消边界
- import-time I/O、网络和可变全局初始化是否破坏启动、测试隔离或多进程模型

## 判断原则

- security/correctness finding 需要真实输入路径或调用链证据
- 不把 formatter、typing 偏好、`== None`、所有 broad exception 等机械规则升级为缺陷
- 框架管理的资源、生命周期和校验要读取实际框架约定后再判断
