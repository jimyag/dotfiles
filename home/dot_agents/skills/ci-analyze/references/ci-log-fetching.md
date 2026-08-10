# CI 日志抓取（按提供方）

## A) GitHub Actions（基线）

```bash
gh run view <run-id> --repo <owner/repo> --log-failed
```

## B) Travis CI

1. 从 PR checks 的 `targetUrl` 找到 Travis 链接（常见形态：`travis-ci.com/.../jobs/<job_id>`）
2. 默认使用 TRAVIS_TOKEN 访问 API（私有仓库必须认证）：

```bash
# 始终带上 TRAVIS_TOKEN，私有仓库必须认证
# 日志保存到 /tmp 目录
curl -fsSL \
  -H "Travis-API-Version: 3" \
  -H "Authorization: token ${TRAVIS_TOKEN}" \
  "https://api.travis-ci.com/v3/job/<job_id>/log.txt" \
  -o /tmp/travis-<job_id>.log
```

3. 如果只有 build URL（如 `https://app.travis-ci.com/github/<owner>/<repo>/builds/<build_id>`），先取 job 再拉日志：

```bash
# 从 build 查 jobs（必须带 token）
# 先保存到文件，再用 jq 解析
curl -fsSL \
  -H "Travis-API-Version: 3" \
  -H "Authorization: token ${TRAVIS_TOKEN}" \
  "https://api.travis-ci.com/v3/build/<build_id>/jobs" \
  -o /tmp/travis-build-<build_id>.json

# 单独执行 jq 解析
jq '.jobs[] | {id, state, number, started_at, finished_at}' /tmp/travis-build-<build_id>.json

# 再用 job id 拉 log.txt
curl -fsSL \
  -H "Travis-API-Version: 3" \
  -H "Authorization: token ${TRAVIS_TOKEN}" \
  "https://api.travis-ci.com/v3/job/<job_id>/log.txt" \
  -o /tmp/travis-<job_id>.log
```

4. 若 API 返回 `"repository not found (or insufficient access)"`，说明 TRAVIS_TOKEN 未设置或无效，立即询问用户：
   ```
   Travis API 访问私有仓库需要认证。请设置 TRAVIS_TOKEN 环境变量：
   1. 登录 https://app.travis-ci.com → Settings → API authentication → Copy token
   2. 执行：export TRAVIS_TOKEN="你的token"
   3. 确认后我将继续分析
   ```

5. 若 API 失败（401/403/其他错误），记录失败原因，并回退到 `targetUrl` 页面中的错误摘要（至少保留报错关键行 + 步骤名）。

命令规范：
- 禁止使用管道 `|` 或 `&&` 组合多个命令
- 每个命令单独执行，便于权限匹配和错误定位
- curl 输出先保存到 /tmp 文件，再用其他命令处理

## C) Codecov

Codecov 通常作为 GitHub Check 暴露，先从 commit check-runs 抓失败详情与链接：

```bash
gh api repos/<owner>/<repo>/commits/<sha>/check-runs \
  -H "Accept: application/vnd.github+json" \
  --jq '.check_runs[] | select(.name|test("codecov";"i")) |
       {name, conclusion, details_url, summary: .output.summary, text: .output.text}'
```

若 `summary/text` 不完整，再打开 `details_url` 并补充以下信息：

1. project/patch 状态（target vs actual）
2. 未达标阈值（例如 `patch < threshold`）
3. 关联文件或 coverage 注解

最少要提取一条"可执行结论"，例如：测试通过但覆盖率门禁失败。
