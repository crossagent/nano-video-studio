import sqlite3
import json
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
DB_PATH = str(ROOT_DIR / "generation_tasks.db")

class TaskDB:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        """Initializes the registry and the single big tasks table."""
        with self._get_connection() as conn:
            # 1. Model Registry (说明书)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS mcp_model_registry (
                channel_id TEXT,
                model_id TEXT,
                task_type TEXT,
                required_params_json TEXT,
                PRIMARY KEY (channel_id, model_id)
            )
            """)
            
            # 2. All Tasks Table (大表)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS all_generation_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                model_id TEXT NOT NULL,
                project TEXT NOT NULL,
                stage TEXT NOT NULL,
                prompt TEXT NOT NULL,
                params_json TEXT,  -- 存储所有模型特定的参数 (JSON)
                status TEXT DEFAULT 'pending',
                output_path TEXT,
                cost_info TEXT,
                error_msg TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()

    def register_model(self, channel_id, model_id, task_type, required_params):
        """Registers a model's requirements in the registry."""
        query = "INSERT OR REPLACE INTO mcp_model_registry VALUES (?, ?, ?, ?)"
        with self._get_connection() as conn:
            conn.execute(query, (channel_id, model_id, task_type, json.dumps(required_params)))
            conn.commit()

    def get_all_model_configs(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mcp_model_registry")
            rows = cursor.fetchall()
            return [{**dict(row), 'required_params': json.loads(row['required_params_json'])} for row in rows]

    def add_task(self, channel_id, model_id, project, stage, prompt, params: dict):
        """Adds a task to the big table."""
        query = """
        INSERT INTO all_generation_tasks (channel_id, model_id, project, stage, prompt, params_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (channel_id, model_id, project, stage, prompt, json.dumps(params)))
            conn.commit()
            return cursor.lastrowid

    def get_task(self, task_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM all_generation_tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row: return None
            d = dict(row)
            d['params'] = json.loads(d['params_json']) if d['params_json'] else {}
            return d

    def update_task(self, task_id, **kwargs):
        if not kwargs: return
        sets = [f"{k} = ?" for k in kwargs.keys()]
        values = list(kwargs.values())
        values.append(task_id)
        query = f"UPDATE all_generation_tasks SET {', '.join(sets)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, values)
            conn.commit()

    def list_tasks(self, channel_id=None, status=None):
        query = "SELECT * FROM all_generation_tasks"
        filters = []
        args = []
        if channel_id:
            filters.append("channel_id = ?")
            args.append(channel_id)
        if status:
            filters.append("status = ?")
            args.append(status)
        
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY created_at DESC"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, args)
            return [dict(row) for row in cursor.fetchall()]
