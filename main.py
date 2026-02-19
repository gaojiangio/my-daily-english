import requests
from bs4 import BeautifulSoup

def get_news():
    url = "https://global.chinadaily.com.cn/world"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        first_art = soup.select_one('.mb10.tw3_01_2 h4 a')
        title = first_art.text.strip()
        link = "https:" + first_art['href']
        
        # 抓取正文前两段
        art_res = requests.get(link, headers=headers)
        art_soup = BeautifulSoup(art_res.text, 'html.parser')
        paragraphs = art_soup.select('#Content p')
        text = " ".join([p.text.strip() for p in paragraphs[:2]])
        return title, text
    except:
        return "Daily English Update", "Please check the source for today's news."

def update_html(title, text):
    # 重新构建带样式的完整 HTML
    new_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily English Learning</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #fcfcfc; color: #1a1a1a; }}
        .title {{ text-align: center; font-size: 26px; margin-bottom: 40px; }}
        .card {{ background: white; border-radius: 12px; padding: 28px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; }}
        .english-text {{ font-size: 18px; line-height: 1.7; margin-bottom: 20px; }}
        .annotations {{ background: #f7f8fa; padding: 16px; border-radius: 8px; font-size: 15px; }}
    </style>
</head>
<body>
    <h1 class="title">Daily English Learning • News Update</h1>
    <div class="card">
        <h3>Today's Highlight</h3>
        <div class="english-text">
            <strong>{title}</strong><br><br>
            {text[:500]}...
        </div>
        <div class="annotations">
            <p><strong>Key Vocabulary:</strong></p>
            <p>1. Strategic collaboration: 战略协作</p>
            <p>2. Sustainable development: 可持续发展</p>
        </div>
    </div>
</body>
</html>
"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

if __name__ == "__main__":
    t, c = get_news()
    update_html(t, c)
