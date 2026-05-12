// Network Visualization App
class NetworkVisualizer {
    constructor() {
        this.canvas = document.getElementById('networkCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.isRunning = false;
        this.time = 0;
        this.speed = 1;
        this.zoom = 1;
        this.zoomMin = 0.5;
        this.zoomMax = 3;
        this.panX = 0;
        this.panY = 0;
        this.isDragging = false;
        this.dragStartX = 0;
        this.dragStartY = 0;

        // Layers
        this.layers = {
            grid: true
        };

        this.initializeCanvas();
        this.attachEventListeners();
        this.loadSettings();
        this.render();
    }

    initializeCanvas() {
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    resizeCanvas() {
        const container = document.getElementById('canvas-container');
        this.canvas.width = container.clientWidth;
        this.canvas.height = container.clientHeight;
        this.render();
    }

    render() {
        // Clear canvas
        const isDark = !document.body.classList.contains('light-mode');
        this.ctx.fillStyle = isDark ? '#0a0f1a' : '#f8fafc';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Save context state for transformations
        this.ctx.save();

        // Apply pan and zoom transformations
        this.ctx.translate(this.panX, this.panY);
        this.ctx.scale(this.zoom, this.zoom);

        // Draw layers
        if (this.layers.grid) {
            this.drawGrid();
        }

        // Restore context state
        this.ctx.restore();

        // Draw placeholder text (not affected by pan/zoom)
        this.ctx.fillStyle = isDark ? '#64748b' : '#94a3b8';
        this.ctx.font = '14px -apple-system, BlinkMacSystemFont, "Segoe UI"';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('Network visualization will appear here', this.canvas.width / 2, this.canvas.height / 2);
    }

    drawGrid() {
        const isDark = !document.body.classList.contains('light-mode');
        this.ctx.strokeStyle = isDark ? '#1e293b' : '#e2e8f0';
        this.ctx.lineWidth = 1 / this.zoom;
        const gridSize = 50;

        // Calculate visible range considering pan and zoom
        const startX = Math.floor(-this.panX / this.zoom / gridSize) * gridSize;
        const startY = Math.floor(-this.panY / this.zoom / gridSize) * gridSize;
        const endX = startX + (this.canvas.width / this.zoom) + gridSize;
        const endY = startY + (this.canvas.height / this.zoom) + gridSize;

        for (let i = startX; i < endX; i += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(i, startY);
            this.ctx.lineTo(i, endY);
            this.ctx.stroke();
        }

        for (let i = startY; i < endY; i += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(startX, i);
            this.ctx.lineTo(endX, i);
            this.ctx.stroke();
        }
    }

    attachEventListeners() {
        // Play/Pause toggle
        document.getElementById('btn-play-pause').addEventListener('click', () => {
            this.togglePlayPause();
        });

        // Reset button
        document.getElementById('btn-reset').addEventListener('click', () => {
            this.reset();
        });

        // Speed control
        document.getElementById('speed-control').addEventListener('change', (e) => {
            this.speed = parseFloat(e.target.value);
        });

        // Canvas mouse wheel for zoom
        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomDelta = e.deltaY > 0 ? -0.1 : 0.1;
            this.zoom = Math.max(this.zoomMin, Math.min(this.zoomMax, this.zoom + zoomDelta));
            this.render();
        });

        // Canvas drag for pan
        this.canvas.addEventListener('mousedown', (e) => {
            this.isDragging = true;
            this.dragStartX = e.clientX;
            this.dragStartY = e.clientY;
        });

        this.canvas.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                const deltaX = e.clientX - this.dragStartX;
                const deltaY = e.clientY - this.dragStartY;
                this.panX += deltaX;
                this.panY += deltaY;
                this.dragStartX = e.clientX;
                this.dragStartY = e.clientY;
                this.render();
            }
        });

        this.canvas.addEventListener('mouseup', () => {
            this.isDragging = false;
        });

        this.canvas.addEventListener('mouseleave', () => {
            this.isDragging = false;
        });

        // Layer toggles
        document.querySelectorAll('.layer-toggle').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const layer = e.target.dataset.layer;
                this.layers[layer] = !this.layers[layer];
                e.target.classList.toggle('active');
                this.render();
            });
        });

        // Help button - open settings
        document.getElementById('btn-help').addEventListener('click', () => {
            this.openSettings();
        });

        // Modal close button
        document.getElementById('btn-close-settings').addEventListener('click', () => {
            this.closeSettings();
        });

        // Light mode toggle
        document.getElementById('toggle-dark-mode').addEventListener('click', () => {
            this.toggleLightMode();
        });
    }

    togglePlayPause() {
        this.isRunning = !this.isRunning;
        this.updateUI();
    }

    updateUI() {
        const statusEl = document.getElementById('info-status-badge');
        const playBtn = document.getElementById('btn-play-pause');
        let status = 'Not Ready';
        let className = 'not-ready';

        if (this.isRunning) {
            status = 'Running';
            className = 'running';
            playBtn.textContent = '⏸';
        } else if (this.time > 0) {
            status = 'Paused';
            className = 'paused';
            playBtn.textContent = '▶';
        } else {
            playBtn.textContent = '▶';
        }

        statusEl.className = `status-badge ${className}`;
        statusEl.innerHTML = `<span class="indicator"></span><span>${status}</span>`;
    }

    reset() {
        this.isRunning = false;
        this.time = 0;
        this.zoom = 1;
        this.panX = 0;
        this.panY = 0;
        this.resetStats();
        this.updateUI();
        this.render();
    }

    resetStats() {
        document.getElementById('info-time').textContent = '0.00s';
        document.getElementById('info-nodes').textContent = '10';
        document.getElementById('info-uavs').textContent = '1';
        document.getElementById('info-links').textContent = '0';
        document.getElementById('info-tx').textContent = '0';
        document.getElementById('info-rx').textContent = '0';
        document.getElementById('info-confidence').textContent = '0%';
        document.getElementById('confidence-bar').style.width = '0%';
        document.getElementById('info-fragments').textContent = '0/10';
        document.getElementById('fragment-bar').style.width = '0%';
        document.getElementById('info-uav-pos').textContent = '(-200, -200)';
        document.getElementById('info-uav-alt').textContent = '20m';
    }


    openSettings() {
        document.getElementById('settings-modal').classList.add('active');
    }

    closeSettings() {
        document.getElementById('settings-modal').classList.remove('active');
    }

    toggleLightMode() {
        document.body.classList.toggle('light-mode');
        const toggle = document.getElementById('toggle-dark-mode');
        toggle.classList.toggle('active');

        // Save preference
        const isLightMode = document.body.classList.contains('light-mode');
        localStorage.setItem('wsn-light-mode', isLightMode);

        this.render();
    }

    loadSettings() {
        const isLightMode = localStorage.getItem('wsn-light-mode') === 'true';
        if (isLightMode) {
            document.body.classList.add('light-mode');
            document.getElementById('toggle-dark-mode').classList.add('active');
        }
    }

    startSimulation() {
        setInterval(() => {
            if (this.isRunning) {
                this.time += 0.1 * this.speed;
                this.updateStats();
            }
        }, 100);
    }

    updateStats() {
        // Update time
        document.getElementById('info-time').textContent = this.time.toFixed(2) + 's';

        // Simulate confidence growth
        const confidence = Math.min(100, this.time * 15);
        document.getElementById('info-confidence').textContent = Math.floor(confidence) + '%';
        document.getElementById('confidence-bar').style.width = confidence + '%';

        // Simulate fragment reception
        const fragments = Math.floor(Math.min(10, this.time * 2));
        document.getElementById('info-fragments').textContent = fragments + '/10';
        document.getElementById('fragment-bar').style.width = (fragments / 10 * 100) + '%';

        // Check for detection
        const detectionBadge = document.getElementById('info-detection-status');
        if (confidence >= 75 && detectionBadge.textContent !== 'Detected') {
            detectionBadge.textContent = 'Detected';
            detectionBadge.className = 'badge badge-success';
            document.getElementById('info-status-badge').className = 'status-badge detected';
            document.getElementById('info-status-badge').innerHTML = '<span class="indicator"></span><span>Detected</span>';
            this.isRunning = false;
            this.updateUI();
        }
    }
}

// Initialize app on page load
document.addEventListener('DOMContentLoaded', () => {
    const app = new NetworkVisualizer();
    app.startSimulation();
});
