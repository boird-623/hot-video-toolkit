#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把多平台搜索到的候选爆款视频汇总：去重、热度归一化、按平台分组排序，生成爆款清单 Markdown。

用法:
  python make_hotlist.py candidates.json --keyword 紫苏籽油 --top 10 -o 爆款清单_紫苏籽油.md

candidates.json 是一个 JSON 数组，每个元素字段（可缺省，缺省用空/0）:
  {
    "platform": "douyin|kuaishou|baidu",
    "author": "作者",
    "title": "标题",
    "likes": 8082,            # 点赞（抖音/快手），数字或"1.2w"/"13万"字符串
    "comments": 387,
    "plays": 290000,          # 播放量（好看视频），同上
    "publish_time": "2026-07-06",
    "url": "https://...",
    "note": "备注"
  }
"""
import argparse
import json
import re
import sys
from datetime import date

PLATFORM_LABEL = {"douyin": "抖音", "kuaishou": "快手", "baidu": "百度好看视频"}
PLATFORM_ORDER = ["douyin", "kuaishou", "baidu"]


def parse_num(v):
    """把 12000 / '1.2w' / '13万' / '8082' 解析为整数；无法解析返回 0。"""
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip().replace(",", "").replace("，", "")
    if not s:
        return 0
    m = re.search(r"(\d+(?:\.\d+)?)\s*([万w亿])?", s)
    if not m:
        return 0
    n = float(m.group(1))
    unit = m.group(2)
    if unit in ("万", "w"):
        n *= 10000
    elif unit == "亿":
        n *= 100000000
    return int(n)


def heat(item):
    """热度归一化：抖音/快手用点赞，百度用播放量；没有则退而求其次。"""
    likes = parse_num(item.get("likes"))
    plays = parse_num(item.get("plays"))
    if item.get("platform") == "baidu":
        return plays if plays else likes
    return likes if likes else plays


def esc(s):
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="候选结果 JSON 文件")
    ap.add_argument("--keyword", default="", help="竞品/产品名，用于标题")
    ap.add_argument("--top", type=int, default=10, help="每平台取前 N，默认 10")
    ap.add_argument("-o", "--output", default="", help="输出 Markdown 路径")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, list):
        sys.exit("输入 JSON 必须是数组")

    # 去重（按 url，其次 平台+标题）
    seen, items = set(), []
    for it in data:
        key = (it.get("url") or "").strip() or f"{it.get('platform')}|{it.get('title')}"
        if key in seen:
            continue
        seen.add(key)
        items.append(it)

    groups = {}
    for it in items:
        groups.setdefault(it.get("platform", "other"), []).append(it)

    lines = []
    kw = f"：{args.keyword}" if args.keyword else ""
    lines.append(f"# 竞品爆款清单{kw}（{date.today()}）")
    lines.append("")
    lines.append("> 口径：抖音/快手按点赞、百度好看视频按播放量；为采集时点近似值，非官方热榜。")
    lines.append("")
    total = 0
    for plat in PLATFORM_ORDER + [p for p in groups if p not in PLATFORM_ORDER]:
        arr = groups.get(plat)
        if not arr:
            continue
        arr.sort(key=heat, reverse=True)
        arr = arr[: args.top]
        total += len(arr)
        label = PLATFORM_LABEL.get(plat, plat)
        lines.append(f"## {label}")
        if plat == "baidu":
            lines.append("| 排名 | 作者 | 标题 | 播放量 | 发布时间 | 链接 | 备注 |")
            lines.append("|---|---|---|---|---|---|---|")
            for i, it in enumerate(arr, 1):
                plays = it.get("plays")
                heat_s = f"{parse_num(plays):,}" if parse_num(plays) else "-"
                lines.append(f"| {i} | {esc(it.get('author'))} | {esc(it.get('title'))} | {heat_s} "
                             f"| {esc(it.get('publish_time'))} | {esc(it.get('url'))} | {esc(it.get('note'))} |")
        else:
            lines.append("| 排名 | 作者 | 标题 | 点赞 | 评论 | 发布时间 | 链接 | 备注 |")
            lines.append("|---|---|---|---|---|---|---|---|")
            for i, it in enumerate(arr, 1):
                likes = parse_num(it.get("likes"))
                comments = parse_num(it.get("comments"))
                lines.append(f"| {i} | {esc(it.get('author'))} | {esc(it.get('title'))} "
                             f"| {likes or '-'} | {comments or '-'} | {esc(it.get('publish_time'))} "
                             f"| {esc(it.get('url'))} | {esc(it.get('note'))} |")
        lines.append("")

    out = "\n".join(lines)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"已写入 {args.output}（去重后 {len(items)} 条，入选 {total} 条）")
    else:
        print(out)


if __name__ == "__main__":
    main()
