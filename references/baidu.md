# 百度（好看视频 / 百度营销）：搜索与下载（已实测）

百度自然短视频主要在**好看视频**；付费投放素材在**百度营销创意中心**。

## 一、好看视频搜索（免登录，已实测）

1. 搜索页（注意是 `/web/search/page`，不是 `/web/search`）：
   ```
   https://haokan.baidu.com/web/search/page?query=<URL编码关键词>
   ```
   用 `bu.navigate(...)` 打开，`bu.wait_for_load()` 后等 3-4 秒。
   也可从首页 `https://haokan.baidu.com` 顶部搜索框 `bu.type(..., submit=True)` 进入。
2. 无需登录即可搜索与播放。
3. 逐组关键词跑；翻页用 `bu.scroll(...)` 后重新观察。
4. 结果批量提取（已实测可用）：
   ```python
   rows = bu.read_all("a[href*='vid=']", fields=["text","href"], limit=30)
   ```
   - `href` 形如 `https://haokan.baidu.com/v?vid=<视频id>`。
   - `text` 一段内含：时长、标题、发布时间（如"8个月前"）、播放量（如"13万次播放"）、视频作者。
   - 解析这段文本拆出 title/plays/author/publish_time；播放量"万/亿"换算为整数。
5. 百度爆款口径：**按播放量（plays）降序**，好看视频网页不直接展示点赞数。
6. 账号主页可从搜索结果点作者名进入，或搜索"视频作者"。

## 二、下载（抓 vdept.bdstatic.com 直链，已实测）

1. 打开播放页：`bu.navigate("https://haokan.baidu.com/v?vid=<vid>")`，`bu.wait_for_load()`。
2. 触发播放（打开后不一定自动播，点一次播放区）：`bu.click_xy(500, 400)`，等 5 秒。
3. 从网络请求取 mp4 直链（已实测域名是百度 VOD `vdept*.bdstatic.com`）：
   ```python
   reqs = bu.network_requests()
   urls = [r.get("url") for r in reqs
           if "bdstatic.com" in (r.get("url") or "") and ".mp4" in (r.get("url") or "")]
   url = urls[-1]
   ```
   直链形如：
   `https://vdept3.bdstatic.com/mda-xxx/540p/h264_.../mda-xxx.mp4?auth_key=...&vid=<vid>`
4. 浏览器下载：
   ```python
   rec = bu.download(url, filename="百度_作者_播放量_vid.mp4")
   print(rec["path"], rec["state"], rec["bytes"])
   ```
5. 清晰度：默认抓到的是"标清 360P"（路径里 540p、日志标 360P）。需要高清时，
   在播放器清晰度菜单切到 720P/1080P 后重新 `bu.network_requests()` 取最新 mp4 直链；
   高清可能要求登录或 App，受阻则交回用户或保留标清并在报告注明。
6. 直链 `auth_key` 有时效，拿到即下；失败重新播放再抓。
7. 播放页是 Next.js 客户端渲染，`http_get` 只能拿到空壳 HTML（无 mp4），
   `bu.js` 读页面数据在本环境可能返回空；**一律以 network_requests 抓到的 mp4 为准**。
8. 下载后读前 16 字节应为 `ftyp`，并确认可解码、时长正确。

## 三、付费投放素材（百度营销创意中心，仅当用户要看跑量素材）

- 入口：百度营销创意中心 `https://chuangyi.baidu.com`（创意/信息流素材灵感），按行业、产品、关键词看跑量素材。
- 需登录百度营销账号；登录/扫码一律 `interaction.request_action` 交接。
- 素材下载受平台权限限制，抓不到就记录链接与数据，不强行抓取。

## 四、字段与命名

- 唯一标识：好看视频 vid（url 中 `vid=` 后的数字）。
- 候选 JSON 字段（喂给 make_hotlist.py）：
  `platform="baidu", author, title, likes=None, comments=None, plays=<播放量>, publish_time, url, note`。
  （好看视频用 plays，点赞/评论可留空，排序时按热度字段统一归一化。）
