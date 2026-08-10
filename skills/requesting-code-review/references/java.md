# Java 专项检查

只在本轮 diff 修改 Java 文件时加载。通用正确性、性能、安全和文档问题仍归入对应分路；本文件只补充 Java 特有风险。

## Null 与边界

- 潜在 NPE 必须沿返回值、字段初始化、集合元素或调用链确认 null 来源；仅凭“未显式判空”不构成 finding
- `Optional`、注解、框架契约或上游校验已排除 null 时，不重复报告
- 数组、列表、substring 和分页计算是否存在 off-by-one、空集合或越界
- boxed primitive 自动拆箱是否可能遇到 null

## 控制流与异常

- 条件是否因运算符优先级、短路逻辑或括号遗漏产生相反行为
- switch 是否存在非预期 fall-through；新式 switch expression 是否覆盖必要分支
- `return`、`break`、`continue` 是否退出了错误的作用域
- catch 是否吞掉关键异常、丢失 cause，或把业务错误错误归类为系统成功
- finally/try-with-resources 是否保证连接、流、锁和事务在所有路径释放

## 并发与线程安全

只有存在多线程调用证据时才报告：

- check-then-act 是否在检查与写入之间暴露竞态
- 需要原子性的多步更新是否只保护了其中一部分
- lazy initialization、缓存或 singleton 是否存在不安全发布
- ArrayList、HashMap 或可变对象是否被多个线程并发写入
- executor、future、线程池和异步任务是否有明确关闭、超时、取消和异常收集
- 锁顺序是否可能死锁，临界区内是否执行不可控 I/O

以下情况默认不报线程安全问题：方法局部变量、不可变对象、只读共享数据、已有正确同步、明确单线程生命周期、构建阶段临时对象。

## 数据访问与性能

- 循环内调用是否确实落到数据库、RPC 或昂贵 I/O；确认后再报告 N+1
- 大结果集是否缺少分页、流式读取或上限；必须结合真实数据规模
- transaction 边界是否覆盖应当原子提交的操作，异常路径是否正确 rollback
- ORM lazy loading 是否在错误生命周期访问，或序列化时意外放大查询
- `equals`/`hashCode`、mutable key 和 comparator 契约是否破坏集合行为

## API 与兼容性

- public/protected API 的签名、checked exception、泛型和 nullability 变化是否破坏调用方
- 序列化字段、Jackson 注解、枚举值和默认构造行为是否兼容旧数据
- Spring 等框架的代理、自调用、事务和生命周期注解是否按实际机制生效
- 新增反射、ServiceLoader 或 annotation processing 路径时，打包与运行时可见性是否同步

## 判断原则

- 优先报告会造成 NPE、数据错误、竞态、资源泄漏或兼容性破坏的问题
- 不把“可以改成 stream”“可以用 Optional”“可以换设计模式”等偏好当作 finding
- 需要框架语义时读取实际版本、配置和调用方，不凭常识猜测
