# 观测

个人文章页。站点名 **观测**，署名 **观测**。用 GitHub Pages 免费发布。

原文 HTML 仍在 `作品/`，网站读取的是处理后的 `articles/`。

仓库名：`notes`

## 本地预览

打开本目录的 `index.html`，或：

```bash
python -m http.server 8080
```

访问 http://127.0.0.1:8080

## 发布到 GitHub Pages

1. 在 GitHub 新建公开仓库 `notes`
2. 上传这些内容（不要传 `作品/`）：
   - `index.html`
   - `styles.css`
   - `.nojekyll`
   - `articles/`
   - `README.md`（可选）
3. 仓库 **Settings → Pages**
4. Source 选 **Deploy from a branch**，分支 `main`，目录 `/ (root)`
5. 地址：https://zf-tang.github.io/notes/

## 以后加文章

1. 把新的 HTML 放到 `作品/`
2. 在 `scripts/extract_media.py` 的 `ARTICLES` 里加一条
3. 运行 `python scripts/extract_media.py`
4. 在 `index.html` 里加一张卡片
