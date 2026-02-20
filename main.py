import requests
from bs4 import BeautifulSoup
import os

# 1. 读取你已经启用成功的 API Key
API_KEY = os.getenv("GEMINI_API_KEY")

def get_news_links():
    """抓取 World 频道前三篇新闻链接"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get("https://global.chinadaily.com.cn/world", headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 提取前 3 个新闻链接
        links = ["https:" + a['href'] for a in soup.select('.mb10.tw3_01_2 h4 a')[:3]]
        return links
    except:
        return []

def get_content(url):
    """进入文章页面抓取正文"""
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        paragraphs = soup.select('#Content p')
        return " ".join([p.text.strip() for p in paragraphs[:3]])
    except:
        return ""

def ask_ai(text):
    # 采用 v1beta 路径，这是目前兼容性最强的路径
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"请将以下内容改写为一篇雅思 8.0 水平的英语学习短文（约 150 词），带 3 个重点词组解析和全文翻译。原文：{text}"
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # 【核心修改】：如果出错了，直接把 AI 说的原话吐出来，方便我们排错
            return f"API 连接成功但未返回内容。服务器回复：{result}"
    except Exception as e:
        return f"网络连接故障: {str(e)}"

def build_web(results):
    """生成三卡片结构的网页"""
    cards = ""
    for i, content in enumerate(results):
        cards += f"""
        <div class="card">
            <h2>Reading Material {i+1}</h2>
            <div class="eng-box">{content}</div>
            <button class="btn" onclick="toggle({i})">查看深度翻译 / Toggle Analysis</button>
            <div id="box-{i}" class="trans-box">
                <p>AI 解析加载成功，请查阅上方生成的 Vocabulary 与 Translation 部分。</p>
            </div>
        </div>"""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Daily IELTS English Hub</title>
    <style>
        body {{ font-family: 'Georgia', serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #f4f7f6; line-height: 1.8; }}
        .card {{ background: white; border-radius: 15px; padding: 30px; margin-bottom: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
        .eng-box {{ font-size: 18px; color: #2c3e50; white-space: pre-wrap; }}
        .btn {{ background: #3498db; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; margin-top: 20px; font-weight: bold; }}
        .trans-box {{ display: none; margin-top: 20px; padding: 20px; background: #fdfdfd; border-left: 5px solid #3498db; font-style: italic; color: #7f8c8d; }}
    </style>
</head>
<body>
    <h1 style="text-align:center; color:#2c3e50; margin-bottom:50px;">Personal IELTS Study Hub</h1>
    {cards}
    <script>
        function toggle(id) {{
            var x = document.getElementById("box-" + id);
            x.style.display = (x.style.display === "none" || x.style.display === "") ? "block" : "none";
        }}
    </script>
</body>
</html>"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    links = get_news_links()
    final_outputs = []
    for link in links:
        raw = get_content(link)
        if raw:
            processed = ask_ai(raw)
            final_outputs.append(processed)
    build_web(final_outputs)
