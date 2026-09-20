# 简化审查

## 判断目标

简化审查关注当前差异是否让读者需要同时理解更多概念、分支、状态、层级或依赖。代码行数只是线索；更短但隐藏副作用、错误语义或业务规则的实现不算更简单。

每条建议都必须回答：

1. 当前复杂度来自哪里。
2. 哪些代码或概念可以删除、合并或移回已有所有者。
3. 替代实现为什么适用于当前类型、接口和调用方。
4. 如何证明返回值、错误、副作用、调用顺序和兼容性不变。

找不到可用替代实现时，将观察结果保留为待确认问题，不输出“应该简化”式 finding。

## 审查方法

先沿当前差异和必要调用链建立行为基线，再检查：

- 新增了多少业务概念、模式、配置项、状态字段和布尔开关；其中哪些只服务一个调用方或一个固定值。
- 同一条件、转换、校验、错误包装或状态更新是否在多处重复。
- wrapper、adapter、interface 或 helper 是否建立了真实边界，还是只转发参数和返回值。
- 外部数据是否在边界完成解析和校验；内部层是否还在重复处理 transport、storage 或 nullable 表示。
- 多个布尔值和散落条件是否允许矛盾状态；现有领域类型能否直接表达合法状态。
- 仓库是否已有承担相同职责的 canonical helper、类型或服务。
- 测试是否因重复 setup 和 assertion 隐藏了真正的行为差异。

按“删除概念”优先于“抽取抽象”、局部改动优先于跨模块重写的顺序寻找方案。替代实现必须覆盖当前需求，不借简化之名缩减错误处理、安全校验、数据保护、可访问性或兼容行为。

## 常见可行改法

以下代码展示判断方式。实际 finding 应使用目标仓库的真实类型、函数名和错误约定，并核对所有调用方。

### 用提前返回减少嵌套

当每层 `if` 只负责拒绝一种无效情况时，提前返回可以让主流程保持线性。

```go
func loadUser(ctx context.Context, id string) (*User, error) {
    if id != "" {
        user, err := repo.Get(ctx, id)
        if err == nil {
            if user.Active {
                return user, nil
            }
            return nil, ErrInactive
        }
        return nil, fmt.Errorf("get user: %w", err)
    }
    return nil, ErrMissingID
}
```

可以改为：

```go
func loadUser(ctx context.Context, id string) (*User, error) {
    if id == "" {
        return nil, ErrMissingID
    }

    user, err := repo.Get(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("get user: %w", err)
    }
    if !user.Active {
        return nil, ErrInactive
    }
    return user, nil
}
```

适用证据是各分支原本就会立即结束，且执行顺序和错误值没有变化。需要继续执行清理、回滚或聚合错误的流程不直接套用。

### 先确定变化值，再执行共同逻辑

分支只改变一个参数时，不必复制整个调用和错误处理。

```go
if account.Premium {
    users, err := store.List(ctx, premiumLimit)
    if err != nil {
        return nil, fmt.Errorf("list users: %w", err)
    }
    return users, nil
}

users, err := store.List(ctx, defaultLimit)
if err != nil {
    return nil, fmt.Errorf("list users: %w", err)
}
return users, nil
```

可以改为：

```go
limit := defaultLimit
if account.Premium {
    limit = premiumLimit
}

users, err := store.List(ctx, limit)
if err != nil {
    return nil, fmt.Errorf("list users: %w", err)
}
return users, nil
```

评审时确认两个分支除了参数外确实相同；如果超时、事务、日志或错误映射不同，保留分支或先说明差异。

### 删除没有策略的薄封装

下面的 wrapper 没有建立权限、缓存、事务、可观测性或领域转换边界：

```go
func (s *Service) getUser(ctx context.Context, id string) (*User, error) {
    return s.repo.Get(ctx, id)
}
```

如果只有一个调用方，且测试不依赖这个 seam，可以让调用方直接使用 `s.repo.Get`。提出建议前检查：

- wrapper 是否属于公开 API 或 interface 实现；
- 后续是否会在这里建立已经确定的策略，而不是假设性的扩展点；
- 删除后是否造成上层直接依赖 storage 或 transport 类型。

满足这些条件才能把删除 wrapper 作为可执行建议；否则它可能是有效边界。

### 用一个状态表达互斥阶段

多个布尔值允许产生业务上不存在的组合时，一个枚举状态通常更容易验证。

```go
type Job struct {
    Pending bool
    Running bool
    Done    bool
}
```

可以改为：

```go
type JobState string

const (
    JobPending JobState = "pending"
    JobRunning JobState = "running"
    JobDone    JobState = "done"
)

type Job struct {
    State JobState
}
```

这个方案只有在三个字段确实互斥、持久化和 API 兼容性可以处理时才成立。评审需要列出迁移路径、序列化变化和现有调用方，而不是只给出新类型。

### 在边界解析一次

HTTP、CLI、配置或存储层的字符串值进入业务逻辑时，应在边界完成解析和校验。

```go
func (s *Service) Resize(ctx context.Context, size string) error {
    parsed, err := strconv.ParseInt(size, 10, 64)
    if err != nil {
        return fmt.Errorf("parse size: %w", err)
    }
    return s.resize(ctx, parsed)
}
```

如果 `size` 来自 HTTP handler，可以在 handler 中解析为 `int64`，让 service 接收已经验证的领域值：

```go
func (h *Handler) resize(w http.ResponseWriter, r *http.Request) {
    size, err := strconv.ParseInt(r.FormValue("size"), 10, 64)
    if err != nil {
        http.Error(w, "invalid size", http.StatusBadRequest)
        return
    }
    if err := h.service.Resize(r.Context(), size); err != nil {
        h.writeServiceError(w, err)
        return
    }
    w.WriteHeader(http.StatusNoContent)
}
```

```go
func (s *Service) Resize(ctx context.Context, size int64) error {
    return s.resize(ctx, size)
}
```

评审时确认错误映射仍由正确层负责，并检查其他调用方是否已经提供数值，避免把 HTTP 语义泄漏进 service。

### 复用仓库已有所有者

新增 helper 与现有实现职责接近时，先搜索定义和调用方：

```bash
rg -n 'func .*Normalize|Normalize\(' .
rg -n 'type .*State|const \(' .
```

建议应指出可以复用的真实符号、两者语义差异以及合并后的调用方式。名称相似但默认值、错误处理或输入范围不同，不足以证明可以复用。

### 合并结构相同的测试

多个测试只有输入和期望值不同，并共享 setup、动作与 assertion 时，可以使用表驱动测试：

```go
func TestNormalize(t *testing.T) {
    tests := []struct {
        name string
        in   string
        want string
    }{
        {name: "trim", in: " a ", want: "a"},
        {name: "lower", in: "A", want: "a"},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := Normalize(tt.in); got != tt.want {
                t.Fatalf("Normalize(%q) = %q, want %q", tt.in, got, tt.want)
            }
        })
    }
}
```

错误路径需要不同 setup、不同副作用检查或不同断言时，独立测试通常更清楚。表驱动形式本身不是简化目标。

## 可用性与验证

输出建议前完成与风险匹配的检查：

- 用当前仓库的定义确认示例中的类型、函数和参数真实存在。
- 搜索所有调用方，确认没有遗漏接口实现、生成代码、序列化格式或外部 API。
- 对照原实现列出必须保持的返回值、错误、日志、指标、事务和调用顺序。
- 能本地修改验证时，至少运行格式化、编译或类型检查，以及受影响路径的针对性测试。
- 只读审查无法修改代码时，给出可以直接落地的 patch 轮廓和验证命令，并明确尚未执行。

复杂度本身通常是 P2 或非阻塞建议。只有它已经造成确定的正确性、安全、并发或兼容性问题时，才按实际影响提高严重度。

## 输出要求

每条简化建议包含：

- 文件和最小相关行范围；
- 当前复杂度来源；
- 适配当前代码的替代实现或具体步骤；
- 为什么减少了认知负担，而不是把复杂度移动到别处；
- 保持的行为和可执行验证方法。

没有找到可行方案时，在摘要中写明已检查的复杂度维度，不输出占位建议。
