import requests
from bs4 import BeautifulSoup
import os

# 1. 从 GitHub 的“保险柜”（Secrets）里读取你的 API 钥匙
API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(text):
    # 调用 Gemini AI 模型的接口
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    # 我们给 AI 的具体学习任务指令
    prompt = (
        f"请将以下新闻内容改写为一段适合雅思 8.0 水平的学习材料。要求包含以下部分：\n"
        f"1. 一段约 120 词的精简英文文章。\n"
        f"2. 4个核心词组及其中文释义。\n"
        f"3. 刚才那段英文文章的全文中英对照翻译。\n"
        f"新闻原文内容：{text}"
    )
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        # 向 AI 发送请求
        response = requests.post(url, json=data)
        # 解析 AI 返回给我们的文字
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"AI 暂时休息了，请检查密钥或稍后再试。错误信息：{e}"

def get_latest_news():
    # 抓取 China Daily 国际新闻频道
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get("https://global.chinadaily.com.cn/world", headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 定位第一篇新闻的网址
    first_link = "https:" + soup.select_one('.mb10.tw3_01_2 h4 a')['href']
    
    # 爬取该新闻的正文内容
    art_res = requests.get(first_link, headers=headers)
    art_soup = BeautifulSoup(art_res.text, 'html.parser')
    paragraphs = art_soup.select('#Content p')
    # 提取前三段作为 AI 的分析素材
    return " ".join([p.text.strip() for p in paragraphs[:3]])

def generate_final_html(ai_content):
    # 构建最终显示在网页上的代码，包含你要求的【翻译按钮】功能
    new_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Daily English Learning | IELTS 8.0</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #fcfcfc; color: #1a1a1a; line-height: 1.8; }}
        .title {{ text-align: center; font-size: 28px; font-weight: 700; margin-bottom: 40px; color: #2d6df6; }}
        .card {{ background: white; border-radius: 16px; padding: 35px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; }}
        .ai-content {{ font-size: 19px; white-space: pre-wrap; margin-bottom: 25px; color: #333; }}
        .toggle-btn {{ background: #2d6df6; color: white; border: none; padding: 14px 28px; border-radius: 10px; font-size: 16px; cursor: pointer; transition: 0.3s; font-weight: 600; }}
        .toggle-btn:hover {{ background: #1b5bd6; transform: translateY(-2px); }}
        #full-analysis {{ display: none; margin-top: 30px; padding-top: 30px; border-top: 2px dashed #eee; }}
    </style>
</head>
<body>
    <h1 class="title">IELTS Daily Hub • AI Editor</h1>
    <div class="card">
        <h3>Today's Intensive Reading</h3>
        <div class="ai-content">{ai_content}</div>
        
        <button class="toggle-btn" onclick="toggleView()">Show/Hide Translation & Notes</button>
        
        <div id="full-analysis">
            <p style="color: #888; font-size: 14px; margin-bottom: 15px;">💡 AI 实时解析完成 (Powered by Gemini)</p>
            <div style="background: #fdfdfd; padding: 20px; border-radius: 10px; border-left: 5px solid #2d6df6;">
                解析内容已展开。
            </div>
        </div>
    </div>

    <script>
        function toggleView() {{
            var x = document.getElementById("full-analysis");
            if (x.style.display === "none" || x.style.display === "") {{
                x.style.display = "block";
            }} else {{
                x.style.display = "none";
            }}
        }}
    </script>
</body>
</html>
"""
    # 覆盖式写入，保证 index.html 永远不会超大报错
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

if __name__ == "__main__":
    # 检查钥匙是否存在
    if API_KEY:
        try:
            # 第一步：抓新闻
            news_text = get_latest_news()
            # 第二步：请 AI 批改、改写
            ai_processed_text = ask_gemini(news_text)
            # 第三步：生成最终网页
            generate_final_html(ai_processed_text)
            print("网页已由 AI 成功更新！")
        except Exception as e:
            print(f"执行过程中出错: {e}")
    else:
        print("错误：未检测到 GEMINI_API_KEY。请在 GitHub Secrets 中配置它。")
