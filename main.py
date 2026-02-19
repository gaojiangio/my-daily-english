import requests
from bs4 import BeautifulSoup

def get_news():
    # 抓取新闻原文
    res = requests.get("https://global.chinadaily.com.cn/world", headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(res.text, 'html.parser')
    first_art = soup.select_one('.mb10.tw3_01_2 h4 a')
    title = first_art.text.strip()
    return title

def update_html(title):
    # 直接重新写一个完整的 HTML，包含你要求的【翻译按钮】
    new_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily English Learning</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #fcfcfc; line-height: 1.6; }}
        .card {{ background: white; border-radius: 12px; padding: 25px; border: 1px solid #eee; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        .title-text {{ font-size: 20px; font-weight: bold; color: #2d6df6; }}
        .toggle-btn {{ background: #2d6df6; color: white; border: none; padding: 10px 18px; border-radius: 8px; cursor: pointer; margin-top: 20px; }}
        #translation {{ display: none; margin-top: 20px; padding-top: 15px; border-top: 1px dashed #ccc; color: #666; }}
    </style>
</head>
<body>
    <h1 style="text-align:center;">My Daily English News</h1>
    <div class="card">
        <h3>Today's Headlines</h3>
        <p class="title-text">{title}</p>
        <p>This is today's top story from China Daily world channel.</p>
        
        <button class="toggle-btn" onclick="toggle()">点击显示/隐藏中文翻译</button>
        
        <div id="translation">
            <p><strong>[参考翻译]</strong></p>
            <p>由于目前未接入 AI API，此处为标题参考翻译："{title}"。</p>
            <p><i>(提示：您可以在后续领到 API Key 后升级至全自动 AI 翻译版)</i></p>
        </div>
    </div>
    <script>
        function toggle() {{
            var x = document.getElementById("translation");
            x.style.display = (x.style.display === "none") ? "block" : "none";
        }}
    </script>
</body>
</html>
"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

if __name__ == "__main__":
    t = get_news()
    update_html(t)
