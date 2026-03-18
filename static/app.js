const API = '';

// ── Utilities ─────────────────────────────────────────────────────────────────

const fmt = {
  currency: v => v != null ? '$' + Number(v).toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0}) : '—',
  pct:      v => v != null ? v.toFixed(2) + '%' : '—',
  date:     v => v ? new Date(v).toLocaleDateString('en-US') : '—',
  num:      v => v != null ? Number(v).toLocaleString() : '—',
};

function badge(text, cls) {
  return `<span class="badge badge-${cls || text.replace(/\s+/g,'-')}">${text}</span>`;
}

async function api(method, path, body) {
  const res = await fetch(API + path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function setTbody(tableId, rows) {
  document.querySelector(`#${tableId} tbody`).innerHTML = rows.join('');
}

// ── Navigation ────────────────────────────────────────────────────────────────

document.querySelectorAll('.nav-links a').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    const page = a.dataset.page;
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-links a').forEach(l => l.classList.remove('active'));
    document.getElementById('page-' + page).classList.add('active');
    a.classList.add('active');
    if (page === 'dashboard') loadDashboard();
    if (page === 'investors') loadInvestors();
    if (page === 'properties') loadProperties();
  });
});

// ── Dashboard ─────────────────────────────────────────────────────────────────

async function loadDashboard() {
  const [stats, investors, properties] = await Promise.all([
    api('GET', '/api/stats'),
    api('GET', '/api/investors'),
    api('GET', '/api/properties'),
  ]);

  const sg = document.getElementById('stats-grid');
  sg.innerHTML = `
    <div class="stat-card">
      <div class="stat-label">Total Investors</div>
      <div class="stat-value">${stats.total_investors}</div>
      <div class="stat-sub">${stats.active_investors} active</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Total Properties</div>
      <div class="stat-value">${stats.total_properties}</div>
      <div class="stat-sub">${stats.owned_properties} owned</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Portfolio Value</div>
      <div class="stat-value">${fmt.currency(stats.total_portfolio_value)}</div>
      <div class="stat-sub">Total equity: ${fmt.currency(stats.total_equity)}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Monthly Rent</div>
      <div class="stat-value">${fmt.currency(stats.total_monthly_rent)}</div>
      <div class="stat-sub">Annual: ${fmt.currency(stats.total_annual_rent)}</div>
    </div>
  `;

  // Top investors
  const sorted = [...investors].sort((a, b) => b.portfolio_value - a.portfolio_value).slice(0, 8);
  setTbody('top-investors-table', sorted.map(i => `
    <tr>
      <td><a href="#" onclick="viewInvestor(${i.id}); return false;">${i.name}</a></td>
      <td>${badge(i.investor_type || 'individual')}</td>
      <td>${i.property_count}</td>
      <td>${fmt.currency(i.portfolio_value)}</td>
    </tr>
  `));

  // Recent properties
  const recent = [...properties].slice(0, 8);
  setTbody('recent-properties-table', recent.map(p => `
    <tr>
      <td>${p.address}${p.city ? ', ' + p.city : ''}</td>
      <td>${badge(p.property_type || 'residential')}</td>
      <td>${fmt.currency(p.current_value)}</td>
      <td>${badge(p.status, p.status)}</td>
    </tr>
  `));
}

// ── Investors ─────────────────────────────────────────────────────────────────

async function loadInvestors() {
  const q = document.getElementById('investor-search').value;
  const status = document.getElementById('investor-status-filter').value;
  const params = new URLSearchParams();
  if (q) params.set('q', q);
  if (status) params.set('status', status);
  const investors = await api('GET', '/api/investors?' + params);

  setTbody('investors-table', investors.length
    ? investors.map(i => `
      <tr>
        <td><a href="#" onclick="viewInvestor(${i.id}); return false;" style="font-weight:600;color:#6c63ff;">${i.name}</a></td>
        <td>${i.company || '—'}</td>
        <td>${badge(i.investor_type || 'individual')}</td>
        <td>${i.email}</td>
        <td>${i.phone || '—'}</td>
        <td>${i.property_count}</td>
        <td>${fmt.currency(i.portfolio_value)}</td>
        <td>${badge(i.status, i.status)}</td>
        <td>
          <div class="action-btns">
            <button class="btn btn-sm btn-edit" onclick="openInvestorModal(${i.id})">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteInvestor(${i.id})">Delete</button>
          </div>
        </td>
      </tr>`)
    : ['<tr><td colspan="9" style="text-align:center;color:#aaa;padding:30px">No investors found.</td></tr>']
  );
}

let currentInvestorId = null;

function openInvestorModal(id) {
  currentInvestorId = id || null;
  const form = document.getElementById('investor-form');
  form.reset();
  document.getElementById('investor-modal-title').textContent = id ? 'Edit Investor' : 'Add Investor';

  if (id) {
    api('GET', '/api/investors/' + id).then(inv => {
      for (const [k, v] of Object.entries(inv)) {
        const el = form.elements[k];
        if (el && v != null) el.value = v;
      }
    });
  }
  showModal('investor-modal');
}

async function saveInvestor(e) {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form));
  if (currentInvestorId) {
    await api('PUT', '/api/investors/' + currentInvestorId, data);
  } else {
    await api('POST', '/api/investors', data);
  }
  closeModal();
  loadInvestors();
  loadDashboard();
}

async function deleteInvestor(id) {
  if (!confirm('Delete this investor and all their properties?')) return;
  await api('DELETE', '/api/investors/' + id);
  loadInvestors();
  loadDashboard();
}

// ── Investor Drawer ───────────────────────────────────────────────────────────

async function viewInvestor(id) {
  const inv = await api('GET', '/api/investors/' + id);
  document.getElementById('drawer-investor-name').textContent = inv.name;

  const props = inv.properties || [];
  const propRows = props.map(p => `
    <tr>
      <td>${p.address}</td>
      <td>${badge(p.property_type)}</td>
      <td>${fmt.currency(p.current_value)}</td>
      <td>${fmt.currency(p.monthly_rent)}</td>
      <td>${fmt.pct(p.cap_rate)}</td>
      <td>${badge(p.status, p.status)}</td>
      <td>
        <div class="action-btns">
          <button class="btn btn-sm btn-edit" onclick="openPropertyModal(${p.id})">Edit</button>
        </div>
      </td>
    </tr>
  `).join('') || '<tr><td colspan="7" style="color:#aaa;text-align:center">No properties</td></tr>';

  document.getElementById('drawer-body').innerHTML = `
    <div class="detail-section">
      <h3>Contact Info</h3>
      <div class="detail-grid">
        <div class="detail-item"><label>Email</label><span>${inv.email}</span></div>
        <div class="detail-item"><label>Phone</label><span>${inv.phone || '—'}</span></div>
        <div class="detail-item"><label>Company</label><span>${inv.company || '—'}</span></div>
        <div class="detail-item"><label>Type</label><span>${inv.investor_type || '—'}</span></div>
        <div class="detail-item"><label>Status</label><span>${badge(inv.status, inv.status)}</span></div>
        <div class="detail-item"><label>Since</label><span>${fmt.date(inv.created_at)}</span></div>
      </div>
    </div>
    <div class="detail-section">
      <h3>Portfolio Summary</h3>
      <div class="detail-grid">
        <div class="detail-item"><label>Properties</label><span>${inv.property_count}</span></div>
        <div class="detail-item"><label>Portfolio Value</label><span>${fmt.currency(inv.portfolio_value)}</span></div>
      </div>
    </div>
    ${inv.notes ? `<div class="detail-section"><h3>Notes</h3><p style="color:#555;line-height:1.6">${inv.notes}</p></div>` : ''}
    <div class="detail-section">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
        <h3 style="margin:0">Properties</h3>
        <button class="btn btn-sm btn-primary" onclick="openPropertyModal(null, ${inv.id})">+ Add Property</button>
      </div>
      <div style="overflow-x:auto">
        <table>
          <thead><tr><th>Address</th><th>Type</th><th>Value</th><th>Mo. Rent</th><th>Cap Rate</th><th>Status</th><th></th></tr></thead>
          <tbody>${propRows}</tbody>
        </table>
      </div>
    </div>
  `;

  document.getElementById('investor-drawer').classList.remove('hidden');
  document.getElementById('overlay').classList.remove('hidden');
}

// ── Properties ────────────────────────────────────────────────────────────────

async function loadProperties() {
  const status = document.getElementById('property-status-filter').value;
  const type = document.getElementById('property-type-filter').value;
  const params = new URLSearchParams();
  if (status) params.set('status', status);
  if (type) params.set('property_type', type);
  const properties = await api('GET', '/api/properties?' + params);

  setTbody('properties-table', properties.length
    ? properties.map(p => `
      <tr>
        <td>
          <div style="font-weight:600">${p.address}</div>
          <div style="font-size:0.78rem;color:#888">${[p.city, p.state, p.zip_code].filter(Boolean).join(', ')}</div>
        </td>
        <td><a href="#" onclick="viewInvestor(${p.investor_id}); return false;" style="color:#6c63ff">${p.investor_name}</a></td>
        <td>${badge(p.property_type)}</td>
        <td>${fmt.currency(p.purchase_price)}</td>
        <td>${fmt.currency(p.current_value)}</td>
        <td style="color:${(p.equity||0)>=0?'#2e7d32':'#c62828'}">${fmt.currency(p.equity)}</td>
        <td>${fmt.currency(p.monthly_rent)}</td>
        <td>${fmt.pct(p.cap_rate)}</td>
        <td>${badge(p.status, p.status)}</td>
        <td>
          <div class="action-btns">
            <button class="btn btn-sm btn-edit" onclick="openPropertyModal(${p.id})">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteProperty(${p.id})">Delete</button>
          </div>
        </td>
      </tr>`)
    : ['<tr><td colspan="10" style="text-align:center;color:#aaa;padding:30px">No properties found.</td></tr>']
  );
}

let currentPropertyId = null;

async function openPropertyModal(id, preselectedInvestorId) {
  currentPropertyId = id || null;
  const form = document.getElementById('property-form');
  form.reset();
  document.getElementById('property-modal-title').textContent = id ? 'Edit Property' : 'Add Property';

  // Populate investor dropdown
  const investors = await api('GET', '/api/investors');
  const sel = document.getElementById('property-investor-select');
  sel.innerHTML = investors.map(i => `<option value="${i.id}">${i.name}</option>`).join('');
  if (preselectedInvestorId) sel.value = preselectedInvestorId;

  if (id) {
    const prop = await api('GET', '/api/properties/' + id);
    for (const [k, v] of Object.entries(prop)) {
      const el = form.elements[k];
      if (el && v != null) el.value = v;
    }
  }
  showModal('property-modal');
}

async function saveProperty(e) {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form));
  // coerce numerics
  ['investor_id','purchase_price','current_value','square_feet','units','monthly_rent'].forEach(k => {
    if (data[k] !== '') data[k] = Number(data[k]);
    else delete data[k];
  });
  if (!data.purchase_date) delete data.purchase_date;

  if (currentPropertyId) {
    await api('PUT', '/api/properties/' + currentPropertyId, data);
  } else {
    await api('POST', '/api/properties', data);
  }
  closeModal();
  loadProperties();
  loadDashboard();
}

async function deleteProperty(id) {
  if (!confirm('Delete this property?')) return;
  await api('DELETE', '/api/properties/' + id);
  loadProperties();
  loadDashboard();
}

// ── Modal helpers ─────────────────────────────────────────────────────────────

function showModal(id) {
  document.getElementById(id).classList.remove('hidden');
  document.getElementById('overlay').classList.remove('hidden');
}

function closeModal() {
  document.getElementById('investor-modal').classList.add('hidden');
  document.getElementById('property-modal').classList.add('hidden');
  if (document.getElementById('investor-drawer').classList.contains('hidden')) {
    document.getElementById('overlay').classList.add('hidden');
  }
}

function closeDrawer() {
  document.getElementById('investor-drawer').classList.add('hidden');
  document.getElementById('overlay').classList.add('hidden');
}

// ── Init ──────────────────────────────────────────────────────────────────────

loadDashboard();
