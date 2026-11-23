# 磁盘 IO 故障复盘与资源围栏手册（2026-11-23 事件）

> 状态：**已结案**（2026-11-24 06:47 完成两轮完整业务周期验证）。
> 本文面向后续运维与开发：既记录事故本身，也沉淀为可复用的资源配置原则与日常检查手册。

---

## 1. 事件概述

| 项 | 内容 |
|---|---|
| 故障现象 | 云服务器周期性"整机无法响应"（SSH 失联），2026-11-23 21:17 多次触发阿里云 `SysDiskBPS` 告警（存储性能达规格上限） |
| 涉事服务 | ai-rss-hub（FastAPI + SQLite WAL + APScheduler 定时全量抓取 RSS） |
| 影响 | SSH 管理通道阻塞、整机能见度丧失；CPU 始终未过载（"假死"而非"真死"） |
| 处置结果 | 分层资源围栏落地，服务恢复；连续运行 7h+ 跨两轮抓取周期无异常 |

## 2. 环境约束（根因的物理前提）

| 项 | 规格 | 瓶颈含义 |
|---|---|---|
| 实例 | 阿里云 ecs.e-c1m1.large，2 vCPU / 2 GiB | 内存极小，任何解析尖峰都可能触发换页 |
| 系统盘 | ESSD Entry 40 GiB | IOPS = 2120、吞吐 = 106 MB/s、随机写时延 1~3ms、**不支持突发** |
| OS | Ubuntu 24.04，cgroup v2 | io/memory 控制器可用，围栏前提 |

**核心认知**：入门型云盘的 IOPS 天花板远低于直觉。2G 内存机器上，"内存尖峰 → swap 换页"这一步产生的 4KB 随机 I/O（数千 IOPS）比应用本身的顺序写更容易击穿盘规格。

## 3. 根因链（多方诊断一致）

```
APScheduler 每 3 小时全量拉取 RSS
  → feedparser 解析内存尖峰 + 进程基线内存
  → 2G 内存耗尽 → Swap 频繁换页（4KB 随机 I/O，数千 IOPS）
  → 叠加 SQLite WAL 追加写 + 周期性 checkpoint 突发刷盘
  → 瞬间击穿 ESSD Entry 的 2120 IOPS / 106 MB/s 天花板
  → 块设备队列拥塞 → 进程大面积 D 状态（不可中断睡眠）
  → SSH 登录所需 I/O 排在拥塞队列尾 → 整机表现为"无法响应"
```

关键机理：**排队无限变长而管理流量（SSH）无优先权**。CPU 并未过载，所以 top 看一切正常，属于典型的"IO 排队型假死"。

## 4. 处置方案：分层资源围栏

核心思想：**把"超额成本"物理限制在肇事 cgroup 内，使"服务发疯"与"整机失联"解耦**。

### 4.1 最终生效参数（systemctl show 实测，2026-11-24 核验）

| 参数 | 实测值 | 拦截的失效模式 |
|---|---|---|
| `MemoryHigh` | 512M（软限，提前回收） | swap thrashing 死亡螺旋（本次主因） |
| `MemoryMax` | 768M（硬限，cgroup 内 OOM 只杀自己） | 同上 |
| `MemorySwapMax` | 512M | 换页用量封顶 |
| `CPUQuota` | 150% | CPU 打满挤占 SSH 时间片 |
| `IOWeight` | 50 | 相对降权（辅助手段） |
| `IOReadBandwidthMax` / `IOWriteBandwidthMax` | 20M / 10M | 应用 I/O 顶穿云盘带宽 |
| `IOReadIOPSMax` / `IOWriteIOPSMax` | 800 / 800 | 应用 I/O 顶穿云盘 IOPS（**写侧 800 是事后补齐**，见 §6） |
| `TasksMax` | 256 | fork/线程泄漏 |
| `OOMPolicy` / `Restart` | stop / on-failure（RestartSec=30，300s 内最多 3 次） | 崩溃-重启风暴 |
| 应用层 | `--workers 1 --limit-concurrency 50` | 内存翻倍、连接堆积 |

I/O 硬限的精准度：云盘上限 106MB/s / 2120 IOPS，硬限压到 20M/10M/800 后，**应用在物理层面已不可能打满盘**——这比 IOWeight 降权可靠得多，是本方案的关键升级。

### 4.2 配置文件位置

- 线上：`/etc/systemd/system/ai-rss-hub.service.d/{limits,override,uvicorn}.conf`
- **仓库唯一事实源**：`config/systemd/`（commit ef96f3d 起纳管）
- 应用层配套：`app/database.py:31-50`（PRAGMA）、`app/services/rss_fetcher.py`（分批错峰 + 收尾 checkpoint）、`config/systemd/uvicorn.conf`（启动约束）

> ⚠️ systemd drop-in 合并机制：同目录多个 drop-in **按文件名字母序加载，后者覆盖前者**（l < o < u），**不做取大值合并**。limits.conf 里保留的 600M/800M/120% 实际已被 override.conf 的 512M/768M/150% 覆盖。**任何参数争议以 `systemctl show ai-rss-hub` 实测为准，不要相信任何单一文件的注释。**

## 5. 应用层配套优化（commit ca7d807 等）

| 措施 | 位置 | 作用 |
|---|---|---|
| `synchronous=NORMAL` + `wal_autocheckpoint=5000` | `app/database.py:35-41` | 减少 fsync 次数、抬高自动 checkpoint 阈值（20MB） |
| `mmap_size=64M` + `cache_size=-65536` | `app/database.py:46-50` | 控制内存驻留上限约 128MB |
| 抓取分批错峰（批 5 源、间隔 5s） | `app/services/rss_fetcher.py` | 削平并发解析的内存/IO 尖峰 |
| 抓取收尾 `wal_checkpoint(PASSIVE)` | `app/services/rss_fetcher.py` | 每轮任务末尾把 WAL 合并入主库，防 MB 级堆积 |
| 摘要批次逐批 pop 释放原文引用 | `rss_fetcher.py` | 压低批次处理期间内存峰值 |

## 6. 关键决策记录（做什么，以及刻意不做什么）

| 决策 | 结论 | 理由 |
|---|---|---|
| iterparse 流式解析重写 | **否决** | 项目用 feedparser（无流式接口），强换解析器高风险大改动；且启动 IO 突发实测来自 .so 加载而非 XML 解析 |
| uvicorn `--limit-max-requests` | **明确不加** | 达阈值后 worker 优雅重启需重新加载 lxml/sqlalchemy 等 C 扩展，iotop 实测启动瞬间约 9.5MB/s 写突发——周期性制造自己要消灭的 IO 尖峰 |
| swapfile 1G + swappiness=0 | 保留 | swap 角色是 OS 兜底（防 OOM killer 误杀系统进程）；防服务 thrashing 靠 MemoryHigh/Max 围栏。若观测到 swap 持续非零，应复查围栏参数而非加 swap |
| 写侧 IOPS 硬限 | 事后补齐 `IOWriteIOPSMax=800` | 带宽限 ≠ IOPS 限：4KB 随机写下 10MB/s 理论换算 2560 IOPS > 盘上限 2120，极端随机写场景盘仍会被打满 |

## 7. 结案验证数据（2026-11-24 06:47）

- 服务自 11-23 23:05 连续运行 7h，跨 **两轮完整抓取周期**（02:05 新增 21 篇、05:05 新增 16 篇）
- 内存峰值 121.8M（硬限 768M 的 16%）；Swap 全程 0B；WAL 稳定 4.0M
- 日志无 OOM/killed/throttle/restart；iostat %util 低、await 亚毫秒级
- 日志非零匹配均定性为无害：坏测试源解析警告 ×4、LLM 429 限流退避 ×3（按设计工作）、孤立 "Invalid model" 400 ×1

## 8. 经验教训（后续借鉴）

1. **低配机器上，内存尖峰是 IO 事故的隐形放大器**。2G 内存 + feedparser 全量解析，先撑爆内存再由 swap 换页产生海量 4KB 随机 I/O——比 SQLite 顺序写更致命。压内存峰值 = 压 IO 峰值，两者是同一件事。
2. **IO 硬限（Bandwidth/IOPS Max）优于相对权重（IOWeight）**。权重只在竞争时起作用，硬限在物理上杜绝击穿。给"最坏情况的自己"设上限，而不是指望调度公平。
3. **写侧带宽限必须配写侧 IOPS 限**。小 IO（4KB）场景下带宽换算出的 IOPS 可以远超盘规格，只限带宽是漏防。
4. **cgroup 围栏是"防失控"，不是"扩容"**。它保证服务失控时整机不失联（SSH 可登录、可排查），但不能让 2G 机器干 4G 的活。可用内存跌破 ~300M 或告警复发时，正确动作是升配（2C4G u1 档 / ESSD AutoPL），不是继续调参。
5. **多 drop-in 叠加时必须实测合并值**。字母序覆盖、不取大值——本次收官报告就因误判合并机制写错了生效参数。`systemctl show` 是唯一可信来源；配置文件必须同步进仓库，否则线上漂移无法追溯。
6. **周期重启型配置要警惕"自己制造自己要消灭的突发"**。`--limit-max-requests` 这类看似减负的参数，实际通过重启进程周期性重演 C 扩展加载的 IO 突发。
7. **验收必须跨完整业务周期**。故障模式是"每 3 小时一次的定时任务"，启动后 3 分钟的稳态"健康"不算数。本事件以连续 7h + 两轮周期 + 数据库写入旁证（article 表新增数）结案。
8. **数据库旁证比日志更可靠**。journalctl 权限受限或日志被轮转时，`SELECT ... WHERE created_at >= 窗口起点`（只读模式 `file:...?mode=ro`）可以直接证明任务是否真实发生、写入了多少。

## 9. 日常检查手册

### 9.1 例行巡检（低频，如每月或告警后）

```bash
# 围栏是否还在（任何参数为空 = 配置漂移，立即排查）
systemctl show ai-rss-hub -p MemoryHigh -p MemoryMax -p MemorySwapMax \
  -p CPUQuotaPerSecUSec -p IOWeight -p TasksMax -p IOReadBandwidthMax \
  -p IOWriteBandwidthMax -p IOReadIOPSMax -p IOWriteIOPSMax

# 一次完整抓取周期后（抓取窗口 = 启动时间 + 3h 的整数倍）
journalctl -u ai-rss-hub --since "3 hours ago" | grep -iE "oom|killed|throttl|restart"
systemctl status ai-rss-hub        # 期望：内存峰值 << 768M
free -h                            # 期望：Swap 使用 0B（持续非零 = 围栏需复查）
ls -lh ai_rss_hub.db-wal           # 期望：KB~低 MB 级（>20MB = checkpoint 失效）
iostat -x 5                        # 期望：%util 有波动但不持续 100%，await 毫秒级
```

### 9.2 告警复发时的处置顺序

1. 先看 `systemctl status ai-rss-hub` 内存峰值与 `free -h` swap——区分"内存型"还是"IO 型"复发；
2. 确认围栏是否仍然生效（§9.1 第一条命令）；
3. `iotop` / `fatrace` / `cat /proc/<PID>/io` 定位 IO 来源进程；
4. 若围栏生效仍告警 → 说明订阅规模增长导致正常写入量已逼近限值或盘规格，走升配预案，不要调大限值硬扛。

### 9.3 升配触发线

| 触发条件 | 预案 |
|---|---|
| 系统可用内存持续 < 300M | 升配 2C4G（u1 实例 199 元/年档） |
| IO 告警在围栏生效下复发 | 升盘 ESSD AutoPL / PL0 |
| 单轮抓取耗时逼近 3h 周期（对比任务起止日志时间戳） | 订阅源规模增长，先查分批参数，再评估升配 |
