import requests
from bs4 import BeautifulSoup
import os

# 1. 从 GitHub Secrets 读取钥匙
API_KEY = os.getenv("GEMINI_API_KEY")

def ask_ai(text):
    # 【核心修正】：将 v1beta 改为 v1，这是最稳定的版本
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{
                "text": f"请将以下新闻内容改写为一段适合雅思 8.0 水平的学习材料。要求包含：1. 一段约 120 词的精简英文文章。2. 4个核心词组及其中文释义。3. 刚才那段英文文章的全文中英对照翻译。新闻原文内容：{text}"
            }]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # 如果还是不行，把错误打印得更清楚一点
            return f"AI 响应异常。完整信息：{result}"
    except Exception as e:
        return f"网络请求失败: {e}"

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
    # 构造 HTML（直接拼接字符串，避免 f-string 嵌套报错）
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
