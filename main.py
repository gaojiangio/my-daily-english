import requests
from bs4 import BeautifulSoup
import os

# 确保你在 GitHub Secret 里填入的是 DeepSeek 的 API Key
API_KEY = os.getenv("GEMINI_API_KEY")

def ask_ai_final(text):
    # DeepSeek 官方标准接口
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat", 
        "messages": [
            {"role": "system", "content": "你是一个资深的雅思教研专家，擅长将新闻改写为雅思8.0难度的学习材料。"},
            {"role": "user", "content": f"请将以下内容改写为一篇雅思8.0水平的短文（约150词），带3个词组解析和中英翻译。原文：{text}"}
        ]
    }
    
    try:
        # 增加超时和报错捕获
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        # 如果返回码不是 200，说明 API 账号有问题
        if response.status_code != 200:
            return f"API 报错！状态码：{response.status_code}，回复：{response.text}"
            
        res_json = response.json()
        return res_json['choices'][0]['message']['content']
    except Exception as e:
        return f"网络请求彻底失败：{str(e)}"

def fetch_top_3():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get("https://global.chinadaily.com.cn/world", headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('.mb10.tw3_01_2 h4 a')[:3]
        data = []
        for it in items:
            link = "https:" + it['href']
            art = BeautifulSoup(requests.get(link, headers=headers).text, 'html.parser')
            body = " ".join([p.text.strip() for p in art.select('#Content p')[:4]])
            data.append({"title": it.text.strip(), "raw": body})
        return data
    except:
        return []

def render_html(data):
    cards = ""
    for i, item in enumerate(data):
        cards += f"""
        <div style="background: white; border-radius: 12px; padding: 25px; margin-bottom: 30px; border: 1px solid #e0e0e0;">
            <h2 style="color: #1a73e8;">{i+1}. {item['title']}</h2>
            <div style="font-size: 18px; line-height: 1.8; white-space: pre-wrap;">{item['processed']}</div>
        </div>"""
    
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>IELTS Hub</title></head>
    <body style="max-width: 800px; margin: 40px auto; padding: 20px; background: #f5f5f5; font-family: serif;">
    <h1 style="text-align: center;">Personal IELTS Study Hub (Stable v3.0)</h1>
    {cards}</body></html>"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    articles = fetch_top_3()
    for a in articles:
        a['processed'] = ask_ai_final(a['raw'])
    render_html(articles)
