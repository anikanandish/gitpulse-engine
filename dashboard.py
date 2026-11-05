"""Enhanced Dashboard HTML generator for GitPulse Engine."""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GitPulse Engine - Real-Time Telemetry & Operations Dashboard</title>
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --card-hover: #1c2128;
      --border: #30363d;
      --text: #c9d1d9;
      --text-muted: #8b949e;
      --heading: #f0f6fc;
      --accent: #58a6ff;
      --accent-bg: rgba(56, 139, 253, 0.15);
      --success: #3fb950;
      --success-bg: rgba(63, 185, 80, 0.15);
      --warning: #d29922;
      --warning-bg: rgba(210, 153, 34, 0.15);
      --danger: #f85149;
      --danger-bg: rgba(248, 81, 73, 0.15);
      --purple: #bc8cff;
      --purple-bg: rgba(188, 140, 255, 0.15);
      --orange: #f0883e;
      --orange-bg: rgba(240, 136, 62, 0.15);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      padding: 24px;
      line-height: 1.5;
    }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }

    /* Header */
    .header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }
    .header-left {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .brand-title {
      color: var(--heading);
      font-size: 1.6rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .pulse-dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: var(--success);
      box-shadow: 0 0 10px var(--success);
      animation: pulse 2s infinite ease-in-out;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(0.85); }
    }
    .system-status-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.8rem;
      color: var(--text-muted);
    }
    .system-status-pill strong { color: var(--heading); }

    .header-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }
    button, .btn {
      background: #21262d;
      border: 1px solid var(--border);
      color: var(--heading);
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }
    button:hover, .btn:hover { background: #30363d; border-color: #8b949e; }
    .btn-primary { background: #238636; border-color: #2ea043; color: #fff; }
    .btn-primary:hover { background: #2ea043; }
    .btn-outline-danger { border-color: var(--danger); color: var(--danger); }
    .btn-outline-danger:hover { background: var(--danger-bg); }
    .btn-sm { padding: 3px 9px; font-size: 0.78rem; border-radius: 4px; }
    .btn-replay { background: var(--accent-bg); border-color: var(--accent); color: var(--accent); }
    .btn-replay:hover { background: rgba(56, 139, 253, 0.3); }

    /* Metrics Grid */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .metric-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      transition: transform 0.15s, border-color 0.15s;
    }
    .metric-card:hover {
      transform: translateY(-2px);
      border-color: #8b949e;
    }
    .metric-card h3 {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 8px;
    }
    .metric-card .value {
      font-size: 2rem;
      font-weight: 700;
      color: var(--heading);
    }

    /* Analytics Leaderboards */
    .analytics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .analytics-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px;
    }
    .analytics-card h2 {
      font-size: 1rem;
      color: var(--heading);
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .rank-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .rank-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 10px;
      background: #0d1117;
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 0.85rem;
    }
    .rank-badge {
      display: inline-block;
      min-width: 20px;
      text-align: center;
      color: var(--accent);
      font-weight: 700;
      margin-right: 8px;
    }
    .rank-count {
      background: #21262d;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.75rem;
      color: var(--heading);
      font-weight: 600;
    }

    /* Filter Toolbar */
    .filter-toolbar {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px 16px;
      margin-bottom: 16px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 12px;
    }
    .filter-input {
      background: #0d1117;
      border: 1px solid var(--border);
      color: var(--heading);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.85rem;
      outline: none;
    }
    .filter-input:focus { border-color: var(--accent); }
    .filter-select {
      background: #0d1117;
      border: 1px solid var(--border);
      color: var(--heading);
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 0.85rem;
      outline: none;
    }

    /* Events Table */
    .table-container {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow-x: auto;
    }
    .table-title {
      padding: 16px;
      border-bottom: 1px solid var(--border);
      font-size: 1.1rem;
      color: var(--heading);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.88rem;
    }
    th, td {
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      vertical-align: middle;
    }
    th {
      background: #11141a;
      color: var(--text-muted);
      font-weight: 600;
    }
    tr:hover { background: var(--card-hover); }
    .tag {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 600;
    }
    .tag-push { background: var(--accent-bg); color: var(--accent); border: 1px solid rgba(88, 166, 255, 0.3); }
    .tag-pull_request { background: var(--purple-bg); color: var(--purple); border: 1px solid rgba(188, 140, 255, 0.3); }
    .tag-issues { background: var(--success-bg); color: var(--success); border: 1px solid rgba(63, 185, 80, 0.3); }
    .tag-workflow_run { background: var(--warning-bg); color: var(--warning); border: 1px solid rgba(210, 153, 34, 0.3); }
    .tag-release { background: var(--orange-bg); color: var(--orange); border: 1px solid rgba(240, 136, 62, 0.3); }
    .tag-ping { background: rgba(110, 118, 129, 0.2); color: var(--text-muted); border: 1px solid rgba(110, 118, 129, 0.3); }
    .tag-default { background: #30363d; color: var(--text); }
    .timestamp { font-size: 0.78rem; color: var(--text-muted); }

    /* Modal */
    .modal-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.75);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 20px;
    }
    .modal-content {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      max-width: 750px;
      width: 100%;
      max-height: 85vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 12px 30px rgba(0,0,0,0.5);
    }
    .modal-header {
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .modal-header h2 { font-size: 1.15rem; color: var(--heading); }
    .modal-body {
      padding: 20px;
      overflow-y: auto;
      font-size: 0.9rem;
    }
    .modal-footer {
      padding: 12px 20px;
      border-top: 1px solid var(--border);
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }
    .payload-pre {
      background: #0d1117;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 12px;
      font-family: monospace;
      font-size: 0.82rem;
      max-height: 350px;
      overflow-y: auto;
      color: #79c0ff;
      white-space: pre-wrap;
      word-break: break-all;
    }

    /* Toast */
    .toast-container {
      position: fixed;
      bottom: 24px;
      right: 24px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      z-index: 2000;
    }
    .toast {
      background: #21262d;
      border: 1px solid var(--border);
      color: var(--heading);
      padding: 10px 16px;
      border-radius: 6px;
      font-size: 0.85rem;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      animation: slideIn 0.25s ease-out;
    }
    .toast-success { border-color: var(--success); }
    .toast-error { border-color: var(--danger); }
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  </style>
</head>
<body>
  <!-- Header -->
  <div class="header">
    <div class="header-left">
      <div class="brand-title">
        <span class="pulse-dot"></span> GitPulse Engine
      </div>
      <div class="system-status-pill">
        <span id="sys-status" style="color:var(--success);">● Healthy</span>
        <span>•</span>
        <span>Uptime: <strong id="sys-uptime">0s</strong></span>
        <span>•</span>
        <span>DB: <strong id="sys-db">Connected</strong></span>
        <span>•</span>
        <span id="dlq-badge" style="cursor:pointer;" onclick="openDlqModal()">DLQ: <strong id="sys-dlq">0</strong></span>
      </div>
    </div>
    <div class="header-actions">
      <span id="last-updated" style="font-size:0.8rem;color:var(--text-muted);margin-right:6px;">Syncing...</span>
      <button onclick="toggleAutoRefresh()" id="btn-autorefresh">Auto-Refresh: ON</button>
      <button onclick="fetchData()">Refresh Now</button>
      <a class="btn" href="/events/export?format=csv" target="_blank" download="gitpulse-events.csv">Export CSV</a>
      <a class="btn" href="/events/export?format=json" target="_blank">Export JSON</a>
      <button class="btn-outline-danger btn-sm" onclick="confirmResetMetrics()">Reset Stats</button>
    </div>
  </div>

  <!-- Metric Counters -->
  <div class="metrics-grid">
    <div class="metric-card">
      <h3>Total Events</h3>
      <div class="value" id="total-events">0</div>
    </div>
    <div class="metric-card">
      <h3>Pushes</h3>
      <div class="value" id="pushes">0</div>
    </div>
    <div class="metric-card">
      <h3>Pull Requests</h3>
      <div class="value" id="pull-requests">0</div>
    </div>
    <div class="metric-card">
      <h3>Issues</h3>
      <div class="value" id="issues">0</div>
    </div>
    <div class="metric-card">
      <h3>Workflows</h3>
      <div class="value" id="workflows">0</div>
    </div>
    <div class="metric-card">
      <h3>Releases</h3>
      <div class="value" id="releases">0</div>
    </div>
  </div>

  <!-- Analytics Leaderboards -->
  <div class="analytics-grid">
    <div class="analytics-card">
      <h2><span>Active Repositories</span><span style="font-size:0.8rem;color:var(--text-muted);">Top Volume</span></h2>
      <ul class="rank-list" id="top-repos-list">
        <li style="color:var(--text-muted);font-size:0.85rem;">No repositories recorded yet.</li>
      </ul>
    </div>
    <div class="analytics-card">
      <h2><span>Top Contributors</span><span style="font-size:0.8rem;color:var(--text-muted);">Activity Volume</span></h2>
      <ul class="rank-list" id="top-senders-list">
        <li style="color:var(--text-muted);font-size:0.85rem;">No contributors recorded yet.</li>
      </ul>
    </div>
  </div>

  <!-- Filter & Search Toolbar -->
  <div class="filter-toolbar">
    <input type="text" id="search-query" class="filter-input" placeholder="Search summaries, repos, authors..." style="flex:1;min-width:220px;" onkeydown="if(event.key==='Enter') executeSearch()">
    <select id="type-filter" class="filter-select" onchange="executeFilter()">
      <option value="">All Event Types</option>
      <option value="push">Push</option>
      <option value="pull_request">Pull Request</option>
      <option value="issues">Issues</option>
      <option value="workflow_run">Workflow Run</option>
      <option value="release">Release</option>
      <option value="ping">Ping</option>
    </select>
    <button onclick="executeSearch()">Search</button>
    <button onclick="clearFilters()">Reset Filters</button>
  </div>

  <!-- Events Stream Table -->
  <div class="table-container">
    <div class="table-title">
      <span>Live Ingested Events Stream</span>
      <span id="event-count" style="font-size:0.85rem;color:var(--text-muted);">0 recorded</span>
    </div>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Type</th>
          <th>Repository</th>
          <th>Sender</th>
          <th>Summary</th>
          <th>Received</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody id="events-body">
        <tr><td colspan="7" style="text-align:center;color:var(--text-muted);">Loading events...</td></tr>
      </tbody>
    </table>
  </div>

  <!-- Event Detail Modal -->
  <div class="modal-overlay" id="event-modal" onclick="if(event.target===this) closeModal()">
    <div class="modal-content">
      <div class="modal-header">
        <h2 id="modal-title">Event Inspection</h2>
        <button onclick="closeModal()">&times;</button>
      </div>
      <div class="modal-body">
        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(180px, 1fr));gap:12px;margin-bottom:16px;">
          <div><span style="color:var(--text-muted);font-size:0.8rem;">EVENT TYPE</span><br><strong id="m-type">-</strong></div>
          <div><span style="color:var(--text-muted);font-size:0.8rem;">REPOSITORY</span><br><strong id="m-repo">-</strong></div>
          <div><span style="color:var(--text-muted);font-size:0.8rem;">SENDER</span><br><strong id="m-sender">-</strong></div>
          <div><span style="color:var(--text-muted);font-size:0.8rem;">TIMESTAMP</span><br><strong id="m-time">-</strong></div>
        </div>
        <div style="margin-bottom:16px;">
          <span style="color:var(--text-muted);font-size:0.8rem;">SUMMARY</span>
          <div id="m-summary" style="background:#0d1117;padding:8px 12px;border:1px solid var(--border);border-radius:6px;margin-top:4px;"></div>
        </div>
        <div>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <span style="color:var(--text-muted);font-size:0.8rem;">PAYLOAD JSON</span>
            <button class="btn-sm" onclick="copyModalPayload()">Copy JSON</button>
          </div>
          <pre class="payload-pre" id="m-payload"></pre>
        </div>
      </div>
      <div class="modal-footer">
        <button id="modal-replay-btn" class="btn-replay">Replay Event</button>
        <button onclick="closeModal()">Close</button>
      </div>
    </div>
  </div>

  <!-- DLQ Modal -->
  <div class="modal-overlay" id="dlq-modal" onclick="if(event.target===this) closeDlqModal()">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Dead-Letter Queue (DLQ) Inspector</h2>
        <button onclick="closeDlqModal()">&times;</button>
      </div>
      <div class="modal-body" id="dlq-body">
        <p style="color:var(--text-muted);">Loading DLQ items...</p>
      </div>
      <div class="modal-footer">
        <button class="btn-outline-danger" onclick="clearDlq()">Clear DLQ</button>
        <button onclick="closeDlqModal()">Close</button>
      </div>
    </div>
  </div>

  <!-- Toast notification container -->
  <div class="toast-container" id="toast-container"></div>

  <script>
    let autoRefresh = true;
    let refreshInterval = null;
    let currentPayloadJson = "";

    function showToast(message, type = 'info') {
      const container = document.getElementById('toast-container');
      const toast = document.createElement('div');
      toast.className = `toast ${type === 'success' ? 'toast-success' : type === 'error' ? 'toast-error' : ''}`;
      toast.innerText = message;
      container.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
      }, 3500);
    }

    function toggleAutoRefresh() {
      autoRefresh = !autoRefresh;
      const btn = document.getElementById('btn-autorefresh');
      if (autoRefresh) {
        btn.innerText = 'Auto-Refresh: ON';
        btn.style.borderColor = 'var(--success)';
        refreshInterval = setInterval(fetchData, 5000);
        showToast('Auto-refresh resumed (5s interval)');
      } else {
        btn.innerText = 'Auto-Refresh: OFF';
        btn.style.borderColor = 'var(--border)';
        clearInterval(refreshInterval);
        showToast('Auto-refresh paused');
      }
    }

    function formatUptime(seconds) {
      if (seconds === undefined || seconds === null) return '0s';
      const sec = Math.floor(seconds);
      if (sec < 60) return `${sec}s`;
      const mins = Math.floor(sec / 60);
      if (mins < 60) return `${mins}m ${sec % 60}s`;
      const hrs = Math.floor(mins / 60);
      return `${hrs}h ${mins % 60}m`;
    }

    async function fetchData() {
      try {
        const [mRes, eRes, hRes, lRes] = await Promise.all([
          fetch('/metrics'),
          fetch('/events?limit=30'),
          fetch('/health'),
          fetch('/analytics/leaderboard?limit=5')
        ]);

        const mData = await mRes.json();
        const eData = await eRes.json();
        const hData = await hRes.json();
        const lData = await lRes.json();

        // 1. Telemetry Counters
        const t = mData.telemetry || {};
        document.getElementById('total-events').innerText = t.total_events || 0;
        document.getElementById('pushes').innerText = t.pushes || 0;
        document.getElementById('pull-requests').innerText = t.pull_requests || 0;
        document.getElementById('issues').innerText = t.issues || 0;
        document.getElementById('workflows').innerText = t.workflow_runs || 0;
        document.getElementById('releases').innerText = t.releases || 0;

        // 2. Health & Status
        document.getElementById('sys-status').innerHTML = hData.status === 'healthy'
          ? '<span style="color:var(--success);">● Healthy</span>'
          : '<span style="color:var(--danger);">● Degraded</span>';
        document.getElementById('sys-uptime').innerText = formatUptime(hData.uptime_seconds);
        document.getElementById('sys-db').innerText = hData.database?.database === 'connected' ? 'Connected' : 'Error';
        const dlqCount = hData.database?.dlq_count || 0;
        document.getElementById('sys-dlq').innerText = dlqCount;
        document.getElementById('sys-dlq').style.color = dlqCount > 0 ? 'var(--danger)' : 'var(--heading)';

        // 3. Analytics Leaderboard
        renderLeaderboards(lData.analytics || {});

        // 4. Events Stream
        renderEventsTable(eData.events || [], eData.total);

        document.getElementById('last-updated').innerText = `Synced at ${new Date().toLocaleTimeString()}`;
      } catch (err) {
        console.error('Fetch error:', err);
      }
    }

    function renderLeaderboards(analytics) {
      const repos = analytics.top_repositories || [];
      const senders = analytics.top_senders || [];

      const repoEl = document.getElementById('top-repos-list');
      if (repos.length === 0) {
        repoEl.innerHTML = '<li style="color:var(--text-muted);font-size:0.85rem;">No repositories recorded yet.</li>';
      } else {
        repoEl.innerHTML = repos.map((r, i) => `
          <li class="rank-item">
            <div>
              <span class="rank-badge">#${i + 1}</span>
              <strong>${escapeHtml(r.repository)}</strong>
            </div>
            <span class="rank-count">${r.events_count} events</span>
          </li>
        `).join('');
      }

      const senderEl = document.getElementById('top-senders-list');
      if (senders.length === 0) {
        senderEl.innerHTML = '<li style="color:var(--text-muted);font-size:0.85rem;">No contributors recorded yet.</li>';
      } else {
        senderEl.innerHTML = senders.map((s, i) => `
          <li class="rank-item">
            <div>
              <span class="rank-badge">#${i + 1}</span>
              <span>@${escapeHtml(s.sender)}</span>
            </div>
            <span class="rank-count">${s.events_count} events</span>
          </li>
        `).join('');
      }
    }

    function renderEventsTable(events, total) {
      document.getElementById('event-count').innerText = `${total !== undefined ? total : events.length} recorded`;
      const tbody = document.getElementById('events-body');
      if (events.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--text-muted);">No webhook events recorded yet. Send a test webhook to populate.</td></tr>';
      } else {
        tbody.innerHTML = events.map(e => `
          <tr>
            <td>#${e.id}</td>
            <td><span class="tag tag-${e.event_type || 'default'}">${e.event_type}</span></td>
            <td><strong>${escapeHtml(e.repository)}</strong></td>
            <td>@${escapeHtml(e.sender)}</td>
            <td>${escapeHtml(e.summary)}</td>
            <td class="timestamp">${formatTime(e.created_at)}</td>
            <td>
              <div style="display:flex;gap:6px;">
                <button class="btn-sm" onclick="inspectEvent(${e.id})">Inspect</button>
                <button class="btn-replay btn-sm" onclick="replayEvent(${e.id})">Replay</button>
              </div>
            </td>
          </tr>
        `).join('');
      }
    }

    async function executeFilter() {
      const type = document.getElementById('type-filter').value;
      let url = '/events?limit=30';
      if (type) url += `&event_type=${encodeURIComponent(type)}`;
      try {
        const res = await fetch(url);
        const data = await res.json();
        renderEventsTable(data.events || [], data.total);
      } catch (err) {
        showToast('Filter error: ' + err, 'error');
      }
    }

    async function executeSearch() {
      const q = document.getElementById('search-query').value.trim();
      if (!q) {
        return executeFilter();
      }
      try {
        const res = await fetch(`/events/search?q=${encodeURIComponent(q)}`);
        if (!res.ok) throw new Error('Search failed');
        const data = await res.json();
        renderEventsTable(data.results || [], data.total_matches);
        showToast(`Found ${data.total_matches} matches for "${q}"`);
      } catch (err) {
        showToast('Search error: ' + err, 'error');
      }
    }

    function clearFilters() {
      document.getElementById('search-query').value = '';
      document.getElementById('type-filter').value = '';
      fetchData();
      showToast('Filters reset');
    }

    async function inspectEvent(id) {
      try {
        const res = await fetch(`/events/${id}`);
        if (!res.ok) throw new Error('Failed to load event details');
        const ev = await res.json();

        document.getElementById('modal-title').innerText = `Event #${ev.id} Inspection`;
        document.getElementById('m-type').innerText = ev.event_type;
        document.getElementById('m-repo').innerText = ev.repository;
        document.getElementById('m-sender').innerText = '@' + ev.sender;
        document.getElementById('m-time').innerText = formatTime(ev.created_at);
        document.getElementById('m-summary').innerText = ev.summary;

        currentPayloadJson = JSON.stringify(ev.payload || {}, null, 2);
        document.getElementById('m-payload').innerText = currentPayloadJson;

        document.getElementById('modal-replay-btn').onclick = () => {
          replayEvent(ev.id);
          closeModal();
        };

        document.getElementById('event-modal').style.display = 'flex';
      } catch (err) {
        showToast('Inspection error: ' + err, 'error');
      }
    }

    function closeModal() {
      document.getElementById('event-modal').style.display = 'none';
    }

    async function openDlqModal() {
      try {
        const res = await fetch('/dlq?limit=25');
        const data = await res.json();
        const items = data.dlq || [];
        const body = document.getElementById('dlq-body');
        if (items.length === 0) {
          body.innerHTML = '<p style="color:var(--success);">Dead-Letter Queue is empty! No delivery failures recorded.</p>';
        } else {
          body.innerHTML = `
            <p style="margin-bottom:12px;color:var(--text-muted);">${items.length} failed delivery events recorded:</p>
            <div style="display:flex;flex-direction:column;gap:10px;">
              ${items.map(it => `
                <div style="background:#0d1117;border:1px solid var(--border);border-radius:6px;padding:10px;">
                  <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <strong style="color:var(--danger);">${escapeHtml(it.event_type)}</strong>
                    <span style="font-size:0.75rem;color:var(--text-muted);">${formatTime(it.created_at)}</span>
                  </div>
                  <div style="font-size:0.85rem;color:var(--heading);">Reason: ${escapeHtml(it.error_reason)}</div>
                </div>
              `).join('')}
            </div>
          `;
        }
        document.getElementById('dlq-modal').style.display = 'flex';
      } catch (err) {
        showToast('Failed to open DLQ: ' + err, 'error');
      }
    }

    function closeDlqModal() {
      document.getElementById('dlq-modal').style.display = 'none';
    }

    async function clearDlq() {
      try {
        const res = await fetch('/dlq/clear', { method: 'POST' });
        if (res.ok) {
          showToast('Dead-Letter Queue cleared successfully!', 'success');
          closeDlqModal();
          fetchData();
        } else {
          showToast('Failed to clear DLQ', 'error');
        }
      } catch (err) {
        showToast('Error: ' + err, 'error');
      }
    }

    function copyModalPayload() {
      if (!currentPayloadJson) return;
      navigator.clipboard.writeText(currentPayloadJson).then(() => {
        showToast('Payload copied to clipboard!', 'success');
      }).catch(err => {
        showToast('Copy failed: ' + err, 'error');
      });
    }

    async function replayEvent(id) {
      try {
        const res = await fetch(`/events/${id}/replay`, { method: 'POST' });
        if (res.ok) {
          showToast(`Event #${id} replayed successfully!`, 'success');
          fetchData();
        } else {
          showToast(`Failed to replay event #${id}`, 'error');
        }
      } catch (err) {
        showToast(`Error replaying event: ${err}`, 'error');
      }
    }

    async function confirmResetMetrics() {
      if (!confirm('Are you sure you want to reset all telemetry metrics and purge event history?')) return;
      try {
        const res = await fetch('/metrics/reset', { method: 'POST' });
        if (res.ok) {
          showToast('Metrics reset successfully!', 'success');
          fetchData();
        } else {
          showToast('Failed to reset metrics', 'error');
        }
      } catch (err) {
        showToast('Reset failed: ' + err, 'error');
      }
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function formatTime(isoStr) {
      if (!isoStr) return '-';
      try {
        return new Date(isoStr).toLocaleTimeString();
      } catch {
        return isoStr;
      }
    }

    fetchData();
    refreshInterval = setInterval(fetchData, 5000);
  </script>
</body>
</html>
"""


def get_dashboard_html() -> str:
    """Return dashboard HTML content."""
    return DASHBOARD_HTML
