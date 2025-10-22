# Dropdown Values Not Inserting - FIXED ✓

## Problem
When adding rooms through the admin panel, dropdown values (department_id and block_id) were selected but the corresponding text values were not being stored in the database. This caused rooms to appear blank in searches and display views.

## Root Cause
The database has both:
- **Old columns**: `department` (TEXT), `block` (TEXT)
- **New columns**: `department_id` (INTEGER), `block_id` (INTEGER)

The `add_room()` function was only inserting the ID values but NOT populating the text columns. Since search and display queries relied on the TEXT columns, newly added rooms appeared empty.

## Solution
Updated `app.py` with three key fixes:

### 1. Fixed `/add-room` endpoint
- When `department_id` is provided, look up the corresponding `code` from `departments` table and populate `department` text field
- When `block_id` is provided, look up the corresponding `name` from `blocks` table and populate `block` text field
- Now both ID columns AND text columns are populated correctly

### 2. Enhanced `/search` endpoint
- Added JOINs with `departments` and `blocks` tables
- Search now works across both text fields and normalized table names
- Includes fallback for backwards compatibility

### 3. Enhanced `/department/<dept>` endpoint
- Added JOINs with normalized tables
- Filter works for both text department codes and normalized department IDs
- Includes fallback for backwards compatibility

## Changes Made

### File: `app.py`

**Before:**
```python
# Only inserted IDs, text fields were empty or used stale data
c.execute('''
    INSERT INTO rooms (room_name, block, floor, department, ...)
    VALUES (?, ?, ?, ?, ...)
''', (data.get('room_name'), data.get('block'), data.get('floor'), data.get('department'), ...))
```

**After:**
```python
# Now resolves text values from IDs before inserting
if dept_id:
    c.execute('SELECT code FROM departments WHERE dept_id=?', (dept_id,))
    row = c.fetchone()
    if row:
        dept_text = row[0]
        
if block_id:
    c.execute('SELECT name FROM blocks WHERE block_id=?', (block_id,))
    row = c.fetchone()
    if row:
        block_text = row[0]

c.execute('''
    INSERT INTO rooms (room_name, block, floor, department, ...)
    VALUES (?, ?, ?, ?, ...)
''', (data.get('room_name'), block_text, data.get('floor'), dept_text, ...))
```

## Testing

### To verify the fix:
1. Restart your Flask app:
   ```powershell
   cd C:\Users\ADMIN\Desktop\dawn\v3\campus-mapper-v1
   python app.py
   ```

2. Open the web interface and login as admin (username: `admin`, password: `12345`)

3. Add a new room using the dropdowns:
   - Select a department from the dropdown
   - Select a block from the dropdown
   - Fill in other fields
   - Click "Add Room / Lab"

4. Search for the room you just added - it should now appear with correct department and block values

5. Run the test script to inspect database values:
   ```powershell
   python test_add_room.py
   ```

## What You Should See Now

✓ Dropdown selections are saved correctly
✓ Department text field is populated from department_id
✓ Block text field is populated from block_id
✓ Search results show correct department and block names
✓ Department filter buttons work correctly
✓ Admin "View Rooms" table shows all values

## Additional Notes

- The fix maintains backwards compatibility - if someone uses text inputs instead of dropdowns, those still work
- The search endpoint now searches across both old text fields and new normalized table names
- All queries use LEFT JOINs so they work even if some rooms don't have normalized IDs yet
- Foreign key constraints are enabled to maintain data integrity

## Files Changed
- `app.py` - Updated `/add-room`, `/search`, and `/department/<dept>` endpoints
- `test_add_room.py` - Created test script for verification
