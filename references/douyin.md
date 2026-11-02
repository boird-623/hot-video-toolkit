# 抖音：搜索与下载（已验证）

## 一、搜索爆款（优先用 video_search 工具）

`video_search` 工具直接按关键词检索抖音，每次返回约 20 条，字段含：
`title`、`url`（iesdouyin 分享链接）、`snippet`（口播文案）、`publish_time`、
`like_count`、`comment_count`、`cover`。

- 逐组关键词调用，snippet 用 `{"mode":"minimum","max_length":300}` 节省上下文。
- 一次搜索不足以覆盖爆款，对每个竞品词跑 3-6 组不同 query（见 SKILL 第1步）。
- 结果按 `like_count` 降序取 Top N。注意该接口是相关性排序，不是纯热榜；
  若要严格"最多点赞"，用下面的浏览器搜索并选择"最多点赞"筛选。

## 二、浏览器搜索（按点赞排序 / 翻页 / 账号主页）

全部走 `browser-use-automation`（computer_use_tool plane="bu"）。

1. 搜索页：`bu.navigate("https://www.douyin.com/search/<URL编码后的关键词>?type=video")`
2. `bu.wait_for_load()` + `bu.snapshot()`；若要求"最多点赞"，在页面筛选区点击"最多点赞"。
3. 翻页用 `bu.scroll(500,500,"down",amount=3)` 后重新 `bu.snapshot()`。
4. 用 `bu.read_all("a[href*='/video/']", fields=["text","href"], limit=50)` 批量取视频链接与标题。
5. 账号主页：`bu.navigate("https://www.douyin.com/user/<sec_uid>")`，同样滚动+`read_all` 取作品。
   不知道 sec_uid 时，先在搜索页点进该账号，或用 `video_search` 命中其作品后从 url 进入。

免登录通常能看搜索与播放；遇到登录/验证码弹窗，用 `interaction.request_action` 让用户接管。

## 三、下载视频（抓 douyinvod CDN 直链，已实测）

分享链接形如 `https://www.iesdouyin.com/share/video/<aweme_id>`，
`bu.navigate` 后会自动跳转到 `https://www.douyin.com/video/<aweme_id>`。

1. `bu.navigate(分享链接)`，`bu.wait_for_load()`，等 5-8 秒让视频开始播放（播放器需加载到流）。
2. 从网络请求里取直链：
   ```python
   reqs = bu.network_requests()
   urls = [r.get("url") for r in reqs if "douyinvod.com" in (r.get("url") or "") and "video/tos" in (r.get("url") or "")]
   url = urls[-1]  # 取最后一条（清晰度/时间最新）
   ```
   直链域名形如 `v11-weba.douyinvod.com/.../video/tos/...?mime_type=video_mp4`。
3. 直接让浏览器下载（带浏览器会话，避免鉴权问题）：
   ```python
   rec = bu.download(url, filename="抖音_账号_点赞_awemeid.mp4")
   print(rec["path"], rec["bytes"])  # 完成后 state 为 completed
   ```
4. 若 `bu.download` 失败，可让视频在页面上完整播放一遍再取最新直链；直链带签名，几分钟内有效，拿到即下。
5. `document.querySelector('video')` 在抖音页面常取不到 src（Web 播放流），不要依赖 video 元素，一律走 network_requests。
6. 下载后校验文件：读前 16 字节应为 `ftyp`，并用 ffmpeg/cv2 确认可解码、时长正确。

## 四、付费投放素材（巨量创意，仅当用户要看跑量素材）

- 入口：巨量创意 `https://cc.oceanengine.com`（创意灵感 / 热门素材 / 线索工具），可按行业、产品、关键词看高消耗素材。
- 需登录巨量引擎账号（投放账号）。登录、扫码一律 `interaction.request_action` 交接，不要自行处理。
- 素材仅展示部分，下载受平台权限限制；抓到的是素材列表与播放链接，下载仍按上面 CDN 方式，
  若页面禁止下载，只在报告里记录链接与数据，不强行抓取。

## 五、字段与命名

- 唯一标识：抖音 aweme_id（url 末段数字）。
- 候选 JSON 字段（喂给 make_hotlist.py）：
  `platform="douyin", author, title, likes, comments, plays, publish_time, url, note`。
