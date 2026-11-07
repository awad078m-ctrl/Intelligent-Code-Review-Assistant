import sqlite3
import json 
from datetime import datetime

DB_NAME ="code_reviews.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
id INTEGER PRIMARY KEY AUTOINCREMENT, programming_language TEXT,
original_code TEXT , review_result TEXT, created_at TIMESTAMP)""")


    conn.commit()
    conn.close()


def save_review (language: str , code: str , result: dict):
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    resultj= json.dumps(result , ensure_ascii=False)

    cursor.execute("""
INSERT INTO reviews (programming_language , original_code , review_result , created_at) VALUES(?,?,?,?)"""
, (language, code, resultj, datetime.now()))

    conn.commit()
    conn.close()


def all_review():
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    cursor.execute("""SELECT id , programming_language , created_at , review_result FROM reviews ORDER BY created_at DESC""") 
    rows=cursor.fetchall()
    conn.close()
    return rows


