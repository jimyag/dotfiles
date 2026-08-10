---
name: x-tweet-fetcher
description: >
  Use when you need tweets, reply threads, user timelines, or Chinese social posts for research,
  especially when you want to avoid official APIs or login requirements.
  Zero-dependency single-tweet fetches work out of the box; threads, timelines, and search need Camofox.
compatibility: Requires Python 3.10+ and uv. Replies, timelines, rendered pages, and discovery also require a running Camofox service and network access.
---

# X Tweet Fetcher

Use this skill to fetch content from X and several Chinese platforms without official APIs. Prefer the zero-dependency path for a single tweet, and switch to Camofox-backed mode only when the task needs replies, timelines, rendered pages, or discovery flows.

## Choose the path

- single public tweet: use the zero-dependency fetch path
- replies, user timelines, X lists, monitoring: use the Camofox-backed path
- WeChat / Weibo / Bilibili / CSDN and similar rendered pages: use `fetch_china.py`
- if browser-backed mode is unavailable, say so explicitly instead of pretending the richer fetch succeeded

## Actual scripts in this skill

- `scripts/fetch_tweet.py`: X tweets, replies, timelines, articles, lists, monitoring
- `scripts/fetch_china.py`: Chinese platform fetching
- `scripts/camofox_client.py`: shared browser-backed client and search helper
- `scripts/x_discover.py`: discovery-oriented workflows

## Additional resources

- For real command examples and the correct script names, see [references/usage.md](references/usage.md).
- For Camofox installation and health checks, see [references/camofox-setup.md](references/camofox-setup.md).
- For output shape and known limitations, see [references/output-and-behavior.md](references/output-and-behavior.md).

## Operating rules

- start with the cheapest path that can answer the question
- do not claim reply, timeline, or rendered-page coverage without browser-backed evidence
- preserve source URLs and key metadata when summarizing fetched content
- call out platform-imposed limits such as login-gated X articles or rate-limited rendered pages

## Output expectations

- say which mode you used: zero-dependency, Camofox-backed, or China-platform fetch
- include the fetched text or summary plus source URL
- mention important gaps such as missing replies, partial article text, or login restrictions
