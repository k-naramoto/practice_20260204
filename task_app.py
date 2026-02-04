import sys
import mysql.connector
import argparse
import unicodedata
from datetime import datetime

MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "task_management"

# DB接続設定
def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
    except mysql.connector.Error as e:
        print_error(f"データベース接続に失敗しました: {e}")
        exit(1)

# メッセージを赤色で出力する
def print_error(msg):
    print(f"\033[31m{msg}\033[0m", file=sys.stderr)

# 整形された一覧表を表示する
def display_table(rows):
    # 全角2、半角1として文字幅を計算する
    def get_width(text):
        return sum(2 if unicodedata.east_asian_width(c) in 'FWA' else 1 for c in str(text))
    # 指定の幅に揃えるためのパディングを追加する
    def pad(text, width):
        return str(text) + ' ' * (width - get_width(text))

    if not rows: return

    cols = [
        (4, 'ID', 'id'),
        (10, 'タスク名', 'title'),
        (30, '内容', 'description'),
        (12, '担当者', 'assignee'),
        (12, '期限', 'deadline'),
        (12, '状態', 'status')
    ]

    sep = "+" + "+".join("-" * (w + 2) for w, _, _ in cols) + "+"
    print(sep)
    print("| " + " | ".join(pad(label, w) for w, label, _ in cols) + " |")
    print(sep)
    for r in rows:
        print("| " + " | ".join(pad(r[key], w) for w, _, key in cols) + " |")
    print(sep)

# ユーザー入力のバリデーション
def validate_input(prompt, required=True, is_date=False):
    while True:
        val = input(prompt).strip()
        if not val:
            if required:
                print_error("この項目は必須入力です。")
                continue
            return None
        if is_date:
            try:
                datetime.strptime(val, '%Y-%m-%d')
            except ValueError:
                print_error("日付形式が正しくありません (YYYY-MM-DD)。")
                continue
        return val

# 指定IDのタスクを取得
def get_task(cursor, task_id):
    sql = "SELECT * FROM tasks WHERE id = %s AND deleted_at IS NULL"
    cursor.execute(sql, (task_id,))
    return cursor.fetchone()

# 新規タスクを追加する
def add_task():
    print("--- 新規タスク追加 ---")
    title = validate_input("● タスク名: ")
    desc = validate_input("● 内容: ")
    user = validate_input("● 担当者: ")
    date = validate_input("● 期限 (YYYY-MM-DD): ", is_date=True)
    stat = validate_input("● ステータス: ")

    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            sql = """
                INSERT INTO tasks
                (title, description, assignee, deadline, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            print(title, desc, user, date, stat)
            cursor.execute(sql, (title, desc, user, date, stat))
            conn.commit()
        print("タスクを追加しました。")
    except Exception as e:
        print_error(f"追加失敗: {e}")
    finally:
        conn.close()

# タスクを一覧表示する
def list_tasks():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        search = input("検索キーワード: ").strip()
        sql = (
            "SELECT id, title, description, assignee, deadline, status "
            "FROM tasks WHERE deleted_at IS NULL "
            "AND (title LIKE %s OR description LIKE %s OR assignee LIKE %s OR status LIKE %s)"
        )
        val = f"%{search}%"
        cursor.execute(sql, (val, val, val, val))
            
        rows = cursor.fetchall()
        display_table(rows)
    finally:
        conn.close()

# 指定IDのタスク情報を更新する
def update_task():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        tid = input("更新するタスクのID: ")
        task = get_task(cursor, tid)
        if not task:
            print_error(f"ID {tid} は存在しません。")
            return

        print("--- 更新情報の入力（変更しない項目は未入力でエンター） ---")
        title = validate_input("● 新しいタスク名: ", required=False) or task['title']
        desc = validate_input("● 新しい内容: ", required=False) or task['description']
        user = validate_input("● 新しい担当者: ", required=False) or task['assignee']
        date = validate_input("● 新しい期限 (YYYY-MM-DD): ", required=False, is_date=True) or task['deadline']
        stat = validate_input("● 新しいステータス: ", required=False) or task['status']

        with conn:
            sql = """
                UPDATE tasks
                SET title=%s, description=%s, assignee=%s, deadline=%s, status=%s
                WHERE id=%s
            """
            cursor.execute(sql, (title, desc, user, date, stat, tid))
            conn.commit()
        print("タスクを更新しました。")
    except Exception as e:
        print_error(f"更新失敗: {e}")
    finally:
        conn.close()

# タスクを論理削除する
def delete_task():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        tid = input("削除するタスクのID: ")
        if not get_task(cursor, tid):
            print_error(f"ID {tid} は存在しません。")
            return

        if input(f"ID:{tid} を削除しますか？(y/n): ").lower() == 'y':
            with conn:
                cursor.execute(
                    "UPDATE tasks SET deleted_at = NOW() WHERE id = %s",
                    (tid,)
                )
                conn.commit()
            print("タスクを削除しました。")
    except Exception as e:
        print_error(f"削除失敗: {e}")
    finally:
        conn.close()

# メイン処理
def main():
    parser = argparse.ArgumentParser(description="Task Management CLI Tool")
    parser.add_argument("command", help="add, list, update, delete")
    args = parser.parse_args()

    if args.command == "add":
        add_task()
    elif args.command == "list":
        list_tasks()
    elif args.command == "update":
        update_task()
    elif args.command == "delete":
        delete_task()
    else:
        print_error(f"'{args.command}' は無効なコマンドです。")

if __name__ == "__main__":
    main()
