#!/usr/bin/env python3
"""AI 新闻日报生成脚本"""
import datetime
import json
import os
import re
import urllib.request

def fetch_hacker_news_ai():
    """从 Hacker News 抓取 AI 相关新闻"""
    try:
        url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
        ids = json.loads(urllib.request.urlopen(url).read())[:30]
        articles = []
        for nid in ids:
            aurl = f'https://hacker-news.firebaseio.com/v0/item/{nid}.json'
            try:
                item = json.loads(urllib.request.urlopen(aurl).read())
                if item.get('score', 0) >= 50 and 'ai' in str(item.get('title', '')).lower():
                    articles.append({
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'score': item.get('score', 0)
                    })
            except Exception:
                pass
        articles.sort(key=lambda x: x['score'], reverse=True)
        with open('hn_ai_articles.json', 'w') as f:
            json.dump(articles[:10], f, ensure_ascii=False, indent=2)
        print(f'Found {len(articles)} AI-related articles from HN')
    except Exception as e:
        print(f'HN fetch failed: {e}')
        with open('hn_ai_articles.json', 'w') as f:
            json.dump([], f)

def generate_markdown():
    """生成每日 Markdown 报告"""
    today = datetime.date.today()
    date_str = today.strftime('%Y-%m-%d')
    date_cn = f'{today.year}年{today.month}月{today.day}日'
    os.makedirs('daily', exist_ok=True)

    hn_articles = []
    if os.path.exists('hn_ai_articles.json'):
        with open('hn_ai_articles.json') as f:
            hn_articles = json.load(f)

    md_lines = []
    md_lines.append(f'# AI 热点日报 - {date_cn}')
    md_lines.append('')
    md_lines.append('---')
    md_lines.append('')
    md_lines.append('## 🔥 今日 AI 热点新闻')
    md_lines.append('')

    news_items = []
    for i, art in enumerate(hn_articles[:5], 1):
        link = f' [{art["title"]}]({art["url"]})' if art.get('url') else art['title']
        news_items.append(f'{i}. {link} (⭐ {art["score"]})')

    if not news_items:
        news_items.append('1. 暂无今日抓取到的新闻数据，请手动补充')

    md_lines.extend(news_items)
    md_lines.append('')
    md_lines.append('## 🧠 热门开源项目 (Skill / Plugin / MCP)')
    md_lines.append('')
    md_lines.append('- 关注 GitHub Trending 中 AI 相关仓库')
    md_lines.append('- 新发布的 skill、plugin、MCP Server')
    md_lines.append('- 值得关注的模型、工具库、框架')
    md_lines.append('')
    md_lines.append('## 🎁 免费与折扣优惠')
    md_lines.append('')
    md_lines.append('- AI API 免费额度更新')
    md_lines.append('- 云服务 AI 产品折扣')
    md_lines.append('- 学生/教育优惠')
    md_lines.append('- 限时免费活动')
    md_lines.append('')
    md_lines.append('## 📈 值得关注的趋势')
    md_lines.append('')
    md_lines.append('1. 开源大模型与地缘政治')
    md_lines.append('2. Agent 协同与多智能体')
    md_lines.append('3. 端侧 AI 部署')
    md_lines.append('4. AI 编程工具发展')
    md_lines.append('5. 多模态与具身智能')
    md_lines.append('')

    content = '\n'.join(md_lines)
    with open(f'daily/{date_str}-full.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Generated: daily/{date_str}-full.md')

def update_html():
    """更新 HTML 页面"""
    today = datetime.date.today()
    date_cn = f'{today.year}年{today.month}月{today.day}日'
    date_md = today.strftime('%Y-%m-%d')

    daily_file = f'daily/{date_md}-full.md'
    if os.path.exists(daily_file):
        with open(daily_file, encoding='utf-8') as f:
            daily_content = f.read()
    else:
        daily_content = f'# AI 热点日报 - {date_cn}\n\n暂无今日新闻内容'

    with open('index.html', encoding='utf-8') as f:
        html = f.read()

    html = re.sub(r'\d{4}年\d+月\d+日', date_cn, html)

    lines = daily_content.split('\n')
    cards_html = []
    current_section = ''
    card_num = 0

    for line in lines:
        if line.startswith('## '):
            current_section = line.replace('## ', '').strip()
            continue
        if line.startswith('# '):
            continue
        if re.match(r'^\d+\.\s', line):
            card_num += 1
            match = re.match(r'^\d+\.\s*(.+?)(?:\s*\([^)]*\))?$', line.strip())
            if match:
                title_part = match.group(1).strip()
                title = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', title_part)
                score_match = re.search(r'\(⭐\s*(\d+)\)', title_part)
                score = score_match.group(1) if score_match else ''

                tag_html = '<span class="tag">🔥 热门</span>' if score else ''
                card = f'''<div class="card">
  <span class="card-number">{card_num:02d}</span>
  <h3>{title}</h3>
  <div class="meta">
      <span class="tag">{current_section}</span>
      <span>{date_cn}</span>
      {tag_html}
  </div>
  <div class="summary">{title}</div>
  <div class="reason">点击查看原文链接</div>
</div>'''
                cards_html.append(card)

    cards_block = '\n'.join(cards_html[:8]) if cards_html else '<div class="card"><h3>今日暂无新闻</h3></div>'
    html = re.sub(r'(<!-- CARDS_START -->).*?(<!-- CARDS_END -->)', f'\\1\\n{cards_block}\\n\\2', html, flags=re.DOTALL)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('Updated index.html')

if __name__ == '__main__':
    print('Starting daily report generation...')
    fetch_hacker_news_ai()
    generate_markdown()
    update_html()
    print('Done!')
