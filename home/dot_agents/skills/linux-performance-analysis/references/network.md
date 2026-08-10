# Network Analysis

## System-Wide Checks

Start with link, socket, and retransmission health:

```bash
sar -n DEV 1 3
sar -n TCP,ETCP 1 3
ss -s
ip -s link
```

Focus on:

- interface throughput and packet rate
- drops, errors, overruns
- retransmits and resets
- listen queue and established socket growth
- backlog pressure or connection-state anomalies

Useful supporting checks:

```bash
netstat -s
ss -lntp
nethogs
iftop
```

## Process Drill-Down

Identify which process owns the busy or unhealthy sockets:

```bash
ss -tpn
ss -lntp
nethogs
```

If packet-level evidence is needed:

```bash
tcpdump -i <iface> -nn -s 128 -c 200
ping <target>
```

`tcpdump` should be short and bounded. Keep packet count capped and avoid full-payload capture unless necessary.

Active load testing (non-production preferred, explicit approval required):

```bash
iperf3 -c <target>
```

## Interpretation

- High retransmits, drops, resets, or backlog overflow indicate network-path or kernel TCP pressure.
- High throughput with normal retransmits may be healthy; check latency and queueing before calling it a bottleneck.
- Many `TIME_WAIT`, `SYN_RECV`, or accept-queue issues can be connection-management problems rather than raw bandwidth shortage.
- If one process owns most hot sockets or drives abnormal connection churn, that process is the application trigger.
- High softirq CPU combined with network traffic often means the bottleneck is in kernel networking or interrupt handling.

## Kernel Vs Application

- Application space: connection storms, poor socket usage, tiny writes, slow reads, or inefficient protocol behavior originate from a process.
- Kernel space: softirq, TCP/IP stack, backlog handling, driver/NIC behavior, or socket buffer pressure dominates.
- Mixed case: an application can trigger kernel network pressure. Report the kernel hotspot and name the process causing it.
