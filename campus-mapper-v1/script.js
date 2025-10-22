// Admin login
function openAdminLogin() { document.getElementById('adminModal').style.display = 'flex'; }
function closeAdminLogin() { document.getElementById('adminModal').style.display = 'none'; }
function openAdminPanel() {
    document.getElementById('adminPanel').style.display = 'flex';
    // default to Add tab when opening
    showAdminTab('add');
    // fetch rooms in background so view tab is ready
    fetchRooms();
    // populate department and block selects
    populateSelects();
}
function closeAdminPanel() { document.getElementById('adminPanel').style.display = 'none'; }

function showAdminTab(tab) {
    const addPanel = document.getElementById('adminAdd');
    const viewPanel = document.getElementById('adminView');
    const addBtn = document.getElementById('tabAddBtn');
    const viewBtn = document.getElementById('tabViewBtn');
    if (tab === 'add') {
        addPanel.style.display = 'block';
        viewPanel.style.display = 'none';
        addBtn.classList.add('active');
        viewBtn.classList.remove('active');
    } else {
        addPanel.style.display = 'none';
        viewPanel.style.display = 'block';
        addBtn.classList.remove('active');
        viewBtn.classList.add('active');
        // ensure rooms are refreshed when viewing
        fetchRooms();
    }
}

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    fetch('http://127.0.0.1:5000/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password }) })
        .then(res => res.json()).then(data => {
            if (data.success) { closeAdminLogin(); openAdminPanel(); }
            else { document.getElementById('loginMessage').innerText = 'Invalid username or password'; }
        });
}

// Admin panel
function fetchRooms() {
    fetch('http://127.0.0.1:5000/rooms').then(res => res.json()).then(data => {
        const tbody = document.querySelector('#roomsTable tbody'); tbody.innerHTML = '';
        data.forEach(r => {
            const row = document.createElement('tr');
            // prefer joined names (block_name, department_name) when available
            const blockLabel = r.block_name || r.block || '';
            const deptLabel = r.department_name || r.department || '';
            row.innerHTML = `<td>${r.room_id}</td><td>${r.room_name}</td><td>${blockLabel}</td><td>${r.floor}</td><td>${deptLabel}</td><td>${r.class_name}</td><td>${r.type}</td><td>${r.faculty_name}</td><td><button onclick="deleteRoom(${r.room_id})">Delete</button></td>`;
            tbody.appendChild(row);
        });
    });
}

function addRoom() {
    const room_name = document.getElementById('room_name').value;
    const floor = document.getElementById('floor').value;
    const class_name = document.getElementById('class_name').value;
    const type = document.getElementById('type').value;
    const faculty_name = document.getElementById('faculty_name').value;
    const deptSelect = document.getElementById('department_select');
    const blockSelect = document.getElementById('block_select');
    const deptId = deptSelect ? deptSelect.value : null;
    const blockId = blockSelect ? blockSelect.value : null;
    // fallback to text inputs if selects are not used
    const deptText = document.getElementById('department') ? document.getElementById('department').value : '';
    const blockText = document.getElementById('block') ? document.getElementById('block').value : '';

    const payload = {
        room_name,
        floor,
        class_name,
        type,
        faculty_name
    };
    if (deptId) payload.department_id = parseInt(deptId);
    else if (deptText) payload.department = deptText;
    if (blockId) payload.block_id = parseInt(blockId);
    else if (blockText) payload.block = blockText;

    fetch('http://127.0.0.1:5000/add-room', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
        .then(() => {
            fetchRooms();
            // reset fields
            document.getElementById('room_name').value = '';
            if (blockSelect) blockSelect.selectedIndex = 0;
            if (deptSelect) deptSelect.selectedIndex = 0;
            if (document.getElementById('block')) document.getElementById('block').value = '';
            document.getElementById('floor').value = '';
            if (document.getElementById('department')) document.getElementById('department').value = '';
            document.getElementById('class_name').value = '';
            document.getElementById('faculty_name').value = '';
        });
}

// populate department and block selects used by the admin Add form
function populateSelects() {
    // departments
    fetch('http://127.0.0.1:5000/departments').then(res => res.json()).then(data => {
        const dept = document.getElementById('department_select');
        if (!dept) return;
        // clear existing (preserve first placeholder)
        dept.innerHTML = '<option value="">Select Department</option>';
        data.forEach(d => {
            const opt = document.createElement('option');
            opt.value = d.dept_id || d.id || d.id;
            opt.text = (d.code ? d.code + ' - ' : '') + (d.name || '');
            dept.appendChild(opt);
        });
    }).catch(() => { });

    // blocks
    fetch('http://127.0.0.1:5000/blocks').then(res => res.json()).then(data => {
        const blk = document.getElementById('block_select');
        if (!blk) return;
        blk.innerHTML = '<option value="">Select Block</option>';
        data.forEach(b => {
            const opt = document.createElement('option');
            opt.value = b.block_id || b.id || b.block_id;
            opt.text = b.name || '';
            blk.appendChild(opt);
        });
    }).catch(() => { });
}

function deleteRoom(id) { fetch(`http://127.0.0.1:5000/rooms/${id}`, { method: 'DELETE' }).then(() => fetchRooms()); }

// Search
function search() {
    const q = document.getElementById('search').value;
    const loading = document.getElementById('resultsLoading');
    const message = document.getElementById('resultsMessage');
    const list = document.getElementById('resultsList');
    const table = document.getElementById('resultsTable');
    const header = document.getElementById('resultsHeader');
    // ui state
    message.style.display = 'none';
    loading.style.display = 'block';
    list.innerHTML = '';
    if (header) header.style.display = 'none';
    fetch(`http://127.0.0.1:5000/search?q=${encodeURIComponent(q)}`)
        .then(res => res.json())
        .then(data => {
            loading.style.display = 'none';
            if (!data || data.length === 0) {
                document.getElementById('resultsSection').style.display = 'block';
                table.style.display = 'none';
                list.style.display = 'none';
                if (header) header.style.display = 'none';
                message.innerText = 'No results found';
                message.style.display = 'block';
                return;
            }
            document.getElementById('resultsSection').style.display = 'block';
            list.style.display = 'block';
            table.style.display = 'none';
            if (header) header.style.display = 'flex';
            data.forEach(r => {
                const blockLabel = r.block_name || r.block || '';
                const deptLabel = r.department_name || r.department || '';
                const card = document.createElement('div');
                card.className = 'result-card';
                card.dataset.roomId = r.room_id;
                card.innerHTML = `<div class="left">${r.room_name}</div>
                                  <div class="meta">
                                    <div class="item">Block: ${blockLabel}</div>
                                    <div class="item">Floor: ${r.floor}</div>
                                    <div class="item">Class: ${r.class_name || ''}</div>
                                  </div>
                                  <div class="tags"><span class="pill">${deptLabel}</span></div>`;
                card.addEventListener('click', () => openRoomModal(r));
                list.appendChild(card);
            });
        })
        .catch(err => {
            loading.style.display = 'none';
            message.innerText = 'Error fetching results';
            message.style.display = 'block';
            console.error('Search error', err);
        });
}

// Department buttons
function showDept(dept) {
    fetch(`http://127.0.0.1:5000/department/${dept}`).then(res => res.json()).then(data => {
        const list = document.getElementById('resultsList');
        const table = document.getElementById('resultsTable');
        const header = document.getElementById('resultsHeader');
        list.innerHTML = '';
        document.getElementById('resultsSection').style.display = 'block';
        list.style.display = 'block';
        table.style.display = 'none';
        if (header) header.style.display = 'flex';
        data.forEach(r => {
            const blockLabel = r.block_name || r.block || '';
            const deptLabel = r.department_name || r.department || '';
            const card = document.createElement('div');
            card.className = 'result-card';
            card.innerHTML = `<div class="left">${r.room_name}</div>
                                  <div class="meta">
                                    <div class="item">Block: ${blockLabel}</div>
                                    <div class="item">Floor: ${r.floor}</div>
                                    <div class="item">Class: ${r.class_name || ''}</div>
                                  </div>
                                  <div class="tags"><span class="pill">${deptLabel}</span></div>`;
            card.dataset.roomId = r.room_id;
            card.addEventListener('click', () => openRoomModal(r));
            list.appendChild(card);
        });
    });
}

function openRoomModal(room) {
    const modal = document.getElementById('roomModal');
    const title = document.getElementById('roomModalTitle');
    const body = document.getElementById('roomModalBody');
    title.innerText = room.room_name + (room.class_name ? ' — ' + room.class_name : '');
    const block = room.block_name || room.block || '';
    const dept = room.department_name || room.department || '';
    body.innerHTML = `<p><strong>Block:</strong> ${block}</p><p><strong>Floor:</strong> ${room.floor}</p><p><strong>Department:</strong> ${dept}</p><p><strong>Type:</strong> ${room.type || ''}</p><p><strong>Faculty:</strong> ${room.faculty_name || ''}</p>`;
    modal.style.display = 'flex';
}

function closeRoomModal() { document.getElementById('roomModal').style.display = 'none'; }

// allow Enter key to trigger search when focus is in the search box
document.addEventListener('keydown', function (e) {
    const el = document.activeElement;
    if (e.key === 'Enter' && el && el.id === 'search') {
        e.preventDefault();
        search();
    }
});

// initialize: populate selects but don't run search automatically
document.addEventListener('DOMContentLoaded', function () {
    try {
        populateSelects();
        // Don't run search on page load - let user initiate search
        // search();
    } catch (e) {
        console.error('Initialization error:', e);
    }
});
