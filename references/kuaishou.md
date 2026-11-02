# 快手：搜索与下载（已验证）

## 一、关键前提：网页版搜索必须登录

已实测：未登录打开快手搜索页，结果区为空（页面显示"登录即可享受更懂你的优质内容"，
`read_all` 取到 0 个视频卡片）。

因此快手流程第一步是登录交接：
1. `bu.navigate("https://www.kuaishou.com/search/video?searchKey=<关键词>")`。
2. 确认出现登录引导（`"登录即可享受" in bu.get_page_text()` 或 blocked 标记），
   立即 `interaction.request_action`（type=browserControl），请用户扫码/验证码登录快手。
3. 用户交回后重新 `bu.snapshot()` 确认结果区出现视频卡片，再继续。
4. 登录态在后续快手抓取中通常可复用，无需每条都登录。

## 二、搜索与结果提取（browser-use-automation）

1. 搜索页 URL：`https://www.kuaishou.com/search/video?searchKey=<URL编码关键词>`
   - 视频搜索：`/search/video`；用户/账号搜索：`/search/user`（页面顶部有"视频/用户"切换）。
2. 逐组关键词跑（同 SKILL 第1步）；翻页用 `bu.scroll(...)` 后重新观察。
3. 结果卡片提取（登录后选择器可能随改版变化，先用 `bu.snapshot()` 核对，再用 `read_all`）：
   ```python
   rows = bu.read_all("a[href*='/short-video/'], a[href*='/fw/photo/'], div[class*='video-item']",
                      fields=["text","href"], limit=50)
   ```
   卡片文本含封面标题、作者名、点赞数（形如"1.2w"）；href 含作品 id。
4. 账号主页：`https://www.kuaishou.com/profile/<user_id>`，滚动 + `read_all` 取作品列表。
5. 按点赞（注意"w/万"换算）降序取 Top N。

## 三、下载（用 doubao-video-extract，官方支持快手）

快手是 `doubao-video-extract` 技能明确支持的平台，不要用浏览器硬抓，优先走其统一入口：

1. 先 `Read` `doubao-video-extract/SKILL.md`（含快手），按其说明把工作目录切到该 skill 根目录。
2. 只下载视频（不进妙记/转写）：
   ```bash
   python3 scripts/minutes/social_video_to_minutes.py "<快手作品链接或分享文本>" --media-mode video
   ```
   - 支持 `v.kuaishou.com` 分享短链、`www.kuaishou.com/short-video/<id>` 等页面链接。
   - 先排障可加 `--check --json`。
3. 该脚本会返回保存路径与标题/作者/时长等元信息；记录实际输出目录，
   下载后按 `快手_账号_点赞_作品id.mp4` 重命名到 `downloads/`。
4. 若统一入口失败：先 `--check --json`，再按 SKILL 用快手 downloader 的 `--print-url --json` 取直链，
   不要手工拼快手接口或写爬虫。
5. 登录态/风控导致失败时，交回浏览器让用户完成验证，不要绕过。

## 四、付费投放素材（磁力引擎，仅当用户要看跑量素材）

- 入口：磁力引擎/磁力创意（快手广告平台）的素材/创意灵感，需要投放账号登录。
- 登录与下载受限处理方式同抖音巨量创意：记录素材链接与数据，不强行抓取。

## 五、字段与命名

- 唯一标识：快手作品 id（url 中 `/short-video/<id>` 的数字段）。
- 候选 JSON 字段（喂给 make_hotlist.py）：
  `platform="kuaishou", author, title, likes, comments, plays, publish_time, url, note`。
- 点赞数字会带"w/万"，汇总前统一换算为整数（如 1.2w=12000）。
