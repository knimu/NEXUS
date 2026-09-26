/**
 * NEXUS Member 4 Investigation Dashboard Application Logic.
 * Handles API fetch, dynamic metric binding, Cytoscape graph rendering,
 * evidence categorization, human analyst decision submission, and audit log.
 */

let currentClusterId = null;
let currentClusterData = null;
let cyInstance = null;

// Initialize dashboard on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    fetchOverview();
    fetchClusters();
    fetchAuditLog();
    loadAdversarialAttack('device_rotation');
});

// 1. Fetch Overview Telemetry
async function fetchOverview() {
    try {
        const response = await fetch('/api/overview');
        if (!response.ok) throw new Error('Failed to load overview telemetry');
        const data = await response.json();

        document.getElementById('metric-total-accounts').textContent = data.total_accounts || 0;
        document.getElementById('metric-cluster-count').textContent = data.cluster_count || 0;
        document.getElementById('metric-clustered-accounts').textContent = data.clustered_account_count || 0;
        document.getElementById('metric-high-severity').textContent = data.high_severity_count || 0;
        document.getElementById('metric-total-evidence').textContent = data.total_evidence_count || 0;
    } catch (err) {
        console.error('Error in fetchOverview:', err);
    }
}

// 2. Fetch Candidate Clusters
async function fetchClusters() {
    const tbody = document.getElementById('clusters-table-body');
    try {
        const response = await fetch('/api/clusters');
        if (!response.ok) throw new Error('Failed to fetch clusters');
        const clusters = await response.json();

        if (!clusters || clusters.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading-cell">No candidate clusters detected.</td></tr>';
            return;
        }

        let html = '';
        clusters.forEach(c => {
            const sevClass = getSeverityBadgeClass(c.severity);
            const isActive = currentClusterId === c.cluster_id ? 'active-row' : '';
            html += `
                <tr class="${isActive}" onclick="selectCluster('${c.cluster_id}', this)">
                    <td style="font-family: var(--font-mono); font-weight: 600;">${c.cluster_id}</td>
                    <td>${c.account_ids ? c.account_ids.length : 0} accs</td>
                    <td style="font-family: var(--font-mono); font-weight: 600;">${c.cluster_risk ? c.cluster_risk.toFixed(2) : '0.00'}</td>
                    <td><span class="badge ${sevClass}">${c.severity || 'LOW'}</span></td>
                    <td style="font-family: var(--font-mono);">${c.confidence ? (c.confidence * 100).toFixed(1) + '%' : '0%'}</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;

        // Auto-select first cluster if none selected
        if (!currentClusterId && clusters.length > 0) {
            const firstRow = tbody.querySelector('tr');
            selectCluster(clusters[0].cluster_id, firstRow);
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5" class="loading-cell" style="color: #f87171;">Error: ${err.message}</td></tr>`;
    }
}

// Filter clusters in table by search input
function filterClusters() {
    const query = document.getElementById('cluster-search').value.toLowerCase().trim();
    const rows = document.querySelectorAll('#clusters-table-body tr');

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
    });
}

// 3. Select & Inspect a Candidate Cluster
async function selectCluster(clusterId, rowElement) {
    currentClusterId = clusterId;

    // Highlight selected row in table
    const rows = document.querySelectorAll('#clusters-table-body tr');
    rows.forEach(r => r.classList.remove('active-row'));
    if (rowElement) {
        rowElement.classList.add('active-row');
    }

    const detailPanelHeader = document.getElementById('selected-cluster-badge');
    detailPanelHeader.innerHTML = `<span style="font-family: var(--font-mono); font-weight: 700; color: var(--accent-blue);">${clusterId}</span>`;

    const detailBody = document.getElementById('detail-body');
    detailBody.innerHTML = '<div class="loading-cell">Loading cluster details & graph topology...</div>';

    try {
        const response = await fetch(`/api/clusters/${clusterId}`);
        if (!response.ok) throw new Error('Cluster details not found');
        const data = await response.json();

        currentClusterData = data;
        renderClusterDetail(data);
    } catch (err) {
        detailBody.innerHTML = `<div class="loading-cell" style="color: #f87171;">Error: ${err.message}</div>`;
    }
}

// Render Cluster Detail View
function renderClusterDetail(data) {
    const detailBody = document.getElementById('detail-body');
    const sevClass = getSeverityBadgeClass(data.severity);

    // Group evidence items
    const relEvidence = (data.evidence || []).filter(e => ['shared_device', 'shared_ip', 'shared_beneficiary'].includes(e.type));
    const tempEvidence = (data.evidence || []).filter(e => e.type === 'temporal_proximity');
    const behEvidence = (data.evidence || []).filter(e => e.type === 'behavioral_overlap');

    let html = `
        <!-- Summary Bar -->
        <div class="detail-summary-bar">
            <div class="detail-stat-item">
                <span class="detail-stat-label">Cluster Risk</span>
                <span class="detail-stat-val">${data.cluster_risk ? data.cluster_risk.toFixed(2) : '0.00'}</span>
            </div>
            <div class="detail-stat-item">
                <span class="detail-stat-label">Severity</span>
                <div><span class="badge ${sevClass}">${data.severity}</span></div>
            </div>
            <div class="detail-stat-item">
                <span class="detail-stat-label">Evidence Strength</span>
                <span class="detail-stat-val">${data.confidence ? (data.confidence * 100).toFixed(1) + '%' : '0%'}</span>
            </div>
            <div class="detail-stat-item">
                <span class="detail-stat-label">Member Accounts</span>
                <span class="detail-stat-val">${data.account_ids ? data.account_ids.length : 0}</span>
            </div>
        </div>

        <!-- Relationship Graph -->
        <div class="evidence-category">
            <div class="evidence-cat-title">RELATIONSHIP TOPOLOGY GRAPH</div>
            <div class="graph-container">
                <div id="cy"></div>
                <div class="graph-controls">
                    <button class="graph-btn" onclick="resetGraphView()">Fit View</button>
                </div>
            </div>
        </div>

        <!-- Categorized Evidence Panel -->
        <div class="evidence-category">
            <div class="evidence-cat-title">RELATIONSHIP EVIDENCE</div>
            <div class="evidence-list">
                ${renderEvidenceItems(relEvidence, 'No shared devices, IPs, or beneficiaries.')}
            </div>
        </div>

        <div class="evidence-category">
            <div class="evidence-cat-title">TEMPORAL EVIDENCE (&le; 30 mins)</div>
            <div class="evidence-list">
                ${renderEvidenceItems(tempEvidence, 'No tight temporal proximity detected.')}
            </div>
        </div>

        <div class="evidence-category">
            <div class="evidence-cat-title">BEHAVIORAL EVIDENCE</div>
            <div class="evidence-list">
                ${renderEvidenceItems(behEvidence, 'No shared suspicious behavior tags.')}
            </div>
        </div>

        <!-- Human Analyst Decision Form -->
        <div class="decision-panel">
            <div class="decision-form-header">ANALYST DECISION SUBMISSION</div>
            <form onsubmit="submitAnalystDecision(event)">
                <div class="decision-options">
                    <label class="decision-radio-label">
                        <input type="radio" name="decision" value="REVIEW" checked> REVIEW
                    </label>
                    <label class="decision-radio-label">
                        <input type="radio" name="decision" value="ALLOW"> ALLOW
                    </label>
                    <label class="decision-radio-label">
                        <input type="radio" name="decision" value="ESCALATE"> ESCALATE
                    </label>
                </div>
                <textarea id="decision-reason" class="reason-textarea" placeholder="Mandatory analyst justification/reason..." required></textarea>
                <button type="submit" class="btn-submit-decision">Submit Decision</button>
            </form>
            <div id="decision-feedback" style="margin-top: 8px; font-size: 11px;"></div>
        </div>
    `;

    detailBody.innerHTML = html;

    // Render Cytoscape Graph Topology
    if (data.graph_topology) {
        renderCytoscapeGraph(data.graph_topology, data.accounts_detail || []);
    }
}

function renderEvidenceItems(items, emptyText) {
    if (!items || items.length === 0) {
        return `<div class="evidence-item" style="color: var(--text-muted); font-style: italic;">${emptyText}</div>`;
    }
    return items.map(item => `
        <div class="evidence-item">
            <div class="evidence-item-desc">${item.description || ''}</div>
            <div class="evidence-item-meta">Involved Accounts: ${(item.accounts || []).join(', ')}</div>
        </div>
    `).join('');
}

// 4. Render Cytoscape.js Graph
function renderCytoscapeGraph(topology, accountsDetail) {
    const container = document.getElementById('cy');
    if (!container) return;

    const accountMap = {};
    accountsDetail.forEach(acc => {
        accountMap[acc.account_id] = acc;
    });

    const cyElements = [];

    // Add nodes
    (topology.nodes || []).forEach(n => {
        const nData = n.data;
        let nodeColor = '#38bdf8'; // Account default cyan
        let shape = 'ellipse';

        if (nData.type === 'account') {
            if (nData.risk_score >= 60) nodeColor = '#f87171'; // Red
            else if (nData.risk_score >= 30) nodeColor = '#facc15'; // Yellow
            else nodeColor = '#4ade80'; // Green
        } else if (nData.type === 'device') {
            nodeColor = '#c084fc'; // Purple
            shape = 'rectangle';
        } else if (nData.type === 'ip') {
            nodeColor = '#fb923c'; // Orange
            shape = 'diamond';
        } else if (nData.type === 'beneficiary') {
            nodeColor = '#e879f9'; // Pink
            shape = 'hexagon';
        }

        cyElements.push({
            data: {
                id: nData.id,
                label: nData.label,
                nodeType: nData.type,
                accountData: accountMap[nData.id] || null,
            },
            style: {
                'background-color': nodeColor,
                'shape': shape,
            }
        });
    });

    // Add edges
    (topology.edges || []).forEach(e => {
        const eData = e.data;
        let lineColor = '#475569';
        if (eData.type === 'shared_device') lineColor = '#c084fc';
        else if (eData.type === 'shared_ip') lineColor = '#fb923c';
        else if (eData.type === 'shared_beneficiary') lineColor = '#e879f9';

        cyElements.push({
            data: {
                id: eData.id,
                source: eData.source,
                target: eData.target,
                label: eData.label,
            },
            style: {
                'line-color': lineColor,
            }
        });
    });

    if (cyInstance) {
        cyInstance.destroy();
    }

    cyInstance = cytoscape({
        container: container,
        elements: cyElements,
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'color': '#f8fafc',
                    'font-size': '10px',
                    'font-family': 'JetBrains Mono',
                    'text-valign': 'bottom',
                    'text-margin-y': 4,
                    'width': '22px',
                    'height': '22px',
                    'border-width': 1,
                    'border-color': '#ffffff',
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 1.5,
                    'curve-style': 'bezier',
                    'opacity': 0.75,
                }
            }
        ],
        layout: {
            name: 'cose',
            animate: false,
            padding: 24,
        }
    });

    // On node tap/click: open account inspection modal if node is an account
    cyInstance.on('tap', 'node', function(evt) {
        const node = evt.target;
        const nData = node.data();
        if (nData.nodeType === 'account' && nData.accountData) {
            openAccountModal(nData.accountData);
        }
    });
}

function resetGraphView() {
    if (cyInstance) {
        cyInstance.fit();
    }
}

// 5. Account Modal Drawer (No Ground Truth)
function openAccountModal(acc) {
    const modal = document.getElementById('account-modal');
    const title = document.getElementById('modal-account-title');
    const body = document.getElementById('modal-account-body');

    title.textContent = `ACCOUNT INSPECTOR: ${acc.account_id}`;

    const sevClass = getSeverityBadgeClass(acc.risk_level);

    body.innerHTML = `
        <div class="account-detail-grid">
            <span class="acc-label">Account ID:</span>
            <span class="acc-val">${acc.account_id}</span>

            <span class="acc-label">Individual Risk:</span>
            <span class="acc-val">${acc.risk_score}</span>

            <span class="acc-label">Risk Level:</span>
            <span><span class="badge ${sevClass}">${acc.risk_level}</span></span>

            <span class="acc-label">Device ID:</span>
            <span class="acc-val">${acc.device_id || 'N/A'}</span>

            <span class="acc-label">IP ID:</span>
            <span class="acc-val">${acc.ip_id || 'N/A'}</span>

            <span class="acc-label">Beneficiary ID:</span>
            <span class="acc-val">${acc.beneficiary_id || 'N/A'}</span>

            <span class="acc-label">Timestamp:</span>
            <span class="acc-val">${acc.timestamp || 'N/A'}</span>

            <span class="acc-label">Amount:</span>
            <span class="acc-val">$${acc.amount ? acc.amount.toFixed(2) : '0.00'}</span>

            <span class="acc-label">Behavior Features:</span>
            <span class="acc-val">${acc.behavior_features || 'None'}</span>
        </div>
    `;

    modal.classList.remove('hidden');
}

function closeAccountModal() {
    document.getElementById('account-modal').classList.add('hidden');
}

// 6. Submit Human Analyst Decision
async function submitAnalystDecision(event) {
    event.preventDefault();
    const feedback = document.getElementById('decision-feedback');
    feedback.innerHTML = '';

    if (!currentClusterId) {
        feedback.innerHTML = '<span style="color: #f87171;">Error: No cluster selected.</span>';
        return;
    }

    const decision = document.querySelector('input[name="decision"]:checked').value;
    const reasonInput = document.getElementById('decision-reason');
    const reason = reasonInput.value.trim();

    if (!reason) {
        feedback.innerHTML = '<span style="color: #f87171;">Reason is mandatory and cannot be empty.</span>';
        return;
    }

    try {
        const response = await fetch('/api/decisions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cluster_id: currentClusterId,
                decision: decision,
                reason: reason
            })
        });

        const resData = await response.json();
        if (!response.ok) {
            throw new Error(resData.error || 'Failed to submit decision');
        }

        feedback.innerHTML = `<span style="color: #4ade80;">Success: Decision recorded for ${currentClusterId}.</span>`;
        reasonInput.value = '';

        // Refresh audit log UI
        fetchAuditLog();
    } catch (err) {
        feedback.innerHTML = `<span style="color: #f87171;">Error: ${err.message}</span>`;
    }
}

// 7. Fetch Audit Log
async function fetchAuditLog() {
    const tbody = document.getElementById('audit-table-body');
    try {
        const response = await fetch('/api/audit');
        if (!response.ok) throw new Error('Failed to fetch audit trail');
        const logs = await response.json();

        if (!logs || logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="loading-cell">No analyst decisions recorded yet.</td></tr>';
            return;
        }

        let html = '';
        logs.forEach(item => {
            let badgeClass = 'badge-review';
            if (item.decision === 'ALLOW') badgeClass = 'badge-allow';
            if (item.decision === 'ESCALATE') badgeClass = 'badge-escalate';

            html += `
                <tr>
                    <td style="font-family: var(--font-mono);">${item.timestamp}</td>
                    <td style="font-family: var(--font-mono); font-weight: 600;">${item.cluster_id}</td>
                    <td><span class="badge ${badgeClass}">${item.decision}</span></td>
                    <td>${escapeHtml(item.reason)}</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" class="loading-cell" style="color: #f87171;">Error: ${err.message}</td></tr>`;
    }
}

// 8. Load Adversarial Resilience Attack Comparison
async function loadAdversarialAttack(attackType, btnElement) {
    if (btnElement) {
        document.querySelectorAll('.attack-btn').forEach(b => b.classList.remove('active'));
        btnElement.classList.add('active');
    }

    const titleEl = document.getElementById('attack-title');
    titleEl.textContent = `RESILIENCE COMPARISON: ${attackType.replace('_', ' ').toUpperCase()}`;

    const tbody = document.getElementById('adversarial-table-body');
    tbody.innerHTML = '<tr><td colspan="4" class="loading-cell">Loading resilience metrics...</td></tr>';

    try {
        const response = await fetch(`/api/adversarial/${attackType}`);
        if (!response.ok) throw new Error('Failed to load attack data');
        const data = await response.json();

        const comp = data.comparison || {};
        const summary = data.summary || {};

        let html = `
            <tr>
                <td>Detected Clusters</td>
                <td style="font-family: var(--font-mono);">${comp.cluster_count ? comp.cluster_count.baseline : '-'}</td>
                <td style="font-family: var(--font-mono);">${comp.cluster_count ? comp.cluster_count.attack : '-'}</td>
                <td style="font-family: var(--font-mono); color: ${getDeltaColor(comp.cluster_count ? comp.cluster_count.change : 0)}">${formatDelta(comp.cluster_count ? comp.cluster_count.change : 0)}</td>
            </tr>
            <tr>
                <td>Clustered Accounts</td>
                <td style="font-family: var(--font-mono);">${comp.clustered_account_count ? comp.clustered_account_count.baseline : '-'}</td>
                <td style="font-family: var(--font-mono);">${comp.clustered_account_count ? comp.clustered_account_count.attack : '-'}</td>
                <td style="font-family: var(--font-mono); color: ${getDeltaColor(comp.clustered_account_count ? comp.clustered_account_count.change : 0)}">${formatDelta(comp.clustered_account_count ? comp.clustered_account_count.change : 0)}</td>
            </tr>
            <tr>
                <td>Shared Devices</td>
                <td style="font-family: var(--font-mono);">${comp.shared_device_count ? comp.shared_device_count.baseline : '-'}</td>
                <td style="font-family: var(--font-mono);">${comp.shared_device_count ? comp.shared_device_count.attack : '-'}</td>
                <td style="font-family: var(--font-mono); color: ${getDeltaColor(comp.shared_device_count ? comp.shared_device_count.change : 0)}">${formatDelta(comp.shared_device_count ? comp.shared_device_count.change : 0)}</td>
            </tr>
            <tr>
                <td>Shared IPs</td>
                <td style="font-family: var(--font-mono);">${comp.shared_ip_count ? comp.shared_ip_count.baseline : '-'}</td>
                <td style="font-family: var(--font-mono);">${comp.shared_ip_count ? comp.shared_ip_count.attack : '-'}</td>
                <td style="font-family: var(--font-mono); color: ${getDeltaColor(comp.shared_ip_count ? comp.shared_ip_count.change : 0)}">${formatDelta(comp.shared_ip_count ? comp.shared_ip_count.change : 0)}</td>
            </tr>
            <tr>
                <td>Shared Beneficiaries</td>
                <td style="font-family: var(--font-mono);">${comp.shared_beneficiary_count ? comp.shared_beneficiary_count.baseline : '-'}</td>
                <td style="font-family: var(--font-mono);">${comp.shared_beneficiary_count ? comp.shared_beneficiary_count.attack : '-'}</td>
                <td style="font-family: var(--font-mono); color: ${getDeltaColor(comp.shared_beneficiary_count ? comp.shared_beneficiary_count.change : 0)}">${formatDelta(comp.shared_beneficiary_count ? comp.shared_beneficiary_count.change : 0)}</td>
            </tr>
            <tr>
                <td>Total Evidence Items</td>
                <td style="font-family: var(--font-mono);">${comp.total_evidence_count ? comp.total_evidence_count.baseline : '-'}</td>
                <td style="font-family: var(--font-mono);">${comp.total_evidence_count ? comp.total_evidence_count.attack : '-'}</td>
                <td style="font-family: var(--font-mono); color: ${getDeltaColor(comp.total_evidence_count ? comp.total_evidence_count.change : 0)}">${formatDelta(comp.total_evidence_count ? comp.total_evidence_count.change : 0)}</td>
            </tr>
            <tr>
                <td>Average Cluster Risk</td>
                <td style="font-family: var(--font-mono);">${comp.average_cluster_risk ? comp.average_cluster_risk.baseline.toFixed(2) : '-'}</td>
                <td style="font-family: var(--font-mono);">${comp.average_cluster_risk ? comp.average_cluster_risk.attack.toFixed(2) : '-'}</td>
                <td style="font-family: var(--font-mono); color: ${getDeltaColor(comp.average_cluster_risk ? comp.average_cluster_risk.change : 0)}">${formatDelta(comp.average_cluster_risk ? comp.average_cluster_risk.change : 0)}</td>
            </tr>
            <tr>
                <td>Average Confidence</td>
                <td style="font-family: var(--font-mono);">${comp.average_confidence ? (comp.average_confidence.baseline * 100).toFixed(1) + '%' : '-'}</td>
                <td style="font-family: var(--font-mono);">${comp.average_confidence ? (comp.average_confidence.attack * 100).toFixed(1) + '%' : '-'}</td>
                <td style="font-family: var(--font-mono); color: ${getDeltaColor(comp.average_confidence ? comp.average_confidence.change : 0)}">${formatDelta(comp.average_confidence ? comp.average_confidence.change : 0)}</td>
            </tr>
            <tr>
                <td style="font-weight: 700;">Evidence Survival Rate</td>
                <td style="font-family: var(--font-mono);">100.0%</td>
                <td style="font-family: var(--font-mono); font-weight: 700;" colspan="2">${comp.evidence_survival_percentage ? comp.evidence_survival_percentage.toFixed(1) + '%' : '100%'}</td>
            </tr>
        `;

        tbody.innerHTML = html;

        // Render neutral technical interpretation prose
        renderInterpretationProse(attackType, comp);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" class="loading-cell" style="color: #f87171;">Error loading attack metrics: ${err.message}</td></tr>`;
    }
}

function renderInterpretationProse(attackType, comp) {
    const box = document.getElementById('interpretation-box');
    let text = '';

    if (attackType === 'device_rotation') {
        text = `Under <strong>Device Rotation</strong> attack, adversary accounts rotate to unique device identifiers. Shared-device relationships drop to 0, fragmenting clusters relying solely on hardware links. However, candidate clusters connected by shared beneficiaries or IPs maintain network evidence survival (${comp.evidence_survival_percentage}% survival rate).`;
    } else if (attackType === 'ip_rotation') {
        text = `Under <strong>IP Rotation</strong> attack, adversary accounts operate across distinct IP addresses (e.g. proxy/VPN rotation). Shared-IP relationships drop to 0. Detector stability remains supported by physical device sharing and financial destination (beneficiary) consolidation.`;
    } else if (attackType === 'combined') {
        text = `Under <strong>Combined Rotation</strong> attack, both device and IP infrastructure identifiers are rotated simultaneously. Network graph fragmentation increases significantly. Residual candidate evidence relies on shared beneficiary destinations, temporal execution bursts, and behavioral feature overlaps.`;
    }

    box.innerHTML = `<p class="neutral-prose">${text}</p>`;
}

// Helpers
function getSeverityBadgeClass(sev) {
    if (sev === 'HIGH') return 'badge-high';
    if (sev === 'MEDIUM') return 'badge-medium';
    return 'badge-low';
}

function formatDelta(val) {
    if (val > 0) return `+${val}`;
    return `${val}`;
}

function getDeltaColor(val) {
    if (val < 0) return '#f87171'; // Red for drop
    if (val > 0) return '#38bdf8'; // Blue for increase
    return '#94a3b8'; // Muted
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
