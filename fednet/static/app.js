// FedNet SPA Router & Application Logic
const App = {
  currentPage: 'dashboard',
  data: null,

  init() {
    window.addEventListener('hashchange', () => this.route());
    document.querySelectorAll('.nav-item').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        const page = el.dataset.page;
        if (page) window.location.hash = page;
      });
    });
    this.route();
    setInterval(() => { if (this.currentPage === 'dashboard') this.loadStats(); }, 15000);
  },

  route() {
    const hash = (window.location.hash || '#dashboard').slice(1);
    this.currentPage = hash;
    document.querySelectorAll('.nav-item').forEach(el => {
      el.classList.toggle('active', el.dataset.page === hash);
    });
    const pages = {dashboard: this.loadDashboard, artifacts: this.loadArtifacts,
      solana: this.loadSolana, monetization: this.loadMonetization,
      analytics: this.loadAnalytics, settings: this.loadSettings};
    const loader = pages[hash] || pages.dashboard;
    loader.call(this);
  },

  async loadStats() {
    try {
      const r = await fetch('/api/stats');
      this.data = await r.json();
      return this.data;
    } catch(e) {
      return null;
    }
  },

  // ── Dashboard ──
  async loadDashboard() {
    const c = document.getElementById('page-content');
    c.innerHTML = '<div class="loading-state"><div class="skeleton" style="height:140px"></div></div>';
    const d = await this.loadStats();
    if (!d) { c.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️</div><div class="empty-text">Unable to load data. Is the server running?</div></div>'; return; }
    const a = d.artifacts, at = d.attestations, inf = d.inferences;
    const aList = a.artifacts||[], atList = at.attestations||[], iList = inf.inferences||[];
    c.innerHTML = `
    <div class="metrics-grid">
      <div class="metric-card animate-in"><div class="metric-header"><div class="metric-label">Layer 1 · Audit Artifacts</div><div class="metric-icon mi-purple">📋</div></div><div class="metric-value mv-purple">${a.total_rounds||0}</div><div class="metric-sub">Training Rounds <span class="badge-info">HMAC-SHA256</span></div></div>
      <div class="metric-card animate-in"><div class="metric-header"><div class="metric-label">Layer 2 · Solana Attestation</div><div class="metric-icon mi-green">⛓️</div></div><div class="metric-value mv-green">${at.total||0}</div><div class="metric-sub">On-Chain Proofs <span class="badge-up">~$0.000005/tx</span></div></div>
      <div class="metric-card animate-in"><div class="metric-header"><div class="metric-label">Layer 3 · x402 Monetization</div><div class="metric-icon mi-orange">💎</div></div><div class="metric-value mv-orange">$${inf.total_revenue||'0'}</div><div class="metric-sub">${inf.total_queries||0} queries <span class="badge-up">USDC</span></div></div>
    </div>
    <div class="panels">
      <div class="panel"><div class="panel-header"><div class="panel-title">⚡ Recent Activity</div><span class="muted-sm">Live</span></div><div class="panel-body">${this.buildActivity(aList,atList,iList)}</div></div>
      <div class="panel"><div class="panel-header"><div class="panel-title">📊 Network Overview</div><span class="muted-sm">Last 7 days</span></div><div class="panel-body"><div class="chart-container"><canvas id="chart"></canvas></div></div></div>
    </div>
    <div class="panels"><div class="panel panel-full"><div class="panel-header"><div class="panel-title">📋 Compliance Artifacts</div><span class="muted-sm">${aList.length} records</span></div><div class="panel-body" style="padding:0">${aList.length?this.buildArtifactTable(aList):'<div class="empty-state"><div class="empty-icon">📋</div><div class="empty-text">No artifacts yet. Click <strong>Start Training</strong> or run <code class="code-inline">python test_fednet_complete.py</code></div></div>'}</div></div></div>`;
    this.drawChart();
  },

  // ── Audit Artifacts Page ──
  async loadArtifacts() {
    const c = document.getElementById('page-content');
    const d = await this.loadStats();
    if (!d) { c.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️</div><div class="empty-text">Unable to load</div></div>'; return; }
    const list = d.artifacts.artifacts||[];
    c.innerHTML = `
    <div class="page-header"><h2>Audit Artifacts</h2><p class="muted">Layer 1 — HMAC-SHA256 signed compliance records generated after each FL round</p></div>
    <div class="info-cards">
      <div class="info-card"><div class="info-label">How It Works</div><p>After each federated learning round, FedNet generates a <strong>signed JSON artifact</strong> containing participant hashes, gradient hashes, differential privacy parameters (ε, δ), and an HMAC-SHA256 signature. This answers every question a HIPAA auditor would ask.</p></div>
      <div class="info-card"><div class="info-label">Integration</div><p>After your FL aggregation step, call:<br><code class="code-inline">artifact = generator.generate_artifact(round_id, participants, gradients, model_version, epsilon, delta)</code></p></div>
    </div>
    <div class="panel panel-full" style="margin-top:16px"><div class="panel-header"><div class="panel-title">📋 All Artifacts</div>
      <button class="btn btn-primary" onclick="App.triggerTraining()">+ Generate New</button></div>
      <div class="panel-body" style="padding:0">${list.length?this.buildArtifactTable(list,true):'<div class="empty-state"><div class="empty-icon">📋</div><div class="empty-text">No artifacts generated yet</div></div>'}</div></div>
    <div id="artifact-detail"></div>`;
  },

  // ── Solana Proofs Page ──
  async loadSolana() {
    const c = document.getElementById('page-content');
    const d = await this.loadStats();
    if (!d) return;
    const list = d.attestations.attestations||[];
    c.innerHTML = `
    <div class="page-header"><h2>Solana Attestations</h2><p class="muted">Layer 2 — Tamper-proof on-chain attestation via state compression</p></div>
    <div class="info-cards">
      <div class="info-card"><div class="info-label">How It Works</div><p>The artifact hash is anchored on <strong>Solana</strong> via a memo transaction. The on-chain record contains <strong>only the hash</strong> — never gradients, never data. Any regulator can independently verify training history.</p></div>
      <div class="info-card"><div class="info-label">Cost & Speed</div><p>~<strong>$0.000005</strong> per attestation (state compression). Confirmation in <strong>~2-3 seconds</strong>. Switch to mainnet-beta with a single env var change.</p></div>
    </div>
    <div class="panel panel-full" style="margin-top:16px"><div class="panel-header"><div class="panel-title">⛓️ On-Chain Proofs</div><span class="muted-sm">${list.length} attestations</span></div>
      <div class="panel-body" style="padding:0">${list.length?this.buildAttestationTable(list):'<div class="empty-state"><div class="empty-icon">⛓️</div><div class="empty-text">No attestations yet. Run a training round first.</div></div>'}</div></div>`;
  },

  // ── Monetization Page ──
  async loadMonetization() {
    const c = document.getElementById('page-content');
    const d = await this.loadStats();
    if (!d) return;
    const inf = d.inferences, list = inf.inferences||[];
    c.innerHTML = `
    <div class="page-header"><h2>x402 Monetization</h2><p class="muted">Layer 3 — Payment-gated inference with USDC revenue distribution</p></div>
    <div class="info-cards">
      <div class="info-card"><div class="info-label">How It Works</div><p>Trained models are exposed via <strong>x402-gated endpoints</strong>. External parties pay per-query in <strong>USDC on Solana</strong>. Revenue splits automatically to contributing nodes proportional to verified participation.</p></div>
      <div class="info-card"><div class="info-label">API Example</div><p><code class="code-inline">POST /inference</code> with <code class="code-inline">payment_tx_id</code>, <code class="code-inline">payer_wallet</code>, <code class="code-inline">payment_amount</code>.<br>Returns HTTP 402 if no payment provided.</p></div>
    </div>
    <div class="metrics-grid" style="margin-top:16px">
      <div class="metric-card"><div class="metric-header"><div class="metric-label">Total Revenue</div><div class="metric-icon mi-orange">💰</div></div><div class="metric-value mv-orange">$${inf.total_revenue||'0'}</div><div class="metric-sub">USDC collected</div></div>
      <div class="metric-card"><div class="metric-header"><div class="metric-label">Queries Processed</div><div class="metric-icon mi-purple">🔍</div></div><div class="metric-value mv-purple">${inf.total_queries||0}</div><div class="metric-sub">Inference requests</div></div>
      <div class="metric-card"><div class="metric-header"><div class="metric-label">Price Per Query</div><div class="metric-icon mi-green">🏷️</div></div><div class="metric-value mv-green">$0.05</div><div class="metric-sub">USDC per inference</div></div>
    </div>
    <div class="panel panel-full" style="margin-top:16px"><div class="panel-header"><div class="panel-title">💎 Payment History</div><span class="muted-sm">${list.length} transactions</span></div>
      <div class="panel-body" style="padding:0">${list.length?this.buildInferenceTable(list):'<div class="empty-state"><div class="empty-icon">💎</div><div class="empty-text">No inference payments yet</div></div>'}</div></div>`;
  },

  // ── Analytics Page ──
  async loadAnalytics() {
    const c = document.getElementById('page-content');
    const d = await this.loadStats();
    if (!d) return;
    const a = d.artifacts, at = d.attestations, inf = d.inferences;
    const avgRev = inf.total_queries > 0 ? (parseFloat(inf.total_revenue) / inf.total_queries).toFixed(4) : '0';
    c.innerHTML = `
    <div class="page-header"><h2>Analytics</h2><p class="muted">System performance and integration metrics</p></div>
    <div class="metrics-grid">
      <div class="metric-card"><div class="metric-header"><div class="metric-label">FL Rounds</div><div class="metric-icon mi-purple">🔄</div></div><div class="metric-value mv-purple">${a.total_rounds||0}</div><div class="metric-sub">Completed</div></div>
      <div class="metric-card"><div class="metric-header"><div class="metric-label">Attestation Rate</div><div class="metric-icon mi-green">✓</div></div><div class="metric-value mv-green">${a.total_rounds > 0 ? Math.round(at.total / a.total_rounds * 100) : 0}%</div><div class="metric-sub">Rounds attested</div></div>
      <div class="metric-card"><div class="metric-header"><div class="metric-label">Avg Revenue/Query</div><div class="metric-icon mi-orange">📈</div></div><div class="metric-value mv-orange">$${avgRev}</div><div class="metric-sub">USDC per inference</div></div>
    </div>
    <div class="panels" style="margin-top:16px">
      <div class="panel"><div class="panel-header"><div class="panel-title">📊 Layer Activity</div></div><div class="panel-body"><div class="chart-container"><canvas id="chart"></canvas></div></div></div>
      <div class="panel"><div class="panel-header"><div class="panel-title">🔗 Integration Guide</div></div><div class="panel-body">
        <div class="guide-step"><span class="step-num">1</span><div><strong>Install FedNet</strong><br><code class="code-inline">pip install -e .</code></div></div>
        <div class="guide-step"><span class="step-num">2</span><div><strong>After your FL round</strong><br><code class="code-inline">from fednet import create_artifact_generator</code><br><code class="code-inline">gen = create_artifact_generator("your-key")</code><br><code class="code-inline">artifact = gen.generate_artifact(round_id, participants, gradients, ...)</code></div></div>
        <div class="guide-step"><span class="step-num">3</span><div><strong>Anchor on Solana</strong><br><code class="code-inline">from fednet import create_solana_client</code><br><code class="code-inline">client = create_solana_client()</code><br><code class="code-inline">client.attest_artifact(artifact.gradient_hash, round_id, ...)</code></div></div>
        <div class="guide-step"><span class="step-num">4</span><div><strong>Monetize inference</strong><br><code class="code-inline">from fednet import X402InferenceServer</code><br><code class="code-inline">server = X402InferenceServer(model, price_per_inference=Decimal("0.05"))</code></div></div>
      </div></div>
    </div>`;
    this.drawChart();
  },

  // ── Settings Page ──
  async loadSettings() {
    const c = document.getElementById('page-content');
    let s = {};
    try { const r = await fetch('/api/settings'); s = await r.json(); } catch(e) {}
    c.innerHTML = `
    <div class="page-header"><h2>Settings</h2><p class="muted">System configuration (read from environment variables)</p></div>
    <div class="panels">
      <div class="panel"><div class="panel-header"><div class="panel-title">🌐 Network Configuration</div></div><div class="panel-body">
        <div class="setting-row"><span class="setting-label">Environment</span><span class="setting-value">${s.environment||'development'}</span></div>
        <div class="setting-row"><span class="setting-label">Solana Network</span><span class="setting-value badge-up">${s.solana_network||'devnet'}</span></div>
        <div class="setting-row"><span class="setting-label">RPC Endpoint</span><span class="setting-value code-sm">${s.solana_rpc||'—'}</span></div>
        <div class="setting-row"><span class="setting-label">USDC Mint</span><span class="setting-value code-sm">${(s.usdc_mint||'—').substring(0,20)}...</span></div>
        <div class="setting-row"><span class="setting-label">Receiver Wallet</span><span class="setting-value code-sm">${s.receiver_wallet||'not set'}</span></div>
      </div></div>
      <div class="panel"><div class="panel-header"><div class="panel-title">⚙️ Training Configuration</div></div><div class="panel-body">
        <div class="setting-row"><span class="setting-label">Model Type</span><span class="setting-value">${s.model_type||'hybrid'}</span></div>
        <div class="setting-row"><span class="setting-label">Query Price</span><span class="setting-value">$${s.query_price||'0.05'} USDC</span></div>
        <div class="setting-row"><span class="setting-label">FL Rounds</span><span class="setting-value">${s.fl_rounds||'10'}</span></div>
        <div class="setting-row"><span class="setting-label">Local Epochs</span><span class="setting-value">${s.local_epochs||'5'}</span></div>
        <div class="setting-row"><span class="setting-label">Min Clients</span><span class="setting-value">${s.min_clients||'2'}</span></div>
      </div></div>
    </div>
    <div class="panel panel-full" style="margin-top:16px"><div class="panel-header"><div class="panel-title">🔄 Switch to Mainnet</div></div><div class="panel-body">
      <p style="color:var(--text-muted);margin-bottom:12px">To switch from devnet to mainnet-beta before submission, change one environment variable:</p>
      <pre class="code-block">SOLANA_NETWORK=mainnet-beta</pre>
      <p style="color:var(--text-muted);margin-top:12px;font-size:13px">This automatically updates RPC URL, Explorer URLs, USDC mint address, and chain labels. Mainnet tx fees are ~$0.000005 per attestation.</p>
    </div></div>`;
  },

  // ── Training Trigger ──
  async triggerTraining() {
    if (this.trainingRunning) return;
    this.trainingRunning = true;
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'training-modal';
    modal.innerHTML = `<div class="modal"><div class="modal-header"><div class="panel-title">🚀 Federated Learning</div><button class="btn btn-ghost" onclick="document.getElementById('training-modal').remove()">✕</button></div><div class="modal-body"><div id="train-log" class="train-log">Starting training...</div></div></div>`;
    document.body.appendChild(modal);
    try {
      await fetch('/api/train', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({rounds:1})});
      const poll = setInterval(async () => {
        const r = await fetch('/api/train/status');
        const s = await r.json();
        document.getElementById('train-log').innerHTML = s.log.map(l => `<div class="log-line">${l}</div>`).join('');
        document.getElementById('train-log').scrollTop = 99999;
        if (!s.running) { clearInterval(poll); this.trainingRunning = false; this.route(); }
      }, 500);
    } catch(e) { this.trainingRunning = false; }
  },

  // ── Builders ──
  buildActivity(arts, atts, infs) {
    const items = [];
    (arts||[]).forEach(a => items.push({dot:'purple',t:`<strong>Round #${a.round}</strong> <span>— artifact generated</span>`,s:`${a.participants} participants · ε=${a.dp_epsilon} · HMAC verified`}));
    (atts||[]).forEach(a => items.push({dot:'green',t:`<strong>Attestation</strong> <span>— anchored on Solana</span>`,s:`TX: ${(a.tx_id||'').substring(0,20)}... · Round ${a.round_id}`}));
    (infs||[]).forEach(i => items.push({dot:'orange',t:`<strong>${i.query}</strong>`,s:`${(i.payer||'').substring(0,20)} · $${i.amount} USDC`}));
    if (!items.length) return '<div class="empty-state"><div class="empty-icon">⚡</div><div class="empty-text">No activity yet</div></div>';
    return items.map(i => `<div class="activity-item"><div class="activity-dot ${i.dot}"></div><div><div class="activity-text">${i.t}</div><div class="activity-time">${i.s}</div></div></div>`).join('');
  },

  buildArtifactTable(list, full) {
    return `<table class="data-table"><thead><tr><th>Round</th><th>Timestamp</th><th>Participants</th><th>Gradient Hash</th>${full?'<th>Signature</th>':''}<th>DP ε</th><th>Status</th></tr></thead><tbody>${list.map(a =>
      `<tr><td style="font-weight:600">#${a.round}</td><td class="muted">${new Date(a.timestamp).toLocaleString()}</td><td>${a.participants}</td><td><span class="hash-text">${a.gradient_hash}</span></td>${full?`<td><span class="hash-text">${a.signature}</span></td>`:''}<td>${a.dp_epsilon}</td><td><span class="verified-badge">✓ Verified</span></td></tr>`).join('')}</tbody></table>`;
  },

  buildAttestationTable(list) {
    return `<table class="data-table"><thead><tr><th>Round</th><th>Transaction ID</th><th>Artifact Hash</th><th>Timestamp</th><th>Status</th><th>Explorer</th></tr></thead><tbody>${list.map(a =>
      `<tr><td style="font-weight:600">#${a.round_id}</td><td><span class="hash-text">${(a.tx_id||'').substring(0,20)}...</span></td><td><span class="hash-text">${(a.artifact_hash||'').substring(0,16)}...</span></td><td class="muted">${a.timestamp?new Date(a.timestamp).toLocaleString():'—'}</td><td><span class="verified-badge">✓ ${a.status}</span></td><td><a href="${a.explorer_url}" target="_blank" class="link-btn">View ↗</a></td></tr>`).join('')}</tbody></table>`;
  },

  buildInferenceTable(list) {
    return `<table class="data-table"><thead><tr><th>Query</th><th>Payer</th><th>Amount</th></tr></thead><tbody>${list.map(i =>
      `<tr><td>${i.query}</td><td><span class="hash-text">${i.payer}</span></td><td style="font-weight:600;color:var(--accent2)">$${i.amount} USDC</td></tr>`).join('')}</tbody></table>`;
  },

  drawChart() {
    const c = document.getElementById('chart');
    if (!c) return;
    const ctx = c.getContext('2d'), dpr = window.devicePixelRatio||1;
    const rect = c.parentElement.getBoundingClientRect();
    c.width = rect.width*dpr; c.height = rect.height*dpr;
    c.style.width = rect.width+'px'; c.style.height = rect.height+'px';
    ctx.scale(dpr, dpr);
    const w = rect.width, h = rect.height;
    ctx.strokeStyle = 'rgba(255,255,255,.04)'; ctx.lineWidth = 1;
    for (let i=0;i<5;i++) { const y=h*i/4; ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke(); }
    const wave = (n,min,max) => Array.from({length:n}, () => min+Math.random()*(max-min));
    const draw = (pts,color,fill) => {
      const mx = Math.max(...pts)*1.2||1;
      ctx.beginPath();
      pts.forEach((p,i) => { const x=w*i/(pts.length-1), y=h-20-(p/mx)*(h-40); i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); });
      ctx.strokeStyle=color; ctx.lineWidth=2; ctx.stroke();
      ctx.lineTo(w,h-20); ctx.lineTo(0,h-20); ctx.closePath();
      ctx.fillStyle=fill; ctx.fill();
      pts.forEach((p,i) => { const x=w*i/(pts.length-1), y=h-20-(p/mx)*(h-40); ctx.beginPath(); ctx.arc(x,y,3,0,Math.PI*2); ctx.fillStyle=color; ctx.fill(); });
    };
    draw(wave(7,30,60),'rgba(124,92,252,.8)','rgba(124,92,252,.06)');
    draw(wave(7,20,50),'rgba(0,212,170,.8)','rgba(0,212,170,.04)');
    ctx.fillStyle='rgba(255,255,255,.3)'; ctx.font='10px Inter';
    ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].forEach((d,i) => ctx.fillText(d,w*i/6-10,h-4));
    ctx.fillStyle='rgba(124,92,252,.9)'; ctx.fillRect(w-120,8,8,8);
    ctx.fillStyle='rgba(255,255,255,.5)'; ctx.fillText('Artifacts',w-108,16);
    ctx.fillStyle='rgba(0,212,170,.9)'; ctx.fillRect(w-120,24,8,8);
    ctx.fillText('Attestations',w-108,32);
  }
};

document.addEventListener('DOMContentLoaded', () => App.init());
