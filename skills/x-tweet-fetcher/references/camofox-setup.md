# Camofox Setup

Advanced features depend on Camofox running on `localhost:9377`.

## What Camofox is for

Use Camofox when the target needs a real browser context:

- reply threads
- user timelines
- X lists
- Google-backed discovery
- JS-heavy Chinese sites

## Install

### Option 1

```bash
openclaw plugins install @askjo/camofox-browser
```

### Option 2

```bash
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser
npm install
npm start
```

## Verify

```bash
curl http://localhost:9377/health
```

Expected response:

```json
{"status":"ok"}
```

## Operational note

If Camofox is unavailable, fall back to zero-dependency single-tweet fetches when possible and say explicitly that replies, timelines, or rendered pages could not be fetched because browser-backed mode is unavailable.
