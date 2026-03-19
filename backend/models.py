import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('rssi_1m', '-55')")
        cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('path_loss', '2.5')")
        cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('local_ip', '192.168.1.100')")
        cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('host_name', 'TrackerProServer')")
        cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('global_mode', 'esp32')")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mac TEXT UNIQUE NOT NULL,
                name TEXT,
                machine TEXT DEFAULT '',
                category TEXT DEFAULT 'Asset',
                interval INTEGER DEFAULT 500,
                status TEXT DEFAULT 'online',
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                x REAL DEFAULT NULL,
                y REAL DEFAULT NULL,
                confidence REAL DEFAULT 0.0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mac TEXT UNIQUE NOT NULL,
                name TEXT,
                mode TEXT,
                role TEXT DEFAULT 'anchor',
                mobility TEXT DEFAULT 'fixed',
                x REAL DEFAULT 0.0,
                y REAL DEFAULT 0.0,
                status TEXT DEFAULT 'online',
                calibration_offset INTEGER DEFAULT 0,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tag_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_mac TEXT NOT NULL,
                node_mac TEXT NOT NULL,
                rssi INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(tag_mac) REFERENCES tags(mac),
                FOREIGN KEY(node_mac) REFERENCES nodes(mac)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS position_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_mac TEXT NOT NULL,
                x REAL,
                y REAL,
                confidence REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(tag_mac) REFERENCES tags(mac)
            )
        ''')
        
        conn.commit()

init_db()
