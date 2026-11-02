# hot-video-toolkit · 爆款短视频工具箱

> 短视频带货素材流水线：**抓爆款 → 修复/溯源 → 预审**，覆盖抖音 / 快手 / 百度好看视频三平台。
>
> Short-video ad-asset pipeline: viral capture & teardown, quality repair & origin tracing, compliance pre-review.

这是一个在豆包（Doubao）工作环境中运行的技能包（Skill），把电商短视频团队最高频的三个环节——竞品爆款分析、素材修复、合规预审——固化成标准化流程，并配套确定性脚本与统一排版规范。

## 三种模式

| 模式 | 干什么 | 固定产出 |
|---|---|---|
| 1. 抓爆款 | 多平台搜索竞品/品类/账号爆款，下载并深度拆解 | `爆款清单_<词>.md` / `爆款拆解_<词>.md` / `爆款开头方案_<词>.md` |
| 2. 修复·溯源 | 画质增强、去水印/字幕/贴纸、溯源原创作者并下载原片 | `修复成片_<id>.mp4` / `原创溯源报告_<id>.md` |
| 3. 预审 | 违禁词与违规风险扫描（广告法/食品功效/导流/价格欺诈） | `素材预审报告_<素材名>.md` |

一句话跨多个模式时（如「抓竞品爆款并下载修复、再帮我预审」），按 1→2→3 顺序串成流水线。

## 仓库结构

```
SKILL.md                    # 技能入口：模式路由、平台范围、强制规则
assets/wordlib.json         # 违禁词库（9 大类，含正则 patterns，可持续增删）
references/
  douyin.md  kuaishou.md  baidu.md   # 三平台搜索与下载的实测方法
  analysis-framework.md     # 拆解维度 + 开头钩子类型库 + 报告模板
  origin-trace.md           # 溯源方法论与置信度判定标准
  repair.md                 # 画质增强 / 叠加擦除 / 成片校验清单
  review-rules.md           # 预审规则要点与语义复核清单
  output-format.md          # 统一输出排版规范（按平台分区）
scripts/
  make_hotlist.py           # 候选汇总：去重、热度归一化、生成爆款清单
  inpaint_box.py            # 图形类贴纸逐帧擦除（OpenCV，自动合回音频）
  scan_words.py             # 确定性违禁词扫描（txt/srt/vtt/json）
```

## 使用

### 在豆包工作台中
作为用户技能安装到 `.user_skills/hot-video-toolkit/`，对话里说「抓紫苏籽油的爆款」「帮我预审这条素材」即可触发。网页采集走豆包内置浏览器自动化；视频抽帧 / ASR / OCR / 画质增强调用 byted-mediakit 工具集。

### 独立使用脚本
脚本可脱离技能环境单独运行：

```bash
# 违禁词扫描
python scripts/scan_words.py 口播.txt 字幕.srt --lib assets/wordlib.json -o 命中清单.md

# 多平台候选汇总成爆款清单
python scripts/make_hotlist.py candidates.json --keyword 紫苏籽油 --top 10

# 视频固定位置贴纸/色块擦除（先 pip install opencv-python-headless numpy imageio-ffmpeg）
python scripts/inpaint_box.py in.mp4 out.mp4 --box 0.55,0.93,0.30,0.06 --box 0.82,0.16,0.16,0.42
```

## 设计要点

- **平台差异显式建模**：抖音/快手按点赞排序、百度按播放量；快手网页版必须登录（触发登录交接而不是绕过）
- **确定性优先**：能用词库正则扫的不交给模型猜；词库命中后仍有语义复核层兜底（谐音拆字、画面暗示、隐含功效）
- **置信度分级溯源**：画面逐帧 + 口播逐句双证据才给高置信；找不到唯一原创时如实说明「疑似共享素材库」
- **产出即交付**：所有报告固定模板、按平台分区、统一字段，可直接贴回工作流

## 合规声明

- 仅用于合规自查与竞品分析；登录/验证码/滑块一律交回用户处理，不绕过平台风控
- 预审结论是自查参考，最终以抖音巨量/快手磁力/百度营销官方审核为准
- 下载的他人视频仅作分析用途并注明来源，不搬运冒充原创
