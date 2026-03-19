const app = {
    state: { nodes: [], tags: [], positions: [], settings: {}, chartInstance: null },

    init() {
        this.navigate('dashboard');
        this.initChart();
        this.pollData();
        this.pollSettings();
        setInterval(() => this.pollData(), 3000);
        setTimeout(() => this.initMap(), 500);
    },

    navigate(viewId) {
        document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
        const view = document.getElementById(`view-${viewId}`);
        if(view) view.classList.remove('hidden');
        document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
        const nav = document.getElementById(`nav-${viewId}`);
        if(nav) nav.classList.add('active');
        if(viewId === 'dashboard' && this.map) this.map.invalidateSize();
        
        if(viewId === 'beta' && !this.betaMapInitialized) {
            this.betaMapInitialized = true;
            setTimeout(() => {
                this.betaMap = L.map('beta-heatmap-container', { crs: L.CRS.Simple, attributionControl: false, zoomControl: false });
                const bounds = [[0,0], [1000,1000]];
                const mapUrl = this.state.settings.map_url || 'https://via.placeholder.com/1000x1000/1e293b/38bdf8?text=Indoor+Floorplan+Layout';
                L.imageOverlay(mapUrl, bounds).addTo(this.betaMap);
                this.betaMap.fitBounds(bounds);
            }, 100);
        }
    },

    exportLogs(type) {
        if(type === 'rssi') window.open('/api/export/logs', '_blank');
        if(type === 'positions') window.open('/api/export/positions', '_blank');
    },

    generateHeatmap() {
        if(!this.betaMap) return alert('Map not initialized yet.');
        if(this.heatLayerGroup) this.heatLayerGroup.clearLayers();
        else this.heatLayerGroup = L.layerGroup().addTo(this.betaMap);
        
        for(let i=0; i<300; i++) {
            const x = 200 + Math.random() * 600;
            const y = 200 + Math.random() * 600;
            const intensity = Math.random();
            const color = intensity > 0.8 ? '#f43f5e' : (intensity > 0.4 ? '#eab308' : '#38bdf8');
            L.circle([y, x], {color: 'transparent', fillColor: color, fillOpacity: 0.15, radius: 30 + Math.random()*50}).addTo(this.heatLayerGroup);
        }
    },

    runSandboxMath() {
        const r1 = parseFloat(document.getElementById('sandbox-rssi-1').value);
        const r2 = parseFloat(document.getElementById('sandbox-rssi-2').value);
        const r3 = parseFloat(document.getElementById('sandbox-rssi-3').value);
        const rssi0 = parseFloat(this.state.settings.rssi_1m || -55);
        const n = parseFloat(this.state.settings.path_loss || 2.5);
        
        const d1 = Math.pow(10, (rssi0 - r1)/(10*n));
        const d2 = Math.pow(10, (rssi0 - r2)/(10*n));
        const d3 = Math.pow(10, (rssi0 - r3)/(10*n));

        const anchors = [{x:0, y:0, d:d1}, {x:10, y:0, d:d2}, {x:5, y:10, d:d3}];
        let gx = 5, gy = 5;
        for(let i=0; i<100; i++) {
            let gradX=0, gradY=0;
            anchors.forEach(a => {
                const dc = Math.hypot(gx - a.x, gy - a.y) || 0.1;
                const err = dc - a.d;
                gradX += 2 * err * (gx - a.x)/dc;
                gradY += 2 * err * (gy - a.y)/dc;
            });
            gx -= 0.05 * gradX; gy -= 0.05 * gradY;
        }
        
        const out = document.getElementById('sandbox-output');
        out.innerHTML = `[Distance Conversion Array]\n  d1 = ${d1.toFixed(2)}m\n  d2 = ${d2.toFixed(2)}m\n  d3 = ${d3.toFixed(2)}m\n\n[Least Squares Convergence]\n  X = ${gx.toFixed(2)}\n  Y = ${gy.toFixed(2)}`;
    },

    switchSetupTab(tabId) {
        document.querySelectorAll('.setup-pane').forEach(el => el.classList.add('hidden'));
        document.getElementById(`setup-${tabId}`).classList.remove('hidden');
        document.querySelectorAll('.setup-tab').forEach(el => {
            el.classList.remove('text-accent', 'border-b-2', 'border-accent');
            el.classList.add('text-slate-400');
        });
        const activeTab = document.querySelector(`.setup-tab[onclick="app.switchSetupTab('${tabId}')"]`);
        if(activeTab) {
            activeTab.classList.remove('text-slate-400');
            activeTab.classList.add('text-accent', 'border-b-2', 'border-accent');
        }
    },

    async pollSettings() {
        try {
            const res = await fetch('/api/settings');
            this.state.settings = await res.json();
            document.getElementById('set-rssi-1m').value = this.state.settings.rssi_1m || -55;
            document.getElementById('set-path-loss').value = this.state.settings.path_loss || 2.5;
            document.getElementById('set-local-ip').value = this.state.settings.local_ip || '192.168.1.100';
            document.getElementById('set-host-name').value = this.state.settings.host_name || 'TrackerProServer';
            document.getElementById('set-map-url').value = this.state.settings.map_url || 'https://via.placeholder.com/1000x1000/1e293b/38bdf8?text=Indoor+Floorplan+Layout';
            document.getElementById('global-mode').value = this.state.settings.global_mode || 'esp32';
        } catch(e) {}
    },

    async saveSettings(e) {
        if(e) e.preventDefault();
        const payload = {
            rssi_1m: document.getElementById('set-rssi-1m').value,
            path_loss: document.getElementById('set-path-loss').value,
            local_ip: document.getElementById('set-local-ip').value,
            host_name: document.getElementById('set-host-name').value,
            map_url: document.getElementById('set-map-url').value
        };
        await fetch('/api/settings', {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
        });
        alert("Global configuration saved successfully!");
    },
    
    async saveGlobalMode(mode) {
        await fetch('/api/settings', {
            method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({global_mode: mode})
        });
    },

    async pollData() {
        try {
            const [nodesRes, tagsRes, posRes] = await Promise.all([
                fetch('/api/nodes'), fetch('/api/tags'), fetch('/api/positions')
            ]);
            this.state.nodes = await nodesRes.json();
            this.state.tags = await tagsRes.json();
            this.state.positions = await posRes.json();
            
            const now = new Date();
            this.state.nodes.forEach(n => {
                if(!n.last_seen) { n.isOnline = false; return; }
                const dt = new Date(n.last_seen + 'Z'); 
                n.isOnline = (now - dt) < 50000;
            });
            
            this.updateDashboard();
            this.renderSetupTables();
            this.updateMapMarkers();
        } catch(e) {}
    },

    updateDashboard() {
        const totalTags = this.state.tags.length;
        const totalNodes = this.state.nodes.length;
        const nodesOnline = this.state.nodes.filter(n => n.isOnline).length;
        const nodesOffline = totalNodes - nodesOnline;
        
        const activePositions = this.state.positions;
        const lowConfTags = activePositions.filter(p => p.confidence < 50).length;
        
        const sumConf = activePositions.reduce((sum, p) => sum + p.confidence, 0);
        const avgConf = activePositions.length ? Math.round(sumConf / activePositions.length) : 0;
        
        document.getElementById('war-total-tags').innerText = totalTags;
        document.getElementById('war-total-nodes').innerText = totalNodes;
        document.getElementById('war-nodes-online').innerText = nodesOnline;
        document.getElementById('war-nodes-offline').innerText = nodesOffline;
        document.getElementById('war-tags-active').innerText = activePositions.length;
        document.getElementById('war-tags-low-conf').innerText = lowConfTags;
        document.getElementById('war-avg-conf').innerText = avgConf + '%';
        
        document.getElementById('war-last-update').innerText = new Date().toLocaleTimeString();
        document.getElementById('war-active-mode').innerText = (this.state.settings.global_mode || 'ESP32').toUpperCase();

        document.getElementById('war-tags-tbody').innerHTML = activePositions.length === 0 
            ? `<tr><td colspan="4" class="text-center py-4 text-slate-500">No active telemetry</td></tr>`
            : activePositions.map(p => {
                const confColor = p.confidence > 70 ? 'text-green-400' : (p.confidence > 40 ? 'text-yellow-400' : 'text-alert');
                const rssiDisplay = p.rssi ? `${p.rssi} dBm` : 'N/A';
                return `
                <tr class="border-b border-slate-700/50 hover:bg-slate-800/30">
                    <td class="px-4 py-3 font-medium text-white">${p.name} <span class="text-[10px] text-slate-500 block mt-0.5">${p.mac} &bull; Seen: ${p.last_seen || 'Connecting...'}</span></td>
                    <td class="px-4 py-3 font-mono text-slate-400 text-xs text-accent">(${p.x}, ${p.y})</td>
                    <td class="px-4 py-3 font-mono text-slate-400 text-xs">${rssiDisplay}</td>
                    <td class="px-4 py-3 text-right font-bold ${confColor}">${p.confidence}%</td>
                </tr>`
            }).join('');
            
        document.getElementById('war-nodes-tbody').innerHTML = this.state.nodes.length === 0
            ? `<tr><td colspan="3" class="text-center py-4 text-slate-500">No nodes registered</td></tr>`
            : this.state.nodes.map(n => {
                const status = n.isOnline 
                    ? `<span class="bg-green-500/10 text-green-400 px-2 py-0.5 rounded border border-green-500/20 text-[10px] uppercase font-bold flex items-center gap-1 inline-flex"><div class="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></div> Online</span>`
                    : `<span class="bg-alert/10 text-alert px-2 py-0.5 rounded border border-alert/20 text-[10px] uppercase font-bold">Offline</span>`;
                return `
                <tr class="border-b border-slate-700/50 hover:bg-slate-800/30">
                    <td class="px-4 py-3 text-white"><div class="font-medium text-sm">${n.name}</div><div class="text-[10px] text-slate-500 font-mono mt-0.5">${n.mac} &bull; Seen: ${n.last_seen || 'Offline'}</div></td>
                    <td class="px-4 py-3 text-slate-400 text-xs uppercase">${n.role} / ${n.mode}</td>
                    <td class="px-4 py-3 text-right">${status}</td>
                </tr>`
            }).join('');

        if(this.state.chartInstance) {
            const chart = this.state.chartInstance;
            chart.data.labels.push(new Date().toLocaleTimeString());
            chart.data.datasets[0].data.push(activePositions.length); 
            if(chart.data.labels.length > 20) { chart.data.labels.shift(); chart.data.datasets[0].data.shift(); }
            chart.update('none');
        }
    },

    initChart() {
        const ctx = document.getElementById('activityChart').getContext('2d');
        Chart.defaults.color = '#94a3b8';
        this.state.chartInstance = new Chart(ctx, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'Active Targets', data: [], borderColor: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.1)', borderWidth: 2, fill: true, tension: 0.4 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false } } }
        });
    },

    initMap() {
        this.map = L.map('leaflet-map', { crs: L.CRS.Simple, minZoom: -2, maxZoom: 2, attributionControl: false });
        const bounds = [[0,0], [1000,1000]];
        const mapUrl = this.state.settings.map_url || 'https://via.placeholder.com/1000x1000/1e293b/38bdf8?text=Indoor+Floorplan+Layout';
        L.imageOverlay(mapUrl, bounds).addTo(this.map);
        this.map.fitBounds(bounds);
        this.map.setZoom(-1);
        
        this.nodeLayer = L.layerGroup().addTo(this.map);
        this.tagLayer = L.layerGroup().addTo(this.map);
        
        document.getElementById('toggle-nodes').addEventListener('change', (e) => e.target.checked ? this.map.addLayer(this.nodeLayer) : this.map.removeLayer(this.nodeLayer));
        document.getElementById('toggle-tags').addEventListener('change', (e) => e.target.checked ? this.map.addLayer(this.tagLayer) : this.map.removeLayer(this.tagLayer));
    },

    updateMapMarkers() {
        if(!this.map) return;
        this.nodeLayer.clearLayers();
        this.state.nodes.forEach(n => {
            const icon = L.divIcon({ className: n.isOnline ? 'pulse-marker-node' : 'pulse-marker-node opacity-40', iconSize: [16, 16] });
            L.marker([n.y * 10, n.x * 10], {icon}).bindTooltip(n.name, {permanent:true, className: 'bg-slate-800 text-white text-[10px] border border-slate-700 mt-2 px-1 py-0.5', direction: 'top', offset: [0,-10]}).addTo(this.nodeLayer);
        });

        this.tagLayer.clearLayers();
        this.state.positions.forEach(p => {
            const colorClass = p.confidence > 70 ? 'bg-green-400' : (p.confidence > 40 ? 'bg-yellow-400' : 'bg-alert');
            const icon = L.divIcon({ className: `flex items-center justify-center w-3 h-3 rounded-full ${colorClass} shadow-[0_0_10px_rgba(56,189,248,0.8)] border border-slate-900`, iconSize: [12, 12] });
            L.marker([p.y * 10, p.x * 10], {icon}).bindTooltip(p.name, {permanent:true, className:'bg-transparent border-0 text-white font-bold text-xs shadow-none', direction: 'bottom', offset: [0,8]}).addTo(this.tagLayer);
        });
    },

    renderSetupTables() {
        const tbodyNodes = document.getElementById('nodes-table-body');
        tbodyNodes.innerHTML = this.state.nodes.length === 0 ? `<tr><td colspan="5" class="py-4 text-center text-slate-500">No nodes</td></tr>` : this.state.nodes.map(n => {
            const status = n.isOnline ? `<span class="text-green-400">Online ping</span>` : `<span class="text-alert">Offline link</span>`;
            return `
            <tr class="border-b border-slate-700/50 hover:bg-slate-800/30">
                <td class="px-6 py-4 font-medium text-white">${n.name}</td>
                <td class="px-6 py-4">
                    <div class="text-xs font-mono text-slate-400 mb-1">${n.mac}</div>
                    <div class="flex gap-1 text-[10px] uppercase font-bold text-accent"><span class="bg-slate-800 px-1 rounded">${n.role}</span><span class="bg-slate-800 px-1 rounded">${n.mobility}</span></div>
                </td>
                <td class="px-6 py-4 text-sm">(${n.x}, ${n.y})</td>
                <td class="px-6 py-4 text-xs font-medium">${status}</td>
                <td class="px-6 py-4 text-right">
                    <button onclick="app.showNodeConfig('${n.mac}')" class="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-accent text-xs rounded border border-slate-600 font-bold">Package Generator</button>
                    <button onclick="app.showNodeModal('${n.mac}')" class="px-2 py-1 text-slate-400 text-xs ml-1 hover:text-white">Edit</button>
                </td>
            </tr>
        `}).join('');

        const tbodyTags = document.getElementById('tags-table-body');
        tbodyTags.innerHTML = this.state.tags.length === 0 ? `<tr><td colspan="4" class="py-4 text-center text-slate-500">No tags</td></tr>` : this.state.tags.map(t => {
            const bindInfo = t.machine ? `<br><span class="text-xs text-slate-400">Bind: ${t.machine}</span>` : '';
            return `
            <tr class="border-b border-slate-700/50 hover:bg-slate-800/30">
                <td class="px-6 py-4">
                    <div class="font-medium text-white">${t.name}</div>
                    <div class="text-xs text-slate-400 mt-1">${t.mac}</div>
                    ${bindInfo}
                </td>
                <td class="px-6 py-4"><span class="text-xs bg-slate-800 text-slate-300 px-2 py-1 rounded inline-block border border-slate-700">${t.category}</span></td>
                <td class="px-6 py-4 text-sm text-slate-300">${t.interval} ms</td>
                <td class="px-6 py-4 text-right">
                    <button onclick="app.showTagConfig('${t.mac}')" class="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-green-400 text-xs rounded border border-slate-600 font-bold">OTA Flash</button>
                    <button onclick="app.showTagModal('${t.mac}')" class="px-2 py-1 text-slate-400 text-xs ml-1 hover:text-white">Edit</button>
                </td>
            </tr>
        `}).join('');
    },

    showModal(id) {
        document.getElementById(id).classList.remove('hidden');
    },
    hideModal(id) {
        document.getElementById(id).classList.add('hidden');
    },

    showNodeModal(mac) {
        let n = this.state.nodes.find(x => x.mac === mac) || { mac: '', name: '', role: 'anchor', mobility: 'fixed', x: 0, y: 0, mode: 'esp32' };
        document.getElementById('node-mac').value = n.mac;
        document.getElementById('node-name').value = n.name;
        document.getElementById('node-role').value = n.role;
        document.getElementById('node-mobility').value = n.mobility;
        document.getElementById('node-x').value = n.x;
        document.getElementById('node-y').value = n.y;
        document.getElementById('node-mode').value = n.mode;
        this.showModal('node-modal');
    },

    async submitNode(e) {
        e.preventDefault();
        await fetch('/api/nodes', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                mac: document.getElementById('node-mac').value,
                name: document.getElementById('node-name').value,
                role: document.getElementById('node-role').value,
                mobility: document.getElementById('node-mobility').value,
                x: parseFloat(document.getElementById('node-x').value) || 0,
                y: parseFloat(document.getElementById('node-y').value) || 0,
                mode: document.getElementById('node-mode').value
            })
        });
        this.hideModal('node-modal');
        this.pollData();
    },

    showTagModal(mac) {
        let t = this.state.tags.find(x => x.mac === mac) || { mac: '', name: '', machine: '', category: 'Asset', interval: 500 };
        document.getElementById('tag-mac').value = t.mac;
        document.getElementById('tag-name').value = t.name;
        document.getElementById('tag-machine').value = t.machine || '';
        document.getElementById('tag-category').value = t.category;
        document.getElementById('tag-interval').value = t.interval;
        this.showModal('tag-modal');
    },

    async submitTag(e) {
        e.preventDefault();
        await fetch('/api/tags', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                mac: document.getElementById('tag-mac').value,
                name: document.getElementById('tag-name').value,
                machine: document.getElementById('tag-machine').value,
                category: document.getElementById('tag-category').value,
                interval: parseInt(document.getElementById('tag-interval').value) || 500
            })
        });
        this.hideModal('tag-modal');
        this.pollData();
    },

    async showNodeConfig(mac) {
        const res = await fetch(`/api/config/node/${mac}`);
        this.populateWizard(await res.json());
    },
    async showTagConfig(mac) {
        const res = await fetch(`/api/config/tag/${mac}`);
        this.populateWizard(await res.json());
    },

    populateWizard(data) {
        if(data.error) return alert(data.error);
        document.getElementById('config-code').innerText = data.snippet;
        document.getElementById('config-json').innerText = data.json;
        document.getElementById('config-filename').value = data.filename;
        const q = document.getElementById('qrcode-container');
        q.innerHTML = '';
        if(window.QRCode) { new QRCode(q, { text: data.json, width: 220, height: 220, colorDark: "#0f172a", colorLight: "#ffffff" }); }
        this.switchConfigTab('snippet');
        this.showModal('config-modal');
    },

    switchConfigTab(tabId) {
        document.querySelectorAll('.config-pane').forEach(el => el.classList.add('hidden'));
        document.getElementById(`tab-${tabId}`).classList.remove('hidden');
        document.querySelectorAll('#config-modal .config-tab').forEach(el => {
            el.classList.remove('text-accent','border-b-2','border-accent'); el.classList.add('text-slate-400');
        });
        const active = document.querySelector(`#config-modal .config-tab[onclick*="'${tabId}'"]`);
        if(active) { active.classList.remove('text-slate-400'); active.classList.add('text-accent','border-b-2','border-accent'); }
    },

    downloadJSON() { this.dlFile(document.getElementById('config-json').innerText, 'config.json', 'application/json'); },
    downloadSource() { this.dlFile(document.getElementById('config-code').innerText, document.getElementById('config-filename').value, 'text/plain'); },
    dlFile(content, name, type) {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(new Blob([content], {type})); a.download = name; a.click();
    }
};

window.onload = () => app.init();
