---
name: linux-performance-analysis
description: 在分析 Linux 主机性能问题时使用。适用于系统变慢、负载高、延迟高、CPU 飙高、内存不足、swap、磁盘阻塞、I/O wait、丢包、连接异常、超时，或需要判断瓶颈在 CPU、内存、I/O、网络、内核态还是应用态的场景。
---

# Linux 性能分析

## 目标

用低侵入方式定位 Linux 性能瓶颈。  
先看系统整体压力，再下钻到 CPU、内存、I/O、网络和具体进程，最后明确瓶颈子系统、内核态/应用态归因，以及主要触发进程。

## 何时使用

- Linux 主机运行缓慢、卡顿、过载、延迟高
- load average 高、CPU 使用率异常、CPU 主频异常降低、I/O wait 高
- 内存紧张、频繁 swap、OOM、major fault 异常
- 磁盘读写慢、文件系统满、inode 耗尽、进程阻塞在 I/O
- 丢包、重传、连接堆积、超时、网络吞吐或延迟异常
- 用户只提供了命令输出，需要基于现有证据判断瓶颈

## 何时不要使用

- 问题不是 Linux 主机或容器运行时性能问题
- 用户只是在问某个命令的语法，不需要做诊断
- 已经明确是业务代码逻辑 bug，应优先用系统化排查

## 安全级别

默认使用最低侵入方式，尤其是生产环境。

- L1：默认，只读、低开销观察，例如 `uptime`、`top`、`vmstat`、`iostat`、`ss`
- L2：短时间采样，有明确时长和目标，例如 `pidstat 1 3`
- L3：attach、trace、抓包、eBPF、主动压测，例如 `perf`、`strace`、`tcpdump`、`iperf3`

执行 L3 前必须先确认：

1. 主机是否生产环境
2. 采样时间窗口
3. 预期风险或开销
4. 明确的 duration、packet count 或 sample cap

## 基本流程

1. 明确症状、时间窗口、影响范围
2. 复用用户已有输出；不足时先补轻量 baseline
3. 横向检查 CPU、内存、I/O、网络，避免只盯第一个异常指标
4. 对可疑子系统从系统级下钻到进程、线程、设备、socket
5. 判断主要瓶颈在内核态还是应用态
6. 给出证据、结论、下一条最能减少不确定性的命令

## Baseline

优先从这些只读命令开始：

```bash
uname -a
uptime
top -b -n 1
vmstat 1 5
pidstat 1 3
```

如果某个方向已经明显异常，再读取对应参考：

- CPU：[references/cpu.md](references/cpu.md)
- 内存：[references/memory.md](references/memory.md)
- I/O：[references/io.md](references/io.md)
- 网络：[references/network.md](references/network.md)
- 报告模板：[references/report-template.md](references/report-template.md)

## 判断规则

- 高 `%wa` 通常先查 I/O，不要简单归为 CPU 问题
- load 高但 CPU 不高时，重点看阻塞任务、I/O、锁等待
- CPU 忙但吞吐低或延迟高时，检查 governor、性能模式、当前主频、最大/最小频率限制和热降频
- 高 `%sy`、`%si`、`%hi`、重传、backlog 压力通常指向内核或网络路径
- swap、major fault、reclaim stall、OOM 指向内存压力
- 网络问题可能由 CPU 饱和、socket backlog、应用读写慢共同触发

## 内核态与应用态

- 应用态：用户进程、业务线程、GC、SQL、序列化、压缩、请求处理等成本占主导
- 内核态：调度、软中断、中断、回收、文件系统、块层、TCP/IP、驱动、系统调用路径占主导
- 混合场景：如果应用触发大量内核工作，要同时说明“瓶颈层在内核态”和“触发进程是谁”

## 输出要求

最终结论必须明确回答：

1. 主要瓶颈是 CPU、内存、I/O 还是网络
2. 瓶颈主要在内核态还是应用态
3. 如果涉及应用态，哪个进程是主要触发者

证据不足时，不要强行定论。说明已经确认什么、仍然怀疑什么，并给出下一条最值得执行的命令。

## 关键约束

- 先看证据，再下结论
- 先系统级，再进程级
- 不主动运行有负载或高侵入命令
- 不把缓存占用直接当成内存泄漏
- 不把单个异常指标直接当成根因
