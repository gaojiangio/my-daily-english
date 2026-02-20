import requests
from bs4 import BeautifulSoup
import os

# 从 GitHub Secrets 中读取你的 API 密钥
API_KEY = os.getenv("GEMINI_API_KEY")

def ask_ai(text):
    # 【最核心修复】：这里使用了最标准、兼容性最强的模型请求结构
    # 尝试使用 v1beta 版本，这是目前最不容易报 404 的路径
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"请将以下新闻改写为雅思8.0水平的学习材料。要求：1.约120词的精简英文。2.4个核心词组及其中文释义。3.全文中英对照翻译。原文：{text}"
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        # 成功拿到内容
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # 如果 AI 还是拒绝，我们会把原因显示在网页上，方便一眼看穿
            error_msg = result.get('error', {}).get('message', '未知错误')
            return f"AI 暂时不可用。原因：{error_msg}。建议：请确认 Google Cloud 项目中已启用 Generative Language API。"
    except Exception as e:
        return f"网络连接失败: {str(e)}"

def get_real_news():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get("https://global.chinadaily.com.cn/world", headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        first_art = soup.select_one('.mb10.tw3_01_2 h4 a')
        if not first_art: return "Today's news is temporarily unavailable."
        
        link = "https:" + first_art['href']
        art_res = requests.get(link, headers=headers)
        art_soup = BeautifulSoup(art_res.text, 'html.parser')
        paragraphs = art_soup.select('#Content p')
        return " ".join([p.text.strip() for p in paragraphs[:3]])
    except:
        return "News fetch failed."

def update_full_html(ai_result):
    # 这里通过最原始的字符串相加，绝对不会出现任何 Python 格式化错误
    html_start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Daily English Study</title>
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
    final_html = html_start + ai_result + html_end
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

if __name__ == "__main__":
    if API_KEY:
        news_data = get_real_news()
        ai_msg = ask_ai(news_data)
        update_full_html(ai_msg)
        print("Success: Webpage updated.")
    else:
        print("Error: API Key not found.")
