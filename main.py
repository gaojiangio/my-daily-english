import requests
from bs4 import BeautifulSoup
import os
import time

API_KEY = os.getenv("GEMINI_API_KEY")

def ask_ai(text):
    # 【多重保险策略】：自动在不同路径和模型之间尝试
    endpoints = [
        # 路径 1: 尝试最稳的老模型 gemini-pro (v1 接口)
        f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}",
        # 路径 2: 尝试新模型 (v1beta 接口)
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    ]
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"请将以下新闻改写为雅思 8.0 水平的学习材料。要求：1.约 150 词的精简英文。2.3个重点动词短语或疑难名词的英文解释。3.全文中英对照翻译。原文内容：{text}"
            }]
        }]
    }
    
    last_error = ""
    for url in endpoints:
        try:
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()
            if 'candidates' in result:
                return result['candidates'][0]['content']['parts'][0]['text']
            last_error = str(result)
            time.sleep(1) # 稍作停顿再试
        except Exception as e:
            last_error = str(e)
            continue
            
    return f"AI 线路尝试均失败。最后回复：{last_error}"

def get_3_news():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get("https://global.chinadaily.com.cn/world", headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = ["https:" + a['href'] for a in soup.select('.mb10.tw3_01_2 h4 a')[:3]]
        
        contents = []
        for l in links:
            art = BeautifulSoup(requests.get(l, headers=headers).text, 'html.parser')
            # 抓取正文前 4 段
            txt = " ".join([p.text.strip() for p in art.select('#Content p')[:4]])
            contents.append(txt)
        return contents
    except:
        return []

def build_final_page(results):
    cards = ""
    for i, content in enumerate(results):
        cards += f"""
        <div class="card" style="background: white; border-radius: 20px; padding: 40px; margin-bottom: 40px; box-shadow: 0 15px 35px rgba(0,0,0,0.06); border: 1px solid #eee;">
            <h2 style="color: #2d6df6; font-family: 'Times New Roman', serif; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px;">IELTS Reading Part {i+1}</h2>
            <div style="font-size: 18px; white-space: pre-wrap; line-height: 1.9; color: #333; font-family: 'Georgia', serif;">{content}</div>
        </div>"""

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>My Daily IELTS</title></head>
    <body style="background: #f8fafc; max-width: 900px; margin: 60px auto; padding: 20px;">
    <h1 style="text-align:center; color:#1a202c; font-size: 32px; margin-bottom: 50px;">Personal IELTS Study Hub</h1>{cards}</body></html>"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    if not API_KEY:
        print("Error: API_KEY is missing!")
    else:
        articles = get_3_news()
        ai_results = [ask_ai(a) for a in articles if a]
        build_final_page(ai_results)
