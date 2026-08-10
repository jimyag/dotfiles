---
name: codecov-coverage
description: 在需要通过 Codecov 查询仓库覆盖率、PR 覆盖率影响、commit 覆盖率、文件级覆盖率或覆盖率对比时使用。
allowed-tools: >-
  Bash(command -v:*) Bash(npm install -g mcporter:*) Bash(mcporter:*)
  Bash(npx -y mcporter:*) Bash(bash scripts/codecov-*:*)
  Bash(git remote get-url:*) Bash(git rev-parse:*) Bash(jq:*)
---

# Codecov Coverage

通过 `npx -y mcporter` 调用 `@egulatee/mcp-codecov`，查询 Codecov 覆盖率数据。默认只读，不修改 Codecov 或仓库数据。

## 何时使用

- 查看仓库整体覆盖率
- 分析 PR 的 base/head/patch 覆盖率影响
- 查看某个 commit 的覆盖率详情
- 查看某个文件的逐行覆盖率
- 比较两个分支、tag 或 commit 之间的覆盖率变化

## 前置条件

- Node.js >= 18
- `mcporter` 可用；若用户说 `mcpporter`，按 `mcporter` 处理，因为 npm 包与可执行名都是 `mcporter`
- `jq` 可用；封装脚本依赖 `jq` 解析和格式化 JSON
- `CODECOV_TOKEN` 已设置，且必须是 Codecov API Access Token，不是 Upload Token

获取 token：<https://app.codecov.io/account> -> API Access Token。

若本机缺少 `mcporter`，先安装：

```bash
npm install -g mcporter
```

如果缺少 `jq`，提示用户安装 `jq` 后再继续。如果 token 未设置或无效，立即停止并提示用户配置，不要猜测或降级到网页抓取。

## 安全边界

- 永远不要输出 `CODECOV_TOKEN` 的值
- 不硬编码 owner/repo；封装脚本仅支持从 GitHub remote 自动检测，无法检测时让用户指定
- 只执行查询类操作，不修改 Codecov 上的任何数据
- 不把覆盖率下降直接定性为阻塞，除非用户或项目规则明确要求

## 推荐调用方式

优先使用 `scripts/` 下的封装脚本；脚本会处理 token 检查、owner/repo 检测和输出格式化。

```bash
# 仓库覆盖率
bash scripts/codecov-repo.sh [--owner OWNER] [--repo REPO] [--branch BRANCH] [--json]

# PR 覆盖率影响
bash scripts/codecov-pr.sh <PR_NUMBER> [--owner OWNER] [--repo REPO] [--json]

# commit 覆盖率
bash scripts/codecov-commit.sh [SHA] [--owner OWNER] [--repo REPO] [--json]

# 覆盖率对比
bash scripts/codecov-compare.sh <BASE> <HEAD> [--owner OWNER] [--repo REPO] [--json]

# 文件逐行覆盖率
bash scripts/codecov-file.sh <FILE_PATH> [--owner OWNER] [--repo REPO] [--ref REF] [--json]
```

## 原始 mcporter 调用

需要更细粒度控制时，直接调用 MCP 工具：

```bash
npx -y mcporter call \
  --stdio "npx -y @egulatee/mcp-codecov" \
  --env CODECOV_TOKEN="$CODECOV_TOKEN" \
  --name codecov \
  get_repo_coverage \
  owner:OWNER repo:REPO
```

可用工具：

- `get_repo_coverage owner: repo: [branch:]`
- `get_commit_coverage owner: repo: commit_sha:`
- `get_pull_request_coverage owner: repo: pull_number:`
- `get_file_coverage owner: repo: file_path: [ref:]`
- `compare_coverage owner: repo: base: head:`

## 参数解析

`owner` 和 `repo` 按以下顺序解析：

1. 命令行 `--owner` / `--repo`
2. 当前目录 `git remote get-url origin`（仅支持 GitHub remote 自动解析）
3. 无法解析时停止并提示用户显式指定

`commit_sha` 必须使用完整或可解析的 hex SHA；若 Codecov 返回找不到 commit，要求用户提供完整 40 位 SHA 再重试。

## 故障处理

- `CODECOV_TOKEN 未设置`：提示用户执行 `export CODECOV_TOKEN="..."`，不要输出 token
- `401 Unauthorized`：token 无效或过期，提示重新生成 API Access Token
- `404 Not Found`：检查 owner/repo 是否正确、仓库是否已接入 Codecov、目标 ref 是否有覆盖率数据
- `commit_sha not found`：使用完整 40 位 commit SHA
- `jq: command not found`：提示安装 `jq`，不要继续执行封装脚本

## 输出要求

- 默认给中文摘要，包含覆盖率百分比和关键变化
- 百分比保留 Codecov 返回精度；需要手动计算时保留两位小数
- 涉及 PR 时说明 base/head/patch 三类覆盖率
- 涉及文件时优先指出未覆盖行或覆盖率最低的文件
- 结论中区分事实与建议，不要把覆盖率变化夸大成业务风险

## Smoke Test

```bash
bash scripts/codecov-repo.sh --help
bash scripts/codecov-pr.sh --help
bash scripts/codecov-commit.sh --help
bash scripts/codecov-compare.sh --help
bash scripts/codecov-file.sh --help
bash -n scripts/_common.sh scripts/codecov-*.sh
python3 ../_shared/lint-skills.py
```

预期：help 命令不需要 `CODECOV_TOKEN`；未设置 `CODECOV_TOKEN` 时执行查询类命令应明确报错且不泄露 token。
