import sqlite3

# Database file name
DB = 'campus.db'

# Connect to SQLite (it will create the file if it doesn't exist)
conn = sqlite3.connect(DB)
c = conn.cursor()

# ===== Create Admin table =====
c.execute('''
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
''')

# Insert default admin if not exists
c.execute("SELECT * FROM admin WHERE username='admin'")
if not c.fetchone():
    c.execute("INSERT INTO admin (username,password) VALUES (?,?)", ('admin','12345'))

# ===== Create Rooms table =====
c.execute('''
CREATE TABLE IF NOT EXISTS rooms (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_name TEXT,
    block TEXT,
    floor TEXT,
    department TEXT,
    class_name TEXT,
    type TEXT,
    faculty_name TEXT
)
''')

# ===== New normalized tables =====
c.execute('''
CREATE TABLE IF NOT EXISTS blocks (
    block_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    address TEXT,
    notes TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS departments (
    dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    name TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    dept_id INTEGER
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
''')

# Add FK columns to rooms if they don't exist
try:
    c.execute("ALTER TABLE rooms ADD COLUMN department_id INTEGER")
except Exception:
    pass
try:
    c.execute("ALTER TABLE rooms ADD COLUMN block_id INTEGER")
except Exception:
    pass

# Populate departments and blocks from existing rooms data
c.execute("SELECT DISTINCT department FROM rooms WHERE department IS NOT NULL AND department<>''")
for (dept,) in c.fetchall():
    # use dept as both code and name by default
    c.execute('SELECT 1 FROM departments WHERE code=?', (dept,))
    if not c.fetchone():
        c.execute('INSERT INTO departments (code,name) VALUES (?,?)', (dept, dept))

c.execute("SELECT DISTINCT block FROM rooms WHERE block IS NOT NULL AND block<>''")
for (blk,) in c.fetchall():
    c.execute('SELECT 1 FROM blocks WHERE name=?', (blk,))
    if not c.fetchone():
        c.execute('INSERT INTO blocks (name) VALUES (?)', (blk,))

# Update rooms to set department_id and block_id
c.execute('SELECT room_id, department, block FROM rooms')
for room_id, dept, blk in c.fetchall():
    dept_id = None
    block_id = None
    if dept:
        c.execute('SELECT dept_id FROM departments WHERE code=?', (dept,))
        row = c.fetchone()
        if row:
            dept_id = row[0]
    if blk:
        c.execute('SELECT block_id FROM blocks WHERE name=?', (blk,))
        row = c.fetchone()
        if row:
            block_id = row[0]
    if dept_id or block_id:
        c.execute('UPDATE rooms SET department_id=?, block_id=? WHERE room_id=?', (dept_id, block_id, room_id))

# Insert pre-defined rooms/faculty if missing (idempotent)
rooms = [
    ('201', 'Ramanujan', '2nd', 'CSE', 'S2 CSE', 'Room', 'Dr. Smith, Dr. Rao'),
    ('202', 'Ramanujan', '2nd', 'CSE', 'S4 CSE', 'Room', 'Dr. Kumar, Dr. Mehta'),
    ('203', 'Ramanujan', '2nd', 'CSE', 'S6 CSE', 'Room', 'Dr. Iyer'),
    ('101', 'Ramanujan', '1st', 'EEE', 'S2 EEE', 'Room', 'Dr. Ramesh, Dr. Patel'),
    ('102', 'Ramanujan', '1st', 'EEE', 'S4 EEE', 'Room', 'Dr. Verma'),
    ('M201', 'Muthoot M George', '2nd', 'CE', 'S2 CE', 'Room', 'Prof. John, Prof. Mathew'),
    ('M202', 'Muthoot M George', '2nd', 'CE', 'S4 CE', 'Room', 'Prof. Abraham'),
    ('M301', 'Muthoot M George', '3rd', 'MECH', 'S2 MECH', 'Room', 'Dr. George, Dr. Varghese'),
    ('M302', 'Muthoot M George', '3rd', 'MECH', 'S4 MECH', 'Room', 'Dr. Philip'),
    ('M101', 'Muthoot M George', '1st', 'ECE', 'S2 ECE', 'Room', 'Dr. Alex, Dr. Jose'),
    ('M102', 'Muthoot M George', '1st', 'ECE', 'S4 ECE', 'Room', 'Dr. Mathew'),
    ('M303', 'Muthoot M George', '3rd', 'MECH', 'S6 MECH', 'Room', 'Mr. Thomas'),
    ('M103', 'Muthoot M George', '1st', 'ECE', 'S6 ECE', 'Room', 'Dr. Joseph'),
    ('M104', 'Muthoot M George', '1st', 'ECE', 'MPMC Lab', 'Lab', 'Dr. Alex'),
    ('M105', 'Muthoot M George', '1st', 'ECE', 'Analog Logical Circuit Lab', 'Lab', 'Dr. Jose'),
    ('M203', 'Muthoot M George', '2nd', 'CE', 'Geo Technical lab', 'Lab', 'Prof. John'),
    ('M304', 'Muthoot M George', '3rd', 'MECH', 'Heat engines lab', 'Lab', 'Dr. George'),
    ('103', 'Ramanujan', '1st', 'EEE', 'Lab EEE 1', 'Lab', 'Dr. Ramesh'),
    ('204', 'Ramanujan', '2nd', 'CSE', 'CCF 1', 'Lab', 'Dr. Smith'),
    ('205', 'Ramanujan', '2nd', 'CSE', 'Foss Lab', 'Lab', 'Dr. Rao'),
    ('M107', 'Muthoot M George', '1', 'Civil', '', 'Room', 'Sandeep'),
]


for r in rooms:
    # Update existing seed entries (match by department + class_name), or insert if missing
    room_name, block, floor, department, class_name, typ, faculty = r
    c.execute("SELECT room_id FROM rooms WHERE department=? AND class_name=?", (department, class_name))
    existing = c.fetchone()
    if existing:
        # update to ensure fields (room_name, block, floor, type, faculty_name) match the seed
        room_id = existing[0]
        c.execute('''
            UPDATE rooms
            SET room_name=?, block=?, floor=?, type=?, faculty_name=?
            WHERE room_id=?
        ''', (room_name, block, floor, typ, faculty, room_id))
    else:
        c.execute('''
            INSERT INTO rooms (room_name, block, floor, department, class_name, type, faculty_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (room_name, block, floor, department, class_name, typ, faculty))

# Commit and close
conn.commit()
conn.close()

print("Database and tables created/updated successfully with seed data.")
