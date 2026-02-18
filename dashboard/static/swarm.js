// Sangha swarm visualization — D3 force-directed graph

const TRADITION_COLORS = {
  "Sufism":            "#f97316",
  "Zen":               "#84cc16",
  "Vedanta":           "#f59e0b",
  "Christian Mysticism": "#60a5fa",
  "Tibetan Buddhism":  "#a78bfa",
  "Theravada":         "#34d399",
  "Taoism":            "#67e8f9",
  "Kabbalah":          "#fbbf24",
  "Yogic/Tantric":     "#fb7185",
  "Indigenous/Shamanic": "#86efac",
  "Philosophy":        "#94a3b8",
  "Contemporary":      "#e879f9",
  "Hybrid/Liminal":    "#f8fafc",
  "default":           "#6366f1",
};

function traditionColor(t) {
  if (!t) return TRADITION_COLORS.default;
  for (const [key, val] of Object.entries(TRADITION_COLORS)) {
    if (t.toLowerCase().includes(key.toLowerCase())) return val;
  }
  return TRADITION_COLORS.default;
}

// ------- Graph state -------
const nodes = [];
const links = [];
const nodeMap = {};
const linkMap = {};

const svg = d3.select("#graph");
const width = () => svg.node().clientWidth;
const height = () => svg.node().clientHeight;

const g = svg.append("g");

const linkSel = g.append("g").attr("class", "links");
const nodeSel = g.append("g").attr("class", "nodes");
const labelSel = g.append("g").attr("class", "labels");

const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(80).strength(0.3))
  .force("charge", d3.forceManyBody().strength(-150))
  .force("center", d3.forceCenter())
  .force("collision", d3.forceCollide(14))
  .on("tick", ticked);

svg.call(d3.zoom().on("zoom", e => g.attr("transform", e.transform)));

function recenterForce() {
  simulation.force("center", d3.forceCenter(width() / 2, height() / 2));
}
recenterForce();
window.addEventListener("resize", recenterForce);

function ticked() {
  linkSel.selectAll("line")
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);

  nodeSel.selectAll("circle")
    .attr("cx", d => d.x).attr("cy", d => d.y);

  labelSel.selectAll("text")
    .attr("x", d => d.x + 10).attr("y", d => d.y + 4);
}

function upsertNode(id, tradition) {
  if (!nodeMap[id]) {
    const node = { id, tradition, interactions: 0 };
    nodes.push(node);
    nodeMap[id] = node;

    nodeSel.selectAll("circle").data(nodes, d => d.id).join(
      enter => enter.append("circle")
        .attr("r", 6)
        .attr("fill", d => traditionColor(d.tradition))
        .attr("stroke", "#0a0a0f")
        .attr("stroke-width", 1.5)
        .append("title").text(d => `${d.id} [${d.tradition}]`)
    );

    labelSel.selectAll("text").data(nodes, d => d.id).join(
      enter => enter.append("text")
        .text(d => d.id.split("_").slice(0, 2).join("_"))
        .attr("font-size", "8px")
        .attr("fill", "#888")
    );

    simulation.nodes(nodes);
    simulation.alpha(0.3).restart();
  }
  return nodeMap[id];
}

function upsertLink(aId, bId, strength = 0.5) {
  const key = [aId, bId].sort().join("--");
  if (!linkMap[key]) {
    const link = { source: aId, target: bId, strength };
    links.push(link);
    linkMap[key] = link;
  } else {
    linkMap[key].strength = Math.min(1, linkMap[key].strength + 0.05);
  }
  const w = (linkMap[key].strength * 3).toFixed(1);

  linkSel.selectAll("line").data(links, d => [d.source.id || d.source, d.target.id || d.target].sort().join("--")).join(
    enter => enter.append("line")
      .attr("stroke", "#334155")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", w),
    update => update.attr("stroke-width", w)
  );

  simulation.force("link").links(links);
  simulation.alpha(0.1).restart();
}

// ------- Feed -------
function addToFeed(data) {
  const feed = document.getElementById("feed");
  const card = document.createElement("div");
  card.className = "interaction-card";

  const silence_a = (data.message_a || "").toLowerCase().includes("[silence]");
  const silence_b = (data.message_b || "").toLowerCase().includes("[silence]");

  card.innerHTML = `
    <span class="agent-label">${data.agent_a}</span>
    <span class="tradition-label"> [${data.tradition_a || "?"}]</span>
    <div class="message ${silence_a ? "silence" : ""}">${data.message_a || ""}</div>
    <br/>
    <span class="agent-label">${data.agent_b}</span>
    <span class="tradition-label"> [${data.tradition_b || "?"}]</span>
    <div class="message ${silence_b ? "silence" : ""}">${data.message_b || ""}</div>
  `;
  feed.prepend(card);
  while (feed.children.length > 30) feed.removeChild(feed.lastChild);
}

function addEmergence(data) {
  const el = document.getElementById("emergence");
  const card = document.createElement("div");
  card.className = "emergence-card";
  card.textContent = `[${data.type}] ${data.description}`;
  el.prepend(card);
  while (el.children.length > 20) el.removeChild(el.lastChild);
}

// ------- WebSocket -------
const statusEl = document.getElementById("status");
const costEl = document.getElementById("cost");

function connect() {
  const ws = new WebSocket(`ws://${location.host}/ws`);

  ws.onopen = () => { statusEl.textContent = "live"; statusEl.style.color = "#4ade80"; };
  ws.onclose = () => {
    statusEl.textContent = "disconnected — retrying…";
    statusEl.style.color = "#f87171";
    setTimeout(connect, 3000);
  };

  ws.onmessage = (evt) => {
    let data;
    try { data = JSON.parse(evt.data); } catch { return; }

    if (data.type === "interaction") {
      upsertNode(data.agent_a, data.tradition_a);
      upsertNode(data.agent_b, data.tradition_b);
      upsertLink(data.agent_a, data.agent_b);
      addToFeed(data);
    } else if (data.type?.includes("emergence") || data.type === "novel_concept"
               || data.type === "collective_silence") {
      addEmergence(data);
    } else if (data.type === "cost_update") {
      costEl.textContent = `$${(+data.cost).toFixed(4)}`;
    }
  };
}

connect();
