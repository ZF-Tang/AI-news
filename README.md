# AI潮来

个人AI作品。用 GitHub Pages 免费发布。

仓库名：`AI-news`  
地址：https://zf-tang.github.io/AI-news/

原文 HTML 仍在 `作品/`，网站读取的是处理后的 `articles/`。

## 本地预览

打开本目录的 `index.html`，或：

```bash
python -m http.server 8080
```

访问 http://127.0.0.1:8080

## 以后加文章

1. 把新的 HTML 放到 `作品/`
2. 在 `scripts/extract_media.py` 的 `ARTICLES` 里加一条
3. 运行 `python scripts/extract_media.py`
4. 在 `index.html` 里加一张卡片
