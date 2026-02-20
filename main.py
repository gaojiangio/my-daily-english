import requests
from bs4 import BeautifulSoup
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def ask_ai(text):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位雅思专家。请将新闻重写为150词左右的雅思8.0难度文章，带3个词组解析和全文翻译。"},
            {"role": "user", "content": f"新闻原文：{text}"}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"AI 暂时不可用 (Error {response.status_code})"
    except:
        return "网络连接失败"

def run_task():
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get("https://global.chinadaily.com.cn/world", headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = soup.select('.mb10.tw3_01_2 h4 a')[:3]
    
    cards = ""
    for i, link in enumerate(links):
        full_url = "https:" + link['href']
        art_res = requests.get(full_url, headers=headers)
        art_soup = BeautifulSoup(art_res.text, 'html.parser')
        body = " ".join([p.text.strip() for p in art_soup.select('#Content p')[:4]])
        processed = ask_ai(body)
        
        cards += f"""
        <div style="background:white; padding:30px; margin:20px; border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.1);">
            <h2 style="color:#2d6df6;">{i+1}. {link.text.strip()}</h2>
            <div style="font-size:18px; line-height:1.8; white-space:pre-wrap;">{processed}</div>
        </div>"""

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>IELTS Hub</title></head>
    <body style="background:#f0f2f5; font-family:serif; max-width:850px; margin:auto; padding:20px;">
    <h1 style="text-align:center; color:#333;">Personal IELTS Study Hub</h1>{cards}</body></html>"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    if API_KEY:
        run_task()
