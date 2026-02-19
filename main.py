import requests
from bs4 import BeautifulSoup

def get_news():
    url = "https://global.chinadaily.com.cn/world"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        first_art = soup.select_one('.mb10.tw3_01_2 h4 a')
        return first_art.text.strip()
    except:
        return "Latest English News"

def update_html(title):
    # 彻底重新写一个 HTML，不再使用之前的 re.sub 替换，避免死循环膨胀
    new_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>English Learning</title>
    <style>body {{ font-family: sans-serif; padding: 30px; line-height: 1.6; }}</style>
</head>
<body>
    <h1>Daily English News</h1>
    <div style="background: #f4f4f4; padding: 20px; border-radius: 10px;">
        <h2>{title}</h2>
        <p>This is your daily update from China Daily.</p>
    </div>
</body>
</html>
"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

if __name__ == "__main__":
    news_title = get_news()
    update_html(news_title)
       
