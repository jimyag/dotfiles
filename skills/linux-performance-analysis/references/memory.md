# Memory Analysis

## System-Wide Checks

Start with capacity, reclaim, swap, and fault behavior:

```bash
free -h
vmstat 1 5
sar -r 1 3
sar -B 1 3
```

Focus on:

- `available` memory, not just `free`
- swap usage and swap in/out
- major page faults
- reclaim pressure
- OOM kills or allocation failures

Useful supporting checks:

```bash
dmesg | tail -n 50
grep -i 'oom\\|killed process' /var/log/messages /var/log/syslog 2>/dev/null
```

## Process Drill-Down

Identify which processes hold memory or trigger faults:

```bash
ps -eo pid,ppid,cmd,%mem,rss,vsz --sort=-rss | head
smem -rk
pidstat -r -p ALL 1 3
```

If a single process is suspect, inspect its mappings and growth pattern:

```bash
pmap -x <pid> | tail -n 20
cat /proc/<pid>/status
cat /proc/<pid>/smaps_rollup
```

## Interpretation

- Low `available` plus active swap in/out means real memory pressure.
- Large page cache with healthy `available` is not automatically a problem.
- High major faults or reclaim stalls can make latency spike even before OOM.
- Repeated OOM events indicate either undersized memory or one or more runaway processes.
- A process with steadily growing RSS or obvious unfreed allocations suggests application-layer leak or retention.

## Kernel Vs Application

- Application space: one or more processes dominate RSS, leak memory, or trigger excessive allocations/faults.
- Kernel space: slab growth, reclaim behavior, page-cache pressure, or other kernel-managed memory behavior is dominant.
- Mixed case: a memory-hungry application can force kernel reclaim and swap storms. Report the layer where time is being lost, and name the process that triggers it.
