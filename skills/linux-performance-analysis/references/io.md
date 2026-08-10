# I/O Analysis

## System-Wide Checks

Start with filesystem capacity and disk latency:

```bash
df -h
df -i
iostat -xz 1 3
vmstat 1 5
```

Focus on:

- `%util`: device busy time
- `await`: end-to-end I/O latency
- `svctm` when available
- `r/s`, `w/s`, `rkB/s`, `wkB/s`
- queue depth and whether latency rises with utilization
- inode exhaustion or full filesystem conditions

Useful supporting checks:

```bash
pidstat -d 1 3
iotop -oPa
```

## Process Drill-Down

Find the processes generating I/O or suffering high I/O delay:

```bash
pidstat -d -p ALL 1 3
iotop -oPa
```

If needed, inspect file and block behavior:

```bash
timeout 10s strace -tt -T -p <pid>
timeout 15s filetop
timeout 15s biotop
timeout 15s biolatency
```

Run the commands above only as escalation steps with explicit approval, because they may require elevated privileges and can add overhead.

## Interpretation

- High `%wa` plus high disk `await` usually means storage is the bottleneck.
- High `%util` with low throughput can still mean a slow device due to small random I/O.
- Full disk or inode exhaustion can look like application slowness but is fundamentally an I/O/filesystem issue.
- One process dominating reads/writes or showing high `iodelay` is a likely application trigger.
- If the storage device is calm but the process is stuck in file operations, inspect filesystem locks, metadata overhead, and syscall timing.

## Kernel Vs Application

- Application space: a process issues inefficient read/write patterns, sync-heavy behavior, or excessive logging/checkpointing.
- Kernel space: block layer, filesystem, page cache writeback, device driver, or mount/filesystem behavior dominates the delay.
- Mixed case: a process can create the pressure while the visible waiting time accumulates in kernel I/O paths. Report both clearly.
