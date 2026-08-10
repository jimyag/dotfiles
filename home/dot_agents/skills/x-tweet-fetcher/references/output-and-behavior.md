# Output And Behavior

## What zero-dependency fetches cover

- regular tweets
- long tweets
- quoted tweets
- basic engagement stats
- media URLs

## What browser-backed fetches add

- reply trees
- user timelines
- X lists
- Google-style discovery
- JS-rendered Chinese platform content

## Output shape

Typical tweet output includes:

```json
{
  "url": "https://x.com/user/status/123",
  "username": "user",
  "tweet_id": "123",
  "tweet": {
    "text": "Tweet content...",
    "author": "Display Name",
    "screen_name": "username",
    "likes": 100,
    "retweets": 50,
    "views": 10000
  },
  "replies": []
}
```

Exact fields vary by mode. When summarizing results for a user, prefer:

- primary text
- author / handle
- created time if available
- engagement counts if they matter
- linked URLs or media when relevant to the task

## Limitations

- some X article pages still require login for full text
- some Chinese platforms degrade or block anonymous scraping
- reply/timeline coverage depends on browser-backed rendering success
- discovery workflows may be rate-limited by upstream pages
