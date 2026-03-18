from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import sqlite3
import datetime
from typing import Optional

app = FastAPI()

def get_db():
    conn = sqlite3.connect("makuake.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/projects")
def get_projects(
    page: int = 1,
    limit: int = 20,
    title: Optional[str] = None,
    keyword: Optional[str] = None,
    min_amount: Optional[int] = None,
    max_amount: Optional[int] = None,
    min_rate: Optional[int] = None,
    max_rate: Optional[int] = None,
    min_supporters: Optional[int] = None,
    max_supporters: Optional[int] = None,
    end_date_from: Optional[str] = None,
    end_date_to: Optional[str] = None,
    sort: Optional[str] = "amount_desc",
):
    conn = get_db()
    c = conn.cursor()
    query = "SELECT * FROM projects WHERE 1=1"
    params = []
    if title:
        query += " AND title LIKE ?"
        params.append(f"%{title}%")
    if keyword:
        query += " AND title LIKE ?"
        params.append(f"%{keyword}%")
    if min_amount:
        query += " AND amount >= ?"
        params.append(min_amount)
    if max_amount:
        query += " AND amount <= ?"
        params.append(max_amount)
    if min_rate:
        query += " AND achievement_rate >= ?"
        params.append(min_rate)
    if max_rate:
        query += " AND achievement_rate <= ?"
        params.append(max_rate)
    if min_supporters:
        query += " AND supporters >= ?"
        params.append(min_supporters)
    if max_supporters:
        query += " AND supporters <= ?"
        params.append(max_supporters)
    if end_date_from:
        ts = int(datetime.datetime.strptime(end_date_from, "%Y-%m-%d").timestamp())
        query += " AND end_date >= ?"
        params.append(ts)
    if end_date_to:
        ts = int(datetime.datetime.strptime(end_date_to, "%Y-%m-%d").timestamp()) + 86400
        query += " AND end_date <= ?"
        params.append(ts)
    sort_map = {
        "amount_desc": "amount DESC",
        "amount_asc": "amount ASC",
        "rate_desc": "achievement_rate DESC",
        "supporters_desc": "supporters DESC",
        "newest": "id DESC",
        "oldest": "id ASC",
    }
    query += f" ORDER BY {sort_map.get(sort, 'amount DESC')}"
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    total = c.execute(count_query, params).fetchone()[0]
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, (page - 1) * limit])
    projects = c.execute(query, params).fetchall()
    conn.close()
    return {"total": total, "page": page, "projects": [dict(p) for p in projects]}

@app.get("/api/stats")
def get_stats():
    conn = get_db()
    c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    max_amount = c.execute("SELECT MAX(amount) FROM projects").fetchone()[0]
    max_rate = c.execute("SELECT MAX(achievement_rate) FROM projects").fetchone()[0]
    total_amount = c.execute("SELECT SUM(amount) FROM projects").fetchone()[0]
    conn.close()
    return {
        "total_projects": total,
        "max_amount": max_amount,
        "max_rate": max_rate,
        "total_amount": total_amount
    }

app.mount("/", StaticFiles(directory="static", html=True), name="static")