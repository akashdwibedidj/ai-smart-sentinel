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

// ==================== REAL-TIME UPDATES (SIMULATED) ====================
function simulateRealTimeUpdates() {
    // Simulate random alert appearing
    setInterval(() => {
        const alertTypes = [
            { type: 'safe', title: 'Access Granted', icon: 'check' },
            { type: 'warning', title: 'Suspicious Movement Detected', icon: 'warning' },
            { type: 'danger', title: 'Spoof Attempt Blocked', icon: 'x' }
        ];

        // 30% chance of new alert
        if (Math.random() > 0.7) {
            const randomAlert = alertTypes[Math.floor(Math.random() * alertTypes.length)];
            console.log(`New alert: ${randomAlert.title}`);

            // Update blocked threats counter occasionally
            if (randomAlert.type === 'danger') {
                const threatCounter = document.getElementById('blockedThreats');
                if (threatCounter) {
                    const currentValue = parseInt(threatCounter.textContent);
                    threatCounter.textContent = currentValue + 1;
                    threatCounter.style.animation = 'none';
                    setTimeout(() => {
                        threatCounter.style.animation = 'pulse 0.5s ease';
                    }, 10);
                }
            }
        }
    }, 30000); // Every 30 seconds
}

// ==================== INITIALIZE ====================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize activity graph
    new ActivityGraph('activityCanvas');

    // Initialize emergency lockdown
    initEmergencyLockdown();

    // Start simulated updates
    simulateRealTimeUpdates();

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
`;
document.head.appendChild(style);
