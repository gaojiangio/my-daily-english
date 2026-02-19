import requests
from bs4 import BeautifulSoup
import os

# 从 GitHub Secrets 中读取 API 密钥
API_KEY = os.getenv("GEMINI_API_KEY")

def ask_ai(text):
    # 【核心修正】采用 v1beta 路径，这是目前对新账号最友好的接口
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"请将以下新闻内容改写为一段雅思 8.0 水平的学习材料。要求包含：1. 一段约 120 词的精简英文文章。2. 4个核心词组及其中文释义。3. 刚才那段英文文章的全文中英对照翻译。新闻原文内容：{text}"}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        # 严谨的提取逻辑，防止因接口返回空值导致脚本崩溃
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # 提取具体的错误消息
            error_detail = result.get('error', {}).get('message', '未知原因')
            return f"AI 暂时无法处理请求。原因：{error_detail}。提示：请检查 API Key 是否已在 Google Cloud 项目中启用 Gemini API。"
    except Exception as e:
        return f"网络连接故障: {str(e)}"

def get_real_news():
    # 抓取 China Daily 国际频道最新新闻
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get("https://global.chinadaily.com.cn/world", headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 提取第一篇文章的链接
        first_art = soup.select_one('.mb10.tw3_01_2 h4 a')
        if not first_art:
            return "No news found today."
        
        link = "https:" + first_art['href']
        # 抓取正文
        art_res = requests.get(link, headers=headers)
        art_soup = BeautifulSoup(art_res.text, 'html.parser')
        paragraphs = art_soup.select('#Content p')
        return " ".join([p.text.strip() for p in paragraphs[:3]])
    except:
        return "Unable to fetch news content today."

def update_full_html(ai_result):
    # 采用最稳妥的字符串拼接，杜绝所有格式化报错
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
            if (x.style.display === "none" || x.style.display === "") {
                x.style.display = "block";
            } else {
                x.style.display = "none";
            }
        }
    </script>
</body>
</html>
"""
    # 拼接并写入文件
    final_html = html_start + ai_result + html_end
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

if __name__ == "__main__":
    if API_KEY:
        news_data = get_real_news()
        ai_msg = ask_ai(news_data)
        update_full_html(ai_msg)
        print("网页已更新，请检查 index.html 内容。")
    else:
        print("未检测到 API Key，请检查 GitHub Secrets。")
