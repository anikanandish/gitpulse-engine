"""Dashboard HTML generator for GitPulse Engine."""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GitPulse Engine - Telemetry Dashboard</title>
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --text: #c9d1d9;
      --heading: #f0f6fc;
      --accent: #58a6ff;
      --success: #3fb950;
      --warning: #d29922;
      --danger: #f85149;
      --purple: #bc8cff;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      padding: 24px;
      line-height: 1.5;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }
    .header h1 {
      color: var(--heading);
      font-size: 1.6rem;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .badge-status {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--success);
      box-shadow: 0 0 8px var(--success);
    }
    .controls {
      display: flex;
      gap: 12px;
      align-items: center;
    }
    button {
      background: #21262d;
      border: 1px solid var(--border);
      color: var(--heading);
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.85rem;
      transition: background 0.2s;
    }
    button:hover { background: #30363d; }
    .btn-replay {
      background: #1f6feb22;
      border-color: #1f6feb;
      color: var(--accent);
      padding: 3px 8px;
      font-size: 0.75rem;
    }
    .btn-replay:hover { background: #1f6feb44; }
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }
    .metric-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      position: relative;
    }
    .metric-card h3 {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #8b949e;
      margin-bottom: 8px;
    }
    .metric-card .value {
      font-size: 1.8rem;
      font-weight: 700;
      color: var(--heading);
    }
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
    }
    th {
      background: #11141a;
      color: #8b949e;
      font-weight: 600;
    }
    tr:hover { background: #1f242c; }
    .tag {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 600;
    }
    .tag-push { background: #1f6feb22; color: var(--accent); border: 1px solid #1f6feb44; }
    .tag-pull_request { background: #8957e522; color: var(--purple); border: 1px solid #8957e544; }
    .tag-issues { background: #23863622; color: var(--success); border: 1px solid #23863644; }
    .tag-workflow_run { background: #9e6a0322; color: var(--warning); border: 1px solid #9e6a0344; }
    .tag-release { background: #f0883e22; color: #f0883e; border: 1px solid #f0883e44; }
    .tag-ping { background: #6e768122; color: #8b949e; border: 1px solid #6e768144; }
    .tag-default { background: #30363d; color: var(--text); }
    .timestamp { font-size: 0.78rem; color: #8b949e; }
  </style>
</head>
<body>
  <div class="header">
    <h1><span class="badge-status"></span> GitPulse Engine &bull; Live Telemetry</h1>
    <div class="controls">
      <span id="last-updated" style="font-size:0.8rem;color:#8b949e;">Updating...</span>
      <button onclick="fetchData()">Refresh Now</button>
    </div>
  </div>

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

  <div class="table-container">
    <div class="table-title">
      <span>Recent Ingested Events</span>
      <span id="event-count" style="font-size:0.85rem;color:#8b949e;">0 events</span>
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
          <th>Action</th>
        </tr>
      </thead>
      <tbody id="events-body">
        <tr><td colspan="7" style="text-align:center;color:#8b949e;">Loading events...</td></tr>
      </tbody>
    </table>
  </div>

  <script>
    async function fetchData() {
      try {
        const [mRes, eRes] = await Promise.all([
          fetch('/metrics'),
          fetch('/events?limit=25')
        ]);
        const mData = await mRes.json();
        const eData = await eRes.json();

        const t = mData.telemetry || {};
        document.getElementById('total-events').innerText = t.total_events || 0;
        document.getElementById('pushes').innerText = t.pushes || 0;
        document.getElementById('pull-requests').innerText = t.pull_requests || 0;
        document.getElementById('issues').innerText = t.issues || 0;
        document.getElementById('workflows').innerText = t.workflow_runs || 0;
        document.getElementById('releases').innerText = t.releases || 0;

        const events = eData.events || [];
        document.getElementById('event-count').innerText = `${eData.total || events.length} recorded`;

        const tbody = document.getElementById('events-body');
        if (events.length === 0) {
          tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#8b949e;">No webhook events recorded yet. Send a test webhook to populate.</td></tr>';
        } else {
          tbody.innerHTML = events.map(e => `
            <tr>
              <td>#${e.id}</td>
              <td><span class="tag tag-${e.event_type || 'default'}">${e.event_type}</span></td>
              <td><strong>${escapeHtml(e.repository)}</strong></td>
              <td>@${escapeHtml(e.sender)}</td>
              <td>${escapeHtml(e.summary)}</td>
              <td class="timestamp">${formatTime(e.created_at)}</td>
              <td><button class="btn-replay" onclick="replayEvent(${e.id})">Replay</button></td>
            </tr>
          `).join('');
        }

        document.getElementById('last-updated').innerText = `Synced at ${new Date().toLocaleTimeString()}`;
      } catch (err) {
        console.error('Fetch error:', err);
      }
    }

    async function replayEvent(id) {
      try {
        const res = await fetch(`/events/${id}/replay`, { method: 'POST' });
        if (res.ok) {
          alert(`Event #${id} replayed successfully!`);
          fetchData();
        } else {
          alert(`Failed to replay event #${id}`);
        }
      } catch (err) {
        alert(`Error replaying event: ${err}`);
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
    setInterval(fetchData, 5000);
  </script>
</body>
</html>
"""


def get_dashboard_html() -> str:
    """Return dashboard HTML content."""
    return DASHBOARD_HTML
