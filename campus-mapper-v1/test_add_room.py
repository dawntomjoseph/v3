"""
Quick test script to verify dropdown values are being inserted correctly
"""
import sqlite3

DB = 'campus.db'

print("Testing dropdown values in database...")
print("\n1. Checking departments table:")
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT * FROM departments")
depts = c.fetchall()
for d in depts:
    print(f"   ID: {d[0]}, Code: {d[1]}, Name: {d[2]}")

print("\n2. Checking blocks table:")
c.execute("SELECT * FROM blocks")
blocks = c.fetchall()
for b in blocks:
    print(f"   ID: {b[0]}, Name: {b[1]}")

print("\n3. Checking recent rooms with department_id and block_id:")
c.execute("""
    SELECT r.room_id, r.room_name, r.department, r.block, r.department_id, r.block_id,
           d.code as dept_code, b.name as block_name
    FROM rooms r
    LEFT JOIN departments d ON r.department_id = d.dept_id
    LEFT JOIN blocks b ON r.block_id = b.block_id
    ORDER BY r.room_id DESC
    LIMIT 5
""")
rooms = c.fetchall()
print("\n   Recent 5 rooms:")
for r in rooms:
    print(f"   Room ID: {r[0]}")
    print(f"      Name: {r[1]}")
    print(f"      Dept (text): {r[2]}, Dept ID: {r[4]} -> Resolved: {r[6]}")
    print(f"      Block (text): {r[3]}, Block ID: {r[5]} -> Resolved: {r[7]}")
    print()

conn.close()
print("✓ Test complete!")
