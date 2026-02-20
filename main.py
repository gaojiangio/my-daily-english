import requests
from bs4 import BeautifulSoup
import os

# 依然读取原来的保险柜名字，但里面请填入 DeepSeek 或备用 API 的 Key
API_KEY = os.getenv("GEMINI_API_KEY")

def ask_deepseek(text):
    # 【核心改动】：使用标准的 OpenAI/DeepSeek 兼容接口
    # 如果你用的是 DeepSeek，把下面的 URL 改为 https://api.deepseek.com/chat/completions
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat", # 这里可以根据你的 API 供应商修改模型名
        "messages": [
            {"role": "system", "content": "你是一个资深的雅思教研专家。"},
            {"role": "user", "content": f"将以下新闻改写为 150 词左右的雅思 8.0 难度文章，并带 3 个核心词汇解析和全文中英翻译。原文：{text}"}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        res_json = response.json()
        return res_json['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 线路故障，请检查 API Key 是否为 DeepSeek 类型。错误：{e}"

def fetch_chinadaily_3():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get("https://global.chinadaily.com.cn/world", headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 抓取前 3 篇
        items = soup.select('.mb10.tw3_01_2 h4 a')[:3]
        results = []
        for it in items:
            link = "https:" + it['href']
            art = BeautifulSoup(requests.get(link, headers=headers).text, 'html.parser')
            body = " ".join([p.text.strip() for p in art.select('#Content p')[:4]])
            results.append({"title": it.text.strip(), "body": body})
        return results
    except:
        return []

def build_web(data_list):
    cards = ""
    for idx, item in enumerate(data_list):
        cards += f"""
        <div class="card">
            <h2 class="article-title">{idx+1}. {item['title']}</h2>
            <div class="article-content">{item['processed']}</div>
            <button class="btn" onclick="toggle({idx})">显示/隐藏 深度翻译</button>
            <div id="box-{idx}" class="trans-box">
                <p>AI 雅思教研分析加载完成。若内容未分段，请查看上方 [Translation] 标识。</p>
            </div>
        </div>
        """

    full_html = f"""
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>My Daily IELTS English</title>
    <style>
        body {{ font-family: 'PingFang SC', 'Microsoft YaHei', serif; background: #f0f2f5; max-width: 800px; margin: 50px auto; padding: 20px; }}
        .card {{ background: white; border-radius: 16px; padding: 35px; margin-bottom: 30px; box-shadow: 0 8px 30px rgba(0,0,0,0.05); }}
        .article-title {{ color: #1a73e8; border-bottom: 2px solid #e8eaed; padding-bottom: 15px; }}
        .article-content {{ font-size: 18px; line-height: 1.8; color: #3c4043; white-space: pre-wrap; }}
        .btn {{ background: #1a73e8; color: white; border: none; padding: 12px 25px; border-radius: 8px; cursor: pointer; margin-top: 20px; }}
        .trans-box {{ display: none; margin-top: 20px; padding: 20px; background: #f8f9fa; border-left: 4px solid #1a73e8; }}
    </style>
</head>
<body>
    <h1 style="text-align:center; color:#202124;">IELTS Study Hub (Stable v2.0)</h1>
    {cards}
    <script>
        function toggle(i) {{
            var el = document.getElementById('box-' + i);
            el.style.display = (el.style.display === 'none' || el.style.display === '') ? 'block' : 'none';
        }}
    </script>
</body>
</html>
"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(full_html)

if __name__ == "__main__":
    articles = fetch_chinadaily_3()
    for a in articles:
        # 给每一篇进行 AI 加工
        a['processed'] = ask_deepseek(a['body'])
    build_web(articles)
