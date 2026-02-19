import requests
from bs4 import BeautifulSoup
import re

def get_news_from_china_daily():
    print("正在连接 China Daily...")
    # 1. 访问国际新闻频道
    url = "https://global.chinadaily.com.cn/world"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. 找到第一篇文章的标题和链接
        first_story = soup.select_one('.mb10.tw3_01_2 h4 a')
        title = first_story.text.strip()
        link = "https:" + first_story['href']
        
        # 3. 点进链接获取正文
        art_res = requests.get(link, headers=headers)
        art_soup = BeautifulSoup(art_res.text, 'html.parser')
        # 拿到前几段文字
        paragraphs = art_soup.select('#Content p')
        full_text = " ".join([p.text.strip() for p in paragraphs[:2]])
        
        return title, full_text
    except Exception as e:
        print(f"抓取失败: {e}")
        return "News Update", "Failed to fetch news today."

def update_index_html(title, text):
    print("正在更新网页文件...")
    # 读取你刚才创建的 index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 准备要替换进去的新内容
    # 英文正文（这里先简单展示标题+前两段）
    new_en_content = f'<b>{title}</b><br><br>{text[:400]}...'
    
    # 词汇注释（这里我们先手工模拟几个，后续可以接入AI自动生成）
    new_anno_content = """
        <p>1. Global perspective: 全球视角</p >
        <p>2. Significant impact: 重大影响</p >
        <p>3. Strategic cooperation: 战略合作</p >
    """

    # 使用“手术刀”（正则表达式）精准替换标记位之间的内容
    html = re.sub(r'.*?', 
                  f'\n        <div class="english-text">{new_en_content}</div>\n        ', 
                  html, flags=re.DOTALL)
    
    html = re.sub(r'.*?', 
                  f'\n        <div class="annotations">{new_anno_content}</div>\n        ', 
                  html, flags=re.DOTALL)

    # 把修改后的内容写回 index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("更新完成！")

if __name__ == "__main__":
    news_title, news_text = get_news_from_china_daily()
    update_index_html(news_title, news_text)
