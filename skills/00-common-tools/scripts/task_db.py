import sqlite3
import json
import os
import sys
import argparse
from datetime import datetime

DB_PATH = "generation_tasks.db"

class TaskDB:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_model_table(self, table_name, extra_columns=None):
        columns = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT",
            "project TEXT NOT NULL",
            "stage TEXT NOT NULL",
            "prompt TEXT NOT NULL",
            "status TEXT DEFAULT 'pending'",
            "output_path TEXT",
            "cost_info TEXT",
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP",
            "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        ]
        if extra_columns:
            columns.extend(extra_columns)
            
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        
        with self._get_connection() as conn:
            conn.execute(query)
            conn.commit()

    def add_task(self, table_name, stage, prompt, **kwargs):
        columns = ["stage", "prompt"]
        values = [stage, prompt]
        
        for k, v in kwargs.items():
            columns.append(k)
            values.append(v)
            
        placeholders = ", ".join(["?"] * len(values))
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid

    def get_task(self, table_name, task_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_task(self, table_name, task_id, **kwargs):
        if not kwargs:
            return
        sets = []
        values = []
        for k, v in kwargs.items():
            sets.append(f"{k} = ?")
            values.append(v)
        values.append(task_id)
        query = f"UPDATE {table_name} SET {', '.join(sets)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, values)
            conn.commit()

    def list_tasks(self, table_name, status=None):
        query = f"SELECT * FROM {table_name}"
        args = []
        if status:
            query += " WHERE status = ?"
            args.append(status)
        query += " ORDER BY created_at DESC"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, args)
            return [dict(row) for row in cursor.fetchall()]

def init_system_tables():
    db = TaskDB()
    db.create_model_table("model_openrouter_gpt54_image", ["size TEXT", "aspect_ratio TEXT", "ref_image_path TEXT"])
    db.create_model_table("model_volcengine_seedream_image", ["size TEXT", "seed INTEGER", "ref_image_path TEXT"])
    db.create_model_table("model_volcengine_seedance_video", ["duration INTEGER", "ref_image_path TEXT", "ref_video_path TEXT", "aspect_ratio TEXT"])

def main():
    parser = argparse.ArgumentParser(description="Generation Task Database Manager")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init")

    lst = subparsers.add_parser("list")
    lst.add_argument("--table", required=True)
    lst.add_argument("--status")

    app = subparsers.add_parser("approve")
    app.add_argument("--table", required=True)
    app.add_argument("id", type=int)

    args = parser.parse_args()
    db = TaskDB()

    if args.command == "init":
        init_system_tables()
        print("Database tables initialized.")
    elif args.command == "list":
        tasks = db.list_tasks(args.table, status=args.status)
        if not tasks:
            print(f"No tasks found in {args.table}.")
        else:
            print(f"{'ID':<5} {'Stage':<15} {'Status':<12} {'Created At'}")
            print("-" * 50)
            for t in tasks:
                print(f"{t['id']:<5} {t['stage']:<15} {t['status']:<12} {t['created_at']}")
    elif args.command == "approve":
        db.update_task(args.table, args.id, status='approved')
        print(f"Task {args.id} in {args.table} approved.")

if __name__ == "__main__":
    main()
