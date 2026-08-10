#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


PATTERNS: list[tuple[str, str]] = [
    ("chatbot residue", r"\b(let'?s dive in|i hope this helps|let me know|of course|certainly)\b|当然|希望这.*帮助"),
    ("chat ui artifact", r"turn\d+search\d+|citeturn\d+search\d+|oai_citation|:contentReference\[|contentReference\[oaicite|\[web:\d+\]|\[attached_file:\d+\]|utm_source=(chatgpt\.com|claude\.ai|copilot\.com|openai)|referrer=grok\.com|grok_card"),
    ("placeholder leakage", r"\[(INSERT NAME|YEAR|COMPANY|INDUSTRY|TODO|TBD)\]|20\d\d-xx-xx"),
    ("cutoff disclaimer", r"\b(as of my last update|i don'?t have access to real-time|specific details are limited|based on available information)\b"),
    ("speculative gap filling", r"\b(believed to have|likely began|appears to have|maintains a relatively low public profile)\b"),
    ("stock transition", r"值得注意的是|总的来说|换句话说|不难看出|可以发现|\b(in conclusion|it is important to note|at its core|key takeaway)\b"),
    ("collaborative lecturer voice", r"接下来我们|我们先来看|下面我们|希望这能帮助你|\b(here'?s what i mean|think about it|this is why|what makes this hard is)\b"),
    ("lecture action phrase", r"拆一拆|盘一盘|捋一捋|聊一聊|划重点|说白了|本质上|归根结底"),
    ("dramatic reveal", r"遮羞布|面具|外衣|揭开.*真面目|戳穿.*真相"),
    ("pseudo academic jargon", r"底层逻辑|宏大叙事|舆论场|赛道|闭环|抓手"),
    ("conditional stack", r"一旦.*就|只有.*才|无论.*都|通过.*来"),
    ("significance inflation", r"重要意义|关键一步|体现了.*重要性|\b(pivotal|crucial|vital|testament|evolving landscape|broader trend)\b"),
    ("promotional language", r"赋能|助力|革命性|颠覆性|全方位|\b(seamless|robust|groundbreaking|world-class|cutting-edge|vibrant)\b"),
    ("vague authority", r"业内人士|专家指出|研究表明|有观点认为|\b(industry reports|experts argue|research suggests|observers have)\b"),
    ("vague endorsement", r"\bworth (reading|paying attention to|a look|exploring|checking out|your time)\b"),
    ("hedge stacking", r"\b(could potentially|may eventually|might ultimately)\b"),
    ("future narrative closer", r"\b(poised to become|could become .* defining|may become .* important|next major chapter)\b"),
    ("real actual inflation", r"\b(real|actual|genuine|true) (utility|product-market fit|tokenomics|sustainability|impact|innovation)\b"),
    ("fake balance", r"不仅.*而且|不是.*而是|既.*也|\b(not just .* but|on the one hand|on the other hand)\b"),
    ("generic ending", r"未来可期|值得持续关注|这只是开始|\b(exciting times ahead|the future looks bright)\b"),
    ("post-action summary", r"\b(to recap|in summary|here'?s what was covered|final thoughts|key takeaways)\b|总结一下"),
    ("didactic disclaimer", r"\b(as always, consult|be mindful that|please ensure|ethical implications)\b|请确保|请注意"),
    ("superficial ing", r"\b(highlighting|underscoring|showcasing|reflecting|fostering|emphasizing)\b"),
    ("copula avoidance", r"\b(serves as|stands as|boasts|features)\b|充当了|构成了"),
    ("false agency", r"\b(the data tells us|the market rewards|the decision emerges|the culture shifts|the conversation moves)\b"),
    ("dramatic fragmentation", r"\b(that'?s it|not always\. not perfectly|not a .* not a .* a .*)\b"),
    ("lazy extreme", r"\b(always|never|everyone|everybody|nobody|the only)\b"),
    ("hashtag stuffing", r"(?:#[\w-]+\s*){6,}"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan one UTF-8 text file for common AI-writing smell patterns."
    )
    parser.add_argument("file", type=Path, help="UTF-8 text or Markdown file to scan")
    return parser.parse_args()


def main() -> int:
    path = parse_args().file
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    findings: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(lines, 1):
        for label, pattern in PATTERNS:
            if re.search(pattern, line, flags=re.IGNORECASE):
                findings.append((lineno, label, line.strip()))

    if not findings:
        print("No common AI-writing smell patterns found.")
        return 0

    for lineno, label, line in findings:
        preview = line[:180] + ("..." if len(line) > 180 else "")
        print(f"{path}:{lineno}: {label}: {preview}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
