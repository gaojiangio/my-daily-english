import requests
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def update_now():
    # 1. 抓取逻辑（这里简单演示，确保能跑通）
    try:
        res = requests.get("https://global.chinadaily.com.cn/world")
        # 这里你可以继续用之前的 BeautifulSoup 抓取逻辑
        content = "Today's latest news from China Daily." 
    except:
        content = "News content update."

    # 2. 准备新的 HTML（带翻译按钮）
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Daily English</title>
    <style>
        body {{ font-family: sans-serif; padding: 40px; line-height: 1.6; max-width: 800px; margin: auto; }}
        .btn {{ background: #2d6df6; color: white; padding: 10px 20px; border-radius: 5px; cursor: pointer; border: none; }}
        #translation {{ display: none; margin-top: 20px; color: #666; }}
    </style>
</head>
<body>
    <h1>AI Daily English Learning</h1>
    <div style="background:#f4f4f4; padding:20px; border-radius:10px;">
        <p>{content}</p>
        <button class="btn" onclick="document.getElementById('translation').style.display='block'">点击翻译</button>
        <div id="translation">这是 AI 为您生成的翻译内容。</div>
    </div>
</body>
</html>
"""
    # 3. 强制写入 index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("文件 index.html 写入完成！")

if __name__ == "__main__":
    update_now()
