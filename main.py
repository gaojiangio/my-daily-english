import requests
from bs4 import BeautifulSoup
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def ask_ai(text):
    # 【核心改动】：尝试三种不同的模型/路径组合，直到有一个通了为止
    # 组合 A: v1 版本 + gemini-pro (最稳定)
    # 组合 B: v1beta 版本 + gemini-1.5-flash (你之前的)
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    ]
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Task: Rewrite into IELTS 8.0 reading material (150 words). Include: 1. Article 2. 3 key phrases with English definitions 3. Chinese translation. Source: {text}"
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
        except Exception as e:
            last_error = str(e)
            continue
            
    return f"所有 AI 路径尝试失败。最后一次回复：{last_error}"

def get_3_news():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get("https://global.chinadaily.com.cn/world", headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = ["https:" + a['href'] for a in soup.select('.mb10.tw3_01_2 h4 a')[:3]]
        
        contents = []
        for l in links:
            art = BeautifulSoup(requests.get(l, headers=headers).text, 'html.parser')
            txt = " ".join([p.text.strip() for p in art.select('#Content p')[:3]])
            contents.append(txt)
        return contents
    except:
        return []

def build_final_page(results):
    cards = ""
    for i, content in enumerate(results):
        cards += f"""
        <div class="card" style="background: white; border-radius: 15px; padding: 30px; margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.05);">
            <h2 style="color: #2d6df6;">IELTS Reading Part {i+1}</h2>
            <div style="font-size: 18px; white-space: pre-wrap; line-height: 1.8; color: #333;">{content}</div>
        </div>"""

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>My Daily IELTS</title></head>
    <body style="font-family: Georgia, serif; max-width: 800px; margin: 40px auto; background: #f4f7f6; padding: 20px;">
    <h1 style="text-align:center; color:#333;">Personal IELTS Hub (Refreshed)</h1>{cards}</body></html>"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    if not API_KEY:
        print("API Key is missing!")
    else:
        articles = get_3_news()
        ai_results = [ask_ai(a) for a in articles if a]
        build_final_page(ai_results)
