import models
import math
import sqlite3

def rssi_to_distance(rssi, measured_power, env_factor):
    """Stage 2: Convert RSSI to distance with a dynamic calibrated path-loss formula."""
    try:
        exponent = (float(measured_power) - float(rssi)) / (10.0 * float(env_factor))
        return 10.0 ** exponent
    except:
        return 10.0

def trilaterate(nodes):
    """Stage 3: Trilateration using 3 or more receivers via gradient descent."""
    if not nodes:
        return 0.0, 0.0
    if len(nodes) == 1:
        return nodes[0]['x'], nodes[0]['y']
        
    total_w = sum(1.0/max(0.1, n['d']) for n in nodes)
    guess_x = sum((1.0/max(0.1, n['d'])) * n['x'] for n in nodes) / total_w
    guess_y = sum((1.0/max(0.1, n['d'])) * n['y'] for n in nodes) / total_w
    
    learning_rate = 0.05
    for _ in range(100):
        grad_x = 0.0
        grad_y = 0.0
        for n in nodes:
            dc = math.hypot(guess_x - n['x'], guess_y - n['y'])
            if dc == 0: continue
            error = dc - n['d']
            grad_x += 2 * error * (guess_x - n['x']) / dc
            grad_y += 2 * error * (guess_y - n['y']) / dc
            
        guess_x -= learning_rate * grad_x
        guess_y -= learning_rate * grad_y
        
    return guess_x, guess_y

def calculate_all_positions():
    """Returns final (x, y, confidence) output for the dashboard."""
    conn = models.get_db()
    
    # Load dynamic globals
    settings = dict(conn.execute('SELECT key, value FROM system_config').fetchall())
    p_power = float(settings.get('rssi_1m', -55.0))
    p_factor = float(settings.get('path_loss', 2.5))
    
    tags = conn.execute("SELECT * FROM tags WHERE last_seen >= datetime('now', '-60 seconds')").fetchall()
    output = []
    
    for tag in tags:
        tag_mac = tag['mac']
        
        query = '''
        SELECT th.node_mac, n.x, n.y, AVG(th.rssi) as smooth_rssi
        FROM tag_history th
        JOIN nodes n ON th.node_mac = n.mac
        WHERE th.tag_mac = ? AND th.timestamp >= datetime('now', '-10 seconds')
        GROUP BY th.node_mac
        '''
        readings = conn.execute(query, (tag_mac,)).fetchall()
        if not readings:
            continue
            
        nodes_data = []
        for r in readings:
            dist = rssi_to_distance(r['smooth_rssi'], p_power, p_factor)
            nodes_data.append({
                'x': r['x'],
                'y': r['y'],
                'd': dist
            })
            
        calc_x, calc_y = trilaterate(nodes_data)
        
        confidence = min(100.0, len(nodes_data) * 25.0 + 25.0)
        if len(nodes_data) < 3: confidence -= 20.0
        
        avg_rssi = sum(r['smooth_rssi'] for r in readings) / len(readings) if readings else 0
        
        old_x = tag['x'] if tag['x'] is not None else calc_x
        old_y = tag['y'] if tag['y'] is not None else calc_y
        
        alpha = 0.2
        final_x = old_x * (1 - alpha) + calc_x * alpha
        final_y = old_y * (1 - alpha) + calc_y * alpha
        
        conn.execute('UPDATE tags SET x=?, y=?, confidence=? WHERE mac=?', (final_x, final_y, confidence, tag_mac))
        conn.execute('INSERT INTO position_history (tag_mac, x, y, confidence) VALUES (?, ?, ?, ?)', (tag_mac, final_x, final_y, confidence))
        
        output.append({
            "mac": tag_mac,
            "name": tag['name'],
            "x": round(final_x, 2),
            "y": round(final_y, 2),
            "confidence": round(confidence, 1),
            "rssi": round(avg_rssi, 1),
            "last_seen": tag['last_seen']
        })
        
    conn.commit()
    return output
