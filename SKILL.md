---
name: hot-video-toolkit
description: 短视频带货一站式素材流水线，覆盖抖音、快手、百度好看视频（默认三平台都做，除非用户明确指定单个平台；不做微信视频号）。三类任务：①抓取竞品/产品/品类或竞品账号的爆款视频，下载并深度拆解，产出爆款开头/前3秒钩子（说"抓爆款、搜爆款素材、找竞品怎么拍、对标账号、爆款开头、爆款钩子"时）；②给爆款视频链接或本地文件修复画质、去噪超分、去水印/字幕/贴纸、溯源原创作者并下载原片（说"修复画质、提高清晰度、超分、去噪、去水印、找原创、找原作者、原视频是谁的、下载原片"时）；③给待投放视频或口播/标题文案做违禁词与违规风险预审（说"素材预审、违禁词、敏感词、广告法极限词、能不能过审、抖音快手百度合规检查"时）。所有抓取与分析结果默认按平台分区、统一表格格式排版。
---

# 爆款短视频工具箱（抖音 / 快手 / 百度）

一个技能串起短视频带货素材流水线：**抓爆款 → 修复/溯源 → 预审**。按用户意图进入对应模式。

## 平台范围与默认规则（先读）

- 默认平台：**抖音 + 快手 + 百度（好看视频）** 三个都做。
- **仅当用户明确指定平台时才只做指定平台**（如"只看抖音""快手的就行"）。
- 模式 2（修复/溯源）、模式 3（预审）若给的是具体链接或文件，平台由该素材本身决定；
  涉及平台规则（尤其预审）时，按素材投放平台或三平台通用规则给结论。
- 不做微信视频号。

## 三种模式路由

| 用户意图 | 模式 | 输入 | 核心参考 |
|---|---|---|---|
| 抓爆款/对标/爆款开头 | 模式1 | 竞品词、产品名、品类、账号名 | 三平台文档 + `analysis-framework.md` |
| 修复画质/去水印/找原创/下原片 | 模式2 | 视频链接或本地文件 | `repair.md` + `origin-trace.md` |
| 违禁词/过审检查 | 模式3 | 视频或文案 | `review-rules.md` + `assets/wordlib.json` |

一句话跨多个模式时（如"抓竞品爆款并下载修复、再帮我预审"），按 1→2→3 顺序串成流水线。

## 模式 1：抓爆款 + 深度拆解 + 开头方案

默认每平台 Top 10（用户可增减），口径：抖音/快手按点赞、百度按播放量；付费跑量素材路径见各平台文档。

1. **扩搜索词**：产品/品牌名 + 卖点痛点 + 人群场景，共 3-6 组；给账号名则进主页。
2. **逐平台搜索**：
   - 抖音：`video_search` 工具 + 浏览器（见 `references/douyin.md`）。
   - 快手：浏览器网页版（**必须先让用户扫码登录**，见 `references/kuaishou.md`）。
   - 百度：好看视频搜索免登录（见 `references/baidu.md`）。
3. **汇总筛选**：候选整理成 JSON，用 `scripts/make_hotlist.py` 去重、热度归一化、按平台排序。
4. **下载 Top**：按三平台文档（抖音 douyinvod、快手 doubao-video-extract、百度 vdept 直链）。
5. **深度拆解**：加载 `byted-mediakit-video`，抽帧/ASR/画面理解，按 `references/analysis-framework.md`。
6. **产出开头**：3-5 个可直接拍摄的开头脚本（钩子类型+前3秒分镜+口播+借鉴链接）。
   要直接生成视频再加载 `doubao-creative-video`，不在本技能内直接生成。

## 模式 2：修复画质 + 溯源原创 + 下载原片

1. **获取文件**：链接按平台文档下载（`references/douyin.md`/`kuaishou.md`/`baidu.md`），本地文件直接用。
2. **画质修复**：加载 `byted-mediakit-video`，`enhance-video` 默认 `standard --scene ugc --resolution 1080p --bitrate-level high`，要更高出 2K；细节见 `references/repair.md`。
3. **去叠加（可选）**：文字类用 `erase-video-subtitle-pro`；图形色块/贴纸用 `scripts/inpaint_box.py` 本地逐帧修复；
   产品标签、包装、衣物印花必须保留。
4. **溯源**：抽关键帧 `visual_search` 反搜 + 口播金句 `video_search`/`general_search` + 跨平台比对，
   方法与置信度判定见 `references/origin-trace.md`；只给有证据的候选，不臆断唯一原创。
5. **下原片**：用户确认或高置信后按平台方法下载最高清原片。

## 模式 3：素材预审（违禁词/违规）

1. 加载 `byted-mediakit-video`：`asr-subtitles` 取口播、`video-ocr` 取画面文字，连同用户标题文案。
2. 确定性扫描：`scripts/scan_words.py <文本...> --lib assets/wordlib.json`，输出命中词/时间点/等级/依据/建议。
3. 语义复核：按 `references/review-rules.md` 补查隐含功效、谐音拆字、画面暗示、不当背书。
4. 产品类目默认普通食品（功效红线从严）；保健食品/其他类目需用户说明。
5. 结论是自查参考，最终以抖音巨量/快手磁力/百度营销官方审核为准。

## 统一输出排版（所有模式都要遵守）

- 所有产出按**平台分节**（抖音 / 快手 / 百度），平台内用统一字段的表格，格式见 `references/output-format.md`。
- 固定产出物：`爆款清单_<词>.md`、`爆款拆解_<词>.md`、`爆款开头方案_<词>.md`、
  `原创溯源报告_<id>.md`、`素材预审报告_<素材名>.md`、成片与原片 mp4、`downloads/`。
- 每份报告开头注明平台、口径、采集时间、数据为近似值（非官方热榜）。

## 强制规则

- 登录/扫码/验证码/滑块：立即 `interaction.request_action`（type=browserControl）让用户接管，不绕过。
- 网页采集一律走 `browser-use-automation`（plane="bu"），不写爬虫、不拼接口；平台改版时重新 `snapshot` 定位。
- 只做合规自查与竞品分析，不编造资质/账号/链接；下载的他人视频注明来源，不冒充原创。
- 视频成片默认 H.264、30fps、保留原音频；交付前抽帧目检 + 元数据核验（分辨率/帧率/时长/音频）。
- 云端异步任务用 `query-task` 轮询，running 且 exit 0 是预期，用同一 task_id 续查。

## 资源索引

- 三平台：`references/douyin.md`、`references/kuaishou.md`、`references/baidu.md`（搜索/下载/付费素材入口）
- 模式1：`references/analysis-framework.md`（拆解维度+钩子库+报告模板）、`scripts/make_hotlist.py`
- 模式2：`references/repair.md`（增强/擦除/校验）、`references/origin-trace.md`（溯源）、`scripts/inpaint_box.py`
- 模式3：`references/review-rules.md`（规则/语义复核/报告模板）、`assets/wordlib.json`、`scripts/scan_words.py`
- 排版：`references/output-format.md`（统一按平台分区的格式）
