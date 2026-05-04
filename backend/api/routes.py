from flask import Blueprint, jsonify, request, Response
import base64

# Import from core
from core import database
from core import positioning
from core import config_gen

api_bp = Blueprint('api', __name__)

@api_bp.before_request
def require_api_key():
    if request.path.startswith('/api/') and request.path not in ['/api/telemetry', '/api/auth']:
        if request.method == 'OPTIONS':
            return Response(status=200)
            
        # Allow GET requests for basic telemetry/config info to guests
        if request.method == 'GET' and request.path in ['/api/nodes', '/api/tags', '/api/settings', '/api/users']:
            return

        token = request.headers.get('X-API-Key')
        if not token:
            return jsonify({"error": "Unauthorized"}), 401
        try:
            decoded = base64.b64decode(token).decode('utf-8')
            username, password = decoded.split(':', 1)
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401
            
        conn = database.get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
            
        if user['role'] == 'ordinary' and request.method != 'GET':
            return jsonify({"error": "Forbidden"}), 403

@api_bp.route('/auth', methods=['POST'])
def check_auth():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    conn = database.get_db()
    user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    if user:
        token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
        return jsonify({"status": "ok", "token": token, "role": user['role'], "username": username}), 200
    return jsonify({"error": "Unauthorized: Invalid username or password"}), 401

@api_bp.route('/users', methods=['GET', 'POST'])
def manage_users():
    conn = database.get_db()
    if request.method == 'POST':
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', 'ordinary')
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        if role not in ['admin', 'ordinary']:
            return jsonify({"error": "Role must be 'admin' or 'ordinary'"}), 400
        existing = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if existing:
            return jsonify({"error": f"User '{username}' already exists"}), 409
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        return jsonify({"status": "ok", "message": f"User '{username}' created"}), 201
    else:
        users = conn.execute('SELECT id, username, role FROM users').fetchall()
        return jsonify([dict(u) for u in users])

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = database.get_db()
    token = request.headers.get('X-API-Key')
    current_username = None
    if token:
        try:
            decoded = base64.b64decode(token).decode('utf-8')
            current_username = decoded.split(':', 1)[0]
        except Exception:
            pass

    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user['username'] == current_username:
        return jsonify({"error": "Cannot delete your own account"}), 403
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    return jsonify({"status": "ok", "message": f"User '{user['username']}' deleted"}), 200

@api_bp.route('/settings', methods=['GET', 'POST'])
def manage_settings():
    conn = database.get_db()
    if request.method == 'POST':
        data = request.json
        for k, v in data.items():
            conn.execute('INSERT OR REPLACE INTO system_config (key, value) VALUES (?, ?)', (k, str(v)))
        conn.commit()
        return jsonify({"status": "ok"})
    else:
        settings = conn.execute('SELECT * FROM system_config').fetchall()
        return jsonify({s['key']: s['value'] for s in settings})

@api_bp.route('/nodes', methods=['GET', 'POST'])
def manage_nodes():
    conn = database.get_db()
    if request.method == 'POST':
        data = request.json
        mac = data.get('mac')
        name = data.get('name', 'Unknown Node')
        mode = data.get('mode', 'esp32')
        role = data.get('role', 'anchor')
        mobility = data.get('mobility', 'fixed')
        category = data.get('category', 'Head Office')
        type_ = data.get('type', '')
        x = data.get('x', 0.0)
        y = data.get('y', 0.0)
        
        node = conn.execute('SELECT * FROM nodes WHERE mac = ?', (mac,)).fetchone()
        if node:
            conn.execute('UPDATE nodes SET name=?, mode=?, role=?, mobility=?, category=?, type=?, x=?, y=? WHERE mac=?', 
                         (name, mode, role, mobility, category, type_, x, y, mac))
        else:
            conn.execute('INSERT INTO nodes (mac, name, mode, role, mobility, category, type, x, y) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                         (mac, name, mode, role, mobility, category, type_, x, y))
        conn.commit()
        return jsonify({"status": "ok"}), 201
    else:
        nodes = conn.execute('SELECT * FROM nodes').fetchall()
        return jsonify([dict(n) for n in nodes])

@api_bp.route('/nodes/calibrate/<mac>', methods=['POST'])
def calibrate_node(mac):
    data = request.json
    offset = data.get('offset', 0)
    conn = database.get_db()
    conn.execute('UPDATE nodes SET calibration_offset = ? WHERE mac = ?', (offset, mac))
    conn.commit()
    return jsonify({"status": "ok"})

@api_bp.route('/tags', methods=['GET', 'POST'])
def manage_tags():
    conn = database.get_db()
    if request.method == 'POST':
        data = request.json
        mac = data.get('mac')
        name = data.get('name', 'Unknown Tag')
        machine = data.get('machine', '')
        category = data.get('category', 'Asset')
        type_ = data.get('type', '')
        interval = data.get('interval', 500)
        
        tag = conn.execute('SELECT * FROM tags WHERE mac = ?', (mac,)).fetchone()
        if tag:
            conn.execute('UPDATE tags SET name=?, machine=?, category=?, type=?, interval=? WHERE mac=?', 
                         (name, machine, category, type_, interval, mac))
        else:
            conn.execute('INSERT INTO tags (mac, name, machine, category, type, interval) VALUES (?, ?, ?, ?, ?, ?)', 
                         (mac, name, machine, category, type_, interval))
        conn.commit()
        return jsonify({"status": "ok"}), 201
    else:
        tags = conn.execute('SELECT * FROM tags').fetchall()
        return jsonify([dict(t) for t in tags])

@api_bp.route('/telemetry', methods=['POST'])
def ingest_telemetry():
    conn = database.get_db()
    net_key = request.headers.get('X-Network-Key')
    correct_key = conn.execute("SELECT value FROM system_config WHERE key='network_key'").fetchone()
    if not correct_key or net_key != correct_key['value']:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    node_mac = data.get('node_mac')
    tag_mac = data.get('tag_mac')
    rssi = data.get('rssi')
    
    tag = conn.execute('SELECT * FROM tags WHERE mac = ?', (tag_mac,)).fetchone()
    if not tag:
        conn.execute('INSERT INTO tags (mac, name, last_seen) VALUES (?, ?, CURRENT_TIMESTAMP)', (tag_mac, f"Tag {tag_mac[-5:]}"))
    else:
        conn.execute('UPDATE tags SET last_seen = CURRENT_TIMESTAMP WHERE mac = ?', (tag_mac,))
        
    node = conn.execute('SELECT calibration_offset FROM nodes WHERE mac = ?', (node_mac,)).fetchone()
    if node:
        conn.execute('UPDATE nodes SET last_seen = CURRENT_TIMESTAMP WHERE mac = ?', (node_mac,))
        rssi += node['calibration_offset']
        
    conn.execute('INSERT INTO tag_history (tag_mac, node_mac, rssi) VALUES (?, ?, ?)', (tag_mac, node_mac, rssi))
    conn.commit()
    
    return jsonify({"status": "logged"}), 201

@api_bp.route('/positions', methods=['GET'])
def get_positions():
    positions = positioning.calculate_all_positions()
    return jsonify(positions)

@api_bp.route('/config/node/<node_mac>', methods=['GET'])
def get_node_config(node_mac):
    conn = database.get_db()
    node = conn.execute('SELECT * FROM nodes WHERE mac = ?', (node_mac,)).fetchone()
    if not node:
        return jsonify({"error": "Node not found"}), 404
        
    settings = dict(conn.execute('SELECT key, value FROM system_config').fetchall())
    return jsonify(config_gen.generate_node(dict(node), settings))

@api_bp.route('/config/tag/<tag_mac>', methods=['GET'])
def get_tag_config(tag_mac):
    conn = database.get_db()
    tag = conn.execute('SELECT * FROM tags WHERE mac = ?', (tag_mac,)).fetchone()
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
        
    settings = dict(conn.execute('SELECT key, value FROM system_config').fetchall())
    return jsonify(config_gen.generate_tag(dict(tag), settings))

@api_bp.route('/export/logs', methods=['GET'])
def export_logs():
    conn = database.get_db()
    records = conn.execute('''
        SELECT th.timestamp, t.name as tag_name, th.tag_mac, n.name as node_name, th.node_mac, th.rssi 
        FROM tag_history th
        LEFT JOIN tags t ON th.tag_mac = t.mac
        LEFT JOIN nodes n ON th.node_mac = n.mac
        ORDER BY th.timestamp DESC LIMIT 10000
    ''').fetchall()
    
    def generate():
        yield "Timestamp,Tag Name,Tag MAC,Node Name,Node MAC,RSSI\n"
        for r in records:
            yield f"{r['timestamp']},{r['tag_name'] or 'Unknown'},{r['tag_mac']},{r['node_name'] or 'Unknown'},{r['node_mac']},{r['rssi']}\n"
            
    return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=rssi_logs.csv'})

@api_bp.route('/export/positions', methods=['GET'])
def export_positions():
    conn = database.get_db()
    records = conn.execute('''
        SELECT ph.timestamp, t.name as tag_name, ph.tag_mac, ph.x, ph.y, ph.confidence 
        FROM position_history ph
        LEFT JOIN tags t ON ph.tag_mac = t.mac
        ORDER BY ph.timestamp DESC LIMIT 10000
    ''').fetchall()
    
    def generate():
        yield "Timestamp,Tag Name,Tag MAC,X,Y,Confidence Score\n"
        for r in records:
            yield f"{r['timestamp']},{r['tag_name'] or 'Unknown'},{r['tag_mac']},{r['x']},{r['y']},{r['confidence']}\n"
            
    return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=position_history.csv'})
