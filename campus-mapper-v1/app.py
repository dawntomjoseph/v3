from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

DB = 'campus.db'  # The database created by init_db.py

app = Flask(__name__)
CORS(app)

# ===== Admin login =====
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return jsonify({'success': bool(result)})

# ===== Add Room/Lab =====
@app.route('/add-room', methods=['POST'])
def add_room():
    data = request.json
    conn = sqlite3.connect(DB)
    conn.execute('PRAGMA foreign_keys = ON')
    c = conn.cursor()
    # accept department_id and block_id (preferred) or fallback to text fields
    dept_id = data.get('department_id')
    block_id = data.get('block_id')
    if not dept_id and data.get('department'):
        # try resolve code
        c.execute('SELECT dept_id FROM departments WHERE code=?', (data.get('department'),))
        row = c.fetchone()
        dept_id = row[0] if row else None
    if not block_id and data.get('block'):
        c.execute('SELECT block_id FROM blocks WHERE name=?', (data.get('block'),))
        row = c.fetchone()
        block_id = row[0] if row else None

    c.execute('''
        INSERT INTO rooms (room_name, block, floor, department, class_name, type, faculty_name, department_id, block_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('room_name'), data.get('block'), data.get('floor'), data.get('department'),
          data.get('class_name'), data.get('type'), data.get('faculty_name',''), dept_id, block_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ===== Fetch all rooms =====
@app.route('/rooms', methods=['GET'])
def get_rooms():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # try to join with departments and blocks if available; if the normalized tables
    # don't exist (migration not run), fall back to returning plain rooms rows.
    try:
        c.execute('''
            SELECT r.*, d.code as department_code, d.name as department_name, b.name as block_name
            FROM rooms r
            LEFT JOIN departments d ON r.department_id = d.dept_id
            LEFT JOIN blocks b ON r.block_id = b.block_id
        ''')
        rows = [dict(ix) for ix in c.fetchall()]
    except sqlite3.OperationalError:
        # fallback: departments/blocks table missing; return rooms as-is
        c.execute('SELECT * FROM rooms')
        rows = [dict(ix) for ix in c.fetchall()]
    conn.close()
    return jsonify(rows)

# ===== Delete room =====
@app.route('/rooms/<int:id>', methods=['DELETE'])
def delete_room(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM rooms WHERE room_id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ===== Search =====
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q','')
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""SELECT * FROM rooms WHERE
                 room_name LIKE ? OR
                 department LIKE ? OR
                 class_name LIKE ?""",
              ('%'+query+'%','%'+query+'%','%'+query+'%'))
    rows = [dict(ix) for ix in c.fetchall()]
    conn.close()
    return jsonify(rows)

# ===== Department filter =====
@app.route('/department/<dept>', methods=['GET'])
def department(dept):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM rooms WHERE department=?", (dept,))
    rows = [dict(ix) for ix in c.fetchall()]
    conn.close()
    return jsonify(rows)


@app.route('/departments', methods=['GET','POST'])
def departments():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        c.execute('INSERT OR IGNORE INTO departments (code,name) VALUES (?,?)', (data.get('code'), data.get('name')))
        conn.commit()
    try:
        c.execute('SELECT * FROM departments')
        rows = [dict(ix) for ix in c.fetchall()]
    except sqlite3.OperationalError:
        # table doesn't exist yet
        rows = []
    conn.close()
    return jsonify(rows)


@app.route('/blocks', methods=['GET','POST'])
def blocks():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        c.execute('INSERT OR IGNORE INTO blocks (name,address,notes) VALUES (?,?,?)', (data.get('name'), data.get('address'), data.get('notes')))
        conn.commit()
    try:
        c.execute('SELECT * FROM blocks')
        rows = [dict(ix) for ix in c.fetchall()]
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return jsonify(rows)


@app.route('/faculty', methods=['GET','POST'])
def faculty():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if request.method == 'POST':
        data = request.json
        c.execute('INSERT INTO faculty (name,email,dept_id) VALUES (?,?,?)', (data.get('name'), data.get('email'), data.get('dept_id')))
        conn.commit()
    c.execute('SELECT * FROM faculty')
    rows = [dict(ix) for ix in c.fetchall()]
    conn.close()
    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True)
