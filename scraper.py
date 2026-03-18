import requests
import sqlite3
import time
import random
from datetime import datetime

API_BASE = "https://api.makuake.com/v2"

def init_db():
    conn = sqlite3.connect("makuake.db")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS projects")
    c.execute('''CREATE TABLE projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        makuake_id TEXT UNIQUE,
        title TEXT,
        url TEXT,
        category TEXT,
        amount INTEGER,
        achievement_rate INTEGER,
        supporters INTEGER,
        start_date TEXT,
        end_date TEXT,
        image_url TEXT,
        is_coming_soon INTEGER,
        created_at TEXT
    )''')
    conn.commit()
    conn.close()

def fetch_projects(page=1, status="ended"):
    url = f"{API_BASE}/projects/"
    params = {
        "status": status,
        "page": page,
        "per_page": 30
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        return res.json()
    except Exception as e:
        print(f"エラー: {e}")
        return None

def save_projects(projects):
    conn = sqlite3.connect("makuake.db")
    c = conn.cursor()
    saved = 0
    for p in projects:
        try:
            c.execute('''INSERT OR IGNORE INTO projects
                (makuake_id, title, url, amount, achievement_rate, 
                supporters, start_date, end_date, image_url, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)''', (
                str(p.get("id", "")),
                p.get("title", ""),
                p.get("url", ""),
                p.get("collected_money", 0),
                p.get("percent", 0),
                p.get("collected_supporter", 0),
                p.get("start_date", ""),
                p.get("expiration_date", ""),
                p.get("image_url", ""),
                datetime.now().isoformat()
            ))
            saved += 1
        except Exception as e:
            print(f"保存エラー: {e}")
    conn.commit()
    conn.close()
    return saved

def main():
    print("🚀 API版スクレイパー開始")
    init_db()
    
    total_saved = 0
    page = 1
    
    while True:

        print(f"ページ {page} 取得中...")
        data = fetch_projects(page=page, status="ended")
        
        if not data:
            print("データなし、終了")
            break
            
        projects = data.get("projects", [])
        if not projects:
            print("プロジェクトなし、終了")
            break
        
        saved = save_projects(projects)
        total_saved += saved
        print(f"  {saved}件保存 (累計: {total_saved}件)")
        
        # 次ページがあるか確認
        pagination = data.get("pagination", {})
        total = pagination.get("total", 0)
        per_page = pagination.get("per_page", 30)
        total_pages = (total + per_page - 1) // per_page
        print(f"  ({page}/{total_pages}ページ, 全{total}件)")

        if page >= total_pages:
            break
            
        page += 1
        # ランダム待機（3〜7秒）
        wait = random.uniform(3, 7)
        print(f"  {wait:.1f}秒待機...")
        time.sleep(wait)
    
    print(f"\n✅ 完了！合計 {total_saved} 件取得しました！")

main()