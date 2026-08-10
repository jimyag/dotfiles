# Usage

## Core commands

Use the actual scripts in this directory:

```bash
# Single tweet; uv reads the script's PEP 723 metadata
uv run scripts/fetch_tweet.py --url "https://x.com/user/status/123456"
uv run scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --text-only
uv run scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --pretty

# Tweet with replies, requires Camofox
uv run scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --replies

# User timeline, requires Camofox
uv run scripts/fetch_tweet.py --user <username> --limit 300

# Long-form article, requires Camofox and may still be limited by X login requirements
uv run scripts/fetch_tweet.py --article "https://x.com/i/article/..."

# X list, requires Camofox
uv run scripts/fetch_tweet.py --list "<list_url_or_id>"

# Mention monitoring, requires Camofox
uv run scripts/fetch_tweet.py --monitor "@username"
```

## Chinese platforms

```bash
python3 scripts/fetch_china.py --url "https://weibo.com/..."
python3 scripts/fetch_china.py --url "https://bilibili.com/..."
python3 scripts/fetch_china.py --url "https://csdn.net/..."
python3 scripts/fetch_china.py --url "https://mp.weixin.qq.com/..."
```

Current support:

- WeChat articles: direct fetch path available
- Weibo: rendered via Camofox
- Bilibili: rendered via Camofox
- CSDN: rendered via Camofox
- Xiaohongshu: partial support, often needs login context

## From Python

```python
from scripts.camofox_client import camofox_search

results = camofox_search("your search query")
```

Use `scripts/x_discover.py` when you need to explore mentions or discovery-oriented workflows beyond a single fetch.

```bash
uv run scripts/x_discover.py --keywords "AI Agent,automation" --limit 5
uv run scripts/sogou_wechat.py --keyword "AI Agent" --limit 3 --resolve --json
```
