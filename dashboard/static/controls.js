// Control Panel Logic and Configuration Management

// ------- State -------
let currentConfig = {
  total_agents: 10,
  cycles_per_run: 50,
  pairs_per_cycle: 5,
  cycle_delay_seconds: 1.0,
  window: 5,
  detection_interval: 25,
  min_novel_phrase_appearances: 3,
};

let stats = {
  agents: 0,
  cycle: 0,
  interactions: 0,
  traditions: new Set(),
};

// ------- UI Controls -------
document.getElementById('toggle-controls')?.addEventListener('click', () => {
  document.getElementById('control-panel').classList.toggle('hidden');
});

document.getElementById('close-controls')?.addEventListener('click', () => {
  document.getElementById('control-panel').classList.add('hidden');
});

// ------- Configuration Management -------
function loadConfigFromForm() {
  currentConfig = {
    total_agents: parseInt(document.getElementById('total-agents').value) || 10,
    cycles_per_run: parseInt(document.getElementById('cycles-per-run').value) || 50,
    pairs_per_cycle: parseInt(document.getElementById('pairs-per-cycle').value) || 5,
    cycle_delay_seconds: parseFloat(document.getElementById('cycle-delay').value) ?? 1.0,
    window: parseInt(document.getElementById('memory-window').value) || 5,
    detection_interval: parseInt(document.getElementById('detection-interval').value) || 25,
    min_novel_phrase_appearances: parseInt(document.getElementById('min-novel-phrase').value) || 3,
  };
  return currentConfig;
}

function populateFormFromConfig(config) {
  document.getElementById('total-agents').value = config.total_agents || 10;
  document.getElementById('cycles-per-run').value = config.cycles_per_run || 50;
  document.getElementById('pairs-per-cycle').value = config.pairs_per_cycle || 5;
  document.getElementById('cycle-delay').value = config.cycle_delay_seconds || 1.0;
  document.getElementById('memory-window').value = config.window || 5;
  document.getElementById('detection-interval').value = config.detection_interval || 25;
  document.getElementById('min-novel-phrase').value = config.min_novel_phrase_appearances || 3;
}

function generateYAMLConfig() {
  const config = loadConfigFromForm();
  return `# Sangha Configuration
# Generated from Dashboard Controls

swarm:
  total_agents: ${config.total_agents}
  cycles_per_run: ${config.cycles_per_run}
  pairs_per_cycle: ${config.pairs_per_cycle}
  cycle_delay_seconds: ${config.cycle_delay_seconds}

memory:
  window: ${config.window}
  swarm_pulse_frequency: 20

pairing:
  affinity_weighted: 0.40
  tradition_crossing: 0.30
  random: 0.20
  anti_affinity: 0.10
  affinity_decay: 0.97

emergence:
  detection_interval: ${config.detection_interval}
  min_novel_phrase_appearances: ${config.min_novel_phrase_appearances}

logging:
  level: INFO
  show_interactions: true
  emergence_journal: data/emergence_journal.jsonl
  database: data/sangha.db

dashboard:
  enabled: true
  host: "127.0.0.1"
  port: 8765
`;
}

// ------- Button Actions -------
document.getElementById('save-config')?.addEventListener('click', async () => {
  const config = loadConfigFromForm();
  const yamlContent = generateYAMLConfig();
  
  try {
    const response = await fetch('/api/save-config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ yaml: yamlContent, config })
    });
    
    if (response.ok) {
      showNotification('Configuration saved! Restart the experiment to apply changes.', 'success');
    } else {
      showNotification('Failed to save configuration. Check console for details.', 'error');
    }
  } catch (err) {
    console.error('Save failed:', err);
    showNotification('Save failed. Configuration API may not be available.', 'warning');
  }
});

document.getElementById('export-config')?.addEventListener('click', () => {
  const yamlContent = generateYAMLConfig();
  const blob = new Blob([yamlContent], { type: 'text/yaml' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'settings.yaml';
  a.click();
  URL.revokeObjectURL(url);
  showNotification('Configuration exported!', 'success');
});

document.getElementById('load-config')?.addEventListener('click', () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.yaml,.yml';
  input.onchange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      const text = await file.text();
      // Simple YAML parsing for our specific format
      try {
        const parsed = parseSimpleYAML(text);
        populateFormFromConfig(parsed);
        showNotification('Configuration loaded!', 'success');
      } catch (err) {
        showNotification('Failed to parse YAML file', 'error');
      }
    }
  };
  input.click();
});

document.getElementById('reset-config')?.addEventListener('click', () => {
  if (confirm('Reset all settings to defaults?')) {
    populateFormFromConfig({
      total_agents: 10,
      cycles_per_run: 50,
      pairs_per_cycle: 5,
      cycle_delay_seconds: 1.0,
      window: 5,
      detection_interval: 25,
      min_novel_phrase_appearances: 3,
    });
    showNotification('Settings reset to defaults', 'success');
  }
});

// ------- Helpers -------
function parseSimpleYAML(text) {
  const config = {};
  const lines = text.split('\n');
  for (const line of lines) {
    const match = line.match(/^\s*(\w+):\s*(.+)$/);
    if (match) {
      const [, key, value] = match;
      const trimmed = value.trim();
      // Handle booleans
      if (trimmed === 'true') {
        config[key] = true;
      } else if (trimmed === 'false') {
        config[key] = false;
      } else if (!isNaN(trimmed) && trimmed !== '') {
        config[key] = parseFloat(trimmed);
      } else {
        config[key] = trimmed.replace(/^["']|["']$/g, ''); // Remove quotes
      }
    }
  }
  return config;
}

function showNotification(message, type = 'info') {
  // Create a simple notification
  const notif = document.createElement('div');
  notif.className = `notification notification-${type}`;
  notif.textContent = message;
  notif.style.cssText = `
    position: fixed;
    top: 80px;
    right: 20px;
    padding: 1rem 1.5rem;
    background: ${type === 'success' ? '#4ade80' : type === 'error' ? '#f87171' : '#fbbf24'};
    color: #000;
    border-radius: 4px;
    z-index: 1000;
    font-size: 0.8rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    animation: slideIn 0.3s ease;
  `;
  document.body.appendChild(notif);
  setTimeout(() => {
    notif.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => notif.remove(), 300);
  }, 3000);
}

// ------- Stats Updates -------
function updateStats(data) {
  if (data.type === 'interaction') {
    stats.interactions++;
    if (data.agent_a) stats.traditions.add(data.tradition_a);
    if (data.agent_b) stats.traditions.add(data.tradition_b);
  }
  
  if (data.cycle !== undefined) {
    stats.cycle = data.cycle;
  }
  
  // Access nodes from global scope (defined in swarm.js)
  const nodeCount = (typeof nodes !== 'undefined' && nodes) ? nodes.length : 0;
  
  // Update stat cards
  document.getElementById('stat-agents').textContent = nodeCount || 0;
  document.getElementById('stat-cycle').textContent = stats.cycle;
  document.getElementById('stat-interactions').textContent = stats.interactions;
  document.getElementById('stat-traditions').textContent = stats.traditions.size;
  
  // Update interaction stats tab
  updateInteractionStats();
  updateTraditionChart();
}

function updateInteractionStats() {
  const el = document.getElementById('interaction-stats');
  if (!el) return;
  
  // Access nodes from global scope (defined in swarm.js)
  const nodeCount = (typeof nodes !== 'undefined' && nodes) ? nodes.length : 0;
  const avgPerAgent = nodeCount > 0 ? (stats.interactions / nodeCount).toFixed(1) : '0';
  
  el.innerHTML = `
    <p><strong>Total Interactions:</strong> ${stats.interactions}</p>
    <p><strong>Current Cycle:</strong> ${stats.cycle}</p>
    <p><strong>Avg per Agent:</strong> ${avgPerAgent}</p>
    <p><strong>Active Agents:</strong> ${nodeCount}</p>
  `;
}

function updateTraditionChart() {
  const el = document.getElementById('tradition-chart');
  if (!el) return;
  
  // Access nodes and traditionColor from global scope (defined in swarm.js)
  if (typeof nodes === 'undefined' || !nodes || nodes.length === 0) {
    el.innerHTML = '<p style="color: #666;">No agents active yet</p>';
    return;
  }
  
  // Count agents per tradition
  const tradCounts = {};
  nodes.forEach(node => {
    const trad = node.tradition || 'Unknown';
    tradCounts[trad] = (tradCounts[trad] || 0) + 1;
  });
  
  const maxCount = Math.max(...Object.values(tradCounts), 1);
  
  el.innerHTML = '';
  Object.entries(tradCounts).sort((a, b) => b[1] - a[1]).forEach(([trad, count]) => {
    const bar = document.createElement('div');
    bar.className = 'tradition-bar';
    const width = (count / maxCount * 100);
    // Use traditionColor if available, otherwise use a default color
    const color = (typeof traditionColor !== 'undefined') ? traditionColor(trad) : '#6366f1';
    
    bar.innerHTML = `
      <div class="tradition-name" title="${trad}">${trad}</div>
      <div class="tradition-progress">
        <div class="tradition-fill" style="width: ${width}%; background: ${color};"></div>
      </div>
      <div class="tradition-count">${count}</div>
    `;
    el.appendChild(bar);
  });
}

// ------- Tab Navigation -------
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const tab = btn.dataset.tab;
    
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`tab-${tab}`)?.classList.add('active');
  });
});

// ------- Graph Controls -------
document.getElementById('recenter-graph')?.addEventListener('click', () => {
  simulation.alpha(0.5).restart();
  recenterForce();
});

let labelsVisible = true;
document.getElementById('toggle-labels')?.addEventListener('click', () => {
  labelsVisible = !labelsVisible;
  labelSel.style('opacity', labelsVisible ? 1 : 0);
});

// ------- Initialize -------
populateFormFromConfig(currentConfig);

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;
document.head.appendChild(style);

// Export for use in swarm.js
window.updateStats = updateStats;
