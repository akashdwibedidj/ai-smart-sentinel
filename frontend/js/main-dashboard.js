/**
 * AI Smart Sentinel - Main Dashboard
 * Interactive JavaScript for dashboard functionality
 */

// ==================== ACTIVITY GRAPH ====================
class ActivityGraph {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.data = this.generateData();
        this.animationProgress = 0;

        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.animate();
    }

    resize() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
    }

    generateData() {
        // Generate 24 hours of mock activity data
        const points = 48;
        const data = [];
        for (let i = 0; i < points; i++) {
            // Create realistic peaks during work hours
            const hour = (i / 2) % 24;
            let base = 0.2;
            if (hour >= 8 && hour <= 18) base = 0.5;
            if (hour >= 9 && hour <= 12) base = 0.7;
            if (hour >= 14 && hour <= 17) base = 0.6;

            data.push(base + Math.random() * 0.3);
        }
        return data;
    }

    draw() {
        const { ctx, canvas, data } = this;
        const width = canvas.width;
        const height = canvas.height;
        const padding = 20;

        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        // Draw gradient fill
        const gradient = ctx.createLinearGradient(0, padding, 0, height - padding);
        gradient.addColorStop(0, 'rgba(0, 212, 255, 0.3)');
        gradient.addColorStop(1, 'rgba(0, 212, 255, 0.0)');

        // Draw area
        ctx.beginPath();
        ctx.moveTo(padding, height - padding);

        const stepX = (width - padding * 2) / (data.length - 1);

        data.forEach((value, i) => {
            const x = padding + i * stepX;
            const y = height - padding - (value * (height - padding * 2) * this.animationProgress);

            if (i === 0) {
                ctx.lineTo(x, y);
            } else {
                // Smooth curve
                const prevX = padding + (i - 1) * stepX;
                const prevY = height - padding - (data[i - 1] * (height - padding * 2) * this.animationProgress);
                const cpX = (prevX + x) / 2;
                ctx.quadraticCurveTo(prevX, prevY, cpX, (prevY + y) / 2);
                ctx.quadraticCurveTo(cpX, (prevY + y) / 2, x, y);
            }
        });

        ctx.lineTo(width - padding, height - padding);
        ctx.closePath();
        ctx.fillStyle = gradient;
        ctx.fill();

        // Draw line
        ctx.beginPath();
        data.forEach((value, i) => {
            const x = padding + i * stepX;
            const y = height - padding - (value * (height - padding * 2) * this.animationProgress);

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                const prevX = padding + (i - 1) * stepX;
                const prevY = height - padding - (data[i - 1] * (height - padding * 2) * this.animationProgress);
                const cpX = (prevX + x) / 2;
                ctx.quadraticCurveTo(prevX, prevY, cpX, (prevY + y) / 2);
                ctx.quadraticCurveTo(cpX, (prevY + y) / 2, x, y);
            }
        });

        ctx.strokeStyle = '#00D4FF';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Draw dots at data points (every 4th point)
        data.forEach((value, i) => {
            if (i % 4 !== 0) return;

            const x = padding + i * stepX;
            const y = height - padding - (value * (height - padding * 2) * this.animationProgress);

            ctx.beginPath();
            ctx.arc(x, y, 3, 0, Math.PI * 2);
            ctx.fillStyle = '#00D4FF';
            ctx.fill();
        });
    }

    animate() {
        if (this.animationProgress < 1) {
            this.animationProgress += 0.02;
            this.draw();
            requestAnimationFrame(() => this.animate());
        } else {
            this.animationProgress = 1;
            this.draw();
        }
    }
}

// ==================== EMERGENCY LOCKDOWN ====================
function initEmergencyLockdown() {
    const btn = document.getElementById('emergencyLockdown');
    if (!btn) return;

    btn.addEventListener('click', () => {
        const confirmed = confirm(
            '⚠️ EMERGENCY LOCKDOWN\n\n' +
            'This will immediately:\n' +
            '• Block all access points\n' +
            '• Alert security personnel\n' +
            '• Log all current sessions\n\n' +
            'Are you sure you want to proceed?'
        );

        if (confirmed) {
            btn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 6v6l4 2"/>
        </svg>
        LOCKDOWN ACTIVE
      `;
            btn.disabled = true;
            btn.style.background = 'var(--accent-red)';
            btn.style.color = 'white';

            // In real implementation, this would call the backend API
            console.log('🔒 Emergency lockdown triggered');
        }
    });
}

// ==================== FETCH REAL STATISTICS ====================
async function fetchDashboardData() {
    // Check if ApiService is available
    if (typeof ApiService === 'undefined') {
        console.warn('ApiService not loaded, using simulated data');
        return;
    }

    try {
        // Fetch statistics from backend
        const stats = await ApiService.getStatistics();

        // Update status cards with real data
        const elementsMap = {
            'accessAttempts': stats.total_attempts || 0,
            'blockedThreats': stats.blocked_threats || stats.denied || 0
        };

        Object.entries(elementsMap).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el) {
                el.textContent = value;
                // Animate the update
                el.style.animation = 'none';
                setTimeout(() => el.style.animation = 'pulse 0.5s ease', 10);
            }
        });

        console.log('📊 Dashboard stats updated from backend');
    } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
    }
}

// ==================== FETCH RECENT ALERTS ====================
async function fetchRecentAlerts() {
    if (typeof ApiService === 'undefined') return;

    try {
        const result = await ApiService.getLogs(5);
        const alertsList = document.getElementById('alertsList');

        if (alertsList && result.logs && result.logs.length > 0) {
            alertsList.innerHTML = '';

            result.logs.forEach(log => {
                const alertItem = document.createElement('div');
                alertItem.className = `alert-item ${log.access_granted ? 'success' : 'danger'}`;

                const time = new Date(log.timestamp).toLocaleTimeString();
                const icon = log.access_granted ? '✓' : '✕';
                const title = log.access_granted ? 'Access Granted' : log.denial_reason || 'Access Denied';

                alertItem.innerHTML = `
                    <span class="alert-icon">${icon}</span>
                    <div class="alert-content">
                        <span class="alert-title">${title}</span>
                        <span class="alert-time">${time}</span>
                    </div>
                `;
                alertsList.appendChild(alertItem);
            });

            console.log('🔔 Alerts updated from backend');
        }
    } catch (error) {
        console.error('Failed to fetch alerts:', error);
    }
}

// ==================== CHECK CONNECTION STATUS ====================
async function checkBackendConnection() {
    if (typeof ConnectionStatus === 'undefined') return;

    const isOnline = await ConnectionStatus.check();
    ConnectionStatus.updateUI();

    console.log(`🔌 Backend status: ${isOnline ? 'Online' : 'Offline'}`);
    return isOnline;
}

// ==================== REAL-TIME UPDATES ====================
function startRealTimeUpdates() {
    // Initial fetch
    fetchDashboardData();
    fetchRecentAlerts();

    // Refresh every 30 seconds
    setInterval(() => {
        fetchDashboardData();
        fetchRecentAlerts();
    }, 30000);
}

// ==================== INITIALIZE ====================
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize activity graph
    new ActivityGraph('activityCanvas');

    // Initialize emergency lockdown
    initEmergencyLockdown();

    // Check backend connection
    const isOnline = await checkBackendConnection();

    if (isOnline) {
        // Start real-time updates with backend data
        startRealTimeUpdates();
    } else {
        console.warn('⚠️ Backend offline - using static data');
    }

    // Add loading complete class
    document.body.classList.add('loaded');

    console.log('🛡️ AI Smart Sentinel Dashboard Initialized');
});

// Add spinning animation for loading states
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  .spin {
    animation: spin 1s linear infinite;
  }
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }
`;
document.head.appendChild(style);

