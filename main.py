import requests
from bs4 import BeautifulSoup
import os

# 1. 从 GitHub Secrets 读取钥匙
API_KEY = os.getenv("GEMINI_API_KEY")

def ask_ai(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    prompt = (
        f"请将以下新闻内容改写为一段适合雅思 8.0 水平的学习材料。要求包含：\n"
        f"1. 一段约 120 词的精简英文文章。\n"
        f"2. 4个核心词组及其中文释义。\n"
        f"3. 刚才那段英文文章的全文中英对照翻译。\n"
        f"新闻原文内容：{text}"
    )
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=data)
        result = response.json()
        if 'candidates' in result:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"AI 拒绝了请求。详细回复内容：{result}"
    except Exception as e:
        return f"网络连接出错: {e}"

def get_real_news():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get("https://global.chinadaily.com.cn/world", headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        first_link = "https:" + soup.select_one('.mb10.tw3_01_2 h4 a')['href']
        art_res = requests.get(first_link, headers=headers)
        art_soup = BeautifulSoup(art_res.text, 'html.parser')
        paragraphs = art_soup.select('#Content p')
        return " ".join([p.text.strip() for p in paragraphs[:3]])
    except:
        return "Unable to fetch news content today."

def update_full_html(ai_result):
    # 构造 HTML 内容（注意：这里我避开了可能导致报错的 f-string 嵌套）
    html_start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily English Study | AI Editor</title>
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #fcfcfc; line-height: 1.8; }
        .card { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; }
        .ai-text { font-size: 18px; white-space: pre-wrap; color: #333; margin-bottom: 25px; }
        .btn { background: #2d6df6; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        #analysis { display: none; margin-top: 25px; padding-top: 20px; border-top: 2px dashed #eee; }
    </style>
</head>
<body>
    <h1 style="text-align:center; color:#2d6df6;">IELTS Daily Learning Hub</h1>
    <div class="card">
        <h3>Today's Intensive Reading</h3>
        <div class="ai-text">"""
    
    html_end = """</div>
        <button class="btn" onclick="toggle()">显示/隐藏 详细分析与翻译</button>
        <div id="analysis">
            <p style="color: #888; font-size: 14px;">💡 AI 实时解析 (Powered by Gemini)</p>
        </div>
    </div>
    <script>
        function toggle() {
            var x = document.getElementById("analysis");
            x.style.display = (x.style.display === "none" || x.style.display === "") ? "block" : "none";
        }
    </script>
</body>
</html>
"""
    # 直接通过加号拼接字符串，绝对不会报错
    final_html = html_start + ai_result + html_end
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

if __name__ == "__main__":
    if API_KEY:
        news_data = get_real_news()
        ai_msg = ask_ai(news_data)
        update_full_html(ai_msg)
        print("全功能 AI 网页已成功更新！")
    else:
        print("未检测到 API Key，请检查 GitHub Secrets 配置。")
